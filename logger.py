import os

import state
import config
import time as t
import inspect

_log_sink = None


def set_log_sink(sink=None):
    global _log_sink
    _log_sink = sink

def _should_emit_log(debug=False, category=""):

    # Los INFO siempre salen
    if not debug:
        return True

    # Los DEBUG requieren modo debug
    if not state.debug_mode:
        return False

    # Si tienen categoría, comprobar si está habilitada
    if category:
        return config.DEBUG.get(category, False)

    return True


def log(message, debug=False, category="", color=None):

    if not _should_emit_log(debug, category):
        return

    timestamp = t.strftime("%H:%M:%S")

    parts = [f"[{timestamp}]"]

    if state.debug_mode:
        level = "DBG" if debug else "INF"
        parts.append(f"[{level}]")

    if category:
        parts.append(f"[{category}]")


    parts.append(message)

    formatted = " ".join(parts)

    if color is None:
        if debug:
            color = "orange"
        else:
            color = "default"




    if _log_sink:
        _log_sink(formatted, color)
    else:
        print(formatted)

    if config.DEBUG_INSPECTION:
        # Obtener el nombre de la función que llamó a log()
        frame = inspect.currentframe().f_back

        filename = os.path.basename(frame.f_code.co_filename)   
        function = frame.f_code.co_name
        line = frame.f_lineno

        origen = f"{filename}:{function}:{line}"
        _log_sink(origen, "gray")
