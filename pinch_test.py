import subprocess
import time

ADB = r"C:\LDPlayer\LDPlayer9\adb.exe"
DEVICE = "emulator-5554"
EVENT = "/dev/input/event2"

# LDPlayer input range from getevent -lp
W, H = 1280, 720

def send(*args):
    cmd = f'"{ADB}" -s {DEVICE} shell sendevent {EVENT} ' + " ".join(map(str, args))
    subprocess.run(cmd, shell=True, check=True)

def sync():
    # EV_SYN / SYN_REPORT
    send(0, 0, 0)

def mt(slot, tracking_id, x, y):
    # ABS_MT_SLOT = 47
    send(3, 47, slot)
    # ABS_MT_TRACKING_ID = 57
    send(3, 57, tracking_id)
    # ABS_MT_POSITION_X = 53
    send(3, 53, x)
    # ABS_MT_POSITION_Y = 54
    send(3, 54, y)

def move(slot, x, y):
    send(3, 47, slot)
    send(3, 53, x)
    send(3, 54, y)

def release(slot):
    send(3, 47, slot)
    # TRACKING_ID = -1 means finger lifted
    send(3, 57, -1)

def pinch_zoom_in():
    # Fingers start apart and move together.
    a0 = (390, 285)
    b0 = (890, 435)
    a1 = (600, 345)
    b1 = (680, 375)

    mt(0, 1001, *a0)
    mt(1, 1002, *b0)
    sync()

    steps = 8
    for i in range(1, steps + 1):
        t = i / steps
        ax = round(a0[0] + (a1[0] - a0[0]) * t)
        ay = round(a0[1] + (a1[1] - a0[1]) * t)
        bx = round(b0[0] + (b1[0] - b0[0]) * t)
        by = round(b0[1] + (b1[1] - b0[1]) * t)

        move(0, ax, ay)
        move(1, bx, by)
        sync()
        time.sleep(0.04)

    release(0)
    release(1)
    sync()

def pinch_zoom_out():
    # Fingers start close and move apart.
    a0 = (600, 345)
    b0 = (680, 375)
    a1 = (390, 285)
    b1 = (890, 435)

    mt(0, 2001, *a0)
    mt(1, 2002, *b0)
    sync()

    steps = 8
    for i in range(1, steps + 1):
        t = i / steps
        ax = round(a0[0] + (a1[0] - a0[0]) * t)
        ay = round(a0[1] + (a1[1] - a0[1]) * t)
        bx = round(b0[0] + (b1[0] - b0[0]) * t)
        by = round(b0[1] + (b1[1] - b0[1]) * t)

        move(0, ax, ay)
        move(1, bx, by)
        sync()
        time.sleep(0.04)

    release(0)
    release(1)
    sync()

print("1 = pinch / zoom IN")
print("2 = spread / zoom OUT")
print("q = salir")

while True:
    option = input("> ").strip().lower()

    if option == "1":
        print("Zoom IN")
        pinch_zoom_in()
    elif option == "2":
        print("Zoom OUT")
        pinch_zoom_out()
    elif option == "q":
        break
    else:
        print("Opcion no valida")
