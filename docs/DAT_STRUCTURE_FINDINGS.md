# DAT Structure Findings - death_the_d0g's `.dat` Contents Document

Analysis of `acz_data_struc.md`, a detailed stage/aircraft/wingman/hangar `.dat` content breakdown supplied by death_the_d0g (already credited elsewhere in this project as a contributor - the GIM converter tool, the `ACZ_makepack_contents_SLUS21346.txt` slot listing, etc.). Compared against this session's own reverse-engineering and the current asset tables in `asset_classes.py`.

**Nothing here has been applied to code yet** - this is a findings/reference document. See `docs/OPEN_DISCREPANCIES.md` for the handful of points that actively conflict with what we'd already established, kept separate so they're easy to re-check later if we hit an inconsistency.

## Stage `.dat` (slots 0-38, `ACZ_STAGE_DAT_ASSET_LIST`)

Matches our existing table closely. Notable new information:

- **Slot `16`** ("Stage props 3D model data") **is a container**, not a single asset - holds one or more `.acm` prop models. Currently `type: ''` in our table (a single, unparsed asset).
- **Slot `17`** ("Stage props texture data") **is also a container**, holding the `.gim` textures for those props. Currently `type: ''`.
- **Slot `19`**'s 12 sub-textures (our `DatAmbientTextures` / `ACZ_AMBIENT_TEXTURES_ASSET_LIST`, currently just positionally named `'00'`-`'11'`) now have real names, in order:
  1. Sun texture 1
  2. Sun texture 2
  3. Sun texture 3
  4. Sun texture 4
  5. Moon texture
  6. Star texture
  7. Cloud map texture
  8. Background cloud texture
  9. Cloud texture
  10. Unknown texture
  11. Lens flare texture
  12. Unknown texture
- **Slot `38`** = "Null or air base stage DAT file" - matches our confirmed `DatStage.is_empty` finding exactly.

## Playable aircraft `.dat` (slots 0-16, `ACZ_AIRCRAFT_DAT_ASSET_LIST`)

| Slot | Our current name | d0g's name | Status |
|---|---|---|---|
| 0 | Unknown parameter block | Aircraft movement stat parameter file | New name, but see `OPEN_DISCREPANCIES.md` - we found this byte-identical between Gripen/Draken, which sits oddly with "movement stats" |
| 1 | Part geometry (`DatAircraftParts`) | Aircraft model and texture asset package | Confirmed; sub-slots below |
| 2 | Unknown parameter block | Camera coordinate placement file | New name, same identical-bytes tension as slot 0 |
| 3 | Hardpoint & special weapon attachment table (`P3D`) | "Possible audio playback parameter file, related to 0004" | **Contradicts our hardpoint hypothesis** - see `OPEN_DISCREPANCIES.md` |
| 4 | Raw data blob (size cross-referenced by slot 3) | Engine sound effect file | Fits neatly with d0g's slot-3 theory (P3D storing an audio sample's length) |
| 5 | Unknown parameter block | Unknown file | Still unresolved by both sources |
| 6 | Unknown parameter block (float values - hangar display data?) | Joint movement limit file | **Correction** - control-surface/gear travel limits fits the float values better than our guess |
| 7 | Unknown parameter block | Properties file 1 | New name |
| 8 | Unknown parameter block | Properties file 2 | New name |
| 9 | Unknown parameter block | GUN parameter file | New name - explains identical bytes across aircraft (shared gun) |
| 10 | Unknown parameter block | MISSILE parameter file | New name - same reasoning as slot 9 |
| 11 | Unknown data - possibly a small container | **Special Weapon (SpW) model/parameter package** - 3 sub-folders (0000/0001/0002, one per SpW option), each: `0000` LoD parameter file, `0001-0003.acm` LOD 0-2 models | **New, and directly confirmed by this session's own crash investigation** - `draken/11/0` (dug into deeply while diagnosing the DatFile crash) is exactly this shape: a 16-byte "LoD parameter file" (3 floats, our own guess was "LOD switch distances") + 3 ACM meshes of decreasing size. See `docs/AIRCRAFT_FORMAT_NOTES.md`. |
| 12 | Unknown data - possibly a small container | Low-poly aircraft package - LoD parameter file + 5 ACM LODs (0-4) + 5 GIM textures (incl. a 128x128 aircraft texture) | New, matches our "possibly a container" guess |
| 13 | Aircraft silhouette icon (lower-right corner) | Aircraft HUD texture file | Compatible - d0g's is a generic label, ours is the specific confirmed usage (from your own visual check via the Image visualizer) |
| 14 | Unknown tiny flag/version block | Unknown file | Still unresolved by both sources |
| 15 | Unknown data - possibly a small container | Missile/SpW HUD texture package - 8 entries: Missile HUD + 3x SpW HUD textures, each paired with an "unknown, related to file above" companion | New, confirms our "possibly a container" guess (8 entries in 8,496 bytes ≈ ~1,062 bytes/entry, plausible for small icons) |
| 16 | Special weapon selection icons (rearm/refuel weapon-selection screen): 3 selection icons + 3 weapon-dynamic-type icons | "SpW HUD texture (refueling mode)" | **Resolved - d0g was right.** Confirmed: these are the icons for the weapon-selection screen shown when rearming at a base ("refueling mode"). Was tracked as a discrepancy in `OPEN_DISCREPANCIES.md` until confirmed. |

