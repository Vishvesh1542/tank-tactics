import numpy as np
import random
import discord
import time
import colorama
import cv2
from io import BytesIO


class Player:

    def __init__(self, name, icon, _id) -> None:
        self.image = icon
        self.score = None
        self.name = name
        self.energy = 69
        self.kills = 0
        self.eliminated = False
        self.killed_by = None
        self._id = _id


class TankTactics:
    default_bg_image = cv2.imread('assets/images/board_background.png')
    default_tank_image_greyscale = cv2.imread(
        'assets/images/tank_greyscale.png')
    default_bg_image = cv2.cvtColor(default_bg_image, cv2.COLOR_RGB2RGBA)

    def __init__(self, players: list):
        self.players = {}

        # Possible exceptions
        self.NOT_ENOUGH_ENERGY = "Not enough energy."
        self.ALREADY_ON_TOP_EDGE = "Already on top edge."
        self.ALREADY_ON_BOTTOM_EDGE = "Already on bottom edge."
        self.ALREADY_ON_LEFT_EDGE = "Already on left edge."
        self.ALREADY_ON_RIGHT_EDGE = "Already on right edge."
        self.TANK_ALREADY_EXISTS = "There is already a tank there"
        self.TANK_ELIMINATED = "Tank eliminated. Cannot play."

        self.grid = self._set_players_to_optimal_spot(players)

        # Possible direction
        self.directions = {'up': ['up', 'w', '↑'],
                           'down': ['down', 's', '↓'],
                           'left': ['left', 'a', '←'],
                           'right': ['right', 'd', '→']}
        
        self.channel_id = None
        self.message = None
        self.channel = None
        self.bot = None

    def _set_players_to_optimal_spot(self, players: list) -> np.array:
        no_of_players = len(players)

        # Hard coding starting positions
        if no_of_players == 2:
            self.players['1'] = [(1, 5), players[0]]
            self.players['2'] = [(8, 5), players[1]]

        elif no_of_players == 3:
            self.players['1'] = [(4, 2), players[0]]
            self.players['2'] = [(1, 5), players[1]]
            self.players['3'] = [(7, 5), players[2]]

        elif no_of_players == 4:
            self.players['1'] = [(1, 1), players[0]]
            self.players['2'] = [(8, 1), players[1]]
            self.players['3'] = [(1, 8), players[2]]
            self.players['4'] = [(8, 8), players[3]]

        elif no_of_players == 5:
            self.players['1'] = [(4, 1), players[0]]
            self.players['2'] = [(2, 3), players[1]]
            self.players['3'] = [(6, 3), players[2]]
            self.players['4'] = [(2, 7), players[3]]
            self.players['5'] = [(6, 7), players[4]]

        elif no_of_players == 6:
            self.players['1'] = [(3, 1), players[0]]
            self.players['2'] = [(6, 1), players[1]]
            self.players['3'] = [(3, 4), players[2]]
            self.players['4'] = [(6, 4), players[3]]
            self.players['5'] = [(3, 7), players[4]]
            self.players['6'] = [(6, 7), players[5]]

        elif no_of_players == 7:
            self.players['1'] = [(3, 0), players[0]]
            self.players['2'] = [(6, 0), players[1]]
            self.players['3'] = [(3, 3), players[2]]
            self.players['4'] = [(6, 3), players[3]]
            self.players['5'] = [(3, 6), players[4]]
            self.players['6'] = [(6, 6), players[5]]
            self.players['7'] = [(3, 9), players[6]]

        elif no_of_players == 8:
            self.players['1'] = [(3, 0), players[0]]
            self.players['2'] = [(6, 0), players[1]]
            self.players['3'] = [(3, 3), players[2]]
            self.players['4'] = [(6, 3), players[3]]
            self.players['5'] = [(3, 6), players[4]]
            self.players['6'] = [(6, 6), players[5]]
            self.players['7'] = [(3, 9), players[6]]
            self.players['8'] = [(6, 9), players[7]]

        else:
            self.players['1'] = [(5, 5), players[0]]

        positions = np.zeros((10, 10), np.int32)
        for key, value in self.players.items():
            positions[value[0]] = int(key)
        return positions

    async def move(self, player: Player | int, direction: str) -> None | str:
        if isinstance(player, Player):
            player = self._get_player_from_class(player)

        direction_tuple = self._get_tuple_from_string(direction)
        previous_position = self.players[str(player)][0]

        new_position = tuple(a + b for a,
                             b in zip(previous_position, direction_tuple))

        # checking for errors.
        if self.players[str(player)][1].eliminated:
            return self.TANK_ELIMINATED

        if self.players[str(player)][1].energy <= 0:
            return self.NOT_ENOUGH_ENERGY
        # Checking if on the edge
        if direction in self.directions['up']:
            if previous_position[0] == 0:
                return self.ALREADY_ON_TOP_EDGE

        elif direction in self.directions['down']:
            if previous_position[0] == 9:
                return self.ALREADY_ON_BOTTOM_EDGE

        elif direction in self.directions['left']:
            if previous_position[1] == 0:
                return self.ALREADY_ON_LEFT_EDGE

        elif direction in self.directions['right']:
            if previous_position[1] == 9:
                return self.ALREADY_ON_RIGHT_EDGE

        if self.grid[new_position] not in [0, 9]:
            return self.TANK_ALREADY_EXISTS

        # Actual stuff
        self.grid[previous_position] = 0
        self.grid[new_position] = player

        self.players[str(player)][0] = new_position
        self.players[str(player)][1].energy -= 1
        
        await self.update()
        return

    # Converting 'up', 'down'.. to tuples which can easily be calculated
    def _get_tuple_from_string(self, direction_string: str) -> tuple:
        direction_string = direction_string.lower()
        if direction_string in self.directions['up']:
            return (-1, 0)

        elif direction_string in self.directions['down']:
            return (1, 0)

        elif direction_string in self.directions['left']:
            return (0, -1)

        elif direction_string in self.directions['right']:
            return (0, 1)

        raise ValueError(f'direction not in {self.directions}')

    # Getting the current state of the game.
    def _get_grid(self) -> np.ndarray:
        return self.grid

    async def start(self, channel_id: int | str, _dict: dict, bot: discord.Bot) -> None:
        self.channel_id = channel_id
        self.bot = bot

        print('starting game')

        image_file = self._get_discord_image_file()
            
        channel = bot.get_channel(int(channel_id))
        self.channel = channel

        message = await channel.send(file=image_file)
        self.message = message

    async def update(self):
        await self.message.delete()

        msg = await self.channel.send(file=self._get_discord_image_file())

        self.message = msg

    def _get_discord_image_file(self) -> discord.File:
        _, png_image = cv2.imencode('.png', self.get_game_state_image())

        with BytesIO(png_image) as binary_stream:
            image_file = discord.File(
                fp=binary_stream, filename='game_state.png')
            return image_file
            

    # Killing tanks nearby ( Feature )
    def blast(self, player: Player | int) -> str | bool:
        if isinstance(player, Player):
            player = self._get_player_from_class(player)

        # Not enough energy
        if self.players[f"{player}"][1].energy < 2:
            return self.NOT_ENOUGH_ENERGY

        if self.players[str(player)][1].eliminated:
            return self.TANK_ELIMINATED

        self.players[str(player)][1].energy -= 2

        player_position = self.players[str(player)][0]

        # Getting the nearby cells. ( top, bottom, left, right...)
        nearby_cells = []
        for a in range(-1, 2):
            for b in range(-1, 2):
                value = (player_position[0] + a, player_position[1] + b)
                if value[0] >= 0 and value[0] < 10 and\
                        value[1] >= 0 and value[1] < 10 and player_position != value:
                    nearby_cells.append(
                        (player_position[0] + a, player_position[1] + b))
                    self.grid[player_position[0] + a,
                              player_position[1] + b] = 9

        b = False
        for player_position, player_class in self.players.values():
            if player_position in nearby_cells:
                player_class.eliminated = True
                player_class.killed_by = self.players[str(player)][1]
                self.players[str(player)][1].kills += 1
                b = True
        if b:
            return True
        return False

    def _get_player_from_class(self, player: Player) -> int:
        # If we get a type of Player class
        for key, value in self.players.items():
            if value[1] == player:
                player = int(key)
                return player

    def add_energy(self) -> None:
        for _, player_class in self.players.values():
            player_class.energy += 1

    def _overlay_image(self, im1, im2, x_offset, y_offset):
        # Mutates im1, placing im2 over it at a given offset.
        img = im1.copy()
        img[y_offset:y_offset+im2.shape[0], x_offset:x_offset+im2.shape[1]] = im2
        return img

    def get_game_state_image(self) -> np.ndarray:
        t = time.time()
        image_new = self.default_bg_image.copy()
        for row in self.grid:
            for value in row:
                if value > 0:
                    player = self.players[str(value)]
                    player_image = player[1].image

                    if player_image is None:
                        player_image = self.default_bg_image.copy()
                    image_new = self._overlay_image(image_new, player_image, player[0][1] * 100 + ((player[0][1] + 1) * 5),
                                                    player[0][0] * 100 + ((player[0][0] + 1) * 5))

        print(f'Created image in {time.time() - t} seconds')
        return image_new


