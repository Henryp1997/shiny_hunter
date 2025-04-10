"""
Automated Shiny Hunter for Pokémon Gen 3 using VisualBoyAdvance emulator

This script automates the process of soft resetting and shiny checking in Pokémon R/S
by simulating keypresses and analysing pixel RGB values in screenshots

Note: VisualBoyAdvance must be using the config file included in this repository (vba.ini)
"""

import os
import sys
import glob
import time
import pywinauto
import pyautogui as gui
from pynput.keyboard import Controller
from PIL import Image


class GameController():
    def __init__(self, target_pokemon, main_path):
        self.btn_a = "z"
        self.btn_b = "x"
        self.btn_left = "c"
        self.btn_right = "v"
        self.btn_start = "enter"
        self.btn_select = "backspace"
        self.btn_scrnshot = "f12"

        if target_pokemon not in ["Treecko", "Mudkip", "Torchic"]:
            sys.exit("Unrecognised starter Pokemon entered!")

        self.target_pokemon = target_pokemon
        self.main_path = main_path

        # Shiny colour dictionary. Use two colours per pokemon just to be sure
        self.shiny_colours = {
            "Treecko": [
                (144, 200, 208), # main teal on body
                (232, 184, 152)  # darker shade on chin
            ],
            "Mudkip": [
                (192, 112, 216), # back of head
                (248, 240, 192)  # lighter colour on tail
            ],
            "Torchic": [
                (248, 216, 112), # back of head (darker part)
                (248, 232, 168)  # back of head (lighter part)
            ]
        }

        # Other colour dictionary. This contains colours used to work out where
        # we currently are in the game. The fourth value in each tuple is the
        # colour's position in the flattened rgb values array
        self.other_colours = {
            "File select": [
                (80,   88, 144,    0),
                (248, 248, 248, 1454)
            ]
        }

        # Remove screenshots if any exist
        self.deleteAllScreenshots()


    def playGame(self):
        """ Run the game in the emulator and perform a single shiny check """
        # TODO: remove timers and use colours instead

        # Check if at file select screen in while loop. If False, something went wrong
        if not self.waitUntilFileSelectScreen():
            return False

        # Interact with bag in overworld
        self.__keypress(self.btn_a)
        time.sleep(1)
        self.__keypress(self.btn_a)

        time.sleep(0.5)
        self.selectStarter()

        # Wait for wild pokemon message, then press a
        time.sleep(6)
        self.__keypress(self.btn_a)

        time.sleep(2)       

        return self.checkColoursMatch(self.shiny_colours[self.target_pokemon])


    ### Screenshot methods
    def captureScreenshot(self):
        self.__keypress(self.btn_scrnshot)


    def deleteAllScreenshots(self):
        for file in self.getLatestScreenshot(get_all=True):
            os.remove(file)

    
    def getLatestScreenshot(self, get_all=False):
        pngs = glob.glob(f"{self.main_path}/*ruby*.png")
        if get_all:
            return pngs
        return pngs[0] # Just return the first one found
    

    def takeShinyScreenshot(self):
        self.deleteAllScreenshots()
        self.captureScreenshot()
        png = self.getLatestScreenshot()
        os.rename(png, f"{png.strip(os.path.basename(png))}SHINYFOUND.png")


    ### Colour checking methods
    def waitUntilFileSelectScreen(self):
        while True:
            blue, white = self.other_colours["File select"]
            blue_present = self.checkColoursMatch(blue, pixelpos=True)
            if blue_present == 1:
                white_present = self.checkColoursMatch(white, pixelpos=True, refresh_screenshot=False)
                if white_present == 1:
                    return True
                return False # This should realistically never be reached

            elif blue_present == 0:
                # Keep pressing 'a' until at file select screen
                self.__keypress(self.btn_a)
                time.sleep(0.15)

            elif blue_present == -1:
                # Errored in checkColoursMatch()
                return False
    

    def checkColoursMatch(self, colours, pixelpos=False, refresh_screenshot=True):
        try:
            if refresh_screenshot:
                self.deleteAllScreenshots()
                self.captureScreenshot()
            
            png = self.getLatestScreenshot()
            img = Image.open(png)
            screenshot_colours = list(img.getdata())

            if pixelpos:
                r, g, b, pos = colours
                if screenshot_colours[pos] != (r, g, b):
                    return 0
                return 1

            elif not pixelpos:
                # TODO: make all colours position based
                # For shiny checking
                if all(colour in screenshot_colours for colour in colours):
                    self.deleteAllScreenshots()
                    return 1
        except IndexError:
            print("Error")
            return -1
        return 0


    ### Bag Pokemon selection methods
    def selectStarter(self):
        method_name = f"_GameController__select{self.target_pokemon}"
        return getattr(self, method_name)()


    def __selectTreecko(self):
        return self.__performStarterSelection(btn=self.btn_left)


    def __selectMudkip(self):
        return self.__performStarterSelection(btn=self.btn_right)
    

    def __selectTorchic(self):
        return self.__performStarterSelection(btn=None)


    def __performStarterSelection(self, btn):
        if btn is not None:
            self.__keypress(btn)
        
        # Press a twice to select pokemon
        for i in range(2):
            time.sleep(0.2)
            self.__keypress(self.btn_a)

    
    ### App interaction methods
    def __keypress(self, key):
        gui.keyDown(key); gui.keyUp(key)


