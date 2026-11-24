"""Command-line interface for valid, auditable strength plan data."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

from .core import DataValidationError, Program, read_program, summarize_program, write_csv


def _publish_csv(output: Path, program: Program, *, force: bool) -> None:
    """Stage complete bytes beside the destination before publishing them."""
    staged: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="", dir=output.parent,
            prefix=".fptk-", suffix=".tmp", delete=False,
        ) as stream:
            staged = Path(stream.name)
            write_csv(program, stream)
            stream.flush()
            os.fsync(stream.fileno())
        if force:
            os.replace(staged, output)
        else:
            # Linking a complete file preserves no-overwrite semantics without a race.
            os.link(staged, output)
    except FileExistsError as exc:
        raise DataValidationError(f"{output}: already exists; pass --force to replace") from exc
    finally:
        if staged is not None:
            staged.unlink(missing_ok=True)


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
            # Refuse accidental destruction of the source, including existing aliases.
            try:
                same_input = args.input.samefile(args.output)
            except FileNotFoundError:
                same_input = False
            if same_input:
                raise DataValidationError("CSV destination must differ from the JSON input")
            # Stage incrementally, publishing only after successful serialization.
            _publish_csv(args.output, program, force=args.force)
            print(f"WROTE: {args.output}")
        return 0
    except (DataValidationError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
