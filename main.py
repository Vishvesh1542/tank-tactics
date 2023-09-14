import discord
from discord import Option
from discord.ext import tasks

import image_generator
import game_manager
import commands


bot = discord.Bot('Hello I am Tank-Tactics!')

with open('token', 'r') as file:
    token = file.read()
   
image_generator.init()
game_manager.init(bot)
commands.init(bot)

# ! Remove the seconds
@tasks.loop(seconds=1)
async def per_minute():
    await game_manager.listen()

per_minute.start()
bot.run(token)