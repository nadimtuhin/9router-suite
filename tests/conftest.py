import importlib.machinery
import importlib.util
import pathlib

import pytest

BIN = pathlib.Path(__file__).resolve().parent.parent / "bin"


def load_script(name):
    """Import an extension-less script from bin/ as a module."""
    path = BIN / name
    loader = importlib.machinery.SourceFileLoader(name.replace("-", "_"), str(path))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


@pytest.fixture
def patcher():
    return load_script("9router-patcher")


@pytest.fixture
def sync_free():
    return load_script("9router-sync-free")
