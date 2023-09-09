import discord
import time
import cv2
import io

from image_generator import generate_image
from game import Game
import utils

def init(_bot) -> None:
    global bot, games, used_ids, listeners

    bot = _bot
    games = {}
    listeners = []
    used_ids = []

    print('[ INFO ]     Initialized game manager.')

class Player:
    def __init__(self, user_class) -> None:
        self.user_class = user_class
        self.block_number = 1
        self.x_pos = 0
        self.y_pos = 0

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
    
    listeners = new_list

async def call(time: float, callback: callable, variables: list):
    listeners.append({'time': time, "callback": callback, "var": variables})

async def listen_for_join(ctx: discord.ApplicationContext, timeout: int=86400):
    view = StartGameView(timeout=timeout)
    await call(time.time() + timeout, start, [ctx])
    return view

async def start(variables: list):
    ctx = variables[0]

    if len(games[ctx.channel_id]['players']) < 2:
        await ctx.send('Game has ended because of insufficient players.')
        return
    games[ctx.channel_id]['state'] = 'started'
    game = Game(games[ctx.channel_id]['players'])
    games[ctx.channel_id]['game'] = game
    game_state_image = generate_image(game.grid)

        # Convert the OpenCV image to bytes
    _, img_bytes = cv2.imencode('.png', game_state_image)
    img_bytes = img_bytes.tobytes()

    # Create an embed with an image
    embed = discord.Embed(title=
            f'Tank Tactics! id: `{games[ctx.channel_id]["id"]}`')
    embed.set_image(url="attachment://image.png")

    # Send the embed with the image
    print('[ INFO ]     game started')
    await ctx.send(embed=embed, file=discord.File(io.BytesIO(img_bytes), filename='image.png'))

async def new(ctx: discord.ApplicationContext):
    global used_ids
    embed = discord.Embed(title=f"`{ctx.user.name}` hosted a game!")
    
    # There is already a game.
    if ctx.channel_id in games:
        embed.add_field(name='Sorry, a game already exists in the chanel.', value='')
        embed.add_field(name='Use another channel for starting a new game.',
                        value='use `/new`', inline=False)
        return embed, None
    
    view = await listen_for_join(ctx, timeout=5)


    highest_id = utils.find_missing_number(used_ids)
    used_ids.append(highest_id)
    embed.add_field(name=f"id:  {highest_id}", value=" ")

    games[ctx.channel_id] = {'id': highest_id, 'author': ctx.user,
                              'players': [Player(ctx.user)],
                              'start_time': time.time(), 'state': 'listening',
                              'game': None}
    return embed, view  