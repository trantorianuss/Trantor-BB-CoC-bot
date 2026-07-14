import state
import config
import time as t

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


def log(message, debug=False, category=""):

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

    if _log_sink:
        _log_sink(formatted)
    else:
        print(formatted)
