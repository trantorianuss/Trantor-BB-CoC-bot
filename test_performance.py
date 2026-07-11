import subprocess
import time

ADB = r"C:\Android\platform-tools\adb.exe"
##DEVICE = "127.0.0.1:5557"
DEVICE = "emulator-5556"


for i in range(5):
    t0 = time.perf_counter()

    with open("prueba.png", "wb") as f:
        subprocess.run(
            [ADB, "-s", DEVICE, "exec-out", "screencap", "-p"],
            stdout=f,
            check=True
        )

    t1 = time.perf_counter()
    print(f"Captura {i+1}: {(t1-t0)*1000:.1f} ms")