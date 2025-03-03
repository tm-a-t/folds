from app import app, bot1, bot2
from common_logic import common_logic

bot1.use_logic(common_logic)
bot2.use_logic(common_logic)

app.run()
