"""Config resolution (issue #3): CLI arg > MOJOBOL_CONFIG env > in-repo default."""
import os

import mojobol


def test_cli_arg_takes_precedence(monkeypatch):
    monkeypatch.setenv("MOJOBOL_CONFIG", "/env/path.conf")
    assert mojobol.resolve_config_path("/cli/path.conf") == "/cli/path.conf"


def test_env_var_used_when_no_cli_arg(monkeypatch):
    monkeypatch.setenv("MOJOBOL_CONFIG", "/env/path.conf")
    assert mojobol.resolve_config_path() == "/env/path.conf"


def test_falls_back_to_repo_sample_config(monkeypatch):
    monkeypatch.delenv("MOJOBOL_CONFIG", raising=False)
    path = mojobol.resolve_config_path()
    assert path.endswith(os.path.join("conf", "sampleserver.conf"))
    assert os.path.isfile(path), "the default sample config must exist in the repo"
