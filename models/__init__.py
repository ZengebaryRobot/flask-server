import pkgutil, importlib

__path__ = pkgutil.extend_path(__path__, __name__)
for _, module_name, _ in pkgutil.iter_modules(__path__):
    importlib.import_module(f"{__name__}.{module_name}")

from .registry import MODELS
