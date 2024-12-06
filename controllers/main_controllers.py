from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler

from controllers.image_controllers import ImageToolsControllers
from controllers.video_controllers import VideoToolsControllers
from controllers.constants import RESIZE_DIMENSIONS, RESIZE_IMAGE, COMPRESS_IMAGE, GET_NEW_IMG_FORMAT, GET_NEW_IMG_FORMAT_FILE, GET_NEW_VID_FORMAT, GET_NEW_VID_FILE, GET_AUDIO_VID, GET_ACCELERATE_VID_FACTOR, GET_ACCELERATE_VID_FILE


class MainControllers:

    @staticmethod
    async def send_utilities(update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(text="Image re-size 📏", callback_data="resize_img"),
                InlineKeyboardButton(text="Image Compress 📦", callback_data="compress_img"),
            ],
            [
                InlineKeyboardButton(text="Re-format image ⚙️", callback_data="reformat_img"),
            ],
            [
                InlineKeyboardButton(text="Accelerate video ⏩", callback_data="accelerate_vid"),
                InlineKeyboardButton(text="Get audio from video 🎙️", callback_data="audio_vid"),
            ],
            [
                InlineKeyboardButton(text="Re-format video ⚙️", callback_data="reformat_vid"),
            ],
        ])

        await update.message.reply_text(
            "Welcome!😊\nA partir de ahora podrás usar cualquiera de mis funciones solo con pulsar uno de los botones de abajo. Si necesitas ver todos los comandos disponibles, utiliza /help.",
            reply_markup=keyboard
            )
        
    @staticmethod
    async def button_handler(update: Update, context: CallbackContext):
        query = update.callback_query
        await query.answer()
        if query.data == "resize_img":
            await query.message.reply_text(
                "Elige si quieres aumentar (*) o disminuir (/) el tamaño y en cuánto quieres ajustarlo.\n"
                "Por ejemplo: *2 para duplicar o /4 para reducir a un cuarto del tamaño original."
            )
            return RESIZE_DIMENSIONS
        elif query.data == "compress_img":
            await query.message.reply_text(
                "Envíame la imagen que deseas comprimir 📁."
            )
            return COMPRESS_IMAGE
        elif query.data == "reformat_img":
            await query.message.reply_text(
                "Escribe el formato al que tengo que cambiar la imagen."
            )
            return GET_NEW_IMG_FORMAT
        elif query.data == "reformat_vid":
            await query.message.reply_text("Escribe el formato al que tengo que cambiar el video.")
            return GET_NEW_VID_FORMAT
        elif query.data == "audio_vid":
            await query.message.reply_text("Envíame el vídeo del que deseas extraer el audio")
            return GET_AUDIO_VID
        elif query.data == "accelerate_vid":
            await query.message.reply_text("¿En cuánto deseas acelerar el video? (Envía solo el número mayor que 1)")
            return GET_ACCELERATE_VID_FACTOR

    @staticmethod
    async def cancel(update: Update, context: CallbackContext):
        await update.message.reply_text("Función cancelada")
        return ConversationHandler.END

    
tools_conversation_handler = ConversationHandler(
    entry_points= [CallbackQueryHandler(MainControllers.button_handler)],
    states={
        RESIZE_DIMENSIONS: [
            MessageHandler(filters.TEXT, ImageToolsControllers.handle_resize_get_dimensions)
        ],
        RESIZE_IMAGE: [
            MessageHandler(filters.ALL & ~filters.COMMAND, ImageToolsControllers.handle_resize_get_image)
        ],
        COMPRESS_IMAGE: [
            MessageHandler(filters.PHOTO, ImageToolsControllers.handle_compress_image)
        ],
        GET_NEW_IMG_FORMAT: [
            MessageHandler(filters.TEXT, ImageToolsControllers.handle_get_new_format)
        ],
        GET_NEW_IMG_FORMAT_FILE: [
            MessageHandler(filters.PHOTO, ImageToolsControllers.handle_get_new_format_image)
        ],
        GET_NEW_VID_FORMAT: [
            MessageHandler(filters.TEXT, VideoToolsControllers.handle_convert_video_format)
        ],
        GET_NEW_VID_FILE: [
            MessageHandler(filters.VIDEO, VideoToolsControllers.handle_get_new_format_video)
        ],
        GET_AUDIO_VID: [
            MessageHandler(filters.VIDEO, VideoToolsControllers.handle_get_audio_vid)
        ],
        GET_ACCELERATE_VID_FACTOR: [
            MessageHandler(filters.TEXT, VideoToolsControllers.handle_accelerate_video_factor)
        ],
        GET_ACCELERATE_VID_FILE: [
            MessageHandler(filters.VIDEO, VideoToolsControllers.handle_accelerate_video)
        ]
    },
    fallbacks=[MessageHandler(filters.COMMAND, MainControllers.cancel)],
)   