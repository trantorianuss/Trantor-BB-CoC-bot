import threading


Bbot_running = threading.Event()


def start():
    Bbot_running.set()


def stop():
    Bbot_running.clear()


def is_running():
    return Bbot_running.is_set()