# PROGRAM STRUCTURE

Listing all necessary files and directories necessary for normal functionality

- LEGEND:

    - "**-**" - When prefixed with "-", the item is a folder. Otherwise, it is a file
    
    - "**INDENTATION**"
        - When there are items indented under a folder:
            - They are the folder's children
        - When the items are indented under a file:
            - "**@**" - When prefixed with "**@**", the item is data. It must be a file's child
            - When not prefixed, the item is a file, and the parent file is a container

## GENERAL STRUCTURE:
- -PROJECTS
    - -EXAMPLE_PROJECT
    - ...
- -GAME_PROFILES
    - EXAMPLE_PROFILE
    - ...
- -MODULES
    - -EXAMPLE_MODULE


## PROJECT
Holds the needed files for a modding session that can be saved and resumed.
Contains original, read-only input game files for that session.
Records changes made to the original files in a differential manner (records only alterations)

### FILE STRUCTURE:
- -PROJECT NAME
    1. METADATA
        - @ GAME
            - AC5
            - ACZ
            - ...
        - @ REGION - (reference: https://consolemods.org/wiki/PS2:Region_Information)
            - NORTH AMERICA
            - JAPAN
            - PAL
            - ...
    1. -ORIGINAL FILES:
        - e.g.: DATA.PAC (depends on the game)



## GAME PROFILE
A profile for each game or version. Holds data on a certain game's data structure.
It is responsible for defining what files are present in the game and what modules can interac with them.

### STRUCTURE
1. File tree
    1. All files present in the game
1. Presets
    - Defines presets for file manipulation. They define standard behavior for each file types and handle exceptional cases as well.
    - A preset for each file. Each preset only defines behavior for the file it is attached to.
    - Preset data:
        1. Child files and their metadata:
            1. Preset
            1. Label


## MODULES
Essentially the backend. Each module deals with one functionality, and shall be grouped together based on file type and game.
For modularity and allowing language-agnosticity, file handling modules shall be accessible by CLI and receive arguments.

As for tools that need integration with the GUI, like file visualizers, deeper integration is needed. In this case, they need to be invoked through the CLI (and open a window with the data to be visualized) when used on the terminal. When invoked through the GUI, it shall be called internally through Python as if it were a package, to allow for visual data to be tranferred internally without workarounds.


E.g.:
- -ACE_COMBAT
    - -AC5-Z (Both AC5 and ACZ have a very similar file structure, as the use the same engine. In this case, they'll be grouped together, and specific modules for each game will be defined separately)
        - -COMMON
            - -PAC
                - -PACKAGER
                    - PAC_unpack.py
                    - PAC_repack.py
            - -DAT
                - -PACKAGER
                    - DAT_unpack.py
                    - DAT_repack.py
            - -SOUNDTRACK(Choose better name later)
            - -PACKAGER
        - -AC5
            - ULZ
                - PACKAGER
                    - ULZ_unpack.py
                    - ULZ_unpack.py

        - -ACZ
