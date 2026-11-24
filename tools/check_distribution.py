"""Verify release artifacts without uploading them or requiring runtime dependencies."""
from __future__ import annotations

import email
import json
import subprocess
import sys
import tarfile
import tempfile
import venv
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run():
    wheel, = (ROOT / "dist").glob("*.whl")
    source, = (ROOT / "dist").glob("*.tar.gz")
    with tarfile.open(source, "r:gz") as archive:
        names = {name.partition("/")[2] for name in archive.getnames()}
        required = {
            "README.md", "LICENSE", "pyproject.toml",
            "schemas/program-1.0.schema.json", "examples/strength_program.json",
            "examples/ficha_treino_ptbr.json", "tests/fixtures/csv_contract_expected.csv",
        }
        if missing := required - names:
            raise RuntimeError(f"Source archive missing files: {sorted(missing)}")
    with zipfile.ZipFile(wheel) as archive:
        names = archive.namelist()
        metadata_name, = [name for name in names if name.endswith(".dist-info/METADATA")]
        metadata = email.message_from_bytes(archive.read(metadata_name))
        requirements = metadata.get_all("Requires-Dist", [])
        if any("extra ==" not in item for item in requirements):
            raise RuntimeError(f"Unexpected runtime requirements: {requirements}")
        bundled = "fitness_programming_toolkit/program-1.0.schema.json"
        if archive.read(bundled) != (ROOT / "schemas/program-1.0.schema.json").read_bytes():
            raise RuntimeError("Wheel schema differs from the repository schema")
        for path in ("fitness_programming_toolkit/core.py", "fitness_programming_toolkit/cli.py"):
            if path not in names:
                raise RuntimeError(f"Wheel missing {path}")
    with tempfile.TemporaryDirectory() as temp:
        folder = Path(temp)
        environment = folder / "venv"
        venv.EnvBuilder(with_pip=True).create(environment)
        bin_dir = environment / ("Scripts" if sys.platform == "win32" else "bin")
        python = bin_dir / ("python.exe" if sys.platform == "win32" else "python")
        cli = bin_dir / ("fptk.exe" if sys.platform == "win32" else "fptk")
        subprocess.run(
            [str(python), "-m", "pip", "install", "--no-deps", "--no-index", str(wheel)],
            cwd=folder, check=True,
        )
        schema_result = subprocess.run(
            [str(cli), "schema"], cwd=folder, check=True, capture_output=True,
            text=True, encoding="utf-8",
        )
        expected_schema = json.loads((ROOT / "schemas/program-1.0.schema.json").read_text(encoding="utf-8"))
        if json.loads(schema_result.stdout) != expected_schema:
            raise RuntimeError("Installed CLI schema differs from repository schema")
        subprocess.run(
            [str(python), "-c", "from fitness_programming_toolkit.ai import call_tool; "
             "assert call_tool('fptk_schema', {})['ok']"], cwd=folder, check=True,
        )
        fixture = ROOT / "examples/strength_program.json"
        result = subprocess.run(
            [str(cli), "summary", str(fixture)], cwd=folder,
            check=True, capture_output=True, text=True, encoding="utf-8",
        )
        if json.loads(result.stdout)["planned_sets"] != 28:
            raise RuntimeError("Installed CLI summary differs from documented example")
        subprocess.run(
            [str(cli), "export-csv", str(ROOT / "tests/fixtures/csv_contract_input.json"),
             "-o", str(folder / "test.csv")], cwd=folder, check=True,
        )
        expected = (ROOT / "tests/fixtures/csv_contract_expected.csv").read_bytes()
        if (folder / "test.csv").read_bytes() != expected:
            raise RuntimeError("Installed CLI CSV differs from the golden fixture")
        subprocess.run([str(python), "-m", "pip", "check"], cwd=folder, check=True)
    print("Source archive, wheel metadata, isolated offline installation and CLI checks passed.")


if __name__ == "__main__":
    run()
