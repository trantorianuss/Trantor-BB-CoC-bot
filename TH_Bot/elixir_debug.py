"""Helpers for debugging Town Hall elixir detection."""

import os
import cv2


def save_elixir_check(image, path="screenshots/th_elixir_check.png"):
    """Save the exact screenshot used by TH elixir-full detection."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    cv2.imwrite(path, image)
    return path