class Console:
    default_bg_image = cv2.imread('assets/images/board_background.png')
    default_tank_image_greyscale = cv2.imread(
        'assets/images/tank_greyscale.png')

    def __init__(self, players: list):
        self.players = {}

        # Possible exceptions
        self.NOT_ENOUGH_ENERGY = -1
        self.ALREADY_ON_TOP_EDGE = 0
        self.ALREADY_ON_BOTTOM_EDGE = 1
        self.ALREADY_ON_LEFT_EDGE = 2
        self.ALREADY_ON_RIGHT_EDGE = 3
        self.TANK_ALREADY_EXISTS = 4
        self.TANK_ELIMINATED = 69

        self.grid = self._set_players_to_optimal_spot(players)

        # Possible direction
        self.directions = {'up': ['up', 'w', '↑'],
                           'down': ['down', 's', '↓'],
                           'left': ['left', 'a', '←'],
                           'right': ['right', 'd', '→']}
        np.set_printoptions(formatter={'int': self.colorize_character})

    def _set_players_to_optimal_spot(self, players: list) -> np.array:
        no_of_players = len(players)

        # Hard coding starting positions
        if no_of_players == 2:
            self.players['1'] = [(1, 5), players[0]]
            self.players['2'] = [(8, 5), players[1]]

        elif no_of_players == 3:
            self.players['1'] = [(4, 2), players[0]]
            self.players['2'] = [(1, 5), players[1]]
            self.players['3'] = [(7, 5), players[2]]

        elif no_of_players == 4:
            self.players['1'] = [(1, 1), players[0]]
            self.players['2'] = [(8, 1), players[1]]
            self.players['3'] = [(1, 8), players[2]]
            self.players['4'] = [(8, 8), players[3]]

        elif no_of_players == 5:
            self.players['1'] = [(4, 1), players[0]]
            self.players['2'] = [(2, 3), players[1]]
            self.players['3'] = [(6, 3), players[2]]
            self.players['4'] = [(2, 7), players[3]]
            self.players['5'] = [(6, 7), players[4]]

        elif no_of_players == 6:
            self.players['1'] = [(3, 1), players[0]]
            self.players['2'] = [(6, 1), players[1]]
            self.players['3'] = [(3, 4), players[2]]
            self.players['4'] = [(6, 4), players[3]]
            self.players['5'] = [(3, 7), players[4]]
            self.players['6'] = [(6, 7), players[5]]

        elif no_of_players == 7:
            self.players['1'] = [(3, 0), players[0]]
            self.players['2'] = [(6, 0), players[1]]
            self.players['3'] = [(3, 3), players[2]]
            self.players['4'] = [(6, 3), players[3]]
            self.players['5'] = [(3, 6), players[4]]
            self.players['6'] = [(6, 6), players[5]]
            self.players['7'] = [(3, 9), players[6]]

        elif no_of_players == 8:
            self.players['1'] = [(3, 0), players[0]]
            self.players['2'] = [(6, 0), players[1]]
            self.players['3'] = [(3, 3), players[2]]
            self.players['4'] = [(6, 3), players[3]]
            self.players['5'] = [(3, 6), players[4]]
            self.players['6'] = [(6, 6), players[5]]
            self.players['7'] = [(3, 9), players[6]]
            self.players['8'] = [(6, 9), players[7]]

        else:
            self.players['1'] = [(5, 5), players[0]]

        positions = np.zeros((10, 10), np.int32)
        for key, value in self.players.items():
            positions[value[0]] = int(key)
        return positions

    def move(self, player: Player | int, direction: str):
        if isinstance(player, Player):
            player = self._get_player_from_class(player)

        if self.players[str(player)][1].eliminated:
            return self.TANK_ELIMINATED

        if self.players[str(player)][1].energy <= 0:
            return self.NOT_ENOUGH_ENERGY
        direction_tuple = self._get_tuple_from_string(direction)

        previous_position = self.players[str(player)][0]

        # Checking if on the edge
        if direction in self.directions['up']:
            if previous_position[0] == 0:
                return self.ALREADY_ON_TOP_EDGE

        elif direction in self.directions['down']:
            if previous_position[0] == 9:
                return self.ALREADY_ON_BOTTOM_EDGE

        elif direction in self.directions['left']:
            if previous_position[1] == 0:
                return self.ALREADY_ON_LEFT_EDGE

        elif direction in self.directions['right']:
            if previous_position[1] == 9:
                return self.ALREADY_ON_RIGHT_EDGE

        new_position = tuple(a + b for a,
                             b in zip(previous_position, direction_tuple))

        if self.grid[new_position] not in [0, 9]:
            return self.TANK_ALREADY_EXISTS

        self.grid[previous_position] = 0
        self.grid[new_position] = player

        self.players[str(player)][0] = new_position
        self.players[str(player)][1].energy -= 1
        return

    def _get_tuple_from_string(self, direction: str) -> tuple:
        direction = direction.lower()
        if direction in self.directions['up']:
            return (-1, 0)

        elif direction in self.directions['down']:
            return (1, 0)

        elif direction in self.directions['left']:
            return (0, -1)

        elif direction in self.directions['right']:
            return (0, 1)

        raise ValueError(f'direction not in {self.directions}')

    def colorize_character(self, number):
        color = colorama.Back.RESET
        if number == 9:
            color = colorama.Back.RED
        elif number == 1:
            color = colorama.Back.CYAN
        elif number == 2:
            color = colorama.Back.MAGENTA
        elif number == 3:
            color = colorama.Back.YELLOW
        elif number == 4:
            color = colorama.Back.LIGHTGREEN_EX
        elif number == 5:
            color = colorama.Back.LIGHTRED_EX
        elif number == 6:
            color = colorama.Back.LIGHTBLUE_EX
        elif number == 7:
            color = colorama.Back.GREEN
        elif number == 8:
            color = colorama.Back.RED

        return f'{color}{number}'

    def _get_grid(self) -> np.ndarray:
        return self.grid

    def blast(self, player: Player | int) -> None | int:
        if isinstance(player, Player):
            player = self._get_player_from_class(player)

        if self.players[f"{player}"][1].energy < 2:
            return self.NOT_ENOUGH_ENERGY

        self.players[str(player)][1].energy -= 2

        player_position = self.players[str(player)][0]

        nearby_cells = []

        for a in range(-1, 2):
            for b in range(-1, 2):
                value = (player_position[0] + a, player_position[1] + b)
                if value[0] >= 0 and value[0] < 10 and\
                        value[1] >= 0 and value[1] < 10 and player_position != value:
                    nearby_cells.append(
                        (player_position[0] + a, player_position[1] + b))
                    self.grid[player_position[0] + a,
                              player_position[1] + b] = 9

        b = False
        for player_position, player_class in self.players.values():
            if player_position in nearby_cells:
                player_class.eliminated = True
                self.players[str(player)][1].kills += 1
                b = True
        if b:
            return f"Player got one more kill. Current kills {self.players[str(player)][1].kills}"

    def _get_player_from_class(self, player: Player) -> int:
        # If we get a type of Player class
        for key, value in self.players.items():
            if value[1] == player:
                player = int(key)
                return player

    def add_energy(self) -> None:
        for _, player_class in self.players.values():
            player_class.energy += 1

    def _overlay_image(self, im1, im2, x_offset, y_offset):
        # Mutates im1, placing im2 over it at a given offset.
        print(im1.shape, im2.shape)
        img = im1.copy()
        img[y_offset:y_offset+im2.shape[0], x_offset:x_offset+im2.shape[1]] = im2
        return img


if __name__ == '__main__':
    time_ = time.time()

    no_of_players = int(input('How many players? \n'))

    games = []
    t1 = time.time()
    for i in range(10000):
        games.append(Console(players=[Player(1, 0, 0) for _ in range(no_of_players)]))

    print(f'Created 10000 games in {time.time()-t1} seconds')

    while True:
        ps = [str(i) for i in range(1, no_of_players + 1)]
        for p in ps:
            direction = input(f'Enter direction for player {p}: ')
            t2 = time.time()
            for game in games:
                if direction == 'b':
                    x = game.blast(p)

                elif direction == 'p':
                    x = None

                else:
                    x = game.move(p, direction)
            print(games[0]._get_grid())

            if x is not None:
                print(f"Error: Code {x}")
            print(f'Moved in 100000 games in {time.time()-t2} seconds')


        for game in games:
            game.add_energy()
        print('Gave energy')
