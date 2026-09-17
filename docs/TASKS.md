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
        1. Central script "AC_Wizard.py" (3)
            - Fix path handling to a system-agnostic standard (os.path.join())
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
            1. `.ACM` mesh format: header (80 bytes) and node/part table (64-byte records) structure confirmed across trees/stage props/aircraft/SpW/low-poly-LOD/briefing samples - see `docs/ACM_FORMAT_NOTES.md`. A minimal 752-byte sample has been fully byte-accounted for, including a first look at the geometry section's internal packet structure (tagged sub-blocks, one of which lines up with 3 vertices' worth of floats) and the 32-byte footer (a bounding-volume descriptor). **Still blocking a visualizer:** this packet structure hasn't been confirmed against a larger, multi-node file, and most of the packet tags' payloads aren't decoded yet.
        1. Text
        1. Audio
            1. Study integrating MFAudio's GUI inside the Wizard's GUI




1. Repacking (write-back) - **not implemented yet**
    1. **Known format quirk to respect when this is built:** a `.dat`'s TOC has (at least) two different conventions for marking an empty/zero-length slot, and they are NOT interchangeable:
        - Top-level stage/mission dats (`DatStage`/`DatMission`, direct children of DATA.PAC): an empty slot's 4-byte offset is the literal `\x00\x00\x00\x00`.
        - The sub-level dat nested inside a stage's own slot 38 (a `DatStage` reused recursively via `ACZ_STAGE_DAT_ASSET_LIST`, e.g. Glacial Skies' landing-stage data): an empty slot instead repeats the *same offset as the following slot* (never a literal 0). Confirmed while fixing the slot-38 header-visualizer bug (raw offset showed as "same as the next file", size 0, and the slot got unpacked as a real 0-byte child before the fix) - see `DatFile.init_offset_table()`'s `zero_offset_list` comment and `git log` around that fix for the full story.
        - Current code detects "empty" uniformly by computed size (`sizes_list[i] == 0`), which handles reading both conventions correctly - but a repacker has to go the other way (decide which convention to *write*), so this can't be papered over the same way. Get this wrong and the game likely won't load the rebuilt file.
        - Open question, not yet decided: whether this nested/substage TOC convention is common to all `DatStage` instances found inside another `DatStage` (i.e. a property of *nesting depth*), or specific to this null/landing-stage slot 38 case - needs more real samples to confirm before repacking is attempted.
    1. **Open design question:** should this nested-dat convention become its own type (e.g. a `DatSubStage`/`DatSubLevel` class, distinct from `DatStage`) rather than reusing `DatStage` as-is? Leaning toward treating it as a distinct on-disk variant of the `.dat` format (different empty-slot encoding = different format, not just a different table), which would also give repacking a natural place to special-case the write-side logic per class. Not decided/implemented - revisit once more nested-dat samples are found.

1. Safety guards
    1. **`DatFile.init_offset_table()` sanity checks (implemented):** a `.dat`'s header (NOF + offset entries) is now checked two ways before being trusted, both raising `DatHeaderError`:
        - Right after reading NOF: does `4 + NOF*4` even fit inside this asset's own declared size? If not, fail immediately instead of looping NOF times (this is what real memory-explosion crashes turned out to be - a misread NOF followed by mostly zero/small bytes still passes a per-entry check, but the loop itself is the cost).
        - Per entry, while reading: does this specific offset point past the asset's own size? Catches a bogus entry even when NOF itself is small enough to look plausible.
        - Both use only the asset's own real, already-known size - no arbitrary constant (a fixed max-entry-count cap was considered and explicitly rejected: it would either let a small-but-still-garbage NOF through, or reject a genuinely large real `.dat`, depending on where the number is set).
        - **Distinct from the earlier-rejected idea of a general "is this really a valid .dat" plausibility check** - that's still not implemented, and for the same reason as before (an in-bounds NOF/offsets can still describe the wrong data, unprovable from bytes alone). What's implemented here only ever rejects headers that are *impossible* (physically can't fit), never ones that are merely *unlikely*.
        - `Container.generate_children()`'s table-driven dispatch catches `DatHeaderError` and falls back to leaving the slot as a generic `Asset` (with a console warning) instead of letting one bad table entry crash the whole project load. The GUI's manual "Cast as" feature (see below) has its own separate try/except showing a dialog instead.

1. Documentation
    1. **README.md needs CLI usage instructions** - `cli.py` (invoked via `python gui_main.py --cli ...`) isn't documented anywhere yet: the `ls`/`hex`/`cast`/`export` commands, the `PATH` addressing scheme (slash-separated `children` dict indices, e.g. `3/19/9`), and the chainable `--cast PATH:TYPE` flag all need a real walkthrough with examples so it's usable without re-deriving it from `cli.py`'s own `--help` output.

1. Future AC5 analysis
    1. **Drop tanks are more common in AC5 than in ACZ.** In ACZ's own hangar-display packages (`hangar_display_dat`/`ACZ_HANGAR_PACKAGE_ASSET_LIST` slot `5`), only the J35J Draken among all 36 playable aircraft has a real fuel-tank mesh there - see `docs/ACM_FORMAT_NOTES.md`'s "Hangar-display mesh packages" section. The user's recollection is that AC5 features drop tanks on more aircraft. Worth re-checking this same slot/shape against AC5's own `DATA.PAC` once that game is analyzed, rather than assuming ACZ's "1 out of 36" rarity carries over.

1. Miscellaneous
    1. The icon for this program could really be Wizard Squadron's roundel lol
        