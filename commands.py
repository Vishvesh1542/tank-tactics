import discord
from discord.ext import commands
from discord import Option
import random

import game_manager

def init(bot_: discord.Bot) -> None:
    global bot, bot_commands
    bot = bot_
    bot_commands = []
    print('[ INFO ]     initialised commands.')

    add_commands()

    print('[ INFO ]     Added commands.')

# Adds all the functions
def add_commands() -> None:
    add_command('new', 'Creates a new tank tactics game!', new)
    add_command('move', 'Move in a game.', move, Option(
        type=str, description='direction (w, a, s, d)', name='direction'),
        Option(int, 'The id of the game. ', name='id', required=False))
    add_command('blast', 'Blast in a game.', blast, Option(
        type=int, name='id', description='The id of the game.', required=False
    ))

    # Our add command function only supports 2 variables so making an exception
    @commands.slash_command(name='info', description='view the info of any tank!',
    options=[Option(name='x', description='The x coordinate of the tank. (1-10)',
            type=int), 
            Option(name='y', description='The y coordinate of the tank. (1-10)',
            type=int),
            Option(name='id', description='The id of the game.', type=int,
                   required=False)])
    async def func(ctx, x, y, id):
        await info(ctx, x, y, id)

def add_command(name:str, description: str, callback:callable,
                option_1: Option=None, option_2: Option=None,
                 group: discord.SlashCommandGroup=None):
    if option_1:
        if option_2:
            @commands.slash_command(name=name, description=description,
                                    options=[option_1, option_2])
            async def func(ctx, option_1, option_2):
                await callback(ctx, option_1, option_2)
        else:
            @commands.slash_command(name=name, description=description,
                                    options=[option_1])
            async def func(ctx, option_1):
                await callback(ctx, option_1)           

    else:
        @commands.slash_command(name=name, description=description,
                                options=[])
        async def func(ctx):
            await callback(ctx)

    if group:
        group.add_command(func)
    else:
        bot.add_application_command(func)

    bot_commands.append({'name': name, 'description': description,'options': 
                    [option_1, option_2], 'callback': callback, 'group': group})

async def send_message(ctx, message: str=None, view: discord.ui.View=None,
                    embed: discord.Embed=None, paginator: str=None):
    try:
        if not paginator:
            if isinstance(ctx, discord.Message):
                await ctx.channel.send(content=message, embed=embed,
                                    reference=ctx, view=view)
            else:
                if embed:
                    embed.color = random.choice([
            0x708090,  # Slate Gray
            0x556B2F,  # Olive Green
            0x008080,  # Teal Blue
            0xDAA520,  # Muted Gold
            0xD87093,  # Dusty Rose
            0x000080,  # Navy Blue
            0x8B4513,  # Earthy Brown
            0xE6E6FA,  # Soft Lavender
            0x36454F,  # Charcoal Gray
            0x98FB98   # Pastel Mint Green
            ]
                    )
                await ctx.respond(message, embed=embed, view=view)
        
        else:
            raise NotImplementedError('Do it fast')
    except discord.Forbidden:
        if isinstance(ctx, discord.Message):
            user = ctx.author
        else:
            user = ctx.user
            await user.send('I do not have permissions\
to send messages in the channel.')

def process_message(message: discord.Message) -> None:
    content = message.content
    if not content.startswith('.'):
        return
    raise NotImplementedError('Implement this maybe.')
    
async def new(ctx: discord.ApplicationContext):
    embed, view = await game_manager.new(ctx)
    await send_message(ctx, embed=embed, view=view)

async def move(ctx: discord.ApplicationContext, 
               direction: any(['w', 'a', 's', 'd']), id: int=None):
    message = await game_manager.move(ctx=ctx, direction_=direction, 
                                      _id=id)
    await send_message(ctx=ctx, message=message)

async def blast(ctx: discord.ApplicationContext, _id: int=None):
    message = await game_manager.blast(ctx=ctx, _id = _id)
    await send_message(ctx=ctx, message=message)

async def info(ctx: discord.ApplicationContext, x: int, y: int,
               _id: int=None):
    message = await game_manager.info(ctx, x, y, _id)
