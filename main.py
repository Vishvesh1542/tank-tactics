import discord
from discord.ext import bridge, tasks, commands
from discord.commands import Option
import utils
from typing import Union
import time

import current_games

bot = bridge.Bot(command_prefix='.', intents=discord.Intents.all())


class Commands(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.check_time.start()

    @bridge.bridge_command(name='new', description='create a new Tank Tactics game!')
    async def new_game(self, ctx: bridge.context.BridgeApplicationContext):
        embed, view = utils.get_start_embed()
        if isinstance(ctx, bridge.context.BridgeExtContext):
            # If it was invoked with . ( message command)
            current_games.write(key=str(ctx.message.channel.id), value={
                                "creator_id": ctx.message.author.id, 'creator_name': ctx.message.author.name, 'members': [], 'start_time': time.time() + 5, 'started': False})  # 86400 is 24 hours
        # if with / command
        else:
            current_games.write(key=str(ctx.channel_id), value={
                                "creator_id": ctx.author.id, 'creator_name': ctx.author.name, 'members': [], 'start_time': time.time() + 5, 'started': False})

        await ctx.respond(embed=embed, view=view)

    @bridge.bridge_command(name='move', description='Move in a  game. (protip: use this in the channel a game is running without a game_id)')
    async def move(self, ctx: bridge.context.BridgeApplicationContext, direction:
                   Option(name='direction', type='str',
                          description='direction you want to move in (w, a, s, d)'),
                   game_id: Option(name='game_id', required=False, type=int, description="ID of the game. Leave empty if you are in the same channel as the game.")):

        if direction.lower() not in ['up', 'w', '↑', 'down', 's', '↓', 'left', 'a', '←', 'right', 'd', '→']:
            await ctx.respond('Invalid direction.')
            return

        if isinstance(ctx, bridge.context.BridgeApplicationContext):
            user_id = ctx.author.id
        else:
            user_id = ctx.message.author.id

        channel_id = None
        _dict = current_games.read()
        for game in _dict.keys():
            if int(game) == game_id:
                channel_id = int(game)

        if channel_id is None:
            if isinstance(ctx, bridge.context.BridgeApplicationContext):
                if ctx.channel_id not in [int(x) for x in _dict.keys()]:
                    await ctx.respond('Sorry, no game could be found in this channel. Try entering the game_id')
                    return
                else:
                    channel_id = ctx.channel_id
            else:
                if ctx.message.channel_id not in [int(x) for x in _dict.keys()]:
                    await ctx.respond('Sorry, no game could be found in this channel. Try entering the game_id')
                    return

                else:
                    channel_id = ctx.message.channel_id

        t = False
        user_class = None
        for player in _dict[str(channel_id)]['members']:
            if player._id == user_id:
                t = True
                user_class = player
                break

        if not t:
            await ctx.respond('You are not in this game.')
            return

        if not _dict[str(channel_id)]['started']:
            await ctx.respond('The game did not start yet.')
            return

        message = await     _dict[str(channel_id)]['game'].move(
            player=user_class, direction=direction)
        print(message)

        await ctx.respond(f"{direction}, {game_id}")

    @tasks.loop(seconds=1)
    async def check_time(self):
        await utils.check_start(bot)


bot.add_cog(Commands(bot))
bot.run(token="MTEwNTg2NzQ4NTkwNDkxNjUxMA.GvKTxU.Yw4H5E_hghnjc_yqlTnhqqRFmlUJU43TUAeUpA")
