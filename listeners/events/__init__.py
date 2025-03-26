from slack_bolt import App
from .app_home_opened import app_home_opened_callback
from .app_mentioned import app_mentioned_callback
from .app_messaged import app_messaged_callback
from .file_shared import file_shared_callback
from ..commands.thread_chat import handle_thread_message


def register(app: App):
    app.event("app_home_opened")(app_home_opened_callback)
    app.event("app_mention")(app_mentioned_callback)
    app.event("message")(app_messaged_callback)
    app.event("file_shared")(file_shared_callback)
    
    # Register thread message handler for continuing conversations
    app.event("message", middleware=[lambda body, context, next: "thread_ts" in body["event"] and next()])(handle_thread_message)
