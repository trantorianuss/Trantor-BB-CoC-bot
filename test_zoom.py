import config
from func import adb

def pinch_zoom_out(event_dev="/dev/input/event2"):
    """
    Simula Pinch Zoom Out en LDPlayer usando /dev/input/event2.
    """
    # Coordenadas:
    # Dedo 0: de X=250 a X=550 (Y=360)
    # Dedo 1: de X=1030 a X=730 (Y=360)

    events = [
        # --- 1. PRESIONAR DEDOS (Posición inicial abierta) ---
        f"sendevent {event_dev} 1 330 1",      # BTN_TOUCH = 1 (Pantalla presionada)
        
        # Dedo 0 (Izquierda)
        f"sendevent {event_dev} 3 47 0",        # ABS_MT_SLOT = 0
        f"sendevent {event_dev} 3 57 1",        # ABS_MT_TRACKING_ID = 1
        f"sendevent {event_dev} 3 58 50",       # ABS_MT_PRESSURE = 50
        f"sendevent {event_dev} 3 53 250",      # X = 250
        f"sendevent {event_dev} 3 54 360",      # Y = 360
        
        # Dedo 1 (Derecha)
        f"sendevent {event_dev} 3 47 1",        # ABS_MT_SLOT = 1
        f"sendevent {event_dev} 3 57 2",        # ABS_MT_TRACKING_ID = 2
        f"sendevent {event_dev} 3 58 50",       # ABS_MT_PRESSURE = 50
        f"sendevent {event_dev} 3 53 1030",     # X = 1030
        f"sendevent {event_dev} 3 54 360",      # Y = 360
        
        f"sendevent {event_dev} 0 0 0",         # SYN_REPORT
        "sleep 0.05",

        # --- 2. PASO 1: Acerque inicial ---
        f"sendevent {event_dev} 3 47 0",
        f"sendevent {event_dev} 3 53 350",      # Dedo 0 avanza a 350
        f"sendevent {event_dev} 3 47 1",
        f"sendevent {event_dev} 3 53 930",      # Dedo 1 avanza a 930
        f"sendevent {event_dev} 0 0 0",
        "sleep 0.03",

        # --- 3. PASO 2: Acerque medio ---
        f"sendevent {event_dev} 3 47 0",
        f"sendevent {event_dev} 3 53 450",      # Dedo 0 avanza a 450
        f"sendevent {event_dev} 3 47 1",
        f"sendevent {event_dev} 3 53 830",      # Dedo 1 avanza a 830
        f"sendevent {event_dev} 0 0 0",
        "sleep 0.03",

        # --- 4. PASO 3: Posición Final (Cerca del centro) ---
        f"sendevent {event_dev} 3 47 0",
        f"sendevent {event_dev} 3 53 550",      # Dedo 0 llega a 550
        f"sendevent {event_dev} 3 47 1",
        f"sendevent {event_dev} 3 53 730",      # Dedo 1 llega a 730
        f"sendevent {event_dev} 0 0 0",
        "sleep 0.05",

        # --- 5. LEVANTAR DEDOS (RELEASE) ---
        f"sendevent {event_dev} 3 47 0",
        f"sendevent {event_dev} 3 57 -1",       # Liberar Dedo 0
        f"sendevent {event_dev} 3 47 1",
        f"sendevent {event_dev} 3 57 -1",       # Liberar Dedo 1
        f"sendevent {event_dev} 1 330 0",       # BTN_TOUCH = 0 (Pantalla liberada)
        f"sendevent {event_dev} 0 0 0"          # SYN_REPORT Final
    ]

    # Concatenamos todo en un solo comando
    batch_cmd = " && ".join(events)
    adb(batch_cmd)

if __name__ == "__main__":
    print("Ejecutando Zoom Out en /dev/input/event2...")
    pinch_zoom_out()

