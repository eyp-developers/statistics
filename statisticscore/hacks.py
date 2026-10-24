# These should be gotten rid of, but as part of the Python version upgrade it
# was necessary to fix some problems using the same hacks as were used before
# instead of taking the time to fix all of the underlying issues all across
# the codebase


import importlib
import inspect
import pkgutil
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import types

@dataclass
class SubmoduleImportResult:
    all_names: list
    globals_dict: dict

def import_submodules(package: str | types.ModuleType, recursive=True) -> SubmoduleImportResult:
    """Recusrively import all submodules and subpackages of a module"""

    if isinstance(package, str):
        package = importlib.import_module(package)
    result = SubmoduleImportResult(all_names=[], globals_dict={})
    for _, name, is_pkg in pkgutil.walk_packages(package.__path__):
        full_name = package.__name__ + '.' + name
        module = importlib.import_module(full_name)
        for name, value in inspect.getmembers(module):
            if name.startswith("__"):
                continue
            result.all_names.append(name)
            result.globals_dict[name] = value
        if recursive and is_pkg:
            rec_result = import_submodules(full_name)
            result.all_names.extend(rec_result.all_names)
            result.globals_dict.update(rec_result.globals_dict)
    return result
