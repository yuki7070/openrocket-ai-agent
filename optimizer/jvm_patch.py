"""JVM patch for Java 17+ module system compatibility.

Monkey-patches jpype.startJVM to add --add-opens options required by
orhelper when running on Java 17+.  Importing this module applies the
patch exactly once.
"""

import jpype

_original_startJVM = jpype.startJVM
_patched = False


def _patched_startJVM(*args, **kwargs):
    add_opens = [
        "--add-opens=java.base/java.lang=ALL-UNNAMED",
        "--add-opens=java.base/java.lang.reflect=ALL-UNNAMED",
        "--add-opens=java.base/java.util=ALL-UNNAMED",
    ]
    _original_startJVM(*args, *add_opens, **kwargs)


def apply_patch():
    """Apply the JVM patch (idempotent)."""
    global _patched
    if not _patched:
        jpype.startJVM = _patched_startJVM
        _patched = True


# Apply on import
apply_patch()
