import subprocess
import sys

import pytest

from landlab_cli._cli import main


def test_help(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0
    assert capsys.readouterr().out.startswith("usage:")


def test_no_args(capsys):
    assert main([]) == 0
    assert capsys.readouterr().out.startswith("usage:")


def test_version(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    assert capsys.readouterr().out.startswith("landlab-cli")


def test_bad_arg():
    with pytest.raises(SystemExit) as exc:
        main(["--foobar"])
    assert exc.value.code == 2


@pytest.mark.parametrize("args", [["--help"], []])
def test_module_help(args):
    result = subprocess.run(
        [sys.executable, "-m", "landlab_cli", *args],
        capture_output=True,
        check=False,
        text=True,
    )
    assert result.returncode == 0
    assert result.stdout.startswith("usage:")
    assert result.stderr == ""
