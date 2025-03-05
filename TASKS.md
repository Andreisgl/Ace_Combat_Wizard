# Tasks

## Housekeeping, initial set-up
1. Old code:
    1. Test and validate old code:
    1. Determine if:
        - (1) No changes are needed
        - (2) MVP is achieved, but later refinement is needed
        - (3) Refactor is needed
        - (4) Complete rewrite is needed
    1. **TARGETS:**
        1. Central script "AC_Wizard.py"
        1. Extraction modules
            1. PAC
            1. DAT
        



## Internal workings
1. Create Centralizer
    1. It receives commands from the User Interfaces
    1. And links the commands to their respective modules
    1. Returns info to interface of choice

1. User Interfaces
    1. Function
        1. Receives status and info from the Centralizer
        1. Prompts user for commands (context-dependent)
        1. Parses commands
        1. Sends commands to Centralizer
    1. Intended interfaces:
        1. Python Terminal
            1. Barebones UI
        1. GUI
            1. More intuitive. Integrates visualization and does what the Python Terminal does
        1. CLI args
            1. Intended for automated workflows and pipelines
                1. Future goal: Integrate with IML2ISO and CDVDGEN

1. Non-destructive file-handling
    1. Creates a read-only copy of unadultered game files, extracts and modifies on a separate location
    1. Allow for comparison between unadultered and modified files (maybe multiple sources?)

1. Asset Documentation - **DATA-DRIVEN FUNCTIONALITY**
    1. Holds a list of the file structure for each supported ISO
        1. Holds asset metadata. Important for context-dependent actions like:
            1. Defining which tools can interact with each file
            1. Important for exceptional cases, like out-of-spec or corrupted files
                - Like the text table of one ace style of the mission "Merlon" that contains an extra table, crashing the extraction script.
        1. Holds documentation and guidance
    1. **Modularity - IMPORTANT!**
        1. By making the decision process data-driven, this software can be easily expanded to handle other games in the franchise or even different games altogether, as long as the Python backend is developed and properly linked with the Asset Documentation

1. Asset Visualization
    1. Data types:
        1. Images
        1. 3D models
        1. Text
        1. Audio
            1. Study integrating MFAudio's GUI inside the Wizard's GUI




1. Miscellaneous
    1. The icon for this program could really be Wizard Squadron's roundel lol
        