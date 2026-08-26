from modules.config import *
from modules.console import *
from modules.input import *

def buy_me_a_coffee():
    console.print('Как вы хотите мне задонатить?')
    console.print('[primary][1][/primary] Долоры $$$ денги')
    console.print('[primary][2][/primary] Telegram подарок')
    choice = v2i('Выберите способ', f'{USERNAME}@{UUID}').strip()

    if choice == '1':
        console.print('Спасибо, если задонатите!')
        console.print('t.me/send?start=IVDFBKzYoE5u')

    elif choice == '2':
        console.print('Спасибо, если подарите подарок!')
        console.print('t.me/hatedfame')
        