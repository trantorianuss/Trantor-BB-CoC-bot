import time
print(f">>> adb_utils.py  starting [{time.perf_counter():.3f}]")

import subprocess

import config
from logger import log


def adb(cmd_rest):
    """
    Ejecuta un comando ADB usando ADB_PATH y ADB_PORT del config.
    cmd_rest es la parte del comando que va después de 'shell'.
    Ejemplo: 'input tap 100 200'
    """
    full_cmd = f'{config.ADB_PATH} -s {config.ADB_PORT} shell {cmd_rest}'.strip()
    log(f" {full_cmd}", debug=True, category="adb")

    result = subprocess.run(full_cmd, capture_output=True, text=True, shell=True)

    if result.returncode != 0:
        log(f"Error: {result.stderr.strip() or result.stdout.strip()}", debug=True, category="adb")
        return ""

    return result.stdout.strip()

def get_real_resolution():
    out = adb("wm size")
    if not out:
        raise RuntimeError("No se pudo obtener la resolución desde ADB")

    # Ejemplo de salida: "Physical size: 1920x1080"
    size_part = out.split(":")[-1].strip()
    w, h = map(int, size_part.split("x"))
    return w, h

