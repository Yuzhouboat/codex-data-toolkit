#!/usr/bin/env node
// Credentials are parsed as literal data, never evaluated as shell code.
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawn, execFileSync } from 'node:child_process';
import { fileURLToPath, pathToFileURL } from 'node:url';

const groups = {
  mysql: ['MYSQL_HOST', 'MYSQL_PORT', 'MYSQL_DATABASE', 'MYSQL_USER', 'MYSQL_PASSWORD'],
  aws: ['AWS_AUTH_MODE', 'AWS_PROFILE', 'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_SESSION_TOKEN'],
  github: ['GITHUB_PERSONAL_ACCESS_TOKEN'],
};
const keys = new Set(Object.values(groups).flat());
const defaultDirectory = path.join(os.homedir(), '.config', 'codex-data-toolkit');

function fail(message) { throw new Error(message); }

function exists(file) {
  try { fs.lstatSync(file); return true; }
  catch (error) { if (error.code === 'ENOENT') return false; throw error; }
}

function checkPrivate(file, directory = false) {
  const stat = fs.lstatSync(file);
  if (stat.isSymbolicLink() || (directory ? !stat.isDirectory() : !stat.isFile())) {
    fail('Credential storage must use regular files and directories, not symbolic links.');
  }
  if (stat.uid !== process.getuid() || (stat.mode & 0o077)) {
    fail('Credential storage must belong to you with directory mode 700 and file mode 600.');
  }
}

export function prepare(directory = defaultDirectory) {
  // Reject symlinked ancestors before creating or opening credential storage.
  let current = path.parse(path.resolve(directory)).root;
  for (const part of path.resolve(directory).split(path.sep).filter(Boolean)) {
    current = path.join(current, part);
    if (exists(current) && fs.lstatSync(current).isSymbolicLink()) {
      fail('Credential storage must not pass through symbolic links.');
    }
  }
  fs.mkdirSync(directory, { recursive: true, mode: 0o700 });
  checkPrivate(directory, true);
  const file = path.join(directory, 'credentials.env');
  if (exists(file)) checkPrivate(file);
  return file;
}

export function parse(text) {
  const result = {};
  for (const line of text.split('\n')) {
    if (!line) continue;
    const index = line.indexOf('=');
    const key = line.slice(0, index);
    if (index < 1 || !keys.has(key) || Object.hasOwn(result, key) || /[\r\0]/.test(line)) {
      fail('Malformed credential file; rerun setup. Values must be single-line text.');
    }
    result[key] = line.slice(index + 1);
  }
  return result;
}

export function load(directory = defaultDirectory) {
  // Missing storage is normal for users who supply credentials through the environment.
  if (!exists(directory)) return {};
  const file = prepare(directory);
  return fs.existsSync(file) ? parse(fs.readFileSync(file, 'utf8')) : {};
}

function requireValues(values, required) {
  const missing = required.filter(key => !values[key]);
  if (missing.length) fail(`Missing ${missing.join(', ')}. Run the setup wizard.`);
}

export function save(service, input, directory = defaultDirectory) {
  if (!groups[service]) fail('Unknown service.');
  const existing = load(directory);
  const selected = Object.fromEntries(groups[service].filter(key => Object.hasOwn(input, key)).map(key => [key, input[key]]));
  if (service === 'mysql') {
    requireValues(selected, groups.mysql);
    if (!/^\d+$/.test(selected.MYSQL_PORT) || Number(selected.MYSQL_PORT) < 1 || Number(selected.MYSQL_PORT) > 65535) {
      fail('MYSQL_PORT must be a number between 1 and 65535.');
    }
  } else if (service === 'github') {
    requireValues(selected, groups.github);
  } else if (selected.AWS_AUTH_MODE === 'profile') {
    requireValues(selected, ['AWS_PROFILE']);
    delete selected.AWS_ACCESS_KEY_ID;
    delete selected.AWS_SECRET_ACCESS_KEY;
    delete selected.AWS_SESSION_TOKEN;
  } else if (selected.AWS_AUTH_MODE === 'keys') {
    requireValues(selected, ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY']);
    delete selected.AWS_PROFILE;
  } else fail('Choose AWS profile or access-key authentication.');
  for (const key of groups[service]) delete existing[key];
  Object.assign(existing, selected);
  for (const value of Object.values(existing)) {
    if (typeof value !== 'string' || /[\n\r\0]/.test(value)) fail('Credentials must be single-line text.');
  }
  const file = prepare(directory);
  const temporary = path.join(directory, `.credentials-${process.pid}-${Date.now()}`);
  try {
    fs.writeFileSync(temporary, Object.entries(existing).map(([key, value]) => `${key}=${value}\n`).join(''), { flag: 'wx', mode: 0o600 });
    fs.renameSync(temporary, file);
  } finally {
    if (fs.existsSync(temporary)) fs.unlinkSync(temporary);
  }
}

export function environment(service, stored, inherited = process.env) {
  const env = { ...inherited };
  const selected = service === 'app' ? groups.github : groups[service];
  if (!selected) fail('Unknown service.');
  for (const key of selected) {
    if (key !== 'AWS_AUTH_MODE' && Object.hasOwn(stored, key)) env[key] = stored[key];
  }
  if (service === 'aws' && stored.AWS_AUTH_MODE === 'profile') {
    for (const key of ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_SESSION_TOKEN', 'AWS_DEFAULT_PROFILE', 'AWS_WEB_IDENTITY_TOKEN_FILE', 'AWS_ROLE_ARN']) delete env[key];
  } else if (service === 'aws' && stored.AWS_AUTH_MODE === 'keys') {
    for (const key of ['AWS_PROFILE', 'AWS_DEFAULT_PROFILE', 'AWS_WEB_IDENTITY_TOKEN_FILE', 'AWS_ROLE_ARN']) delete env[key];
    if (!stored.AWS_SESSION_TOKEN) delete env.AWS_SESSION_TOKEN;
  }
  if (service === 'mysql') requireValues(env, groups.mysql);
  if (service === 'app') requireValues(env, groups.github);
  return env;
}

export function serverCommand(service) {
  if (service === 'mysql') return ['npx', ['-y', '@toolbox-sdk/server@1.16.0', '--prebuilt', 'mysql', '--stdio']];
  if (service === 'aws') return ['uvx', ['mcp-proxy-for-aws@1.6.3', 'https://aws-mcp.us-east-1.api.aws/mcp']];
  fail('Unknown service.');
}

function appExecutable(explicit) {
  if (process.platform !== 'darwin') fail('The app launcher currently supports macOS only.');
  let bundle = explicit;
  if (!bundle) {
    const matches = execFileSync('/usr/bin/mdfind', ['kMDItemCFBundleIdentifier == "com.openai.codex"'], { encoding: 'utf8' }).trim().split('\n');
    const candidates = ['/Applications/ChatGPT.app', path.join(os.homedir(), 'Applications/ChatGPT.app'), ...matches];
    bundle = candidates.find(candidate => {
      if (!candidate || !fs.existsSync(candidate)) return false;
      try {
        return execFileSync('/usr/libexec/PlistBuddy', ['-c', 'Print :CFBundleIdentifier', path.join(candidate, 'Contents/Info.plist')], { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] }).trim() === 'com.openai.codex';
      } catch { return false; }
    });
  }
  if (!bundle) fail('Desktop app not found. Use: node runtime.mjs app --app /path/to/Your.app');
  const executable = execFileSync('/usr/libexec/PlistBuddy', ['-c', 'Print :CFBundleExecutable', path.join(bundle, 'Contents/Info.plist')], { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] }).trim();
  if (!executable || path.basename(executable) !== executable) fail('Invalid app executable.');
  const fullPath = path.resolve(bundle, 'Contents/MacOS', executable);
  const processes = execFileSync('/bin/ps', ['-axo', 'comm='], { encoding: 'utf8' }).split('\n').map(value => value.trim());
  if (processes.includes(fullPath)) fail('Fully quit the desktop app, then rerun this command. It will not be force-quit.');
  return fullPath;
}

