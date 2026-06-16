from modules.mock_data import SETTINGS_OPTIONS
from modules.ui_sections import render_card
from ui.components import render_header


def render_settings():
    render_header("Settings", "Static MVP settings prepared for later personalization and data connections.")
    for option in SETTINGS_OPTIONS:
        render_card(option["label"], option["value"])
