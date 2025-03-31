import random
from html import escape
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, CallbackQueryHandler, CommandHandler
from shivu import application, SUPPORT_CHAT, UPDATE_CHAT, BOT_USERNAME, db, GROUP_ID
from shivu import pm_users as collection
import logging

# Image URLs
private = ["https://postimg.cc/Mv52Yq9j", "https://postimg.cc/CBCSTDsc", "https://postimg.cc/471kFGXM"]
group = ["https://postimg.cc/w3Jpz4CB", "https://postimg.cc/pmfcTGz4", "https://postimg.cc/rKdv8Nh2"]

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Constants for button labels and URLs
SUMMON_BUTTON_TEXT = "🌸 𝒮𝓊𝓂𝓂𝑜𝓃 𝒴𝑜𝓊𝓇 𝒲𝒶𝒾𝒻𝓊! 💖"
SUMMON_BUTTON_URL = "http://t.me/Waifu_Chan_Robot?startgroup=new"
SUPPORT_BUTTON_TEXT = "🆘 𝒮𝓊𝓅𝓅𝑜𝓇𝓉 𝒢𝒸"
UPDATE_BUTTON_TEXT = "🔔 𝒰𝓅𝒹𝒶𝓉𝑒𝓈"
HELP_BUTTON_TEXT = "📜 𝐻𝑒𝓁𝓅"
SOURCE_BUTTON_TEXT = "💻 𝒮𝑜𝓊𝓇𝒸𝑒 𝒞𝑜𝒹𝑒"

# Welcome Note
START_CAPTION = """╔═════════════════════ஓ๑♡๑ஓ═════════════════════╗
🌸✨ Welcome, Master! ✨🌸
╚═════════════════════ஓ๑♡๑ஓ═════════════════════╝

🌸 A world of waifus awaits you! 🌸
❥ Collect, cherish, and trade your favorite waifus! 💖
❥ Unlock rare beauties and build the ultimate collection! ✨
❥ Who knows? Your dream waifu might be waiting just for you! 💫

╭───────────────────🌸───────────────────╮
💕 Every waifu has a story... 💕
🎀 Will you be the one to claim her heart? 🎀
╰───────────────────🌸───────────────────╯

💌 Your adventure begins now, Master! 💌
🎀 Step into the world of love, luck, and endless surprises! 🎀"""

GROUP_CAPTION = "Hello, darling! ✨ I'm wide awake and ready to serve! How can I make your day sweeter? 💕"

HELP_TEXT = """📜 Help Section:
🔹 /sealwaifu - Seal a character (groups only)
🔹 /fav - Add your favorite waifu
🔹 /trade - Trade waifus
🔹 /gift - Gift a waifu (groups only)
🔹 /collection - View your collection
🔹 /topgroups - See top active waifu groups
🔹 /top - View top waifu collectors
🔹 /ctop - Your chat's top waifu fans
🔹 /changetime - Adjust waifu drop time (groups only)"""

async def start(update: Update, context: CallbackContext) -> None:
    """Send a welcome message when the command /start is issued."""
    try:
        user_id = update.effective_user.id
        first_name = update.effective_user.first_name
        username = update.effective_user.username

        # Update or insert user data  
        user_data = await collection.find_one({"_id": user_id})  
          
        if user_data is None:  
            await collection.insert_one({  
                "_id": user_id,  
                "first_name": first_name,  
                "username": username  
            })  
            if GROUP_ID:  
                await context.bot.send_message(  
                    chat_id=GROUP_ID,  
                    text=f"🌟 New user joined!\n👤 User: <a href='tg://user?id={user_id}'>{escape(first_name)}</a>",  
                    parse_mode='HTML'  
                )  
        else:  
            if user_data['first_name'] != first_name or user_data['username'] != username:  
                await collection.update_one(  
                    {"_id": user_id},  
                    {"$set": {"first_name": first_name, "username": username}}  
                )  

        # Create keyboard  
        keyboard = [  
            [InlineKeyboardButton(SUMMON_BUTTON_TEXT, url=SUMMON_BUTTON_URL)],  
            [  
                InlineKeyboardButton(SUPPORT_BUTTON_TEXT, url="https://t.me/+ZTeO__YsQoIwNTVl"),  
                InlineKeyboardButton(UPDATE_BUTTON_TEXT, url="https://t.me/Anime_P_F_P")  
            ],  
            [InlineKeyboardButton(HELP_BUTTON_TEXT, callback_data='help')],  
            [InlineKeyboardButton(SOURCE_BUTTON_TEXT, url="http://postimg.cc/bsFFs4YF")]  
        ]  
        reply_markup = InlineKeyboardMarkup(keyboard)  

        # Send appropriate message based on chat type  
        if update.effective_chat.type == "private":  
            await context.bot.send_photo(  
                chat_id=update.effective_chat.id,  
                photo=random.choice(private),  
                caption=START_CAPTION,  
                reply_markup=reply_markup,  
                parse_mode='markdown'  
            )  
        else:  
            await context.bot.send_photo(  
                chat_id=update.effective_chat.id,  
                photo=random.choice(group),  
                caption=GROUP_CAPTION,  
                reply_markup=reply_markup  
            )  

    except Exception as e:  
        logger.error(f"Error in start handler: {e}")  
        if update.effective_chat.type == "private":  
            await context.bot.send_message(  
                chat_id=update.effective_chat.id,  
                text="❌ Something went wrong! Please try again later."  
            )

async def button(update: Update, context: CallbackContext) -> None:
    """Handle button callbacks."""
    query = update.callback_query
    await query.answer()

    try:  
        if query.data == 'help':  
            help_keyboard = [[InlineKeyboardButton("⤾ 𝔹𝕒𝕔𝕜", callback_data='back')]]  
            reply_markup = InlineKeyboardMarkup(help_keyboard)  

            await query.edit_message_caption(  
                caption=HELP_TEXT,  
                reply_markup=reply_markup,  
                parse_mode='markdown'  
            )  

        elif query.data == 'back':  
            keyboard = [  
                [InlineKeyboardButton(SUMMON_BUTTON_TEXT, url=SUMMON_BUTTON_URL)],  
                [  
                    InlineKeyboardButton(SUPPORT_BUTTON_TEXT, url="https://t.me/+ZTeO__YsQoIwNTVl"),  
                    InlineKeyboardButton(UPDATE_BUTTON_TEXT, url="https://t.me/Anime_P_F_P")  
                ],  
                [InlineKeyboardButton(HELP_BUTTON_TEXT, callback_data='help')],  
                [InlineKeyboardButton(SOURCE_BUTTON_TEXT, url="http://postimg.cc/bsFFs4YF")]
            ]  
            reply_markup = InlineKeyboardMarkup(keyboard)

            # Send a new message with the original options
            await query.edit_message_caption(
                caption=START_CAPTION,
                reply_markup=reply_markup,
                parse_mode='markdown'
            )

    except Exception as e:
        logger.error(f"Error in button handler: {e}")
        await query.answer("❌ Something went wrong! Please try again later.")

async def help(update: Update, context: CallbackContext) -> None:
    """Show the help menu."""
    keyboard = [[InlineKeyboardButton("⤾ 𝔹𝕒𝕔𝕜", callback_data='back')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        HELP_TEXT,
        reply_markup=reply_markup,
        parse_mode='markdown'
    )

# Handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button))
application.add_handler(CommandHandler("help", help))

if __name__ == "__main__":
    application.run_polling()
