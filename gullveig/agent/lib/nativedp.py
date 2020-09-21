import importlib


def has_python_library(name: str) -> bool:
    if not hasattr(importlib, 'util'):
        return importlib.find_loader(name) is not None
    else:
        return importlib.util.find_spec(name) is not None
