from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from dotenv import load_dotenv
import os

from controllers.image_controllers import ImageToolsControllers
from controllers.main_controllers import MainControllers, tools_conversation_handler

load_dotenv()

application = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    print(f"Exception while handling update {update}: {context.error}")


application.add_handler(CommandHandler("start", MainControllers.send_utilities))
application.add_handler(CommandHandler("tools", MainControllers.send_utilities))
application.add_handler(tools_conversation_handler)
application.add_error_handler(error_handler)

if os.getenv("ENV") != "production":
    application.run_polling()
else:
    webhook_url = f"{os.getenv('URL')}{os.getenv('TELEGRAM_BOT_TOKEN')}"
    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8443)),
        url_path = os.getenv("TELEGRAM_BOT_TOKEN"),
        webhook_url=webhook_url
    )