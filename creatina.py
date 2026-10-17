import os
from datetime import time
from zoneinfo import ZoneInfo
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (Application, CallbackQueryHandler,
                          CommandHandler, ContextTypes)

TOKEN = os.environ["BOT_TOKEN"]
HORA = time(10, 00, tzinfo=ZoneInfo("Europe/Madrid"))
FICHERO = "chat_id.txt"
TECLADO = InlineKeyboardMarkup([[
    InlineKeyboardButton("✅ Tomada", callback_data="ok"),
    InlineKeyboardButton("⏰ En 1h", callback_data="luego"),
]])

async def recordatorio(context: ContextTypes.DEFAULT_TYPE):
    if context.job is None:
        return
    chat_id = context.job.chat_id
    if chat_id is None:
        return
    await context.bot.send_message(
        chat_id=chat_id,
        text="💊 Toca la creatina",
        reply_markup=TECLADO
    )


def programar(job_queue, chat_id):
    job_queue.run_daily(recordatorio, HORA, chat_id=chat_id, name=str(chat_id))


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None or update.effective_chat is None:
        return
    chat_id = update.effective_chat.id
    with open(FICHERO, "w") as f:
        f.write(str(chat_id))
    programar(context.job_queue, chat_id)
    await update.message.reply_text("Listo, te avisaré cada día a las 10:00 💪")

async def botones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    if q is None or update.effective_chat is None:
        return
    await q.answer()
    if q.data == "ok":
        await q.edit_message_text("✅ Creatina tomada. ¡Bien!")
    else:
        if context.job_queue is None:
            await q.edit_message_text("⚠️ No se pudo programar el recordatorio")
            return
        context.job_queue.run_once(
            recordatorio, 3600, chat_id=update.effective_chat.id
        )
        await q.edit_message_text("⏰ Te lo recuerdo en 1 hora")

async def arrancar(app: Application):
    if os.path.exists(FICHERO):
        with open(FICHERO) as f:
            programar(app.job_queue, int(f.read()))


app = Application.builder().token(TOKEN).post_init(arrancar).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(botones))
app.run_polling()