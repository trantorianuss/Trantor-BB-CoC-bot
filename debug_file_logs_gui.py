"""GUI controls for diagnostic log files.

The existing Debug tab owns the normal debug-log controls. This module adds
independent switches for the two diagnostic history files without changing
the main BotInterface implementation.
"""

import customtkinter as ctk

import config


_INSTALLED = False


def _toggle_file_log(key, variable):
    config.DEBUG_FILE_LOGS[key] = bool(variable.get())


def _add_controls(app):
    """Add the file-history controls to the already-created Debug tab."""
    tab_debug = app.tabs.tab("Debug")

    # The existing category grid starts at row 3 and uses two columns.
    category_rows = (len(config.DEBUG) + 1) // 2
    row = 3 + category_rows + 1

    label = ctk.CTkLabel(tab_debug, text="Diagnostic file logs:")
    label.grid(row=row, column=0, columnspan=2, padx=5, pady=(10, 5), sticky="w")

    row += 1

    drop_variable = ctk.IntVar(
        value=1 if config.DEBUG_FILE_LOGS.get("drop_finder", False) else 0
    )
    drop_checkbox = ctk.CTkCheckBox(
        tab_debug,
        text="Write Drop Finder history",
        variable=drop_variable,
        command=lambda: _toggle_file_log("drop_finder", drop_variable),
    )
    drop_checkbox.grid(row=row, column=0, columnspan=2, padx=5, pady=3, sticky="w")

    row += 1

    state_variable = ctk.IntVar(
        value=1 if config.DEBUG_FILE_LOGS.get("state_machine", False) else 0
    )
    state_checkbox = ctk.CTkCheckBox(
        tab_debug,
        text="Write State Machine history",
        variable=state_variable,
        command=lambda: _toggle_file_log("state_machine", state_variable),
    )
    state_checkbox.grid(row=row, column=0, columnspan=2, padx=5, pady=3, sticky="w")


def install(app):
    """Install the controls so they appear when the Debug tab is opened."""
    global _INSTALLED

    if _INSTALLED:
        return

    original_show_side_panel = app._show_side_panel

    def show_side_panel_with_file_logs():
        original_show_side_panel()
        if not _INSTALLED:
            _add_controls(app)
            _mark_installed()

    def _mark_installed():
        global _INSTALLED
        _INSTALLED = True

    app._show_side_panel = show_side_panel_with_file_logs