function launch(command, args, env, detached = false) {
  const child = spawn(command, args, { env, shell: false, stdio: detached ? 'ignore' : 'inherit', detached });
  child.on('error', () => { console.error(`Data Toolkit: unable to start ${path.basename(command)}. Check runtime installation and PATH.`); process.exitCode = 1; });
  if (detached) {
    child.on('spawn', () => console.error('Data Toolkit: desktop app started with the saved GitHub token. Verify access with Check Connectors.'));
    child.unref();
  } else {
    const signals = ['SIGINT', 'SIGTERM', 'SIGHUP'];
    for (const signal of signals) process.on(signal, () => child.kill(signal));
    child.on('exit', (code, signal) => { process.exitCode = code ?? (signal ? 1 : 0); });
  }
}

export function setupCommand(script = path.join(path.dirname(fileURLToPath(import.meta.url)), 'setup.sh')) {
  // Quote for Terminal's shell, while passing the command to AppleScript as data.
  const quoted = "'" + script.replaceAll("'", "'\\''") + "'";
  const appleScript = 'on run argv\n  tell application "Terminal"\n    activate\n    do script (item 1 of argv)\n  end tell\nend run';
  return ['/usr/bin/osascript', ['-e', appleScript, `bash ${quoted}`]];
}

export function main(args = process.argv.slice(2), directory = defaultDirectory) {
  const [command, ...rest] = args;
  if (command === 'setup' && !rest.length) {
    if (process.platform !== 'darwin') fail('Automatic setup launch supports macOS. Run bash scripts/setup.sh in your own terminal instead.');
    const [executable, parameters] = setupCommand();
    try {
      execFileSync(executable, parameters, { stdio: 'ignore', timeout: 30000 });
    } catch {
      fail('Unable to open Terminal. Run bash scripts/setup.sh from the plugin root in your own terminal. macOS may require permission to control Terminal.');
    }
    console.log('Opened setup in Terminal. Enter credentials there, then return here to check connections.');
    return;
  }
  if (command === 'prepare' && !rest.length) { prepare(directory); return; }
  if (command === 'save' && rest.length === 2) {
    checkPrivate(rest[1]);
    save(rest[0], parse(fs.readFileSync(rest[1], 'utf8')), directory);
    return;
  }
  if ((command === 'mysql' || command === 'aws') && !rest.length) {
    const [executable, parameters] = serverCommand(command);
    launch(executable, parameters, environment(command, load(directory)));
    return;
  }
  if (command === 'app' && (!rest.length || (rest.length === 2 && rest[0] === '--app'))) {
    launch(appExecutable(rest[1]), [], environment('app', load(directory)), true);
    return;
  }
  fail('Usage: node runtime.mjs setup|mysql|aws|app [--app /path/to/Your.app]');
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) {
  try { main(); }
  catch (error) {
    // Filesystem errors include paths, not values. Never print input or raw child output.
    console.error(`Data Toolkit: ${error.code ? 'Unable to access configuration or required runtime.' : error.message}`);
    process.exitCode = 1;
  }
}
