class Config(object):
    LOGGER = True

    # Get this value from my.telegram.org/apps
    OWNER_ID = "7885908019"
    sudo_users = "7885908019", "7640076990", "7756901810" 
    GROUP_ID =-1002640379822
    TOKEN = "7583740884:AAEsWTCQNJiOjNQdXw4MBFU9-rL5l82mLQA" 
    mongo_url = "mongodb+srv://naruhina:harshitkichut@cluster0.03pl6.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0" 
    PHOTO_URL = "https://files.catbox.moe/0nb1p7.jpg" 
    SUPPORT_CHAT = "blade_x_support"
    UPDATE_CHAT = "blade_x_community"
    BOT_USERNAME = "Devine_wifu_bot"
    CHARA_CHANNEL_ID = "-1002640379822"
    api_id = 26626068
    api_hash = "bf423698bcbe33cfd58b11c78c42caa2"

    
class Production(Config):
    LOGGER = True


class Development(Config):
    LOGGER = True
