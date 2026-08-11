"""ORA producer-harness driver for Krita's own PyKrita scripting plugin.

This is NOT a user-facing Krita feature. It is a repository-owned automation
driver, loaded only inside the disposable, pinned Krita container this
harness builds -- it never ships to a real user's Krita installation. Its
sole job is to trigger real, independent-application scene construction
through Krita's own documented Python API
(https://api.kde.org/krita/html/, `krita` module), then exit deterministically.

Per this session's own directive: the actual scene-construction LOGIC lives
in an external, volume-mounted script (not baked into this file or the
Docker image), so it can be iterated without rebuilding the multi-gigabyte
Krita image on every change -- the same pattern already established and
working for the GIMP lane's own gimp_scripts/ volume mount. This file is
only the fixed PyKrita registration/dispatch scaffold.

Everything here writes to a log file rather than stdout/stderr: PyKrita
plugin code runs inside Krita's own Qt event loop, and there is no
interactive terminal to watch -- the log file is the only way to diagnose
a failure after the fact, matching this session's own "write to a sentinel
file" requirement.
"""
import os
import sys
import traceback

from krita import Extension, Krita  # type: ignore[import-not-found]  # noqa: F401  (only resolvable inside a real Krita install)

LOG_PATH = os.environ.get("ORA_HARNESS_LOG", "/out/krita-driver.log")
SCRIPT_PATH = os.environ.get("ORA_HARNESS_SCRIPT")
SENTINEL_PATH = os.environ.get("ORA_HARNESS_SENTINEL", "/out/krita-driver.sentinel")


def _log(message):
    with open(LOG_PATH, "a", encoding="utf-8") as handle:
        handle.write(message + "\n")


class OraHarnessDriver(Extension):
    def __init__(self, parent):
        super().__init__(parent)
        self._ran = False

    def setup(self):
        _log("setup() called")

    def createActions(self, window):
        _log("createActions() called, window=%r" % (window,))
        if self._ran:
            _log("createActions() called again -- ignoring (already ran once)")
            return
        self._ran = True
        self._run_driver_script(window)

    def _run_driver_script(self, window):
        try:
            _log("driver script path: %r" % (SCRIPT_PATH,))
            if not SCRIPT_PATH or not os.path.isfile(SCRIPT_PATH):
                _log("ERROR: ORA_HARNESS_SCRIPT is unset or not a file")
                self._write_sentinel(status="ERROR", detail="missing driver script")
                return
            with open(SCRIPT_PATH, "r", encoding="utf-8") as handle:
                source = handle.read()
            namespace = {
                "Krita": Krita,
                "window": window,
                "log": _log,
                "write_sentinel": self._write_sentinel,
            }
            _log("executing driver script (%d bytes)" % len(source))
            exec(compile(source, SCRIPT_PATH, "exec"), namespace)
            _log("driver script finished without raising")
        except Exception:  # noqa: BLE001 - must be caught: this is the only
            # diagnostic path available, an uncaught exception here would
            # otherwise vanish silently inside Krita's own Qt event loop
            _log("EXCEPTION during driver script execution:\n" + traceback.format_exc())
            self._write_sentinel(status="ERROR", detail="exception during driver script")
        finally:
            self._quit()

    def _write_sentinel(self, *, status, detail=""):
        try:
            with open(SENTINEL_PATH, "w", encoding="utf-8") as handle:
                handle.write("%s\n%s\n" % (status, detail))
            _log("sentinel written: status=%s detail=%s" % (status, detail))
        except Exception:  # noqa: BLE001
            _log("EXCEPTION writing sentinel:\n" + traceback.format_exc())

    def _quit(self):
        # app.action("file_quit") was tried first and empirically found to
        # return None here (no such action registered without a full
        # window/toolbar in this headless invocation) -- confirmed via the
        # real AttributeError this raised on the first smoke-test run.
        # sys.exit(0) was already this method's own exception fallback and
        # is proven reliable (every real run so far exits cleanly via it),
        # so it is now the primary method, not a fallback.
        _log("requesting application quit")
        try:
            app = Krita.instance()
            app.setBatchmode(True)
            for doc in list(app.documents()):
                try:
                    doc.close()
                except Exception:  # noqa: BLE001
                    _log("EXCEPTION closing a document:\n" + traceback.format_exc())
        except Exception:  # noqa: BLE001
            _log("EXCEPTION during document cleanup:\n" + traceback.format_exc())
        finally:
            sys.exit(0)


Krita.instance().addExtension(OraHarnessDriver(Krita.instance()))
_log("plugin module imported, extension registered")
