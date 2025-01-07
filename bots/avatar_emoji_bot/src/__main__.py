import logging
import os

from dotenv import load_dotenv

from src.logic import logic
from folds import Bot

logging.basicConfig(
    format='%(asctime)s    %(levelname)s  %(message)s    %(pathname)s:%(lineno)d',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO,
)

load_dotenv()
bot_token, api_id, api_hash = os.environ['BOT_TOKEN'], int(os.environ['API_ID']), os.environ['API_HASH']
bot = Bot(bot_token, api_id, api_hash, parse_mode='html')
bot.use_logic(logic)

bot.run()
