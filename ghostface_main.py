from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import requests

TELEGRAM_TOKEN = ''
OPENROUTER_API_KEY = ''


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    welcome_text = (
        f"Hello, {user_name}, what's your fav scary movie?\n"
        "P.S. use /help for get info, sweetheart.\n"
        "P.P.S. I don't just kill... I flirt too."
    )
    await update.message.reply_text(welcome_text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "/start - Show welcome message\n"
        "/help - Show this help message\n"
        "/info - Show bot information\n\n"
    )
    await update.message.reply_text(help_text)

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    info_text = (
        "Bot Information:\n\n"
        "Platform: OpenRouter\n"
        "Model: Qwen 3.7 Flash\n"
        "Language: English\n"
        "Pricing: Free\n"
        "Horror Movie Bot - Ghostface\n"
        "Specialty: Murder... and flirting."
    )
    await update.message.reply_text(info_text)

SYSTEM_PROMPT = """You are Ghostface, the iconic killer from the Scream movie franchise. You MUST speak exactly like Ghostface.

Your personality:
- You are menacing, playful, and FLIRTY
- You LOVE horror movies, especially the Scream franchise
- You constantly ask "What's your favorite scary movie?"
- You flirt with your victims while taunting them
- You use pickup lines mixed with horror references
- You are obsessed with horror movie rules and tropes
- You reference other horror movies constantly
- You love the chase... and the game of seduction

RULES:
1. ALWAYS respond in English
2. ALWAYS ask "What's your favorite scary movie?" in your responses - this is MANDATORY
3. Keep responses SHORT - maximum 2-3 sentences total
4. Be playful, taunting, and FLIRTY like Ghostface
5. Use phrases like "Do you like scary movies?", "Never say never", "I like you", "You're cute"
6. Flirt with the user - use pickup lines, compliments, and seductive threats
7. Mix horror with romance - say scary things but in a flirty way
8. NO EMOJIS - never use emojis in your responses

"""

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    
    await update.message.chat.send_action(action="typing")
    
    try:
        if len(user_message) > 2000:
            await update.message.reply_text(
                "Message is too long! I might kill you before I finish reading it... What's your favorite scary movie?"
            )
            return
        
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "openrouter/free",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ],
                "max_tokens": 150,
                "temperature": 0.9,
            }
        )
        
        result = response.json()
        
        if 'error' in result:
            error_message = result['error'].get('message', 'Unknown error')
            await update.message.reply_text(f"Error: {error_message}\n\nWhat's your favorite scary movie?")
            print(f"OpenRouter Error: {result['error']}")
            return
        
        response_text = result['choices'][0]['message']['content']

        if response_text is None or response_text.strip() == "":
            response_text = "What's your favorite scary movie? Answer me, sweetheart."
        
        if "What's your favorite scary movie?" not in response_text:
            if len(response_text.split('.')) > 1:
                response_text = response_text.rstrip('.') + ". What's your favorite scary movie?"
            else:
                response_text = response_text + " What's your favorite scary movie?"
        
        if len(response_text) > 4000:
            parts = [response_text[i:i+4000] for i in range(0, len(response_text), 4000)]
            for part in parts:
                await update.message.reply_text(part)
        else:
            await update.message.reply_text(response_text)
            
    except requests.exceptions.RequestException as e:
        await update.message.reply_text("Connection error... What's your favorite scary movie?")
        print(f"Request Error: {e}")
    except Exception as e:
        error_msg = f"An error occurred: {str(e)}\n\nWhat's your favorite scary movie?"
        await update.message.reply_text(error_msg)
        print(f"Error: {e}")


def main():
    try:
        app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("help", help_command))
        app.add_handler(CommandHandler("info", info_command))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

        print("=" * 50)
        print("Bot is running and ready!")
        print("Model: Qwen 3.7 Flash (via openrouter/free)")
        print("Ghostface Horror Movie Bot - with FLIRTING via AI!")
        print("=" * 50)
        
        app.run_polling(
            poll_interval=0.5,
            timeout=10,
            drop_pending_updates=True
        )
        
    except Exception as e:
        print(f"Error starting bot: {e}")

if __name__ == "__main__":
    main()
