from pywinauto.application import Application
import pyautogui as gui
from pynput.keyboard import Key, Controller
from PIL import Image
import os
import glob
import time

main_path = os.path.dirname(os.path.realpath(__file__))
keyboard = Controller()
btn_a = 'z'
btn_b = 'x'
btn_start = 'enter'
btn_select = 'backspace'

def click_then_open(child, name):
    child.window(title=name, found_index=0).click_input()
    child.window(title=name, control_type="ListItem", found_index=0).type_keys('{ENTER}')

def keypress(key):
    gui.keyDown(key)
    gui.keyUp(key)

def reset_emu():
    all_btns = [btn_b, btn_a, btn_start, btn_select]
    for btn in all_btns:
        gui.keyDown(btn)
    time.sleep(0.2)
    for btn in all_btns:
        gui.keyUp(btn)

def open_game(game_name, full_scheme=True):
    app = Application(backend="uia")
    app.start(f'{os.path.dirname(os.path.realpath(__file__))}/VisualBoyAdvance.exe')

    # this will open the game by searching through the given directory structure
    # listed below (under the NOTE). By default, this is not the chosen way to
    # open the game as it takes a while, so you MUST make sure to open the correct
    # ROM in VisualBoyAdvance BEFORE you run this script. Otherwise, it will attempt
    # to open whatever was the most recently opened ROM, which could be the wrong one
    if full_scheme:
        app.window().wait('visible')
        app.VisualBoyAdvance.menu_select('File->Open...')

        child = app.window().child_window(title='Select ROM')

        child.Desktop.click_input()
        child.window(title="Vertical", control_type="ScrollBar").wheel_mouse_input(wheel_dist=-100)

        # NOTE: these MUST be changed to match your file structure
        for name in ['Programming', 'shiny_hunter', f'{game_name}.gba']:
            click_then_open(child, name)
    
    elif not full_scheme:
        app.window().wait('visible')
        gui.keyDown('ctrl')
        gui.keyDown('f1')
        gui.keyUp('ctrl')
        gui.keyUp('f1')

    return app

def remove_screenshot():
    try:
        for file in glob.glob(f'{main_path}/*.png'):
            os.remove(file)
    except:
        return
    return

def capture_screenshot():
    keypress('f12')
    return

def check_shiny():
    # first take screen capture of game
    capture_screenshot()

    # then analyse screen capture to see if shiny
    png = glob.glob(f'{main_path}/*.png')
    try:
        img = Image.open(png[0])
    except:
        print('\nNot shiny')
        return False
    width, height = 240, 160
    rgb_vals = img.getdata()

    pixel_loc_and_rgb = []
    for i, val in enumerate(rgb_vals):
        x = i % width
        y = int(i/width)
        pixel_loc_and_rgb.append((x, y, val))

    # non_shiny_colour = (152, 208, 72)
    shiny_colour1 = (144, 200, 208)
    shiny_colour2 = (72, 160, 144)
    count1 = len([val for val in pixel_loc_and_rgb if val[-1] == shiny_colour1])
    count2 = len([val for val in pixel_loc_and_rgb if val[-1] == shiny_colour2])
   
    if count1 != 0 and count2 != 0:
        return True
    else:
        return False
        
def game_loop(reset_count):
    # check screenshot to see if at file select menu
    white_col = (248, 248, 248)
    blue_col = (136, 144, 248)

    while True:
        remove_screenshot()
        capture_screenshot()
        try:
            png = glob.glob(f'{main_path}/*.png')
            img = Image.open(png[0])
            rgb_vals = list(img.getdata())

            if white_col in rgb_vals and blue_col in rgb_vals:
                remove_screenshot()
                break
            else:
                keypress(btn_a)
                time.sleep(0.8)

        except IndexError:
            print('Error')
            return False, reset_count

    # interact with bag in overworld
    keypress(btn_a)
    time.sleep(1)
    keypress(btn_a)

    # press left to hover over treecko
    time.sleep(0.5)
    keypress('c')

    # press a twice to select treecko
    for i in range(2):
        time.sleep(0.2)
        keypress(btn_a)

    # wait for wild pokemon message, then press a
    time.sleep(7)
    keypress(btn_a)

    time.sleep(2.5)

    # check if treecko is shiny or not
    shiny = check_shiny()

    if not shiny:
        print('Not shiny')
        reset_count += 1

    else:
        print('Shiny found!')
        reset_count += 1

    return shiny, reset_count

if __name__ == "__main__":
    shiny = False
    reset_count = 0
    game_name = 'ruby'
    remove_screenshot()
    while not shiny:
        app = open_game(game_name, full_scheme=False)

        shiny, reset_count = game_loop(reset_count)

        with open(f'{main_path}/counter.txt', 'r') as f:
            lines = f.readlines()

        total_count = int(lines[0])  

        print(f'Total reset count = {total_count}')
        print(f'Current run reset count = {reset_count}\n')

        total_count += 1

        f.close()

        with open(f'{main_path}/counter.txt', 'w') as f:
            f.write(f'{total_count}')

        if shiny:
            break

        app.kill()
