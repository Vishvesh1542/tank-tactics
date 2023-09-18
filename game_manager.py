import discord
import time
import cv2
import io

from image_generator import generate_image
from game import Game, Player
import utils

def init(_bot) -> None:
    global bot, games, used_ids, listeners

    bot = _bot
    games = {}
    listeners = []
    used_ids = []

    print('[ INFO ]     Initialized game manager.')



class StartGameView(discord.ui.View):

    # Creating the button
    @discord.ui.button(label="Join Game!", style=discord.ButtonStyle.blurple, emoji="🎮")
    # What happens when the button is pressed
    async def button_callback(self, button: discord.Button, 
                              interaction: discord.Interaction):
        player_classes = [x.user_class for x in 
                          games[interaction.channel_id]['players']]
        if interaction.user not in player_classes:
            games[interaction.channel_id]['players'].append(
                Player(interaction.user)
            )
            await interaction.response.send_message('Successfully joined game!')
        else:
            await interaction.response.send_message('You are already in the game!')

async def listen():
    global listeners
    new_list = []
    for listener in listeners:
        if listener['time'] <= time.time():
            await listener['callback'](listener['var'])
        else:
            new_list.append(listener)
    print(new_list)
    
    listeners = new_list

async def call(time: float, callback: callable, variables: list):
    listeners.append({'time': time, "callback": callback, "var": variables})

async def listen_for_join(ctx: discord.ApplicationContext, timeout: int=86400):
    view = StartGameView(timeout=timeout)
    await call(time.time() + timeout, start, [ctx])
    return view

async def start(variables: list):
    ctx = variables[0]

    # !if len(games[ctx.channel_id]['players']) < 2:
    # !    await ctx.send('Game has ended because of insufficient players.')
    # !    return
    games[ctx.channel_id]['state'] = 'started'
    _id = games[ctx.channel_id]['id']
    game = Game(games[ctx.channel_id]['players'],
                 update_channel=ctx.channel, _id=_id)
    games[ctx.channel_id]['game'] = game
    await game.update()
    print('[ INFO ]     game started')

async def is_in_game(ctx: discord.ApplicationContext, _id: int=None):   
    if not _id:
        channel = ctx.channel
        if ctx.channel_id not in games:
            return 'No raid found in this channel.'
        game = games[ctx.channel_id]

    else:
        found = False
        for ch_id, game_ in games.items():
            if game_['id'] == _id:
                game = game_
                found = True
                channel= ch_id
                continue
        if not found:
            return 'Error: Invalid id!'
        
    found = False
    for player in game['players']:
        if player.user_class.id == ctx.user.id:
            player_class = player
            found = True
            continue
    
    if not found:
        return 'You are not in the game!'
    
    return game, channel, player_class

async def new(ctx: discord.ApplicationContext):
    global used_ids
    embed = discord.Embed(title=f"`{ctx.user.name}` hosted a game!")
    
    # There is already a game.
    if ctx.channel_id in games:
        embed.add_field(name='Sorry, a game already exists in the chanel.', value='')
        embed.add_field(name='Use another channel for starting a new game.',
                        value='use `/new`', inline=False)
        return embed, None
    
    # ! Change the 5 seconds to appropriate time.
    view = await listen_for_join(ctx, timeout=5)


    highest_id = utils.find_missing_number(used_ids)
    used_ids.append(highest_id)
    embed.add_field(name=f"id:  {highest_id}", value=" ")

    games[ctx.channel_id] = {'id': highest_id, 'author': ctx.user,
                              'players': [Player(ctx.user)],
                              'start_time': time.time(), 'state': 'listening',
                              'game': None}
    return embed, view  

async def move(ctx: discord.ApplicationContext, direction_: str, _id: int=None):
    global games
    direction = Game.get_direction(direction_)

    values = await is_in_game(ctx, _id=_id)
    if isinstance(values, str):
        return values
    else:
        game, channel, player_class =values
    
    message = await game['game'].move(direction, player_class)
    return message
    
async def blast(ctx: discord.ApplicationContext, _id: int=None):

    values = await is_in_game(ctx, _id)
    if isinstance(values, str):
        return values

    else:
        game, channel, player_class = values

    return await game['game'].blast(player_class)
    


    