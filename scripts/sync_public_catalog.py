#!/usr/bin/env python3
"""Fetch a purpose-built Neuromedia public catalog export and validate it."""
import argparse
import json
import shutil
import sys
import tempfile
import urllib.request
from pathlib import Path

from validate_catalog import validate_catalog


def read_export(args: argparse.Namespace) -> bytes:
    if args.input:
        return Path(args.input).read_bytes()
    request = urllib.request.Request(args.url, headers={"User-Agent": "Neuromedia-Public-Catalog-Sync/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        if response.status != 200:
            raise ValueError(f"Export returned HTTP {response.status}")
        return response.read()


def main() -> int:
    parser = argparse.ArgumentParser()
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--url")
    source.add_argument("--input")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    try:
        raw = read_export(args)
        data = json.loads(raw.decode("utf-8"))
        validate_catalog(data)
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=output.parent) as temp:
            json.dump(data, temp, ensure_ascii=False, indent=2)
            temp.write("\n")
            temporary = Path(temp.name)
        shutil.move(temporary, output)
    except Exception as error:
        print(f"Sync failed: {error}", file=sys.stderr)
        return 1
    print(f"Updated validated public catalog: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
