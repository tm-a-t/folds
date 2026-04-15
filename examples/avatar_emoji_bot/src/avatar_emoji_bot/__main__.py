import logging

from dotenv import load_dotenv

from avatar_emoji_bot.skill import skill
from folds import Bot

logging.basicConfig(
    format='%(asctime)s    %(levelname)s  %(message)s    %(pathname)s:%(lineno)d',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO,
)

load_dotenv()
bot = Bot(parse_mode='html')
bot.use(skill)

bot.run()