def game_loop(main_path):
    shiny = False
    reset_count = 0

    # Open global counter file whose counter remains the same each time this script is ran
    with open(f"{main_path}/reset_counter.txt", "r") as f:
        lines = f.readlines()
    total_count = int(lines[0])  

    try:
        while not shiny:
            print(f"Total reset count = {total_count}")
            print(f"Current run reset count = {reset_count}")

            # If full_scheme is True, this will open the game by searching through the given directory structure
            # i.e., the dir_structure variable. By default, full_scheme is False as full_scheme=True takes a while,
            # so to use full_scheme=False, you MUST make sure to open the correct ROM in VisualBoyAdvance BEFORE you
            # run this script. Otherwise, it will attempt to open whatever was the most recently opened ROM, which could be the wrong one
            app = open_game(game_name, dir_structure, main_path, full_scheme=False)

            # Need to sleep after opening so the first screenshot is not taken too early
            # TODO: investigate this, because it wasn't needed previously
            time.sleep(0.8)

            # reset_count is a temporary counter, i.e., it resets each time this script is run
            # this value is increment upon each pass through the game_loop function
            shiny = emu.playGame()
            if not shiny:
                print("Not shiny\n")
            else:
                print("Shiny found!\n")
                emu.takeShinyScreenshot()
                break

            total_count += 1; reset_count += 1

            with open(f"{main_path}/reset_counter.txt", "w") as f:
                f.write(f"{total_count}")

            app.kill()
    except KeyboardInterrupt:
        # Ensure the emulator is killed when stopping this program
        app.kill()


def click_then_open(child, name):
    child.window(title=name, found_index=0).click_input()
    child.window(title=name, control_type="ListItem", found_index=0).type_keys("{ENTER}")


def open_game(game_name, dir_structure, main_path, full_scheme=True):
    app = pywinauto.Application(backend="uia")
    app.start(f"{main_path}/VisualBoyAdvance.exe")

    if full_scheme:
        wait_until_VBA_open(app)

        # Open ROM
        app.VisualBoyAdvance.menu_select("File->Open...")
        child = app.window().child_window(title="Select ROM")
        child.Desktop.click_input()
        child.window(title="Vertical", control_type="ScrollBar").wheel_mouse_input(wheel_dist=-100)
        for name in dir_structure:
            click_then_open(child, name)
    
    elif not full_scheme:
        # CTRL + F1 emulates clicking File-->recent-->game.gba
        # Therefore, before running the first time (or if the
        # emulator has opened a different file recently), game.gba
        # must be opened
        wait_until_VBA_open(app)
        gui.keyDown("ctrl")
        gui.keyDown("f1")
        gui.keyUp("ctrl")
        gui.keyUp("f1")

    return app


def wait_until_VBA_open(app, timeout=10):
    """ Wait until VisualBoyAdvance window is detected. Exit program if timeout exceeded """
    try:
        app.window().wait("visible", timeout=timeout)
    except pywinauto.timings.TimeoutError:
        sys.exit("Timed out waiting for VisualBoyAdvance window to open")


if __name__ == "__main__":
    keyboard = Controller()
    game_name = "ruby"

    # NOTE: these MUST be changed to match your file structure
    # if using full_scheme=True in the open_game function
    dir_structure = ['Programming', 'shiny_hunter', f'{game_name}.gba']

    # Set up emulator object
    emu = GameController(target_pokemon="Mudkip", main_path=os.path.dirname(os.path.realpath(__file__)))

    # Main loop
    game_loop(main_path=os.path.dirname(os.path.realpath(__file__)))
