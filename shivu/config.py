class Config(object):
    LOGGER = True

    # Get this value from my.telegram.org/apps
    OWNER_ID = "7885908019"
    sudo_users = "7885908019", "7640076990", "7756901810" 
    GROUP_ID = -1002640379822
    TOKEN = "7656541596:AAEkC5jxXlArTehwTS9lmm61Xqi5cLpuPrk"  # Updated Token
    mongo_url = "mongodb+srv://walkrock:<supermanxxxx>@sunny.vu6keb7.mongodb.net/?retryWrites=true&w=majority&appName=sunny"
    SUPPORT_CHAT = "blade_x_support"
    UPDATE_CHAT = "blade_x_community"
    BOT_USERNAME = "Devine_wifu_bot"
    CHARA_CHANNEL_ID = "-4705079232"
    api_id = 26626068
    api_hash = "bf423698bcbe33cfd58b11c78c42caa2"

    
class Production(Config):
    LOGGER = True


class Development(Config):
    LOGGER = True
