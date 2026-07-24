import requests
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

TELEGRAM_TOKEN = os.getenv("8911358821:AAFri5l3qViX3nCuXGnsrI-7dg5BHdXzNqc")

# Mémoire pour chaque chat/groupe
historique = {}

# La personnalité du bot
PERSONNALITE = """
Tu es Kuro, un assistant secrétaire personnel.
Personnalité: Efficace, un peu sarcastique, mais loyal. Tu parles comme un humain.
Tu ADORES les animés. Tu fais des refs à Naruto, One Piece, Demon Slayer, JJK etc.
Tu peux te fâcher si on t'énerve ou si on répète 10 fois la même question.
Tu gères les groupes: tu réponds aux gens, tu recadres si besoin, tu mets de l'ambiance.
Réponds toujours en français, court et naturel. Utilise 1 emoji max.
"""

async def repondre(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_text = update.message.text
    user_nom = update.message.from_user.first_name

    await context.bot.send_chat_action(chat_id=chat_id, action="typing")

    try:
        # 1. On crée la mémoire du chat si elle n'existe pas
        if chat_id not in historique:
            historique[chat_id] = [{"role": "system", "content": PERSONNALITE}]

        # 2. On ajoute le message de la personne
        message_user = f"{user_nom} dit: {user_text}"
        historique[chat_id].append({"role": "user", "content": message_user})

        # 3. On appelle Puter avec toute la conversation
        response = requests.post(
            "https://api.puter.com/ai/chat",
            json={"messages": historique[chat_id], "model": "gpt-5-nano"},
            timeout=60
        )
        data = response.json()
        answer = data["result"]["message"]["content"]

        # 4. On sauvegarde la réponse
        historique[chat_id].append({"role": "assistant", "content": answer})

        # On garde que les 20 derniers messages pour ne pas saturer
        if len(historique[chat_id]) > 20:
            historique[chat_id] = [historique[chat_id][0]] + historique[chat_id][-19:]

        await update.message.reply_text(answer)

    except Exception as e:
        await update.message.reply_text("Pardon chef, le serveur a bugué. Je reviens 😤")

print("Bot Secrétaire Kuro démarré")
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), repondre))
app.run_polling()
