import json
import numpy as np
import random
import discord
import io
import cv2
import asyncio

from image_generator import generate_image, _get_image

global info

class Player:
    def __init__(self, user_class, block_image: None, block_number: int=1) -> None:
        self.user_class = user_class
        self.block = block_image
        self.block_number = block_number

        if block_image is None:
            self.fetch_image()

        self.x_pos = 0
        self.y_pos = 0

        self.is_dead = False
        self.kills = []
        self.hero = 'becky'

        # ! Change back
        self.energy = 1000
    
    async def die(self) -> None:
        self.is_dead = True
    
    def fetch_image(self) -> None:
        self.block = _get_image(self.block_number)

class Game:
    def __init__(self, players: list | tuple, 
                 update_channel: discord.InteractionMessage.channel,
                 _id: int) -> None:
        self.players = players

        # Setting up variables
        self.update_channel = update_channel
        self.previous_message = None
        self.game_id = _id

        # creating grid
        if len(players) < 10:
            self.grid = np.zeros((10, 10))
        else:
            self.grid = np.zeros((25, 25))
        self._generate_start_positions(players)

        try:
            # Loading in all the .json files
            with open(r"data/blast_map.json", "r") as file:
                self.blast_map = json.load(file)
                print('[ INFO ]     Loaded blast map.')
            
            with open(r"data/energy_costs.json", "r") as file:
                self.energy_costs = json.load(file)
                print('[ INFO ]     Loaded energy costs.')
        except Exception as e:
            print(e)
    
    # Generates where the players starts at the start of game
    def _generate_start_positions(self, players: list) -> None:
        random.shuffle(players)
        
        # Define the starting positions for each number of players
        starting_positions = {
            # ! Remove the 1
            1: [(9, 9)],
            2: [(0, 0), (8, 5)],
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
        game_state_image = generate_image(self.grid, self.players)

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
            print(' [ ERROR ]     Cannot update message. discord.Forbidden!')
            return False

# ! Glitches out when on corner
    async def _get_blast_blocks(self, hero):
        if hero in self.blast_map:
            return self.blast_map[hero]
        return self.blast_map['normal']
    
    async def _get_energy_costs(self, hero, blast=False):
        cost = 0
        if hero in self.energy_costs:
            if blast:
                cost = self.energy_costs[hero]['blast']
            else:
                cost = self.energy_costs[hero]['move']
        else:
            if blast:
                cost = self.energy_costs['normal']['blast']
            else:
                cost = self.energy_costs['normal']['move']

        return cost

    async def _move_to_grid(self, old_position: tuple, new_position: tuple,
                       block: int, player: Player):
        self.grid[old_position[1], old_position[0]] = 0
        new_block = self.grid[new_position[1], new_position[0]]
        player.x_pos = new_position[0]
        player.y_pos = new_position[1]
        if new_block >   0:
            for player_2 in self.players:
                if player_2.x_pos == new_position[0] and\
                    player_2.y_pos == new_position[1]:
                    self.grid[new_position[1], new_position[0]] = block
                    return player_2
                
        self.grid[new_position[1], new_position[0]] = block
        
    async def move(self, direction: tuple, player: Player):
        player_x = player.x_pos
        player_y = player.y_pos

        if player.is_dead:
            return 'Sorry, you are dead.'

        energy_cost = await self._get_energy_costs(player.hero)
        if energy_cost < energy_cost:
            return 'Sorry, you do not have enough energy to move.'
        
        
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

        player.energy -= energy_cost
        result = await self.update()
        if not result:
            return f'You have moved! But I do not have access to send messages :('
        if did_kill:
            await did_kill.die()     
            return f'Successfully moved!\
            \n You also killed {did_kill.user_class.display_name}!'   
        return 'Successfully moved!'
            
    async def _get_player(self, x, y) -> Player | None:
        for player in self.players:
            if player.x_pos == x and player.y_pos == y:
                return player
        return False

    async def blast(self, player: Player) -> str:

        if player.is_dead:
            return 'Sorry, you are dead.'

        energy_cost = await self._get_energy_costs(
            player.hero, True)
        if player.energy < energy_cost:
            return 'Sorry, you do not have enough energy to blast.'


        directions = await self._get_blast_blocks(player.hero)
        killed = []
        killed_string = ''

        for direction in directions:
            x = player.x_pos + direction[0]
            y = player.y_pos + direction[1]
            if 10 > x > -1 and 10 > y > -1:
                self.grid[y, x] = -1

                other_player = await self._get_player(x, y)
                if other_player and not other_player.is_dead:
                    await other_player.die()
                    killed.append(other_player)
                    killed_string += other_player.user_class.display_name + ' '
                    player.kills.append(other_player)

        player.energy -= energy_cost

        result = await self.update()
        if not result:

            if killed_string == '':
                return 'Successfully blasted! You did not kill anyone.' + \
                    ' But I do not have the permission to send the game state :('
            else:
                return 'Sucessfully blasted! You killed: ' + killed_string + \
                    ' But I do not have the permission to send the game state :('
