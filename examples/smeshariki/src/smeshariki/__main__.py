from smeshariki.app import app, ezhik_bot, losyash_bot, barash_bot
from smeshariki.skills.ezhik import ezhik_skill
from smeshariki.skills.barash import barash_skill
from smeshariki.skills.losyash import losyash_skill
from smeshariki.skills.pm import pm_skill

ezhik_bot.use(ezhik_skill, pm_skill)
barash_bot.use(barash_skill, pm_skill)
losyash_bot.use(losyash_skill, pm_skill)

app.run()
