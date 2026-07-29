import threading


bot_run_event = threading.Event()

def start():
    bot_run_event.set()


def stop():
    bot_run_event.clear()


def should_run():
    return bot_run_event.is_set()