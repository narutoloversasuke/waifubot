import random
from html import escape
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, CallbackQueryHandler, CommandHandler
from shivu import application, SUPPORT_CHAT, UPDATE_CHAT, BOT_USERNAME, db, GROUP_ID
from shivu import pm_users as collection
import logging

private = ["https://postimage.me/image/1df98d70e8c9f0c00426c3251c63a583.UMJdS4",https://postimage.me/image/cf9a427cbe3cc531fcc9c28926b60b71.UMJF4e", "https://postimage.me/image/1ab368db00683ddb5ae51dd812b1cdc1.UMJPus"]
group = ["https://postimage.me/image/dcf5916afcd09500a9fc18455622dfd9.UMJyAj", "https://postimage.me/image/90ddff5520df99d869165f2ccd665ad9.UMJYkW"]

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Constants for button labels and URLs
ADD_BUTTON_TEXT = "ADD ME"
ADD_BUTTON_URL = f'http://t.me/{BOT_USERNAME}?startgroup=new'
SUPPORT_BUTTON_TEXT = "SUPPORT"
UPDATE_BUTTON_TEXT = "UPDATES"
HELP_BUTTON_TEXT = "HELP"
SOURCE_BUTTON_TEXT = "SOURCE"

# Updated Start Message
START_CAPTION = """Nyaa~! Welcome home, Goshujin-sama!~ (≧◡≦) ♡
Your waifu adventure starts meow~! 💕✨

🐾 /sealwaifu – Seal a super cute waifu! 🎀
🌸 /upload – Add even more adorable waifus! 🥰

Will you become the ultimate waifu master? (๑>ᴗ<๑)!~"""

GROUP_CAPTION = "🎴 Alive!?... Connect to me in PM for more information."

# Updated Help Message
HELP_TEXT = """✅ Check if you’re alive: /checkseal  
🚀 Start the journey: /start  

🎲 Play & win coins: /rocket  
🪙 Win coins randomly: /luckdraw  
🏹 Explore & earn coins: /explore  

🔒 Add a waifu: /sealwaifu  
📜 See your waifus: /sealedvault  
🏆 Top global waifu collectors: /topgroups  
👑 Top global users: /top  
🎭 Top waifu collectors in this group: /ctop  

🔄 Trade a waifu: /soultrade  
🎁 Gift a waifu: /giftseal  
💰 Sell a waifu: /wsell  

⏳ Change waifu claim time: /sealshift  
🏪 Enter Waifu Market: /slaveshop  

📊 See your progress report: /sealedprogress  
💎 Check your balance: /soulbalance  
🎟️ Redeem a code: /sealredeem  
🔑 Generate a code: /sealcode"""

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
                    text=f"New user Started The Bot..\n User: <a href='tg://user?id={user_id}'>{escape(first_name)}</a>",
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
            [InlineKeyboardButton(ADD_BUTTON_TEXT, url=ADD_BUTTON_URL)],
            [
                InlineKeyboardButton(SUPPORT_BUTTON_TEXT, url=f"https://t.me/+ZTeO__YsQoIwNTVl"),
                InlineKeyboardButton(UPDATE_BUTTON_TEXT, url=f"https://t.me/Anime_P_F_P")
            ],
            [InlineKeyboardButton(HELP_BUTTON_TEXT, callback_data='help')],
            [InlineKeyboardButton(SOURCE_BUTTON_TEXT, url=f"http://postimg.cc/bsFFs4YF")]
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
                text="Sorry, something went wrong. Please try again later."
            )

async def button(update: Update, context: CallbackContext) -> None:
    """Handle button callbacks."""
    query = update.callback_query
    await query.answer()

    try:
        if query.data == 'help':
            help_keyboard = [[InlineKeyboardButton("⤾ Back", callback_data='back')]]
            reply_markup = InlineKeyboardMarkup(help_keyboard)

            await query.edit_message_caption(
                caption=HELP_TEXT,
                reply_markup=reply_markup,
                parse_mode='markdown'
            )

        elif query.data == 'back':
            keyboard = [
                [InlineKeyboardButton(ADD_BUTTON_TEXT, url=ADD_BUTTON_URL)],
                [
                    InlineKeyboardButton(SUPPORT_BUTTON_TEXT, url=f"https://t.me/+ZTeO__YsQoIwNTVl"),
                    InlineKeyboardButton(UPDATE_BUTTON_TEXT, url=f"https://t.me/Anime_P_F_P")
                ],
                [InlineKeyboardButton(HELP_BUTTON_TEXT, callback_data='help')],
                [InlineKeyboardButton(SOURCE_BUTTON_TEXT, url=f"http://postimg.cc/bsFFs4YF")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_caption(
                caption=START_CAPTION,
                reply_markup=reply_markup,
                parse_mode='markdown'
            )

    except Exception as e:
        logger.error(f"Error in button handler: {e}")
        await query.edit_message_text(text="Sorry, something went wrong. Please try again.")

# Add handlers
application.add_handler(CallbackQueryHandler(button, pattern='^help$|^back$', block=False))
application.add_handler(CommandHandler('start', start, block=False))
