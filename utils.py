import discord
import current_games
import time


# Create a class called GameView has buttons to create a new game.
class CreateGameView(discord.ui.View):

    # Creating the button
    @discord.ui.button(label="Join Game!", style=discord.ButtonStyle.blurple, emoji="🎮")
    # What happens when the button is pressed
    async def button_callback(self, button, interaction):
        dict_ = current_games.read()
        if str(interaction.channel_id) not in dict_:
            await interaction.response.send_message("Sorry, the game could not be found.")

        elif not dict_[str(interaction.channel_id)]['started']:

            dict_[str(interaction.channel_id)]['members'].append(
                interaction.user.name)
            current_games.rewrite(dict_)
            current_games.sync()

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


async def check_start() -> None:

    _dict = current_games.read()
    async for channel_id in async_keys(_dict):
        if _dict[channel_id]['start_time'] <= time.time() and not _dict[channel_id]['started']:
            _dict[channel_id]['started'] = True
            print(f'started in {channel_id}')

    current_games.rewrite(_dict)
