RUNNING = "running"
STOPPING = "stopping"
STOPPED = "stopped"

bot_status = STOPPED


def start():
    global bot_status
    bot_status = RUNNING


def stop():
    global bot_status
    bot_status = STOPPING


def set_stopped():
    global bot_status
    bot_status = STOPPED


def should_run():
    return bot_status == RUNNING


def get_status():
    return bot_status
