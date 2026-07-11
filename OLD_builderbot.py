import time
import customtkinter as ctk

import func as f
import botcontroller as controller
import paint as p


# -----------------------------
#   FUNCIONES DE BOTONES
# -----------------------------

def bttn_start_Farm():
    attacks = parse_int(App.attacks_entry.get(), default=2)
    controller.start_farm(attacks_per_cycle=attacks)


def bttn_stop():
    controller.stop()


def bttn_screenshot():
    try:
        filename = f.screenshot()
        log(f"Screenshot saved: {filename}")
    except Exception as e:
        log(f"Screenshot failed: {e}")


def bttn_recognize():
    try:
        result = f.recognize_screenshot()
        log(f"OCR result: {result}")
    except Exception as e:
        log(f"Image recognition failed: {e}")


def bttn_buscar_carro():
    try:
        dx = parse_int(App.swipe_dx_entry.get(), default=0)
        dy = parse_int(App.swipe_dy_entry.get(), default=400)
        f.buscar_carro(dy, debug=True)
    except Exception as e:
        log(f"Buscar Carro failed: {e}")


def bttn_test():
    log("Running test: hago swipe")
    try:
        xi = 1450
        yi = 150
        dy = parse_int(App.swipe_dy_entry.get(), default=400)

        log("=== TEST INICIADO ===")

        filename = f.screenshot()
        log(f"Screenshot antes de saved: {filename}")

        # 1) Screenshot real
        p.paint_test()
        
        f.swipe(xi, yi, xi, yi + dy, 500)
        #f.swipe_test()

        filename = f.screenshot()
        log(f"Screenshot despues de saved: {filename}")

        log("Test swipe completed")
    except Exception as e:
        log(f"Test swipe failed: {e}")


def parse_int(value, default=0):
    try:
        return int(value)
    except Exception:
        return default


# -----------------------------
#   INTERFAZ GRÁFICA
# -----------------------------

App = ctk.CTk()
App.title("Wal CoC BBot")
App.geometry("400x500")   # mismo ancho, más alto


# ---------- TABS ----------
App.tabs = ctk.CTkTabview(App)
App.tabs.pack(fill="x", padx=10, pady=10)

tab_bot = App.tabs.add("Bot")
tab_tools = App.tabs.add("Herramientas")


# ---------- TAB BOT ----------
tab_bot.columnconfigure(0, weight=1)
tab_bot.columnconfigure(1, weight=1)

App.button_Farm = ctk.CTkButton(tab_bot, text="Start Farm", command=bttn_start_Farm)
App.button_Farm.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

App.button_Stop = ctk.CTkButton(tab_bot, text="Stop", command=bttn_stop)
App.button_Stop.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

App.attacks_label = ctk.CTkLabel(tab_bot, text="Ataques/ciclo:")
App.attacks_label.grid(row=1, column=0, padx=5, pady=(10, 2), sticky="w")

App.attacks_entry = ctk.CTkEntry(tab_bot, placeholder_text="2")
App.attacks_entry.grid(row=2, column=0, padx=5, pady=2, sticky="ew")


# ---------- TAB HERRAMIENTAS ----------
tab_tools.columnconfigure(0, weight=1)
tab_tools.columnconfigure(1, weight=1)

App.button_Screenshot = ctk.CTkButton(tab_tools, text="Screenshot", command=bttn_screenshot)
App.button_Screenshot.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

App.button_Test = ctk.CTkButton(tab_tools, text="Test", command=bttn_test)
App.button_Test.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

App.button_Recognize = ctk.CTkButton(tab_tools, text="Recognize", command=bttn_recognize)
App.button_Recognize.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

App.button_Buscar_Carro = ctk.CTkButton(tab_tools, text="Buscar Carro", command=bttn_buscar_carro)
App.button_Buscar_Carro.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

App.swipe_dx_label = ctk.CTkLabel(tab_tools, text="Swipe dx:")
App.swipe_dx_label.grid(row=2, column=0, padx=5, pady=(10, 2), sticky="w")
App.swipe_dx_entry = ctk.CTkEntry(tab_tools, placeholder_text="0")
App.swipe_dx_entry.grid(row=3, column=0, padx=5, pady=2, sticky="ew")

App.swipe_dy_label = ctk.CTkLabel(tab_tools, text="Swipe dy:")
App.swipe_dy_label.grid(row=2, column=1, padx=5, pady=(10, 2), sticky="w")
App.swipe_dy_entry = ctk.CTkEntry(tab_tools, placeholder_text="400")
App.swipe_dy_entry.grid(row=3, column=1, padx=5, pady=2, sticky="ew")


# ---------- LOG ----------
App.log_frame = ctk.CTkFrame(App)
App.log_frame.pack(fill="both", expand=True, padx=10, pady=10)

App.log_textbox = ctk.CTkTextbox(App.log_frame, wrap="word")
App.log_textbox.pack(fill="both", expand=True)


# -----------------------------
#   FUNCIÓN DE LOG
# -----------------------------

def log(message):
    timestamp = time.strftime("%H:%M:%S")
    formatted_message = f"[{timestamp}] {message}"

    def append():
        textbox = App.log_textbox._textbox
        textbox.tag_configure("spacing", spacing3=8)
        textbox.insert("end", formatted_message + "\n", "spacing")
        textbox.see("end")

    App.after(0, append)


f.log = log


# -----------------------------
#   INICIO
# -----------------------------

App.mainloop()
