import random

def play_roulette(bet):
    """
    Логика игры в рулетку: рассчитывает результат и обновляет ставку.
    """
    red_numbers = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
    black_numbers = {2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35}
    green_numbers = {0, '00'}

    # Выпадение случайного числа
    numbers = list(range(0, 37)) + ['00']
    rolled_number = random.choice(numbers)

    # Определяем цвет выпавшего числа
    if rolled_number in red_numbers:
        rolled_color = 'red'
    elif rolled_number in black_numbers:
        rolled_color = 'black'
    else:
        rolled_color = 'green'

    # Рассчитываем выигрыш
    payout = 0
    if rolled_color == bet.color:
        if rolled_color == 'green':
            payout = bet.amount * 35
        else:
            payout = bet.amount * 2

    return rolled_number, rolled_color, payout