### Aircraft model package (slot 1 / `DatAircraftParts`, `ACZ_AIRCRAFT_PARTS_ASSET_LIST`)

| Slot | Our current name | d0g's name |
|---|---|---|
| 0 | `00` (positional) | Airframe model |
| 1 | `01` (positional) | Landing gear model |
| 2 | `02` (positional) | Cockpit model |
| 3 | `03` (positional) | Cockpit model (back view) |
| 4 | `04` (`AHM`, purpose unknown all session) | **Related to the aircraft's dynamic shadow** |
| 5 | `05` (positional - the one sample with zero real sub-nodes) | Unknown model file - still unidentified even by d0g |
| 6 | `06` (positional) | Low-poly model version of the aircraft |
| 7 | `07` (positional) | Fuel tank model |
| 8 | Main aircraft texture | Aircraft texture file (512x512) - confirms resolution |
| 9 | Cockpit texture | Cockpit texture file |

## Wingman aircraft (gameplay) `.dat` (slots 714/715)

Matches what we already knew from the wingman mod-pack tutorial studied earlier this session (the `0714.dat`/`0715.dat`/`0941.dat`/`0946.dat` rename scheme). Adds: the nested model package includes 5 ACM LODs + textures at confirmed 256x256 and 128x128 resolutions, plus a separate landing gear ACM at its own slot.

## Hangar aircraft `.dat`

**Answers an open question flagged in `docs/AIRCRAFT_FORMAT_NOTES.md`** ("whether `DatAircraftHangar` shares this same slot layout") - **it does not**. A hangar aircraft's package is much simpler than the flight model: just one container holding a small mesh/texture package. No P3D, no gun/missile parameters, no separate SpW package - hangar display doesn't need any of that.

**Independently confirmed via CLI casting** (see `docs/ACM_FORMAT_NOTES.md`'s "Hangar aircraft mesh packages" section) - the real shape is 10 children: 3-4 ACM meshes, 2-3 sixteen-byte placeholder slots, 3 GIM textures, and a trailing small `Asset` that looks like inert debug-heap padding (`0xCC` fill bytes) rather than real data. This is close to but not exactly d0g's original description ("2 ACM LODs, a landing gear model, a fuel tank ACM" = 4 meshes) - Draken's own package does have 4 real ACM meshes including a fuel tank sized identically to its flight-model fuel tank, but the MPBM/TLS unique-aircraft packages (see below) only have 3, lacking a fuel tank mesh entirely.

## Not covered here

Anything from d0g's doc that matched our tables closely enough not to need a note (most of the stage `.dat` slots 0-15, 18, 20-37) is left as-is - this document only calls out what's genuinely new, corrected, or in tension with prior findings.
