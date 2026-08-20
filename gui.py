import time
import customtkinter as ctk
import botstate
import settings
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
        self.top_frame.columnconfigure(0, weight=1)
        self.top_frame.columnconfigure(1, weight=4)
        self.top_frame.columnconfigure(2, weight=4)
        self.top_frame.columnconfigure(3, weight=1)

        self.button_Farm = ctk.CTkButton(self.top_frame, text="Start Farm", command=self._pre_start_farm)
        self.button_Farm.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        self.button_Stop = ctk.CTkButton(self.top_frame, text="Stop", command=self.on_stop)
        self.button_Stop.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        self.button_side_panel = ctk.CTkButton(self.top_frame, text="☰ ", width=40, command=self._show_side_panel)
        self.button_side_panel.grid(row=0, column=3, padx=5, pady=5, sticky="e")

        self.label_bot_status = ctk.CTkLabel(self.top_frame, text="Status: ?")
        self.label_bot_status.grid(row=1, column=1, columnspan=3, padx=5, pady=(0, 5), sticky="w")

        self.label_bot_status_indicator = ctk.CTkLabel(
            self.top_frame,
            text="●",
            font=ctk.CTkFont(size=18),
        )
        self.label_bot_status_indicator.grid(row=1, column=0, padx=(5, 0), pady=(0, 5), sticky="e")

        self.log_frame = ctk.CTkFrame(self)
        self.log_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.log_textbox = ctk.CTkTextbox(self.log_frame, wrap="word")
        self.log_textbox.pack(fill="both", expand=True)
        self.tk_log = self.log_textbox._textbox

        for name, color in config.LOG_COLORS.items():
            if color is None:
                self.tk_log.tag_configure(name)
            else:
                self.tk_log.tag_configure(name, foreground=color)

        self.tk_log.tag_configure("spacing", spacing3=8)

        self.log_controls_frame = ctk.CTkFrame(self)
        self.log_controls_frame.pack(fill="x", padx=10, pady=(0, 10))
        self.log_controls_frame.columnconfigure(0, weight=1)

        self.autoscroll_switch = ctk.CTkCheckBox(
            self.log_controls_frame,
            text="Auto Scroll",
            command=self._toggle_autoscroll,
        )
        self.autoscroll_switch.select()
        self.autoscroll_switch.grid(row=0, column=0, padx=5, pady=5, sticky="w")

    def update_bot_status(self):
        status = botstate.get_status()

        if status == botstate.RUNNING:
            self.label_bot_status_indicator.configure(text_color="green")
            self.label_bot_status.configure(text="Running")
            self.button_Farm.configure(state="disabled")
            self.button_Stop.configure(state="normal")
        elif status == botstate.STOPPING:
            self.label_bot_status_indicator.configure(text_color="orange")
            self.label_bot_status.configure(text="Stopping")
            self.button_Farm.configure(state="disabled")
            self.button_Stop.configure(state="disabled")
        else:
            self.label_bot_status_indicator.configure(text_color="red")
            self.label_bot_status.configure(text="Stopped")
            self.button_Farm.configure(state="normal")
            self.button_Stop.configure(state="disabled")

        self.after(500, self.update_bot_status)

    def log(self, formatted_message, color="default"):
        def append():
            textbox = self.tk_log
            textbox.configure(state="normal")
            textbox.insert("end", formatted_message + "\n", (color, "spacing"))
            if self.autoscroll_switch.get() == 1:
                textbox.see("end")
            textbox.configure(state="disabled")
        self.after(0, append)

    def _toggle_autoscroll(self):
        if self.autoscroll_switch.get() == 1:
            self.tk_log.see("end")

    # ---------- Handlers ----------
    def _on_attack_mode_change(self, choice):
        settings.set_attack_mode(choice)

    def _on_swipe_dx_change(self, event=None):
        try:
            value = self.swipe_dx_entry.get()
            if value:
                settings.set_swipe_values(value, settings.swipe_dy)
        except Exception:
            pass

    def _on_swipe_dy_change(self, event=None):
        try:
            value = self.swipe_dy_entry.get()
            if value:
                settings.set_swipe_values(settings.swipe_dx, value)
        except Exception:
            pass

    def _on_attacks_change(self, event=None):
        try:
            min_value = self.attacks_min_entry.get()
            max_value = self.attacks_max_entry.get()
            if min_value and max_value:
                settings.set_attacks_range(min_value, max_value)
        except Exception:
            pass

    def _on_extra_troops_change(self, event=None):
        min_value = self.extra_troops_min_entry.get()
        max_value = self.extra_troops_max_entry.get()
        if min_value and max_value:
            settings.set_extra_troops_range(min_value, max_value)

    def _toggle_debug_mode(self):
        settings.set_debug(self.debug_checkbox.get() == 1)

    def _toggle_debug_category(self, category, variable):
        config.DEBUG_CATEGORIES[category] = bool(variable.get())

    def _toggle_debug_inspection(self):
        config.DEBUG_INSPECTION = bool(self.debug_inspection_checkbox.get())

    def _toggle_debug_file_log(self, log_name, variable):
        config.DEBUG_FILE_LOGS[log_name] = bool(variable.get())

    def _pre_start_farm(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Zoom Required")
        popup.geometry("300x180")
        popup.grab_set()
        label = ctk.CTkLabel(popup, text="Zoom out manually.\nClick Continue when ready.", justify="center")
        label.pack(pady=20)
        continue_button = ctk.CTkButton(popup, text="Continue", command=lambda: self._start_after_zoom(popup))
        continue_button.pack(pady=10)

    def _start_after_zoom(self, popup):
        popup.destroy()
        self.on_start_farm()

    def _pre_calibrar_zoom(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Initial Calibration")
        popup.geometry("300x180")
        popup.grab_set()
        label = ctk.CTkLabel(popup, text="Zoom OUT manually\nand center the camera.\n\nClick Continue.", justify="center")
        label.pack(pady=20)
        btn = ctk.CTkButton(popup, text="Continue", command=lambda: self.on_calibrar_zoom(popup))
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

        # ---------------- BB ----------------
        tab_bb = self.tabs.add("BB")
        tab_bb.columnconfigure(0, weight=1)

        self.attack_mode_label = ctk.CTkLabel(tab_bb, text="Attack mode:")
        self.attack_mode_label.grid(row=0, column=0, padx=5, pady=(10, 2), sticky="w")
        self.attack_mode_menu = ctk.CTkOptionMenu(
            tab_bb,
            values=["Surrender", "Full attack (Beta)"],
            command=self._on_attack_mode_change,
        )
        attack_mode_visible = {
            "surrender": "Surrender",
            "full": "Full attack (Beta)",
        }.get(settings.get_attack_mode(), "Surrender")
        self.attack_mode_menu.set(attack_mode_visible)
        self.attack_mode_menu.grid(row=1, column=0, padx=5, pady=2, sticky="ew")

        self.attacks_label = ctk.CTkLabel(tab_bb, text="Attacks per cycle (min/max):")
        self.attacks_label.grid(row=2, column=0, padx=5, pady=(10, 2), sticky="w")
        self.attacks_min_entry = ctk.CTkEntry(tab_bb, placeholder_text="2")
        self.attacks_min_entry.insert(0, str(settings.attacks_min_per_cycle))
        self.attacks_min_entry.bind("<KeyRelease>", self._on_attacks_change)
        self.attacks_min_entry.grid(row=3, column=0, padx=5, pady=2, sticky="ew")
        self.attacks_max_entry = ctk.CTkEntry(tab_bb, placeholder_text="4")
        self.attacks_max_entry.insert(0, str(settings.attacks_max_per_cycle))
        self.attacks_max_entry.bind("<KeyRelease>", self._on_attacks_change)
        self.attacks_max_entry.grid(row=4, column=0, padx=5, pady=2, sticky="ew")

        self.extra_troops_label = ctk.CTkLabel(tab_bb, text="Extra troops per attack (min/max):")
        self.extra_troops_label.grid(row=5, column=0, padx=5, pady=(10, 2), sticky="w")
        self.extra_troops_min_entry = ctk.CTkEntry(tab_bb, placeholder_text="0")
        self.extra_troops_min_entry.insert(0, str(settings.extra_troops_min))
        self.extra_troops_min_entry.bind("<KeyRelease>", self._on_extra_troops_change)
        self.extra_troops_min_entry.grid(row=6, column=0, padx=5, pady=2, sticky="ew")
        self.extra_troops_max_entry = ctk.CTkEntry(tab_bb, placeholder_text="4")
        self.extra_troops_max_entry.insert(0, str(settings.extra_troops_max))
        self.extra_troops_max_entry.bind("<KeyRelease>", self._on_extra_troops_change)
        self.extra_troops_max_entry.grid(row=7, column=0, padx=5, pady=2, sticky="ew")

        # ---------------- Tools ----------------
        tab_tools = self.tabs.add("Tools")
        tab_tools.columnconfigure(0, weight=1)
        self.button_Screenshot = ctk.CTkButton(tab_tools, text="Screenshot", command=self.on_screenshot)
        self.button_Screenshot.grid(row=0, column=0, padx=5, pady=10, sticky="ew")

        self.screenshot_resize_checkbox = ctk.CTkCheckBox(
            tab_tools,
            text="Resize screenshot to base resolution (1920x1080)",
        )
        self.screenshot_resize_checkbox.select()
        self.screenshot_resize_checkbox.grid(row=1, column=0, padx=5, pady=(0, 10), sticky="w")

        # ---------------- Dev Tools ----------------
        tab_dev_tools = self.tabs.add("Dev Tools")
        tab_dev_tools.columnconfigure(0, weight=1)
        tab_dev_tools.columnconfigure(1, weight=1)

        self.button_Test = ctk.CTkButton(tab_dev_tools, text="Test", command=self.on_test)
        self.button_Test.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.button_Recognize = ctk.CTkButton(tab_dev_tools, text="Recognize", command=self.on_recognize)
        self.button_Recognize.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        self.button_Buscar_Carro = ctk.CTkButton(tab_dev_tools, text="Find Cart", command=self.on_buscar_carro)
        self.button_Buscar_Carro.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        self.swipe_dx_label = ctk.CTkLabel(tab_dev_tools, text="Swipe dx:")
        self.swipe_dx_label.grid(row=2, column=0, padx=5, pady=(10, 2), sticky="w")
        self.swipe_dx_entry = ctk.CTkEntry(tab_dev_tools, placeholder_text="0")
        self.swipe_dx_entry.insert(0, str(settings.swipe_dx))
        self.swipe_dx_entry.bind("<KeyRelease>", self._on_swipe_dx_change)
        self.swipe_dx_entry.grid(row=3, column=0, padx=5, pady=2, sticky="ew")

        self.swipe_dy_label = ctk.CTkLabel(tab_dev_tools, text="Swipe dy:")
        self.swipe_dy_label.grid(row=2, column=1, padx=5, pady=(10, 2), sticky="w")
        self.swipe_dy_entry = ctk.CTkEntry(tab_dev_tools, placeholder_text="400")
        self.swipe_dy_entry.insert(0, str(settings.swipe_dy))
        self.swipe_dy_entry.bind("<KeyRelease>", self._on_swipe_dy_change)
        self.swipe_dy_entry.grid(row=3, column=1, padx=5, pady=2, sticky="ew")

        self.button_Calibrar = ctk.CTkButton(tab_dev_tools, text="Calibrate Zoom & Center", command=self._pre_calibrar_zoom)
        self.button_Calibrar.grid(row=4, column=0, columnspan=2, padx=5, pady=10, sticky="ew")
        self.button_Calibrate = ctk.CTkButton(tab_dev_tools, text="Calibrate", command=self.on_calibrate)
        self.button_Calibrate.grid(row=5, column=0, columnspan=2, padx=5, pady=10, sticky="ew")

        # ---------------- Debug ----------------
        tab_debug = self.tabs.add("Debug")
        tab_debug.columnconfigure(0, weight=1)
        tab_debug.columnconfigure(1, weight=1)

        self.debug_checkbox = ctk.CTkCheckBox(
            tab_debug,
            text="Enable debug logs",
            command=self._toggle_debug_mode,
        )
        if settings.debug_mode:
            self.debug_checkbox.select()
        self.debug_checkbox.grid(row=0, column=0, columnspan=2, padx=5, pady=(10, 8), sticky="w")

        self.debug_inspection_checkbox = ctk.CTkCheckBox(
            tab_debug,
            text="Show log source (file / function / line)",
            command=self._toggle_debug_inspection,
        )
        if config.DEBUG_INSPECTION:
            self.debug_inspection_checkbox.select()
        self.debug_inspection_checkbox.grid(row=1, column=0, columnspan=2, padx=5, pady=(0, 8), sticky="w")

        self.debug_categories_label = ctk.CTkLabel(tab_debug, text="Log categories:")
        self.debug_categories_label.grid(row=2, column=0, columnspan=2, padx=5, pady=(0, 5), sticky="w")

        self.debug_category_vars = {}
        row = 3
        for index, (category, enabled) in enumerate(config.DEBUG_CATEGORIES.items()):
            label = category.replace("_", " ").title()
            variable = ctk.IntVar(value=1 if enabled else 0)
            checkbox = ctk.CTkCheckBox(
                tab_debug,
                text=label,
                variable=variable,
                command=lambda c=category, v=variable: self._toggle_debug_category(c, v),
            )
            checkbox.grid(row=row + index // 2, column=index % 2, padx=5, pady=3, sticky="w")
            self.debug_category_vars[category] = variable

        file_logs_row = row + (len(config.DEBUG_CATEGORIES) + 1) // 2 + 1
        self.debug_file_logs_label = ctk.CTkLabel(tab_debug, text="Diagnostic file logs history:")
        self.debug_file_logs_label.grid(row=file_logs_row, column=0, columnspan=2, padx=5, pady=(10, 5), sticky="w")

        self.debug_file_log_vars = {}
        for index, (log_name, enabled) in enumerate(config.DEBUG_FILE_LOGS.items()):
            label = log_name.replace("_", " ").title()
            variable = ctk.IntVar(value=1 if enabled else 0)
            checkbox = ctk.CTkCheckBox(
                tab_debug,
                text=f"{label}",
                variable=variable,
                command=lambda n=log_name, v=variable: self._toggle_debug_file_log(n, v),
            )
            checkbox.grid(row=file_logs_row + 1 + index // 2, column=index % 2, padx=5, pady=3, sticky="w")
            self.debug_file_log_vars[log_name] = variable

        self.panel_window.lift()
        self.panel_window.focus_force()