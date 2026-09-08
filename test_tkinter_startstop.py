import customtkinter as ctk

class SingleActionButton(ctk.CTkButton):
    def __init__(self, master, on_start=None, on_stop=None, **kwargs):
        super().__init__(master, **kwargs)
        self.on_start = on_start
        self.on_stop = on_stop
        self.is_running = False
        
        # Configuración inicial (Estado: Detenido)
        self._update_appearance()
        self.configure(command=self._toggle_state)

    def _toggle_state(self):
        self.is_running = not self.is_running
        self._update_appearance()

        if self.is_running and self.on_start:
            self.on_start()
        elif not self.is_running and self.on_stop:
            self.on_stop()

    def _update_appearance(self):
        if self.is_running:
            self.configure(
                text="Stop Bot",
                fg_color="#dc2626",        # Rojo
                hover_color="#b91c1c"
            )
        else:
            self.configure(
                text="Start Bot",
                fg_color="#16a34a",        # Verde
                hover_color="#15803d"
            )

# --- Ejemplo de uso ---
if __name__ == "__main__":
    app = ctk.CTk()
    app.geometry("250x120")

    def arrancar():
        print("Bot iniciado...")

    def parar():
        print("Bot detenido...")

    btn = SingleActionButton(app, on_start=arrancar, on_stop=parar, height=38, font=ctk.CTkFont(weight="bold"))
    btn.pack(pady=40, padx=20, fill="x")

    app.mainloop()