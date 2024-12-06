from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, MessageHandler, ConversationHandler
from PIL import Image
import io
import os

from controllers.constants import RESIZE_DIMENSIONS, RESIZE_IMAGE, GET_NEW_IMG_FORMAT, GET_NEW_IMG_FORMAT_FILE

class ImageToolsControllers:
    
    @staticmethod
    async def handle_resize_get_dimensions(update: Update, context: ContextTypes.DEFAULT_TYPE):
        resize_ratio = update.message.text.strip()

        if resize_ratio.startswith("*") or resize_ratio.startswith("/"):
            try:
                operator = resize_ratio[0]
                factor = float(resize_ratio[1:])

                if factor <= 0:
                    raise ValueError("El factor debe ser mayor que 0.")
                context.user_data['resize_ratio'] = (operator, factor)
                await update.message.reply_text("Genial! Ahora envía la foto que quieres redimensionar.")
                
                return RESIZE_IMAGE
            
            except ValueError:
                await update.message.reply_text("Formato inválido. Usa *2 o /4. Inténtalo de nuevo.")
                
                return ConversationHandler.END
        else:
            await update.message.reply_text("Formato inválido. Usa *2 o /4. Inténtalo de nuevo.")
            
            return ConversationHandler.END

    @staticmethod
    async def handle_resize_get_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
        image = update.effective_message.photo
        if image:
            try:
                image = update.effective_message.photo[-1]
                image_file = await image.get_file()
                image_bytes = await image_file.download_as_bytearray()

                im = Image.open(io.BytesIO(image_bytes))

                if im.mode != "RGB":
                    im = im.convert("RGB")

                operator, factor = context.user_data.get('resize_ratio', ("*", 1))

                if operator == "*":      
                    new_size = (int(im.width * factor), int(im.height * factor))
                elif operator == "/":
                    new_size = (int(im.width / factor), int(im.height / factor))
                else:
                    raise ValueError("Operador no válido ('*' o '/')")
                
                im_resized = im.resize(new_size)
                
                resized_image_io = io.BytesIO()
                im_resized.save(resized_image_io, format=im.format)
                resized_image_io.seek(0)
                
                image_byte_size = len(resized_image_io.getbuffer())
                
                if image_byte_size / 1024 > 20000:
                    await update.message.reply_text("El tamaño de la imagen final es demasiado grande, selecciona otra opción.")
                    
                    return RESIZE_DIMENSIONS
                
                await update.message.reply_photo(photo=resized_image_io)
                context.user_data.clear()
                
                return ConversationHandler.END

            except Exception as e:
                if "too big for a photo" in str(e):
                    await update.message.reply_text("Telegram no me permite enviar una imagen tan pesada 😔. Selecciona otro ratio de redimensión.")
                    
                    return RESIZE_DIMENSIONS
                
                await update.message.reply_text("Hubo un error. Inténtalo de nuevo. Si el problema persiste, prueba con un ratio de conversión más bajo (Por ejemplo: *2).")
                print(e)
                
                return ConversationHandler.END

        else:
            await update.message.reply_text("No se ha proporcionado ninguna imagen")
            
            return ConversationHandler.END

    @staticmethod
    async def handle_compress_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
        image = update.effective_message.photo

        if image:
            image = update.effective_message.photo[-1]

            try:
                image_file = await image.get_file()
                image_bytes = await image_file.download_as_bytearray()

                im = Image.open(io.BytesIO(image_bytes))
                
                if im.mode != "RGB":
                    im = im.convert("RGB")

                compressed_image_io = io.BytesIO()
                im.save(compressed_image_io, format=im.format, quality=60)
                compressed_image_io.seek(0)
                
                await update.message.reply_photo(compressed_image_io)
                await update.message.reply_text("Listo! Se ha comprimido tu imagen de manera que mantenga la máxima calidad posible.")

                return ConversationHandler.END

            except Exception as e:
                print(f"Error processing image: {e}")
                await update.message.reply_text("Vaya! Hubo un error procesando la imagen. Vuelve a intentarlo más tarde 😔")

                return ConversationHandler.END

        else:
            await update.message.reply_text("No se ha proporcionado ninguna imagen")
            return ConversationHandler.END

    @staticmethod
    async def handle_get_new_format(update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            valid_formats = ["JPG", "JPEG", "PNG", "GIF", "BMP", "TIFF", "WEBP"]
            context.user_data['new_format'] = update.message.text.strip().split(' ')[0].upper()
            if context.user_data['new_format'] not in valid_formats:
                await update.message.reply_text("Por favor, introduce un formato válido. (JPG, JPEG, PNG, GIF, BMP, TIFF o WEBP)")
                return GET_NEW_IMG_FORMAT
            await update.message.reply_text(f"Genial! Convertiré tu imagen a formato {context.user_data['new_format']}. Ahora adjunta la imagen.")
            
            return GET_NEW_IMG_FORMAT_FILE        
        
        except Exception as e:
            print(e)
    
    @staticmethod
    async def handle_get_new_format_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
        image = update.effective_message.photo
        new_format = context.user_data["new_format"]

        if image:
            image = update.effective_message.photo[-1]
            try:
                image_file = await image.get_file()
                image_bytes = await image_file.download_as_bytearray()

                im = Image.open(io.BytesIO(image_bytes))
                
                new_format_image_io = io.BytesIO()
                im.save(new_format_image_io, format=new_format, quality=100)
                new_format_image_io.seek(0)

                file_name = f"converted_image.{new_format}"
                
                await update.message.reply_document(
                    document=new_format_image_io,
                    filename=file_name
                )
                await update.message.reply_text(f"Aquí tienes la imagen en formato {new_format}")
                context.user_data.clear()

                return ConversationHandler.END
            except Exception as e:
                print(e)
                await update.message.reply_text("Hubo un error al procesar la imagen. Por favor, inténtalo de nuevo.")
                
                return ConversationHandler.END

        else:
            await update.message.reply_text("No has proporcionado ninguna imagen.")
            
            return ConversationHandler.END
