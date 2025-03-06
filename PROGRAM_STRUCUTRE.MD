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
        - @ ASSETLIST
    - ...






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
    1. 

