import time
import customtkinter as ctk
import botstate
import state
import config


class BotInterface(ctk.CTk):
    def __init__(self, on_start_farm, on_stop, on_screenshot, on_recognize, on_buscar_carro, on_test, on_calibrar_zoom, on_calibrate):
        super().__init__()

        self.title("Trantor CoC BB-Bot")
        self.geometry("400x500")
        self.panel_window = None

        self.on_start_farm = on_start_farm
        self.on_stop = on_stop
        self.on_screenshot = on_screenshot
        self.on_recognize = on_recognize
        self.on_buscar_carro = on_buscar_carro
        self.on_test = on_test
        self.on_calibrar_zoom = on_calibrar_zoom
        self.on_calibrate = on_calibrate

        self._init_components()
        self.update_bot_status()

    def _init_components(self):
        self.top_frame = ctk.CTkFrame(self)
        self.top_frame.pack(fill="x", padx=10, pady=(10, 0))
        self.top_frame.columnconfigure(0, weight=4)
        self.top_frame.columnconfigure(1, weight=4)
        self.top_frame.columnconfigure(2, weight=1)

        self.button_Farm = ctk.CTkButton(self.top_frame, text="Start Farm", command=self._pre_start_farm)
        self.button_Farm.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.button_Stop = ctk.CTkButton(self.top_frame, text="Stop", command=self.on_stop)
        self.button_Stop.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.button_side_panel = ctk.CTkButton(self.top_frame, text="☰ ", width=40, command=self._show_side_panel)
        self.button_side_panel.grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.label_bot_status = ctk.CTkLabel(self.top_frame, text="Estado: ?")
        self.label_bot_status.grid(row=1, column=0, columnspan=3, padx=5, pady=(0, 5), sticky="w")

        self.log_frame = ctk.CTkFrame(self)
        self.log_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.log_textbox = ctk.CTkTextbox(self.log_frame, wrap="word")
        self.log_textbox.pack(fill="both", expand=True)
        self.tk_log = self.log_textbox._textbox
        self.tk_log.tag_configure("default")
        self.tk_log.tag_configure("green", foreground="green")
        self.tk_log.tag_configure("red", foreground="red")
        self.tk_log.tag_configure("orange", foreground="orange")
        self.tk_log.tag_configure("blue", foreground="blue")
        self.tk_log.tag_configure("gray", foreground="gray")
        self.tk_log.tag_configure("spacing", spacing3=8)

    def update_bot_status(self):
        if botstate.should_run():
            self.label_bot_status.configure(text="Run request: ON")
        else:
            self.label_bot_status.configure(text="Run request: OFF")
        self.after(500, self.update_bot_status)
    
    def log(self, formatted_message, color="default"):
        def append():
            textbox = self.tk_log
            textbox.configure(state="normal")
            textbox.insert("end", formatted_message + "\n", (color, "spacing"))
            textbox.see("end")
            textbox.configure(state="disabled")
        self.after(0, append)

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
            min_value = self.attacks_min_entry.get()
            max_value = self.attacks_max_entry.get()
            if min_value and max_value:
                state.set_attacks_range(min_value, max_value)
        except:
            pass

    def _on_extra_troops_change(self, event=None):
        min_value = self.extra_troops_min_entry.get()
        max_value = self.extra_troops_max_entry.get()
        if min_value and max_value:
            state.set_extra_troops_range(min_value, max_value)

    def _pre_start_farm(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Zoom requerido")
        popup.geometry("300x180")
        popup.grab_set()
        label = ctk.CTkLabel(popup, text="Haz zoom out manualmente.\nPulsa continuar cuando estés listo.", justify="center")
        label.pack(pady=20)
        continue_button = ctk.CTkButton(popup, text="Continuar", command=lambda: self._start_after_zoom(popup))
        continue_button.pack(pady=10)

    def _start_after_zoom(self, popup):
        popup.destroy()
        self.on_start_farm()

    def _pre_calibrar_zoom(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Calibración inicial")
        popup.geometry("300x180")
        popup.grab_set()
        label = ctk.CTkLabel(popup, text="Haz zoom OUT manualmente\ny deja la cámara centrada.\n\nPulsa continuar.", justify="center")
        label.pack(pady=20)
        btn = ctk.CTkButton(popup, text="Continuar", command=lambda: self.on_calibrar_zoom(popup))
        btn.pack(pady=10)

    def _show_side_panel(self):
        if self.panel_window is not None and self.panel_window.winfo_exists():
            self.panel_window.lift()
            self.panel_window.focus_force()
            return

        self.panel_window = ctk.CTkToplevel(self)
        self.panel_window.title("Panel")
        self.panel_window.geometry("300x500")
        self.panel_window.transient(self)

        main_x = self.winfo_x()
        main_y = self.winfo_y()
        main_w = self.winfo_width()
        panel_w = 300
        screen_w = self.winfo_screenwidth()
        right_x = main_x + main_w + 10
        panel_x = right_x if right_x + panel_w <= screen_w else main_x - panel_w - 10
        self.panel_window.geometry(f"{panel_w}x500+{panel_x}+{main_y}")

        self.tabs = ctk.CTkTabview(self.panel_window)
        self.tabs.pack(fill="x", padx=10, pady=10)
        tab_tools = self.tabs.add("Herramientas")
        tab_settings = self.tabs.add("Settings")
        tab_debug = self.tabs.add("Debug")

        tab_tools.columnconfigure(0, weight=1)
        tab_tools.columnconfigure(1, weight=1)
        self.button_Screenshot = ctk.CTkButton(tab_tools, text="Screenshot", command=self.on_screenshot)
        self.button_Screenshot.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        tab_debug.columnconfigure(0, weight=1)
        tab_debug.columnconfigure(1, weight=1)
        self.button_Test = ctk.CTkButton(tab_debug, text="Test", command=self.on_test)
        self.button_Test.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.button_Recognize = ctk.CTkButton(tab_debug, text="Recognize", command=self.on_recognize)
        self.button_Recognize.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        self.button_Buscar_Carro = ctk.CTkButton(tab_debug, text="Buscar Carro", command=self.on_buscar_carro)
        self.button_Buscar_Carro.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.swipe_dx_label = ctk.CTkLabel(tab_debug, text="Swipe dx:")
        self.swipe_dx_label.grid(row=2, column=0, padx=5, pady=(10, 2), sticky="w")
        self.swipe_dx_entry = ctk.CTkEntry(tab_debug, placeholder_text="0")
        self.swipe_dx_entry.insert(0, str(state.swipe_dx))
        self.swipe_dx_entry.bind("<KeyRelease>", self._on_swipe_dx_change)
        self.swipe_dx_entry.grid(row=3, column=0, padx=5, pady=2, sticky="ew")
        self.swipe_dy_label = ctk.CTkLabel(tab_debug, text="Swipe dy:")
        self.swipe_dy_label.grid(row=2, column=1, padx=5, pady=(10, 2), sticky="w")
        self.swipe_dy_entry = ctk.CTkEntry(tab_debug, placeholder_text="400")
        self.swipe_dy_entry.insert(0, str(state.swipe_dy))
        self.swipe_dy_entry.bind("<KeyRelease>", self._on_swipe_dy_change)
        self.swipe_dy_entry.grid(row=3, column=1, padx=5, pady=2, sticky="ew")
        self.button_Calibrar = ctk.CTkButton(tab_debug, text="Calibrar Zoom y Centro", command=self._pre_calibrar_zoom)
        self.button_Calibrar.grid(row=4, column=0, columnspan=2, padx=5, pady=10, sticky="ew")
        self.button_Calibrate = ctk.CTkButton(tab_debug, text="Calibrate", command=self.on_calibrate)
        self.button_Calibrate.grid(row=5, column=0, columnspan=2, padx=5, pady=10, sticky="ew")

        tab_settings.columnconfigure(0, weight=1)
        self.attacks_label = ctk.CTkLabel(tab_settings, text="Ataques/ciclo (min/max):")
        self.attacks_label.grid(row=0, column=0, padx=5, pady=(10, 2), sticky="w")
        self.attacks_min_entry = ctk.CTkEntry(tab_settings, placeholder_text="2")
        self.attacks_min_entry.insert(0, str(state.attacks_min_per_cycle))
        self.attacks_min_entry.bind("<KeyRelease>", self._on_attacks_change)
        self.attacks_min_entry.grid(row=1, column=0, padx=5, pady=2, sticky="ew")
        self.attacks_max_entry = ctk.CTkEntry(tab_settings, placeholder_text="4")
        self.attacks_max_entry.insert(0, str(state.attacks_max_per_cycle))
        self.attacks_max_entry.bind("<KeyRelease>", self._on_attacks_change)
        self.attacks_max_entry.grid(row=2, column=0, padx=5, pady=2, sticky="ew")

        self.extra_troops_label = ctk.CTkLabel(tab_settings, text="Tropas extra/ataque (min/max):")
        self.extra_troops_label.grid(row=3, column=0, padx=5, pady=(10, 2), sticky="w")
        self.extra_troops_min_entry = ctk.CTkEntry(tab_settings, placeholder_text="0")
        self.extra_troops_min_entry.insert(0, str(state.extra_troops_min))
        self.extra_troops_min_entry.bind("<KeyRelease>", self._on_extra_troops_change)
        self.extra_troops_min_entry.grid(row=4, column=0, padx=5, pady=2, sticky="ew")
        self.extra_troops_max_entry = ctk.CTkEntry(tab_settings, placeholder_text="4")
        self.extra_troops_max_entry.insert(0, str(state.extra_troops_max))
        self.extra_troops_max_entry.bind("<KeyRelease>", self._on_extra_troops_change)
        self.extra_troops_max_entry.grid(row=5, column=0, padx=5, pady=2, sticky="ew")

        self.debug_label = ctk.CTkLabel(tab_settings, text="Modo DEBUG:")
        self.debug_label.grid(row=6, column=0, padx=5, pady=(10, 2), sticky="w")
        self.debug_switch = ctk.CTkSwitch(tab_settings, text="Activar", command=self._toggle_debug)
        if state.debug_mode:
            self.debug_switch.select()
        self.debug_switch.grid(row=7, column=0, padx=5, pady=2, sticky="w")

        self.panel_window.lift()
        self.panel_window.focus_force()
