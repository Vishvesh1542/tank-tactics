import discord
import time
import aiohttp
import numpy as np
import cv2

import current_games
import game

async def download_image(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            image_ = await response.read()
            return image_


async def get_image(url):
    image_raw = await download_image(url)
    np_image = np.frombuffer(image_raw, np.uint8)
    image_ = cv2.imdecode(np_image, cv2.IMREAD_UNCHANGED)
    return cv2.resize(image_, (100, 100))


# Create a class called GameView has buttons to create a new game.
class CreateGameView(discord.ui.View):

    # Creating the button
    @discord.ui.button(label="Join Game!", style=discord.ButtonStyle.blurple, emoji="🎮")
    # What happens when the button is pressed
    async def button_callback(self, button, interaction):
        dict_ = current_games.read()
        if str(interaction.channel_id) not in dict_:
            await interaction.response.send_message("Sorry, the game could not be found.")
            return

        if interaction.user.id in [x.id for x in dict_[str(interaction.channel_id)]['members']]:
            await interaction.response.send_message("You are already in this game.")

        if not dict_[str(interaction.channel_id)]['started']: 
            user_image_url = interaction.user.avatar.url
            user_image = await get_image(user_image_url)

            dict_[str(interaction.channel_id)]['members'].append(game.Player(name=interaction.user.name, icon=user_image, _id=interaction.user.id))
            current_games.rewrite(dict_)

            # Send a message when the button is clicked
            await interaction.response.send_message(f"You joined the game hosted by {dict_[f'{interaction.channel_id}']['creator_name']}")

        else:
            await interaction.response.send_message("Sorry, the game already started.")


# Helps in looping through dictionaries ( current_games )
async def async_keys(d):
    for key in d.keys():
        yield key


# Creating
def get_start_embed() -> discord.Embed:
    embed = discord.Embed(title='Create a new game!')

    return embed, CreateGameView()


async def check_start(bot) -> None:
    _dict = current_games.read()
    for channel_id in _dict:
        if _dict[channel_id]['start_time'] <= time.time() and not _dict[channel_id]['started']:
            _dict[channel_id]['started'] = True
            _dict[channel_id]['game'] = game.TankTactics(_dict[channel_id]['members'])
            await _dict[channel_id]['game'].start(channel_id, _dict[channel_id], bot)
            print(f'started in {channel_id}')

    current_games.rewrite(_dict)
