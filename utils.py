
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
