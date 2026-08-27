"""Interactive screenshot tool for inspecting pixel coordinates and RGB values."""

import tkinter as tk

import cv2
import func as f
import logger as l


class PixelInspector:
    """Display a screenshot in a resizable window and report clicked pixels."""

    def __init__(self, parent):
        self.parent = parent
        self.window = None
        self.image = None
        self.display_image = None
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.canvas = None
        self.info_label = None

    def open(self):
        """Capture a screenshot and open the interactive pixel inspector."""
        try:
            image = f.capture_screenshot()
            if image is None:
                raise RuntimeError("Screenshot capture returned no image")

            self.image = image

            if self.window is not None and self.window.winfo_exists():
                self.window.destroy()

            self.window = tk.Toplevel(self.parent)
            self.window.title("Pixel Inspector")
            self.window.transient(self.parent)

            screen_w = self.window.winfo_screenwidth()
            screen_h = self.window.winfo_screenheight()
            window_w = max(800, int(screen_w * 0.75))
            window_h = max(600, int(screen_h * 0.75))
            self.window.geometry(f"{window_w}x{window_h}")
            self.window.minsize(600, 450)

            self.info_label = tk.Label(
                self.window,
                text="Click a pixel to inspect its coordinates and RGB color.",
                anchor="w",
                padx=8,
                pady=6,
            )
            self.info_label.pack(fill="x")

            self.canvas = tk.Canvas(self.window, background="black", highlightthickness=0)
            self.canvas.pack(fill="both", expand=True, padx=8, pady=(0, 8))
            self.canvas.bind("<Button-1>", self._on_click)
            self.canvas.bind("<Configure>", self._redraw)

            self.window.protocol("WM_DELETE_WINDOW", self._close)
            self.window.lift()
            self.window.focus_force()

        except Exception as exc:
            l.log(f"Pixel Inspector failed: {exc}")

    def _redraw(self, _event=None):
        if self.image is None or self.canvas is None:
            return

        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()
        if canvas_w <= 1 or canvas_h <= 1:
            return

        image_h, image_w = self.image.shape[:2]
        self.scale = min(canvas_w / image_w, canvas_h / image_h)
        display_w = max(1, int(image_w * self.scale))
        display_h = max(1, int(image_h * self.scale))

        resized = cv2.resize(
            self.image,
            (display_w, display_h),
            interpolation=cv2.INTER_AREA if self.scale < 1 else cv2.INTER_LINEAR,
        )
        rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)

        # Tkinter PhotoImage can load PPM data without an extra Pillow dependency.
        header = f"P6\\n{display_w} {display_h}\\n255\\n".encode("ascii")
        self.display_image = tk.PhotoImage(data=header + rgb.tobytes(), format="PPM")

        self.offset_x = (canvas_w - display_w) // 2
        self.offset_y = (canvas_h - display_h) // 2

        self.canvas.delete("all")
        self.canvas.create_image(
            self.offset_x,
            self.offset_y,
            image=self.display_image,
            anchor="nw",
        )

    def _on_click(self, event):
        if self.image is None:
            return

        image_h, image_w = self.image.shape[:2]
        x = int((event.x - self.offset_x) / self.scale)
        y = int((event.y - self.offset_y) / self.scale)

        if not (0 <= x < image_w and 0 <= y < image_h):
            return

        # OpenCV stores pixels as BGR; report the requested RGB order.
        b, g, r = (int(value) for value in self.image[y, x])
        rgb = (r, g, b)

        text = f"Pixel: ({x}, {y})    RGB: {rgb}"
        self.info_label.configure(text=text)
        l.log(f"Pixel Inspector: ({x}, {y}) RGB={rgb}")

    def _close(self):
        if self.window is not None and self.window.winfo_exists():
            self.window.destroy()
        self.window = None
        self.display_image = None


def install(app):
    """Add the Pixel Inspector button to the existing Tools tab."""
    inspector = PixelInspector(app)
    tab_tools = app.tabs.tab("Tools")
    button = tk.Button(
        tab_tools,
        text="Pixel Inspector",
        command=inspector.open,
    )
    button.grid(row=2, column=0, padx=5, pady=(0, 10), sticky="ew")
    app.pixel_inspector = inspector
