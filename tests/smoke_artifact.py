"""Smoke test of the PUBLISHED artifact: check the built wheel holds only the package and its metadata, install it
into a fresh venv of the Python running this script (no index, no repo on the path) and run the README "Testing"
example (offline, against MockOnlineSim) taken from the wheel's own metadata.

Build first (``python -m build``), then: ``python tests/smoke_artifact.py [dist-dir]``. CI runs it on the floor
Python and the latest one.
"""

from __future__ import annotations

import email
import os
import re
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


def run(*args: str, cwd: Path) -> str:
    return subprocess.run(args, cwd=cwd, check=True, text=True, stdout=subprocess.PIPE).stdout  # noqa: S603


def main(dist: Path) -> None:
    wheels = sorted(dist.glob("onlinesimru-*-py3-none-any.whl"))
    assert len(wheels) == 1, f"expected one wheel in {dist}, found {[w.name for w in wheels]}"
    wheel = wheels[0].resolve()
    version = wheel.name.split("-")[1]
    info = f"onlinesimru-{version}.dist-info/"

    with zipfile.ZipFile(wheel) as z:
        names = z.namelist()
        readme = email.message_from_bytes(z.read(info + "METADATA")).get_payload()
    stray = [n for n in names if not n.startswith(("onlinesimru/", info))]
    assert not stray, f"wheel holds only the package and its metadata, got {stray}"
    for required in (
        "onlinesimru/__init__.py",
        "onlinesimru/py.typed",
        "onlinesimru/mock/__init__.py",
        info + "licenses/LICENSE",
    ):
        assert required in names, f"wheel contains {required}"
    print(f"{wheel.name}: {len(names)} files")

    assert isinstance(readme, str)
    match = re.search(r"^## Testing\n.*?```python\n(.*?)```", readme, re.S | re.M)
    assert match, 'README has a "## Testing" section with a python example'

    with tempfile.TemporaryDirectory(prefix="onlinesim-smoke-") as tmp:
        root = Path(tmp)
        run(sys.executable, "-m", "venv", str(root / "venv"), cwd=root)
        python = str(root / "venv" / ("Scripts" if os.name == "nt" else "bin") / "python")
        run(python, "-m", "pip", "install", "--quiet", "--no-index", "--no-deps", str(wheel), cwd=root)

        app = root / "app"
        app.mkdir()
        (app / "readme_testing.py").write_text(match.group(1), "utf-8")
        run(python, "-I", "readme_testing.py", cwd=app)
        print('README "Testing" example: ok')

        check = (
            "import onlinesimru, pathlib, sys; "
            f"assert onlinesimru.__version__ == {version!r}, onlinesimru.__version__; "
            "assert (pathlib.Path(onlinesimru.__file__).parent / 'py.typed').is_file(); "
            "print(sys.version.split()[0])"
        )
        print(f"import, __version__ {version}, py.typed: ok (python {run(python, '-I', '-c', check, cwd=app).strip()})")


if __name__ == "__main__":
    main(Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "dist"))
