"""Tests for slop-farm CLI."""

import subprocess
import sys

def test_import():
    from slop_farm import __version__
    assert __version__ == "0.1.0"

def test_cli_status():
    result = subprocess.run([sys.executable, "-m", "slop_farm.cli", "status"], 
                          capture_output=True, text=True)
    assert result.returncode == 0

def test_cli_help():
    result = subprocess.run([sys.executable, "-m", "slop_farm.cli", "--help"],
                          capture_output=True, text=True)
    assert result.returncode == 0
    assert "slop-farm" in result.stdout
