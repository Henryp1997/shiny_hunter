from pywinauto.application import Application
import pyautogui as gui
from pynput.keyboard import Controller
from PIL import Image
import os
import glob
import time


class gen3Emu():
    def __init__(self, target_pokemon):
        self.btn_a = "z"
        self.btn_b = "x"
        self.btn_left = "c"
        self.btn_right = "v"
        self.btn_start = "enter"
        self.btn_select = "backspace"
        self.btn_scrnshot = "f12"
        self.target_pokemon = target_pokemon

    def keypress(self, key):
        gui.keyDown(key); gui.keyUp(key)

    def capture_screenshot(self):
        self.keypress(self.btn_scrnshot)

    def check_at_file_select_screen(self):
        while True:
            at_file_select = self.check_colours_match(other_colours["File select"])
            if at_file_select == 1:
                # Success
                return True
            elif at_file_select == 0:
                # Keep pressing 'a' until at file select screen
                self.keypress(self.btn_a)
                time.sleep(0.2)
            elif at_file_select == -1:
                # Errored in check_colours_match()
                return False
    
    def select_starter(self):
        method_name = f"_gen3Emu__select_{self.target_pokemon}"
        return getattr(self, method_name)()

    def __select_treecko(self):
        return self.__perform_starter_selection(btn=self.btn_left)
        
    def __select_mudkip(self):
        return self.__perform_starter_selection(btn=self.btn_right)
    
    def __select_torchic(self):
        return self.__perform_starter_selection(btn=None)

    def __perform_starter_selection(self, btn):
        if btn is not None:
            self.keypress(btn)
        
        # Press a twice to select pokemon
        for i in range(2):
            time.sleep(0.2)
            self.keypress(self.btn_a)

    def check_colours_match(self, colours):
        remove_screenshots()
        self.capture_screenshot()
        try:
            png = glob.glob(f"{main_path}/*ruby*.png")
            img = Image.open(png[0])
            screenshot_colours = list(img.getdata())

            checking_colour_positions = len(colours[0]) == 4
            if checking_colour_positions:
                # For general colour checking to check progress in the game
                if all(colour[:-1] in screenshot_colours for colour in colours):
                    remove_screenshots()
                    return 1
            elif not checking_colour_positions:
                # For shiny checking
                if all(colour in screenshot_colours for colour in colours):
                    remove_screenshots()
                    return 1

        except IndexError:
            print("Error")
            return -1
        return 0


def game_loop():
    shiny = False
    reset_count = 0
    while not shiny:
        # If full_scheme is True, this will open the game by searching through the given directory structure
        # i.e., the dir_structure variable. By default, full_scheme is False as full_scheme=True takes a while,
        # so to use full_scheme=False,you MUST make sure to open the correct ROM in VisualBoyAdvance BEFORE you
        # run this script. Otherwise, it will attempt to open whatever was the most recently opened ROM, which could be the wrong one
        app = open_game(game_name, dir_structure, full_scheme=False)

        # Need to sleep after opening so the first screenshot is not taken too early
        # TODO: investigate this, because it wasn't needed previously
        time.sleep(0.8)

        # reset_count is a temporary counter, i.e., it resets each time this script is run
        # this value is increment upon each pass through the game_loop function
        shiny, reset_count = play_game(emu, reset_count)

        # Open global counter file whose counter remains the same each time this script is ran
        with open(f"{main_path}/counter.txt", "r") as f:
            lines = f.readlines()
        total_count = int(lines[0])  

        print(f"Total reset count = {total_count}")
        print(f"Current run reset count = {reset_count}\n")

        total_count += 1

        f.close()

        with open(f"{main_path}/counter.txt", "w") as f:
            f.write(f"{total_count}")

        if shiny:
            break

        app.kill()


def play_game(emu, reset_count):
    # TODO: remove timers and use colours instead

    # Check if at file select screen. If False, something went wrong
    if not emu.check_at_file_select_screen():
        return False, reset_count

    # Interact with bag in overworld
    emu.keypress(emu.btn_a)
    time.sleep(1)
    emu.keypress(emu.btn_a)

    time.sleep(0.5)
    emu.select_starter()

    # Wait for wild pokemon message, then press a
    time.sleep(6)
    emu.keypress(emu.btn_a)

    time.sleep(2)

    # Check if pokemon is shiny or not
    shiny = emu.check_colours_match(shiny_colours[emu.target_pokemon])
    if not shiny:
        print("Not shiny")
        reset_count += 1

    else:
        print("Shiny found!")
        reset_count += 1

    return shiny, reset_count


def click_then_open(child, name):
    child.window(title=name, found_index=0).click_input()
    child.window(title=name, control_type="ListItem", found_index=0).type_keys("{ENTER}")


def open_game(game_name, dir_structure, full_scheme=True):
    app = Application(backend="uia")
    app.start(f"{main_path}/VisualBoyAdvance.exe")

    if full_scheme:
        app.window().wait("visible")
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
        app.window().wait("visible")
        gui.keyDown("ctrl")
        gui.keyDown("f1")
        gui.keyUp("ctrl")
        gui.keyUp("f1")

    return app


def remove_screenshots():
    for file in glob.glob(f"{main_path}/*ruby*.png"):
        os.remove(file)


if __name__ == "__main__":
    main_path = os.path.dirname(os.path.realpath(__file__))
    keyboard = Controller()
    game_name = "ruby"

    # NOTE: these MUST be changed to match your file structure
    # if using full_scheme=True in the open_game function
    dir_structure = ['Programming', 'shiny_hunter', f'{game_name}.gba']

    # Shiny colour dictionary. Use two colours per pokemon just to be sure
    shiny_colours = {
        "treecko": [
            (144, 200, 208), # main teal on body
            (232, 184, 152)  # darker shade on chin
        ],
        "mudkip": [
            (192, 112, 216), # back of head
            (248, 240, 192)  # lighter colour on tail
        ],
        "torchic": [
            (248, 216, 112), # back of head (darker part)
            (248, 232, 168)  # back of head (lighter part)
        ]
    }

    # Other colour dictionary. This contains colours used to work out where
    # we currently are in the game. The fourth value in each tuple is the
    # colour's position in the flattened rgb values array
    other_colours = {
        "File select": [
            (248, 248, 248, 1000),
            (80, 88, 144, -1)
        ]
    }

    # Remove screenshots if any exist
    remove_screenshots()

    # Set up emulator object
    emu = gen3Emu(target_pokemon="mudkip")

    # Main loop
    game_loop()
