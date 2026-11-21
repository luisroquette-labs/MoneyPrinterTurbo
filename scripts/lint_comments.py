import json
import subprocess
import sys
import tokenize
from io import StringIO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "scripts/comment-baseline.json"


def python_lines(source):
    return {
        token.start[0]
        for token in tokenize.generate_tokens(StringIO(source).readline)
        if token.type == tokenize.COMMENT
        and not (
            token.start == (1, 0)
            and (token.string.startswith("#!/") or token.string.startswith("#! /"))
        )
    }


def hash_lines(source, name):
    found = set()
    for number, line in enumerate(source.splitlines(), 1):
        quote = None
        escaped = False
        for position, char in enumerate(line):
            if escaped:
                escaped = False
                continue
            if char == "\\":
                escaped = True
                continue
            if quote:
                if char == quote:
                    quote = None
            elif char in ("'", '"'):
                quote = char
            elif char == "#":
                if name.endswith((".sh", ".yml", ".yaml")) and position and not line[position - 1].isspace():
                    continue
                if name.startswith("Dockerfile") or name in {".gitignore", ".dockerignore"}:
                    if line[:position].strip():
                        continue
                if number != 1 or not line.startswith(("#!/", "#! /")):
                    found.add(number)
                break
    return found


assert python_lines('url = "https://example.test/#frag"\n') == set()
assert python_lines('x = 1 # why\n') == {1}
assert python_lines('x = 1 #! bypass\n') == {1}
assert hash_lines('url = "https://example.test/#frag"\n', 'x.toml') == set()
assert hash_lines('x = 1 # why\n', 'x.toml') == {1}
assert hash_lines('url: https://example.test/#frag\n', 'x.yml') == set()
assert hash_lines('echo foo#bar\n', 'x.sh') == set()
assert hash_lines('\\#literal\n', '.gitignore') == set()

files = subprocess.check_output(
    ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"], cwd=ROOT
).decode().split("\0")
counts = {}
for name in files:
    path = ROOT / name
    if not path.is_file():
        continue
    if path.suffix == ".py":
        lines = python_lines(path.read_text())
    elif path.suffix in {".toml", ".yml", ".yaml", ".sh"} or path.name in {
        ".gitignore", ".dockerignore", "Dockerfile", "Dockerfile.gpu"
    }:
        lines = hash_lines(path.read_text(), path.name)
    else:
        continue
    if lines:
        counts[name] = len(lines)

if "--baseline" in sys.argv:
    print(json.dumps(counts, indent=2, ensure_ascii=False))
else:
    baseline = json.loads(BASELINE.read_text())
    increases = [
        f"{name}: {count} > {baseline.get(name, 0)}"
        for name, count in counts.items()
        if count > baseline.get(name, 0)
    ]
    if increases:
        raise SystemExit("Comment ratchet exceeded:\n" + "\n".join(increases))
    print(f"Comment ratchet passed ({sum(counts.values())} existing comment lines).")
