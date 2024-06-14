# shiny_hunter
Starter Pokemon shiny hunting automation for Pokemon gen 3 (currently Treecko only)

## Before using
- You must open the correct ROM file in the VisualBoyAdvance emulator before ever running this script! This is because we need to populate the top entry in the 'Open->Recent...' dropdown menu so that the program opens the right file. Otherwise, the file will not be found and the script will run in a loop indefinitely.
- Please ensure that the correct VisualBoyAdvance emulator .exe is being used - the one in this project directory. This references two config files: `vba-over.ini` and `vba.ini`, and the Python code expects certain keyboard controls based on these config files.

## To use
1. Copy a Pokemon Ruby file into this directory, and rename it `ruby.gba`. There is a `ruby.sav` file already in this directory which has been set up to place the player right before you open Professor Birch's bag and choose a Pokemon.
2. Run `shiny.py` and wait for the shiny to appear. You will not be able to use your PC at this time so it's best to run this overnight.

## Shiny Treecko found after 7282 resets
![shiny_treecko](https://user-images.githubusercontent.com/118852495/232248425-ba7a4f39-75f1-42c7-a32b-85764812cde3.png)
