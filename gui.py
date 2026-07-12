from doctest import debug
import time
import customtkinter as ctk
import state
import config

class BotInterface(ctk.CTk):
    def __init__(self, on_start_farm, on_stop, on_screenshot, on_recognize, on_buscar_carro, on_test, on_calibrar_zoom):
        super().__init__()

        # Configuración de ventana
        self.title("Trantor CoC BB-Bot")
        self.geometry("400x500")
        
        # Guardar callbacks lógicos
        self.on_start_farm = on_start_farm
        self.on_stop = on_stop
        self.on_screenshot = on_screenshot
        self.on_recognize = on_recognize
        self.on_buscar_carro = on_buscar_carro
        self.on_test = on_test
        self.on_calibrar_zoom = on_calibrar_zoom

        self._init_components()

    def _init_components(self):
        # ---------- TABS ----------
        self.tabs = ctk.CTkTabview(self)
        self.tabs.pack(fill="x", padx=10, pady=10)

        tab_bot = self.tabs.add("Bot")
        tab_tools = self.tabs.add("Herramientas")
        tab_settings = self.tabs.add("Settings")

        # ---------- TAB BOT ----------
        tab_bot.columnconfigure(0, weight=1)
        tab_bot.columnconfigure(1, weight=1)

        self.button_Farm = ctk.CTkButton(tab_bot, text="Start Farm", command=self._pre_start_farm)


        self.button_Farm.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.button_Stop = ctk.CTkButton(tab_bot, text="Stop", command=self.on_stop)
        self.button_Stop.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # ---------- TAB HERRAMIENTAS ----------
        tab_tools.columnconfigure(0, weight=1)
        tab_tools.columnconfigure(1, weight=1)

        self.button_Screenshot = ctk.CTkButton(tab_tools, text="Screenshot", command=self.on_screenshot)
        self.button_Screenshot.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.button_Test = ctk.CTkButton(tab_tools, text="Test", command=self.on_test)
        self.button_Test.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.button_Recognize = ctk.CTkButton(tab_tools, text="Recognize", command=self.on_recognize)
        self.button_Recognize.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        self.button_Buscar_Carro = ctk.CTkButton(tab_tools, text="Buscar Carro", command=self.on_buscar_carro)
        self.button_Buscar_Carro.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        self.swipe_dx_label = ctk.CTkLabel(tab_tools, text="Swipe dx:")
        self.swipe_dx_label.grid(row=2, column=0, padx=5, pady=(10, 2), sticky="w")
        self.swipe_dx_entry = ctk.CTkEntry(tab_tools, placeholder_text="0")
        self.swipe_dx_entry.insert(0, str(state.swipe_dx))
        self.swipe_dx_entry.bind("<KeyRelease>", self._on_swipe_dx_change)
        self.swipe_dx_entry.grid(row=3, column=0, padx=5, pady=2, sticky="ew")

        self.swipe_dy_label = ctk.CTkLabel(tab_tools, text="Swipe dy:")
        self.swipe_dy_label.grid(row=2, column=1, padx=5, pady=(10, 2), sticky="w")
        self.swipe_dy_entry = ctk.CTkEntry(tab_tools, placeholder_text="400")
        self.swipe_dy_entry.insert(0, str(state.swipe_dy))
        self.swipe_dy_entry.bind("<KeyRelease>", self._on_swipe_dy_change)
        self.swipe_dy_entry.grid(row=3, column=1, padx=5, pady=2, sticky="ew")

        self.button_Calibrar = ctk.CTkButton(
            tab_tools,
            text="Calibrar Zoom y Centro",
            command=self._pre_calibrar_zoom
        )
        self.button_Calibrar.grid(row=4, column=0, columnspan=2, padx=5, pady=10, sticky="ew")


        # ---------- TAB SETTINGS ----------
        tab_settings.columnconfigure(0, weight=1)

        self.attacks_label = ctk.CTkLabel(tab_settings, text="Ataques/ciclo:")
        self.attacks_label.grid(row=0, column=0, padx=5, pady=(10, 2), sticky="w")

        self.attacks_entry = ctk.CTkEntry(tab_settings, placeholder_text="2")
        self.attacks_entry.insert(0, str(state.attacks_per_cycle))
        self.attacks_entry.bind("<KeyRelease>", self._on_attacks_change)
        self.attacks_entry.grid(row=1, column=0, padx=5, pady=2, sticky="ew")

        # Interruptor DEBUG
        self.debug_label = ctk.CTkLabel(tab_settings, text="Modo DEBUG:")
        self.debug_label.grid(row=2, column=0, padx=5, pady=(10, 2), sticky="w")

        self.debug_switch = ctk.CTkSwitch(tab_settings, text="Activar", command=self._toggle_debug)
        if state.debug_mode:
            self.debug_switch.select()
        self.debug_switch.grid(row=3, column=0, padx=5, pady=2, sticky="w")




        # ---------- LOG ----------
        self.log_frame = ctk.CTkFrame(self)
        self.log_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.log_textbox = ctk.CTkTextbox(self.log_frame, wrap="word")
        self.log_textbox.pack(fill="both", expand=True)

    # Métodos públicos para interactuar con la interfaz desde fuera
    """
    def log(self, message, debug=False, category=""):
        if category:
            category_cfg = getattr(config, "DEBUG", {})
            if not category_cfg.get(category, False):
                return
            if not state.debug_mode:
                return

        if debug and not state.debug_mode:
            return

        level = "DBG" if (debug or category) else "INF"

        # Timestamp
        timestamp = time.strftime("%H:%M:%S")
        
        # Formato final
        if state.debug_mode:
            formatted_message = f"[{timestamp}] [{level}]-{category}-{message}"
        else:
            formatted_message = f"[{timestamp}]-{category}- {message}"
        
        def append():
            textbox = self.log_textbox._textbox
            textbox.tag_configure("spacing", spacing3=8)
            textbox.insert("end", formatted_message + "\n", "spacing")
            textbox.see("end")

        self.after(0, append)
    """
    def log(self, formatted_message):

        def append():
            textbox = self.log_textbox._textbox
            textbox.tag_configure("spacing", spacing3=8)
            textbox.insert("end", formatted_message + "\n", "spacing")
            textbox.see("end")

        self.after(0, append)
        
    def get_attacks(self):
        return state.attacks_per_cycle

    def get_swipe_values(self):
        return state.swipe_dx, state.swipe_dy

    def _toggle_debug(self):
        state.set_debug(self.debug_switch.get() == 1)

    def _on_swipe_dx_change(self, event=None):
        try:
            value = self.swipe_dx_entry.get()
            if value:
                state.set_swipe_values(value, state.swipe_dy)
        except:
            pass

    def _on_swipe_dy_change(self, event=None):
        try:
            value = self.swipe_dy_entry.get()
            if value:
                state.set_swipe_values(state.swipe_dx, value)
        except:
            pass

    def _on_attacks_change(self, event=None):
        try:
            value = self.attacks_entry.get()
            if value:
                state.set_attacks(value)
        except:
            pass

    def _pre_start_farm(self):
        # Crear ventana emergente
        popup = ctk.CTkToplevel(self)
        popup.title("Zoom requerido")
        popup.geometry("300x180")
        popup.grab_set()  # Bloquea la ventana principal hasta cerrar esta

        label = ctk.CTkLabel(
            popup,
            text="Haz zoom out manualmente.\nPulsa continuar cuando estés listo.",
            justify="center"
        )
        label.pack(pady=20)

        # Botón continuar
        continue_button = ctk.CTkButton(
            popup,
            text="Continuar",
            command=lambda: self._start_after_zoom(popup)
        )
        continue_button.pack(pady=10)

    def _start_after_zoom(self, popup):
        popup.destroy()  # Cerrar ventana
        self.on_start_farm()  # Ahora sí, arrancar el bot

    def _pre_calibrar_zoom(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Calibración inicial")
        popup.geometry("300x180")
        popup.grab_set()

        label = ctk.CTkLabel(
            popup,
            text="Haz zoom OUT manualmente\n"
                "y deja la cámara centrada.\n\n"
                "Pulsa continuar.",
            justify="center"
        )
        label.pack(pady=20)

        btn = ctk.CTkButton(
            popup,
            text="Continuar",
            command=lambda: self.on_calibrar_zoom(popup)
        )
        btn.pack(pady=10)



