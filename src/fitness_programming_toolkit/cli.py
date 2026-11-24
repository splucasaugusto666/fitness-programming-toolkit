"""Command-line interface for valid, auditable strength plan data."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .core import DataValidationError, export_csv, read_program, summarize_program


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="fptk", description="Offline strength plan validator")
    sub = parser.add_subparsers(dest="command", required=True)
    for command, helptext in (
        ("validate", "Validate a plan without changing files"),
        ("summary", "Print aggregate planned work as JSON"),
        ("export-csv", "Export planned sets as spreadsheet-safe CSV"),
    ):
        command_parser = sub.add_parser(command, help=helptext)
        command_parser.add_argument("input", type=Path, help="UTF-8 JSON plan")
        if command == "export-csv":
            command_parser.add_argument("--output", "-o", type=Path, required=True)
            command_parser.add_argument("--force", action="store_true", help="Replace existing file")
    args = parser.parse_args(argv)
    try:
        program = read_program(args.input)
        if args.command == "validate":
            print(f"VALID: {program.program_id} (schema {program.schema_version})")
        elif args.command == "summary":
            print(json.dumps(summarize_program(program), indent=2, ensure_ascii=False))
        else:
            # Serialize to memory first, avoiding a partially written file for bad data.
            content = export_csv(program)
            try:
                with args.output.open(
                    "w" if args.force else "x", encoding="utf-8", newline=""
                ) as destination:
                    destination.write(content)
            except FileExistsError as exc:
                raise DataValidationError(
                    f"{args.output}: already exists; pass --force to replace"
                ) from exc
            print(f"WROTE: {args.output}")
        return 0
    except (DataValidationError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
