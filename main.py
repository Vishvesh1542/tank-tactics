import discord
from discord import Option

import image_generator
import commands


bot = discord.Bot('Hello I am Tank-Tactics!')

with open('token', 'r') as file:
    token = file.read()
   
image_generator.init()
commands.init(bot_=bot)

bot.run(token)