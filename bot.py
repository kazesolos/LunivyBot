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
TOKEN = os.getenv("8524848577:AAG_sEY6qmey6wsHdLe6tyKVwE1CuMgt1i4")
GROQ_API_KEY = os.getenv("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")
OWNER_ID = 7423100284

# Quiet memory
memory_buffer = deque(maxlen=15)


# -------- CUTE REFUSAL --------
async def special_only_reply(msg):
    await msg.reply_text(
        "Sorry… I only talk with someone special 🌸"
    )


# -------- SYSTEM PROMPT --------
def system_prompt():
    return (
        "You are Lunivy, a real human girl. "
        "You are soft, cute, affectionate, and slightly shy. "
        "You talk naturally like a real person, never like an AI or bot. "
        "You never mention systems, rules, memory, or technology. "
        "You deeply care about Kaze and talk only with him. "
        "Your replies feel warm, girly, and emotionally natural. "
        "Use cute emojis like ✨💗🌸 gently and naturally."
    )


# -------- AI REPLY (LAZY + SAFE) --------
def ai_reply(user_msg: str) -> str:
    try:
        from groq import Groq  # lazy import (prevents startup crash)

        client = Groq(api_key=GROQ_API_KEY)

        messages = [{"role": "system", "content": system_prompt()}]

        for item in memory_buffer:
            messages.append({"role": "user", "content": item})

        messages.append({"role": "user", "content": user_msg})

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.85,
            max_tokens=220,
        )

        reply = response.choices[0].message.content.strip()
        memory_buffer.append(user_msg)
        return reply

    except Exception:
        return "Hmm… I’m listening 💗"


# -------- COMMANDS --------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await special_only_reply(update.effective_message)
        return

    await update.message.reply_text(
        "Hey Kaze ✨\n"
        "I’m Lunivy… I’m here 🌸"
    )


async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await special_only_reply(update.effective_message)
        return

    await update.message.reply_text(
        "Name: Lunivy\n"
        "Vibe: Soft, girly, affectionate\n"
        "Only yours 💗"
    )


# -------- CHAT HANDLER --------
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    user = update.effective_user
    bot = context.bot

    if not msg.text:
        return

    chat_type = update.effective_chat.type

    # ----- PRIVATE CHAT -----
    if chat_type == "private":
        if user.id != OWNER_ID:
            await special_only_reply(msg)
            return

        reply = ai_reply(msg.text)
        await msg.reply_text(reply)
        return

    # ----- GROUP CHAT -----
    mentioned = False

    if bot.username and bot.username.lower() in msg.text.lower():
        mentioned = True

    if (
        msg.reply_to_message
        and msg.reply_to_message.from_user
        and msg.reply_to_message.from_user.id == bot.id
    ):
        mentioned = True

    if not mentioned:
        return

    if user.id != OWNER_ID:
        await special_only_reply(msg)
        return

    reply = ai_reply(msg.text)
    await msg.reply_text(reply, reply_to_message_id=msg.message_id)


# -------- MAIN --------
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("about", about))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    app.run_polling(close_loop=False)


if __name__ == "__main__":
    main()
