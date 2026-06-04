import { existsSync } from "node:fs";
import { join } from "node:path";
import { spawnSync } from "node:child_process";

const moduleArgs = process.argv.slice(2);

if (moduleArgs.length === 0) {
  console.error("Usage: node scripts/run-python-module.mjs <module> [...args]");
  process.exit(1);
}

const candidates = [];

if (process.env.PYTHON) {
  candidates.push({ command: process.env.PYTHON, args: [] });
}

if (process.platform === "win32" && process.env.LOCALAPPDATA) {
  const localPython = join(
    process.env.LOCALAPPDATA,
    "Programs",
    "Python",
    "Python312",
    "python.exe",
  );

  if (existsSync(localPython)) {
    candidates.push({ command: localPython, args: [] });
  }
}

candidates.push(
  { command: "python", args: [] },
  { command: "python3", args: [] },
  { command: "py", args: ["-3.12"] },
  { command: "py", args: ["-3"] },
);

for (const candidate of candidates) {
  const result = spawnSync(
    candidate.command,
    [...candidate.args, "-m", ...moduleArgs],
    {
      stdio: "inherit",
      shell: false,
    },
  );

  if (result.error?.code === "ENOENT") {
    continue;
  }

  if (result.error) {
    console.error(result.error.message);
    process.exit(1);
  }

  process.exit(result.status ?? 1);
}

console.error(
  "Could not find Python. Install Python 3.12+, add it to PATH, or set the PYTHON environment variable.",
);
process.exit(1);
