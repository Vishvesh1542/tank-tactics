
def find_missing_number(nums: list):
    if not nums:
        return 1
        
    nums.sort()
    
    expected_num = 1

    for num in nums:
        if num == expected_num:
            expected_num += 1
        elif num > expected_num:
            return expected_num
    
    return expected_num

def get_direction(direction_raw: str) -> tuple:
    direction_raw = direction_raw.lower()
    maps = {(0, -1): ['w', 'up', '↑'],
            (-1, 0): ['a', 'left', '←'],
            (0, 1): ['s', 'down', '↓'], 
            (1, 0): ['d', 'right', '→']}
    for _direction, values in maps.items():
        if direction_raw in values:
            return _direction
    return None