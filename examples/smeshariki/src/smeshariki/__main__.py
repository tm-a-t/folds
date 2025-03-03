from app import app, bot1, bot2
from common_skill import common_skill

bot1.use(common_skill)
bot2.use(common_skill)

app.run()
