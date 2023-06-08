import discord
from discord.ext import bridge, tasks, commands
import current_games
import utils
import time

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

    @tasks.loop(seconds=1)
    async def check_time(self):
        await utils.check_start()


bot.add_cog(Commands(bot))
bot.run(token="MTEwNTg2NzQ4NTkwNDkxNjUxMA.GvKTxU.Yw4H5E_hghnjc_yqlTnhqqRFmlUJU43TUAeUpA")
bot.get_user