# GAME PROFILE FILE STRUCTURE:

The Game Profile holds information about the game's internal structure and its files.
It does that through file presets, which determine how each file can be opened and interacted with. In the case of container files, it also documents its internal structure, the files stored inside it.


As planned, each preset file will hold data for the files inside the game file it is assigned to.

Data:
- Opening method
- Internal file structure (Only for packages and folders)




- LEGEND:

    - "**-**" - When prefixed with "-", the item is a folder. Otherwise, it is a file

## STRUCTURE FOR ACE COMBAT ZERO

TODO: Consider unpacking the .iso as well.

- -BIN
    - DATA.PAC
        - 0000-5115.dat
            - (Each .dat has a different structure. need a preset for each type.)
    - DATA.TBL
- -IRX
    - PS2 libraries (irrelevant for now)
- -SMV
    - BRIEF.PAC
    - MOVIEUS.PAC
- -STREAM
    - BGM.PAC
    - RADIOUSA.PAC
- ioprp300.img
- SLUS_213.46
- SYSTEM.CNF


