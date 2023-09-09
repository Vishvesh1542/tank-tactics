import numpy as np
import cv2
import json
import time

# Initialize all the file reading
def init() -> None:
    global block_map, block_size
    block_size = 75
    # block map
    with open("data/block_map.json", "r") as file:
        _block_map = json.load(file)
        block_map = {}
        # Turning all the values back to integers
        for block in _block_map:
            block_map[int(block)] = _block_map[block]

    print('[ INFO ]     Initialized image generation.')
            
# Put's an image on top of another
def _overlay_image(im1: np.array, im2: np.array, x_offset: int, y_offset: int):
    # Mutates im1, placing im2 over it at a given offset.
    img = im1.copy()
    img[y_offset:y_offset+im2.shape[0], x_offset:x_offset+im2.shape[1]] = im2
    return img

def _get_image(block: int, theme: str='normal'):
    return cv2.resize(
        cv2.imread(
        # block map : theme > block 
        f"images/{theme}/{block_map[block]}.png"
    ), (block_size, block_size))

def _get_bg(theme: str='normal'):
    return cv2.resize(
        cv2.imread(f"images/{theme}/{block_map[0]}.png"),
          (block_size * 10, block_size * 10))

def generate_image(board: np.array, theme: str ='normal'):
    image = _get_bg(theme)
    x, y = 0, 0
    t_1 = time.time()
    for row in board:
        for block in row:
            if block != 0:
                overlay_image = _get_image(block=block, theme=theme)
                image = _overlay_image(im1=image, im2=overlay_image,
                            x_offset=x * block_size, y_offset=y * block_size)
            x += 1
        x = 0
        y += 1
    t_2 = time.time()
    print('[ INFO ]     Generated image in ' +  str(t_2-t_1) + ' seconds')
    return image

# Test
if __name__ == '__main__':
    image = np.zeros((10, 10), np.int8)
    print(image)
    image[5, 5] = 1
    init()
    generated_image = generate_image(image)
    cv2.imshow('Demo image', generated_image)    
    key = cv2.waitKey(0)
    if key != -1:
        cv2.destroyAllWindows()