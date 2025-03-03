import logging
import os

from dotenv import load_dotenv

from avatar_emoji_bot.skill import skill
from folds import Bot

logging.basicConfig(
    format='%(asctime)s    %(levelname)s  %(message)s    %(pathname)s:%(lineno)d',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO,
)

load_dotenv()
bot_token, api_id, api_hash = os.environ['BOT_TOKEN'], int(os.environ['API_ID']), os.environ['API_HASH']
bot = Bot(bot_token, api_id, api_hash, parse_mode='html')
bot.use(skill)

bot.run()
