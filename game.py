import json
import numpy as np
import random
import discord
import io
import cv2

from image_generator import generate_image

class Player:
    def __init__(self, user_class) -> None:
        self.user_class = user_class
        self.block_number = 1
        self.x_pos = 0
        self.y_pos = 0
        self.is_dead = False
    
    async def die(self) -> None:
        self.is_dead = True

class Game:
    def __init__(self, players: list | tuple, 
                 update_channel: discord.InteractionMessage.channel,
                 _id: int) -> None:
        self.players = players

        self.update_channel = update_channel
        self.previous_message = None
        self.game_id = _id

        if len(players) < 10:
            self.grid = np.zeros((10, 10))
        else:
            self.grid = np.zeros((25, 25))
        self._generate_start_positions(players)
    
    # Generates where the players starts at the start of game
    def _generate_start_positions(self, players: list) -> None:
        random.shuffle(players)
        
        # Define the starting positions for each number of players
        starting_positions = {
            1: [(5, 5)],
            2: [(1, 5), (8, 5)],
            3: [(4, 2), (1, 5), (7, 5)],
            4: [(1, 1), (8, 1), (1, 8), (8, 8)],
            5: [(4, 1), (2, 3), (6, 3), (2, 7), (6, 7)],
            6: [(3, 1), (6, 1), (3, 4), (6, 4), (3, 7), (6, 7)],
            7: [(3, 0), (6, 0), (3, 3), (6, 3), (3, 6), (6, 6), (3, 9)],
            8: [(3, 0), (6, 0), (3, 3), (6, 3), (3, 6), (6, 6), (3, 9), (6, 9)]
        }

        index = 0
        no_ = len(players)
        for player in players:
            x, y = starting_positions[no_][index]
            player.x_pos = x
            player.y_pos = y

            self.grid[y, x] = player.block_number

            index += 1

    def get_direction(direction_raw: str) -> tuple:
        direction_raw = direction_raw.lower()
        maps = {'w': ['w', 'up', '↑'],
                'a': ['a', 'left', '←'],
                's': ['s', 'down', '↓'], 
                'd': ['d', 'right', '→']}
        for _direction, values in maps.items():
            if direction_raw in values:
                return _direction
        return None
    
    async def update(self) -> None:
        game_state_image = generate_image(self.grid)

            # Convert the OpenCV image to bytes
        _, img_bytes = cv2.imencode('.png', game_state_image)
        img_bytes = img_bytes.tobytes()

        # Create an embed with an image
        embed = discord.Embed(title=
                f'Tank Tactics! id: `{self.game_id}`')
        embed.set_image(url="attachment://image.png")

        old_message = self.previous_message

        # Send the embed with the image
        try:
            self.previous_message = await self.update_channel.send(embed=embed, 
                file=discord.File(io.BytesIO(img_bytes), filename='image.png'))
            if old_message:
                await old_message.delete()
                return True
        except discord.Forbidden:
            return False
        


    async def _move_to_grid(self, old_position: tuple, new_position: tuple,
                       block: int, player: Player):
        self.grid[old_position[1], old_position[0]] = 0
        new_block = self.grid[new_position[1], new_position[0]]
        player.x_pos = new_position[0]
        player.y_pos = new_position[1]
        if new_block != 0:
            for player_2 in self.players:
                if player_2.x_pos == new_position[0] and\
                    player_2.y_pos == new_position[1]:
                    self.grid[new_position[1], new_position[0]] = block
                    return player_2
                
        self.grid[new_position[1], new_position[0]] = block
        
    async def move(self, direction: tuple, player: Player):
        player_x = player.x_pos
        player_y = player.y_pos
        
        if direction == 'a':
            if player_x < 1:
                return 'Player is already on edge!'
            else:
                did_kill = await self._move_to_grid((player_x, player_y),
                            (player_x-1, player_y), player.block_number,
                            player)

        elif direction == 'd':
            if player_x > 8:
                return 'Player is already on edge!'
            else:
                did_kill = await self._move_to_grid((player_x, player_y),
                            (player_x+1, player_y), player.block_number,
                            player)
                
        if direction == 'w':
            if player_y < 1:
                return 'Player is already on edge!'
            else:
                did_kill = await self._move_to_grid((player_x, player_y),
                            (player_x, player_y - 1), player.block_number,
                            player)
        elif direction == 's':
            if player_y > 8:
                return 'Player is already on edge!'
            else:
                did_kill = await self._move_to_grid((player_x, player_y),
                            (player_x, player_y + 1), player.block_number,
                            player)

        result = await self.update()
        if not result:
            return f'You have moved! But I do not have access to send messages :('
        if did_kill:
            await did_kill.die()     
            return f'Successfully moved!\
            \n You also killed {did_kill.user_class.display_name}!'   
        return 'Successfully moved!'
            
 