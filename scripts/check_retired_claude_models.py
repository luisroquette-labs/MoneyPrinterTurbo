#!/usr/bin/env python3
import re
import sys
from pathlib import Path

RETIRED = re.compile(r"anthropic/claude-sonnet-4[-.]5|claude-sonnet-4-5-[0-9]{8}")
ROOT = Path(__file__).resolve().parents[1]
TARGETS = [ROOT / "app", ROOT / "webui", ROOT / "config.example.toml"]

hits: list[str] = []
for target in TARGETS:
    files = [target] if target.is_file() else target.rglob("*")
    for path in files:
        if not path.is_file() or path.suffix in {".pyc", ".png", ".jpg", ".ttc"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for number, line in enumerate(text.splitlines(), 1):
            if RETIRED.search(line):
                hits.append(f"{path.relative_to(ROOT)}:{number}:{line.strip()}")

if hits:
    print("[model-retirement] BLOQUEADO: referência executável ao Sonnet 4.5", file=sys.stderr)
    print("\n".join(hits), file=sys.stderr)
    raise SystemExit(1)

print("[model-retirement] OK: nenhum Sonnet 4.5 executável")
