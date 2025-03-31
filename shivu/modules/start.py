import random
from html import escape
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, CallbackQueryHandler, CommandHandler
from shivu import application, SUPPORT_CHAT, UPDATE_CHAT, BOT_USERNAME, db, GROUP_ID
from shivu import pm_users as collection
import logging

private = ["https://postimg.cc/Mv52Yq9j", "https://postimg.cc/CBCSTDsc", "https://postimg.cc/471kFGXM"]
group = ["https://postimg.cc/w3Jpz4CB", "https://postimg.cc/pmfcTGz4", "https://postimg.cc/rKdv8Nh2"]

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Constants for button labels and URLs
SUMMON_BUTTON_TEXT = "🌸 Grasp Your Waifu! 💖"
SUMMON_BUTTON_URL = "http://t.me/Waifu_Chan_Robot?startgroup=new"
SUPPORT_BUTTON_TEXT = "🆘 Support GC"
UPDATE_BUTTON_TEXT = "🔔 Updates"
HELP_BUTTON_TEXT = "📜 Help"
SOURCE_BUTTON_TEXT = "💻 Source Code"
MY_WAIFUS_BUTTON_TEXT = "💖 My Waifus"

# Welcome Note (Isekai style)
START_CAPTION = """╔═══════════════════ஓ๑♡๑ஓ═══════════════════╗  
              ✨ *Summoned to Another World!* ✨  
╚═══════════════════ஓ๑♡๑ஓ═══════════════════╝  

🌸 *Master!* Fate has chosen you! 🌸  
💖 You have been transported to the world of waifus!  
🎀 Here, rare beauties await your call—summon them, cherish them, and build your legendary collection!  
💫 *Will you be the one to claim the ultimate waifu?* 💫  

🔮 *Your isekai journey begins now!* 🔮"""

GROUP_CAPTION = "Hello, darling! ✨ I'm wide awake and ready to serve! How can I make your day sweeter? 💕"

HELP_TEXT = """*📜 Help Section:*
🔹 */guess* - Guess a character (groups only)
🔹 */fav* - Add your favorite waifu
🔹 */trade* - Trade waifus
🔹 */gift* - Gift a waifu (groups only)
🔹 */collection* - View your collection
🔹 */topgroups* - See top active waifu groups
🔹 */top* - View top waifu collectors
🔹 */ctop* - Your chat's top waifu fans
🔹 */changetime* - Adjust waifu drop time (groups only)"""

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
            [InlineKeyboardButton(MY_WAIFUS_BUTTON_TEXT, callback_data='my_waifus')],
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
            help_keyboard = [[InlineKeyboardButton("⤾ Back", callback_data='back')]]
            reply_markup = InlineKeyboardMarkup(help_keyboard)

            await query.edit_message_caption(
                caption=HELP_TEXT,
                reply_markup=reply_markup,
                parse_mode='markdown'
            )

        elif query.data == 'my_waifus':
            await query.edit_message_text(
                text="📖 *Your Waifu Collection:* \n\n🔹 View and cherish the waifus you have grasped!",
                parse_mode='markdown'
            )

        elif query.data == 'back':
            keyboard = [
                [InlineKeyboardButton(SUMMON_BUTTON_TEXT, url=SUMMON_BUTTON_URL)],
                [InlineKeyboardButton(MY_WAIFUS_BUTTON_TEXT, callback_data='my_waifus')],
                [
                    InlineKeyboardButton(SUPPORT_BUTTON_TEXT, url="https://t.me/+ZTeO__YsQoIwNTVl"),
                    InlineKeyboardButton(UPDATE_BUTTON_TEXT, url="https://t.me/Anime_P_F_P")
                ],
                [InlineKeyboardButton(HELP_BUTTON_TEXT, callback_data='help')],
                [InlineKeyboardButton(SOURCE_BUTTON_TEXT, url="http://postimg.cc/bsFFs4YF")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_caption(
                caption=START_CAPTION,
                reply_markup=reply_markup,
                parse_mode='markdown'
            )

    except Exception as e:
        logger.error(f"Error in button handler: {e}")
        await query.edit_message_text(text="❌ Oops! Something went wrong.")

# Add handlers
application.add_handler(CallbackQueryHandler(button, pattern='^help$|^back$|^my_waifus$', block=False))
application.add_handler(CommandHandler('start', start, block=False))
