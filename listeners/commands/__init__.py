from slack_bolt import App
from .ask_command import ask_callback
from .localai_settings import localai_settings_callback, handle_localai_settings_submission


def register(app: App):
    app.command("/ask-bolty")(ask_callback)
    app.command("/localai-settings")(localai_settings_callback)
    app.view("localai_settings_modal")(handle_localai_settings_submission)
