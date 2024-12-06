from moviepy import VideoFileClip, vfx
from moviepy.video.fx import MultiplySpeed
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
import tempfile
import io
import os

from controllers.constants import GET_NEW_VID_FORMAT, GET_NEW_VID_FILE, GET_ACCELERATE_VID_FACTOR, GET_ACCELERATE_VID_FILE

class VideoToolsControllers:

    @staticmethod
    async def handle_convert_video_format(update: Update, context: ContextTypes):
        try:
            valid_formats = ["MP4", "AVI", "MOV", "MKV", "FLV", "WEBM", "OGV", "WMV", "3GP"]
            context.user_data["new_format"] = update.message.text.strip().split(' ')[0].upper()
            if context.user_data["new_format"] not in valid_formats:
                await update.message.reply_text("Por favor, introduce un formato válido. (MP4, AVI, MOV, MKV, FLV, WEBM, OGV, WMV, 3GP)")
                return GET_NEW_VID_FORMAT
            await update.message.reply_text(f"Genial! Ahora adjunta el video y lo convertiré formato {context.user_data['new_format']}.")

            return GET_NEW_VID_FILE
        
        except Exception as e:
            print(e)

    @staticmethod
    async def handle_get_new_format_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
        video = update.effective_message.video
        new_format = context.user_data["new_format"]

        if video:
            try:
                file = await context.bot.get_file(video.file_id)
                input_video = await file.download_as_bytearray()

                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_input:
                    tmp_input.write(input_video)
                    input_path = tmp_input.name

                vid = VideoFileClip(input_path)
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{new_format.lower()}") as tmp_output:
                    output_path = tmp_output.name
                    vid.write_videofile(output_path, codec="libx264", threads=4) 


                with open(output_path, 'rb') as f:
                    output_video = io.BytesIO(f.read())
                    
                output_video.seek(0)

                file_name = f"converted_video.{new_format.lower()}"

                await update.message.reply_text(f"Aquí tienes el video en formato {new_format}⬇️")
                await update.message.reply_document(
                    document=output_video,
                    filename=file_name
                )
                
                context.user_data.clear()
                vid.close()

                os.remove(input_path)
                os.remove(output_path)

                return ConversationHandler.END
            
            except Exception as e:
                print(e)
                await update.message.reply_text("Hubo un error al procesar el video. Por favor, inténtalo de nuevo.")
                return ConversationHandler.END

        else:
            await update.message.reply_text("No has proporcionado ninguna imagen.")
            return ConversationHandler.END

    @staticmethod
    async def handle_get_audio_vid(update: Update, context: ContextTypes.DEFAULT_TYPE):
        video = update.effective_message.video

        if video:
            file = await context.bot.get_file(video.file_id)
            input_video = await file.download_as_bytearray()

            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_input:
                tmp_input.write(input_video)
                input_path = tmp_input.name

            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_audio:
                audio_path = tmp_audio.name
            
            vid = VideoFileClip(input_path)
            audio = vid.audio
            audio.write_audiofile(audio_path)
            vid.close()

            with open(audio_path, "rb") as audio_file:
                audio_io = io.BytesIO(audio_file.read())
                
            audio_io.seek(0)
            os.remove(input_path)
            os.remove(audio_path)

            await update.message.reply_document(document=audio_io, filename="video_audio.mp3")
            return ConversationHandler.END

        else:
            await update.message.reply_text("Necesitas enviar un video 🎬")
            return ConversationHandler.END
        
    @staticmethod
    async def handle_accelerate_video_factor(update= Update, context = ContextTypes.DEFAULT_TYPE):
        factor = int(update.message.text)

        if factor:
            if factor > 1:
                context.user_data['accelerate_factor'] = factor
                await update.message.reply_text("¿Qué video deseas modificar?")
                return GET_ACCELERATE_VID_FILE
            
            else:
                await update.message.reply_text("Introduce un número válido")

        else:
            await update.message.reply_text("Has de introducir un valor mayor a 1")

    @staticmethod
    async def handle_accelerate_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
        video = update.effective_message.video
        factor = context.user_data['accelerate_factor']

        if video:
            try:
                file = await context.bot.get_file(video.file_id)
                input_video = await file.download_as_bytearray()

                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_input:
                    tmp_input.write(input_video)
                    input_path = tmp_input.name
                
                vid = VideoFileClip(input_path)

                speed_effect = MultiplySpeed(factor=factor)
                accelerated_vid = speed_effect.apply(vid)

                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_output:
                    output_path = tmp_output.name
                    accelerated_vid.write_videofile(output_path, codec="libx264", threads=4)

                with open(output_path, 'rb') as f:
                    output_video = io.BytesIO(f.read())
                
                output_video.seek(0)
                os.remove(input_path)
                os.remove(output_path)
                
                await update.message.reply_video(video=output_video)
                return ConversationHandler.END
            except Exception as e:
                print(e)
        else:
            await update.message.reply_text("No has enviado ningún video.")
            return ConversationHandler.END

        
