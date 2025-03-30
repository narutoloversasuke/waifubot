import random
from html import escape
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, CallbackQueryHandler, CommandHandler
from shivu import application, SUPPORT_CHAT, UPDATE_CHAT, BOT_USERNAME, db, GROUP_ID
from shivu import pm_users as collection
import logging

private = ["https://postimg.cc/sBwHJ3dX", 
           "https://postimg.cc/TyvMLdjW", 
           "http://postimg.cc/K4DVK9jh"]
group = ["http://postimg.cc/PLDVdy9c", "http://postimg.cc/mPJ6xJXC", "http://postimg.cc/ZWCDM4cJ"]

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Constants for button labels and URLs
ADD_BUTTON_TEXT = "ADD ME"
ADD_BUTTON_URL = f'http://t.me/Madara_Husbando_grabber_Bot?startgroup=new'
SUPPORT_BUTTON_TEXT = "SUPPORT"
UPDATE_BUTTON_TEXT = "UPDATES"
HELP_BUTTON_TEXT = "HELP"
SOURCE_BUTTON_TEXT = "SOURCE"

# Message templates
START_CAPTION = """╔═════════════════════ஓ๑♡๑ஓ═════════════════════╗  
               🌸✨ **Welcome, Master!** ✨🌸  
╚═════════════════════ஓ๑♡๑ஓ═════════════════════╝  

🌸 **A world of waifus awaits you!** 🌸  
❥ Collect, cherish, and trade your favorite waifus! 💖  
❥ Unlock rare beauties and build the **ultimate collection**! ✨  
❥ Who knows? **Your dream waifu** might be waiting just for you! 💫  

╭───────────────────🌸───────────────────╮  
        💕 **Every waifu has a story...** 💕  
     🎀 **Will you be the one to claim her heart?** 🎀  
╰───────────────────🌸───────────────────╯  

💌 **Your adventure begins now, Master!** 💌  
🎀 **Step into the world of love, luck, and endless surprises!** 🎀"""

GROUP_CAPTION = "🎴 Alive!?... Connect to me in PM for more information."

HELP_TEXT = """*Help Section:*
*/guess* - To guess a character (works in groups only)
*/fav* - Add your favorite character
*/trade* - Trade characters
*/gift* - Give a character from your collection to another user (works in groups only)
*/collection* - View your collection
*/topgroups* - See the top groups where people guess the most
*/top* - View top users
*/ctop* - Your chat's top users
*/changetime* - Change character appearance time (works in groups only)"""

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
