
import customtkinter as ctk

# --- 1. COMPONENTE PILL TOGGLE ---
class PillToggle(ctk.CTkFrame):
    def __init__(self, master, option1="Town Hall", option2="Builder Base", command=None, **kwargs):
        super().__init__(
            master, 
            fg_color="#1a1a1e", 
            corner_radius=20, 
            border_width=1, 
            border_color="#2a2a30", 
            **kwargs
        )
        self.command = command
        self.current_state = 0

        self.btn_kwargs = {
            "corner_radius": 18,
            "height": 28,
            "font": ctk.CTkFont(size=12, weight="bold"),
            "hover": False,
        }

        self.btn1 = ctk.CTkButton(
            self, text=option1, fg_color="#2563eb", text_color="#ffffff",
            command=lambda: self._select(0), **self.btn_kwargs
        )
        self.btn1.grid(row=0, column=0, padx=(3, 1), pady=3, sticky="ew")

        self.btn2 = ctk.CTkButton(
            self, text=option2, fg_color="transparent", text_color="#a1a1aa",
            command=lambda: self._select(1), **self.btn_kwargs
        )
        self.btn2.grid(row=0, column=1, padx=(1, 3), pady=3, sticky="ew")

        self.grid_columnconfigure((0, 1), weight=1)

    def _select(self, index):
        if self.current_state == index: return
        self.current_state = index

        if index == 0:
            self.btn1.configure(fg_color="#2563eb", text_color="#ffffff")
            self.btn2.configure(fg_color="transparent", text_color="#a1a1aa")
        else:
            self.btn1.configure(fg_color="transparent", text_color="#a1a1aa")
            self.btn2.configure(fg_color="#2563eb", text_color="#ffffff")

        if self.command: self.command(index)

    def get(self): return self.current_state


# --- 2. COMPONENTE CHIPS DESACOPLADOS ---
class ChipToggle(ctk.CTkFrame):
    def __init__(self, master, option1="Town Hall", option2="Builder Base", command=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.command = command
        self.current_state = 0

        self.inactive_style = {
            "fg_color": "#1a1a1e",
            "border_width": 1,
            "border_color": "#2a2a30",
            "text_color": "#a1a1aa"
        }

        self.active_style = {
            "fg_color": "#2563eb",
            "border_width": 0,
            "text_color": "#ffffff"
        }

        self.chip1 = ctk.CTkButton(
            self, text=option1, corner_radius=8, height=30,
            font=ctk.CTkFont(size=12, weight="bold"),
            command=lambda: self._select(0),
            **self.active_style
        )
        self.chip1.grid(row=0, column=0, padx=(0, 4), sticky="ew")

        self.chip2 = ctk.CTkButton(
            self, text=option2, corner_radius=8, height=30,
            font=ctk.CTkFont(size=12, weight="bold"),
            command=lambda: self._select(1),
            **self.inactive_style
        )
        self.chip2.grid(row=0, column=1, padx=(4, 0), sticky="ew")

        self.grid_columnconfigure((0, 1), weight=1)

    def _select(self, index):
        if self.current_state == index: return
        self.current_state = index

        if index == 0:
            self.chip1.configure(**self.active_style)
            self.chip2.configure(**self.inactive_style)
        else:
            self.chip1.configure(**self.inactive_style)
            self.chip2.configure(**self.active_style)

        if self.command: self.command(index)

    def get(self): return self.current_state


# --- APLICACIÓN DE PRUEBA Y COMPARACIÓN ---
if __name__ == "__main__":
    ctk.set_appearance_mode("dark")

    app = ctk.CTk()
    app.geometry("340x360")
    app.title("Demo de Selector de Modo")

    # Opción A: Pill Toggle
    label1 = ctk.CTkLabel(app, text="Opción A: Pill Toggle Flotante", font=ctk.CTkFont(size=11, weight="bold"))
    label1.pack(anchor="w", padx=20, pady=(20, 5))
    
    toggle_pill = PillToggle(app, option1="TH", option2="BB", 
                             command=lambda idx: print(f"Pill: {'TH' if idx==0 else 'BB'}"))
    toggle_pill.pack(fill="x", padx=20)

    # Opción B: Chips Desacoplados
    label2 = ctk.CTkLabel(app, text="Opción B: Chips Desacoplados", font=ctk.CTkFont(size=11, weight="bold"))
    label2.pack(anchor="w", padx=20, pady=(20, 5))

    toggle_chips = ChipToggle(app, option1="Town Hall", option2="Builder Base", 
                              command=lambda idx: print(f"Chips: {'TH' if idx==0 else 'BB'}"))
    toggle_chips.pack(fill="x", padx=20)

    # Opción C: SegmentedButton Nativo de CustomTkinter
    label3 = ctk.CTkLabel(app, text="Opción C: CTkSegmentedButton Nativo", font=ctk.CTkFont(size=11, weight="bold"))
    label3.pack(anchor="w", padx=20, pady=(20, 5))

    toggle_segmented = ctk.CTkSegmentedButton(
        app,
        values=["Town Hall", "Builder Base"],
        selected_color="#2563eb",
        selected_hover_color="#1d4ed8",
        unselected_color="#1a1a1e",
        unselected_hover_color="#2a2a30",
        text_color="#ffffff",
        font=ctk.CTkFont(size=12, weight="bold"),
        command=lambda val: print(f"Segmented: {val}")
    )
    toggle_segmented.set("Town Hall")  # Valor por defecto
    toggle_segmented.pack(fill="x", padx=20)

    app.mainloop()