from statisticscore.hacks import import_submodules

# Terrible import system crimes are committed here in order to not need to
# refactor the entire codebase right now
result = import_submodules(__name__)
globals().update(result.globals_dict)
__all__ = result.all_names
