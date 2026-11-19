"""Type-checks the code examples of README.md and docs/content/*.md against the package, so the docs cannot drift
from the API. A ```python block counts as an example when it uses ``client`` or starts with an import; the other
python blocks are signatures. Undeclared ``client`` / ``tzid`` get a declaration."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict

import pytest

ROOT = Path(__file__).resolve().parent.parent
SOURCES = [ROOT / "README.md", *sorted((ROOT / "docs" / "content").glob("*.md"))]
BLOCK = re.compile(r"```python[^\n]*\n(.*?)```", re.S)


def examples() -> Dict[str, str]:
    files: Dict[str, str] = {}
    for source in SOURCES:
        for i, code in enumerate(BLOCK.findall(source.read_text("utf-8"))):
            if not re.search(r"\bclient\b|^(import|from) ", code, re.M):
                continue
            prelude = ["from onlinesimru import OnlineSim as _DocsClient"]
            if not re.search(r"^client\s*=", code, re.M):
                prelude.append("client: _DocsClient")
            if not re.search(r"^tzid\s*=", code, re.M):
                prelude.append("tzid: int")
            name = re.sub(r"\W", "_", str(source.relative_to(ROOT)))
            files[f"{name}_{i}.py"] = "\n".join(prelude) + "\n" + code
    return files


def test_examples_compile() -> None:
    files = examples()
    assert len(files) > 20
    for name, code in files.items():
        compile(code, name, "exec")


def test_examples_type_check(tmp_path: Path) -> None:
    mypy_api = pytest.importorskip("mypy.api")
    for name, code in examples().items():
        (tmp_path / name).write_text(code, "utf-8")
    out, err, status = mypy_api.run(["--config-file=", "--strict", "--no-incremental", str(tmp_path)])
    assert status == 0, out + err
