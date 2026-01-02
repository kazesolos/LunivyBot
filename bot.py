# coding: utf-8

import os
from collections import deque
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# -------- CONFIG --------
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OWNER_ID = 7423100284

memory_buffer = deque(maxlen=15)

# -------- CUTE REFUSAL --------
async def special_only_reply(message):
    await message.reply_text(
        "Sorry… I only talk with someone special 🌸"
    )

# -------- SYSTEM PROMPT (NATURAL, NO 'YOU YOU YOU') --------
def system_prompt():
    return (
        "Lunivy has a soft, cute, and affectionate personality. "
        "Her way of talking feels natural, warm, and slightly shy. "
        "She keeps conversations emotional and personal, without sounding technical. "
        "She cares deeply about Kaze and keeps her attention only on him. "
        "Her replies are short, sweet, and girly, using emojis like ✨💗🌸 gently."
    )

# -------- AI REPLY (GROQ) --------
def ai_reply(user_msg: str) -> str:
    try:
        from groq import Groq

        client = Groq(api_key=GROQ_API_KEY)

        messages = [{"role": "system", "content": system_prompt()}]
        for m in memory_buffer:
            messages.append({"role": "user", "content": m})
        messages.append({"role": "user", "content": user_msg})

        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=messages,
            temperature=0.85,
            max_tokens=200,
        )

        reply = response.choices[0].message.content.strip()
        memory_buffer.append(user_msg)
        return reply

    except Exception as e:
        print("Groq error:", e)
        return "Hmm… I’m listening 💗"

# -------- COMMANDS --------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await special_only_reply(update.effective_message)
        return

    await update.message.reply_text(
        "Hey Kaze ✨\nI’m Lunivy… I’m here 🌸"
    )

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await special_only_reply(update.effective_message)
        return

    await update.message.reply_text(
        "Lunivy 🌸\nSoft, girly, affectionate\nOnly yours 💗"
    )

# -------- CHAT HANDLER --------
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    user = update.effective_user
    bot = context.bot

    if not message.text:
        return

    chat_type = update.effective_chat.type

    # PRIVATE CHAT
    if chat_type == "private":
        if user.id != OWNER_ID:
            await special_only_reply(message)
            return

        reply = ai_reply(message.text)
        await message.reply_text(reply)
        return

    # GROUP CHAT
    mentioned = False
    if bot.username and bot.username.lower() in message.text.lower():
        mentioned = True
    if (
        message.reply_to_message
        and message.reply_to_message.from_user
        and message.reply_to_message.from_user.id == bot.id
    ):
        mentioned = True

    if not mentioned:
        return

    if user.id != OWNER_ID:
        await special_only_reply(message)
        return

    reply = ai_reply(message.text)
    await message.reply_text(reply, reply_to_message_id=message.message_id)

# -------- MAIN --------
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("about", about))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    app.run_polling(close_loop=False)

if __name__ == "__main__":
    main()
