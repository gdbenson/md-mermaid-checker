#!/usr/bin/env python3
"""
validate_mermaid.py — Validate Mermaid code blocks embedded in Markdown by using mmdc.

Usage examples:
  python validate_mermaid.py README.md
  python validate_mermaid.py docs/**/*.md
  python validate_mermaid.py -c mermaid.config.json -t dark README.md docs/**/*.md

Exit codes:
  0 = success (no invalid blocks, or no blocks found)
  1 = at least one invalid block
  2 = usage / environment error (e.g., mmdc/npx missing)
"""

from __future__ import annotations
import argparse
import glob
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, List, Tuple

FENCE_RE = re.compile(r"^\s*```(mermaid|mermaidjs)\s*$")
END_FENCE_RE = re.compile(r"^\s*```\s*$")

@dataclass
class Block:
    file: Path
    start_line: int
    index_in_file: int
    content: str

def find_mermaid_blocks(path: Path) -> List[Block]:
    """Scan a Markdown file and return all ```mermaid / ```mermaidjs blocks."""
    blocks: List[Block] = []
    if not path.is_file():
        return blocks
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        # fallback read (binary, ignore errors)
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()

    in_block = False
    start_line = 0
    buf: List[str] = []
    block_idx = 0

    for i, line in enumerate(lines, start=1):
        if not in_block and FENCE_RE.match(line):
            in_block = True
            start_line = i
            buf = []
            continue
        if in_block and END_FENCE_RE.match(line):
            block_idx += 1
            blocks.append(Block(path, start_line, block_idx, "\n".join(buf)))
            in_block = False
            buf = []
            continue
        if in_block:
            buf.append(line)
    return blocks

def expand_inputs(patterns: List[str]) -> List[Path]:
    """Expand shell-style globs for cross-platform behavior."""
    out: List[Path] = []
    for p in patterns:
        matches = glob.glob(p, recursive=True)
        if matches:
            out.extend(Path(m) for m in matches)
        else:
            out.append(Path(p))
    # de-dup while preserving order
    seen = set()
    deduped: List[Path] = []
    for p in out:
        rp = p.resolve()
        if rp not in seen:
            deduped.append(rp)
            seen.add(rp)
    return deduped

def which_mmdc() -> List[str] | None:
    """Return the command vector to run mmdc. Prefer global mmdc; fallback to npx."""
    mmdc_bin = shutil.which("mmdc")
    if mmdc_bin:
        return [mmdc_bin]
    npx = shutil.which("npx")
    if npx:
        # Use npx to invoke mermaid-cli without requiring global install
        return [npx, "-y", "@mermaid-js/mermaid-cli", "mmdc"]
    return None

def safe_name(p: Path) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]", "_", str(p))

def run_mmdc(cmd_base: List[str], in_file: Path, out_file: Path, theme: str, config: Path | None) -> Tuple[bool, str]:
    cmd = list(cmd_base) + ["-i", str(in_file), "-o", str(out_file), "--theme", theme]
    if config:
        cmd += ["--configFile", str(config)]
    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        ok = (proc.returncode == 0)
        # Prefer stderr for error details (mmdc writes errors there)
        msg = (proc.stderr or proc.stdout).decode("utf-8", errors="ignore").strip()
        return ok, msg
    except FileNotFoundError as e:
        return False, f"Failed to execute mmdc: {e}"

def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser(description="Validate Mermaid code blocks in Markdown using mmdc.")
    ap.add_argument("inputs", nargs="+", help="Markdown files or glob patterns (e.g., docs/**/*.md)")
    ap.add_argument("-c", "--config", type=Path, default=None, help="Mermaid config JSON file for mmdc")
    ap.add_argument("-t", "--theme", default="default", help="Mermaid theme (default|dark|forest|neutral)")
    ap.add_argument("-k", "--keep", action="store_true", help="Keep temp files (for debugging)")
    ap.add_argument("-q", "--quiet", action="store_true", help="Only print errors and summary")
    args = ap.parse_args(argv)

    cmd_base = which_mmdc()
    if not cmd_base:
        print("ERROR: `mmdc` not found, and `npx` not available.", file=sys.stderr)
        print("Install globally with: npm i -g @mermaid-js/mermaid-cli", file=sys.stderr)
        return 2

    if args.config and not args.config.exists():
        print(f"ERROR: config file not found: {args.config}", file=sys.stderr)
        return 2

    files = [p for p in expand_inputs(args.inputs) if p.exists()]
    if not files:
        print("ERROR: no input files found.", file=sys.stderr)
        return 2

    tmpdir = Path(tempfile.mkdtemp(prefix="mermaid_check_"))
    failed = 0
    total = 0
    found_any = 0

    try:
        for md in files:
            blocks = find_mermaid_blocks(md)
            if not blocks:
                continue
            found_any = 1
            for b in blocks:
                total += 1
                # Write block to temp file
                stem = f"{safe_name(md)}.block_{b.index_in_file:03d}.mmd"
                in_file = tmpdir / stem
                out_file = tmpdir / (stem + ".svg")
                in_file.write_text(b.content, encoding="utf-8")

                ok, msg = run_mmdc(cmd_base, in_file, out_file, args.theme, args.config)
                if ok:
                    if not args.quiet:
                        print(f"OK   {md}:{b.start_line}  ({in_file.name})")
                else:
                    failed += 1
                    # Show first line of error to keep logs tight; include more if not quiet
                    first_line = msg.splitlines()[0] if msg else "mmdc failed"
                    print(f"ERR  {md}:{b.start_line}  ({in_file.name})  {first_line}", file=sys.stderr)
                    if not args.quiet and msg:
                        # Indent full error block for readability
                        for line in msg.splitlines()[1:]:
                            print(f"      {line}", file=sys.stderr)

        if not found_any:
            print("No Mermaid blocks found in inputs.")
            return 0

        print("----")
        print(f"Checked: {total}   Failed: {failed}")
        return 0 if failed == 0 else 1
    finally:
        if not args.keep:
            try:
                # Best-effort cleanup
                for child in tmpdir.iterdir():
                    try: child.unlink()
                    except Exception: pass
                tmpdir.rmdir()
            except Exception:
                if not args.quiet:
                    print(f"Note: could not remove temp dir {tmpdir}", file=sys.stderr)

def cli():
    """Entry point for the md-mermaid-checker command."""
    sys.exit(main(sys.argv[1:]))

if __name__ == "__main__":
    cli()