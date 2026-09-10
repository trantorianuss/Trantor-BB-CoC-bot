import tkinter as tk
import ttkbootstrap as ttk

import botstate
import settings


class BotInterface(ttk.Window):
    """Minimal ttkbootstrap GUI used for the toolkit migration test."""

    def __init__(
        self,
        on_start_farm,
        on_stop,
        on_screenshot,
        on_recognize,
        on_buscar_carro,
        on_test,
        on_calibrar_zoom,
        on_calibrate,
        on_pixel_inspector,
    ):
        super().__init__(title="Trantor CoC Bot", themename="darkly", size=(400, 500))

        self.on_start_farm = on_start_farm
        self.on_stop = on_stop
        self.on_screenshot = on_screenshot
        self.on_recognize = on_recognize
        self.on_buscar_carro = on_buscar_carro
        self.on_test = on_test
        self.on_calibrar_zoom = on_calibrar_zoom
        self.on_calibrate = on_calibrate
        self.on_pixel_inspector = on_pixel_inspector

        self._log_lines = []
        self.screenshot_resize_var = tk.IntVar(value=1)
        self.screenshot_resize_checkbox = ttk.Checkbutton(
            self,
            text="Resize screenshot to base resolution (1920x1080)",
            variable=self.screenshot_resize_var,
        )

        self._init_components()
        self.update_bot_status()

    def _init_components(self):
        top_frame = ttk.Frame(self, padding=(10, 10, 10, 0))
        top_frame.pack(fill="x")
        top_frame.columnconfigure(0, weight=1)
        top_frame.columnconfigure(1, weight=0)

        self.button_Farm = ttk.Button(
            top_frame,
            text="Start BB",
            command=self._on_farm_button_click,
            bootstyle="success",
        )
        self.button_Farm.grid(row=0, column=0, padx=(0, 5), pady=5, sticky="ew")

        self.bot_type_switch = ttk.Checkbutton(
            top_frame,
            text="TH",
            command=self._on_bot_type_change,
            bootstyle="success-round-toggle",
        )
        if settings.get_bot_type() == "TH":
            self.bot_type_switch.invoke()
        self.bot_type_switch.grid(row=0, column=1, padx=(5, 0), pady=5)

        status_frame = ttk.Frame(self, padding=(10, 0, 10, 5))
        status_frame.pack(fill="x")

        self.label_bot_status_indicator = ttk.Label(status_frame, text="●", font=("TkDefaultFont", 16))
        self.label_bot_status_indicator.pack(side="left", padx=(0, 5))

        self.label_bot_status = ttk.Label(status_frame, text="Status: ?")
        self.label_bot_status.pack(side="left")

        log_frame = ttk.Frame(self, padding=10)
        log_frame.pack(fill="both", expand=True)

        self.log_textbox = tk.Text(log_frame, wrap="word", state="disabled")
        self.log_textbox.pack(fill="both", expand=True)
        self.tk_log = self.log_textbox

        controls = ttk.Frame(self, padding=(10, 0, 10, 10))
        controls.pack(fill="x")

        self.autoscroll_var = tk.IntVar(value=1)
        self.autoscroll_switch = ttk.Checkbutton(
            controls,
            text="Auto Scroll",
            variable=self.autoscroll_var,
            bootstyle="round-toggle",
        )
        self.autoscroll_switch.pack(side="left")

    def update_bot_status(self):
        status = botstate.get_status()

        if status == botstate.RUNNING:
            self.label_bot_status_indicator.configure(bootstyle="success")
            self.label_bot_status.configure(text="Running")
            self.button_Farm.configure(text="Stop", bootstyle="danger", state="normal")
            self.bot_type_switch.configure(state="disabled")
        elif status == botstate.STOPPING:
            self.label_bot_status_indicator.configure(bootstyle="warning")
            self.label_bot_status.configure(text="Stopping")
            self.button_Farm.configure(text="Stopping", bootstyle="warning", state="disabled")
            self.bot_type_switch.configure(state="disabled")
        else:
            self.label_bot_status_indicator.configure(bootstyle="danger")
            self.label_bot_status.configure(text="Stopped")
            bot_type = settings.get_bot_type()
            self.button_Farm.configure(
                text="Start TH" if bot_type == "TH" else "Start BB",
                bootstyle="success",
                state="normal",
            )
            self.bot_type_switch.configure(state="normal")

        self.after(500, self.update_bot_status)

    def log(self, formatted_message, color="default"):
        def append():
            self.log_textbox.configure(state="normal")
            self.log_textbox.insert("end", formatted_message + "\n")
            if self.autoscroll_var.get() == 1:
                self.log_textbox.see("end")
            self.log_textbox.configure(state="disabled")

        self.after(0, append)

    def _on_farm_button_click(self):
        if botstate.get_status() == botstate.RUNNING:
            self.on_stop()
        else:
            self._pre_start_farm()

    def _on_bot_type_change(self):
        bot_type = "TH" if self.bot_type_switch.instate(["selected"]) else "BB"
        settings.set_bot_type(bot_type)
        if botstate.get_status() not in (botstate.RUNNING, botstate.STOPPING):
            self.button_Farm.configure(text="Start TH" if bot_type == "TH" else "Start BB")

    def _pre_start_farm(self):
        popup = ttk.Toplevel(self, title="Zoom Required", size=(300, 180), transient=self)
        popup.grab_set()

        ttk.Label(
            popup,
            text="Zoom out manually.\nClick Continue when ready.",
            justify="center",
        ).pack(pady=20)

        ttk.Button(
            popup,
            text="Continue",
            command=lambda: self._start_after_zoom(popup),
            bootstyle="primary",
        ).pack(pady=10)

    def _start_after_zoom(self, popup):
        popup.destroy()
        self.on_start_farm()

    def get_swipe_values(self):
        return "", "400"


if __name__ == "__main__":
    app = BotInterface(
        on_start_farm=lambda: None,
        on_stop=lambda: None,
        on_screenshot=lambda: None,
        on_recognize=lambda: None,
        on_buscar_carro=lambda: None,
        on_test=lambda: None,
        on_calibrar_zoom=lambda popup=None: None,
        on_calibrate=lambda popup=None: None,
        on_pixel_inspector=lambda: None,
    )
    app.mainloop()
