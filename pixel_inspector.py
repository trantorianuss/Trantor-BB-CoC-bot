"""Interactive screenshot tool for inspecting pixel coordinates and RGB values."""

import base64
import tkinter as tk

import cv2
import func as f
import logger as l
import coords


class PixelInspector:
    """Display the current emulator screenshot and report pixel information."""

    def __init__(self, parent):
        self.parent = parent
        self.window = None
        self.image = None
        self.display_image = None
        self.display_scale = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.canvas = None
        self.info_label = None

    def open(self):
        """Capture a screenshot at the emulator's current resolution."""
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
                text=self._resolution_text(),
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

    def _resolution_text(self):
        image_h, image_w = self.image.shape[:2]
        return (
            f"Real: {image_w}x{image_h}    |    "
            f"Base: {coords.BASE_W}x{coords.BASE_H}    |    "
            "Click a pixel to inspect"
        )

    def _redraw(self, _event=None):
        if self.image is None or self.canvas is None:
            return

        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()
        if canvas_w <= 1 or canvas_h <= 1:
            return

        image_h, image_w = self.image.shape[:2]
        self.display_scale = min(canvas_w / image_w, canvas_h / image_h)
        display_w = max(1, int(image_w * self.display_scale))
        display_h = max(1, int(image_h * self.display_scale))

        resized = cv2.resize(
            self.image,
            (display_w, display_h),
            interpolation=cv2.INTER_AREA if self.display_scale < 1 else cv2.INTER_LINEAR,
        )
        rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)

        header = f"P6\\n{display_w} {display_h}\\n255\\n".encode("ascii")
        ppm_data = base64.b64encode(header + rgb.tobytes())
        self.display_image = tk.PhotoImage(data=ppm_data, format="PPM")

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
        if self.image is None or self.display_scale <= 0:
            return

        image_h, image_w = self.image.shape[:2]
        real_x = int((event.x - self.offset_x) / self.display_scale)
        real_y = int((event.y - self.offset_y) / self.display_scale)

        if not (0 <= real_x < image_w and 0 <= real_y < image_h):
            return

        b, g, r = (int(value) for value in self.image[real_y, real_x])
        rgb = (r, g, b)

        base_x = int(real_x * coords.BASE_W / image_w)
        base_y = int(real_y * coords.BASE_H / image_h)

        text = (
            f"Real: ({real_x}, {real_y})    "
            f"Base: ({base_x}, {base_y})    "
            f"RGB: {rgb}"
        )
        self.info_label.configure(text=text)
        l.log(
            f"Pixel Inspector: real=({real_x}, {real_y}) "
            f"base=({base_x}, {base_y}) RGB={rgb}"
        )

    def _close(self):
        if self.window is not None and self.window.winfo_exists():
            self.window.destroy()
        self.window = None
        self.display_image = None


_inspector = None


def open(parent):
    """Open the Pixel Inspector using the given GUI parent window."""
    global _inspector
    if _inspector is None or _inspector.parent != parent:
        _inspector = PixelInspector(parent)
    _inspector.open()
