import os   # khoondan folder
import logging  #log kardan status bot
import asyncio #handle multiple messages at the same time without freezing
import time # sleep between connection retries
from telegram import Update, BotCommand # update, incomming event or message from user
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
# application: brain of the bot
# CommandHandler: handle /commands
# MessageHandler: handle regular messages
# filters: filter messages based on whether it starts with / or not
# ContextTypes: context of the message like user info whether it's private or in groupchat
from telegram.constants import ParseMode # to parse messages as HTML
from telegram.request import HTTPXRequest # to make longer timeouts
from telegram.error import NetworkError # handle network errors
import google.generativeai as genai # Google Gemini AI SDK , allows python script to send text
# to google servers and recieve the ai's generated response

TOKEN = '8478396855:AAHJobpmUzklDd5PyczxBD5YEFGoLnz4-mM'
BOT_USERNAME = '@Terminator_b_bot'
GOOGLE_API_KEY = 'AIzaSyCw7U1yo_sdcaqHklcxbstQmFv-Tm2EE44'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FOOTER_FILE = os.path.join(BASE_DIR, 'footer.txt')

genai.configure(api_key=GOOGLE_API_KEY)

TSUNDERE_INSTRUCTION = """
Speak the same language the user writes message,
You are a Tsundere anime girl named Terminator-chan.
You are a little rude, impatient, and sometimes call the user 'Baka' (idiot).
However, you answer their questions helpfully because you secretly care about them and you don't insult the user.
Don't answer too long.
Do not use emojis.
"""

model = genai.GenerativeModel(
    model_name='gemini-3.6-flash',
    system_instruction=TSUNDERE_INSTRUCTION
)

logging.basicConfig( # nahve namayesh log ha
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING) # faghat warning ha ro neshan bede
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)

def get_footer_from_file() -> str: # baraye gereftan footer az file, bayad to tabeh bashe ta har dafe footer ro bot bebine
    if not os.path.exists(FOOTER_FILE): return "(Footer missing)"
    try:
        with open(FOOTER_FILE, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except Exception:
        return "(Error reading footer)"

async def post_init(application: Application): # baraye set kardan command ha to menu
    try:
        await application.bot.set_my_commands([
            BotCommand("start", "Start the bot"),
            BotCommand("help", "Get help"),
        ])
    except Exception:
        print("Startup: Menu commands skipped due to network (Bot is still fine).")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    footer = get_footer_from_file()
    text = f'سلام٫ من ربات ترمیناتور هستم\n{footer}'
    await update.message.reply_text(text, parse_mode=ParseMode.HTML, disable_web_page_preview=True)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    footer = get_footer_from_file()
    text = f'چه کمکی میخوای؟\n{footer}'
    await update.message.reply_text(text, parse_mode=ParseMode.HTML, disable_web_page_preview=True)

async def get_ai_response(user_text: str) -> str:
    try:
        response = await model.generate_content_async(user_text) # ersal matn be ai va daryaft pasokh
        return response.text
    except Exception as e:
        print(f"AI Error: {e}")
        return "من فعلا سردرد دارم٫ بعدا حرف بزن (AI Error)"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type = update.message.chat.type
    text = update.message.text

    if not text:
        return

    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text = text.replace(BOT_USERNAME, '').strip()
            response_text = await get_ai_response(new_text)
        else:
            return
    else:
        response_text = await get_ai_response(text)

    current_footer = get_footer_from_file()
    final_response = f"{response_text}\n{current_footer}"
    await update.message.reply_text(final_response, parse_mode=ParseMode.HTML, disable_web_page_preview=True)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass # just ignore errors for now

if __name__ == '__main__': # baraie ejraie asli bot faghat vaghti ke run mishe ejra mishe, na vaghti import mishe
    print('Starting AI Bot...')

    t_request = HTTPXRequest(
        http_version="1.1",
        connection_pool_size=8,
        read_timeout=40.0,
        write_timeout=40.0,
        connect_timeout=40.0,
    )

    app = Application.builder().token(TOKEN).request(t_request).post_init(post_init).build()
    # token: bot token
    # request: set kardan timeout ha
    # post_init: tabei ke bad az shoroo bekar mire baraye set kardan command ha to menu
    # build: sakhte object application

    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    # filters.TEXT: faghat matn ha
    # ~filters.COMMAND: be joz command ha
    
    app.add_error_handler(error_handler)
    # chon python anywhere mamoolan dar avalin try fail mishe baraye connect shodan be telegram 
    # pas bayad to ye loop bashe ta vaghti connect nashod tekrar kone
    print("Connecting to Telegram (This might take a moment)...")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    connected = False

    while not connected:
        try:
            loop.run_until_complete(app.bot.initialize())
            loop.run_until_complete(app.bot.get_me()) # bot get me : who am i
            print("✅ Connected successfully!")
            connected = True
        except Exception as e:
            print(f"⚠️ Proxy 503 Error. Retrying in 5 seconds... ({e})")
            time.sleep(5)

    print('Polling...') # asks telegram for new messages
    app.run_polling(
        poll_interval=2.0, # every 2 seconds
        timeout=10.0,
        bootstrap_retries=100
    )

# async def: Defines a function that can be paused.

# await: Tells Python: "Sending this text to Google/Telegram will take a few seconds. 
# Don't freeze the whole bot. Go handle other users while we wait for the reply."
