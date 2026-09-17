# Aircraft .dat Format Notes

Reverse-engineering log for a flyable aircraft's `.dat` (`DatAircraft` / `ACZ_AIRCRAFT_DAT_ASSET_LIST` in [asset_classes.py](asset_classes.py)), written up from exporting and hex-analyzing two real sample aircraft this session: **Gripen C (STANDARD)** and **J35J Draken (STANDARD)**. Everything below is either directly confirmed by comparing the two samples, or explicitly marked as an open question - nothing here is guessed at silently.

## Prior art

[krishty/acanalysis](https://github.com/krishty/acanalysis) (a fork of the original [ArthurRichard/acanalysis](https://github.com/ArthurRichard/acanalysis)) is a predecessor tool for Ace Combat 4/5/Zero with partial 3D visualization/export. Its `AC4Analysis/SM.cs` parses AC4's `.SM` model format and confirms a **64-byte per-part record**: 4-float position, 4-float rotation (quaternion), keyframe/mesh offsets, and a **component type ID** with named ranges - `50-55` weapon pylons, `58-63` special racks, `40-45` landing gear, `0` body/root. Its `BIN_Analysis.xls` documents one real `.SM` file's byte layout: a `root_part`/`sub_part.list` header and 25+ recursively-nested parts spanning ~320KB.

ACZ's format is **related but not byte-identical**: different magic (`P3Dp` vs `SM`), and (per the findings below) the hardpoint/attachment table and the mesh geometry are split into two separate files rather than one monolithic hierarchy. `SM.cs`'s part-type-ID scheme is the best available lead on what the numeric "group"/"ID" fields inside ACZ's `P3D` records might mean, but isn't confirmed to apply directly.

## Confirmed signatures

| Format | Signature (hex) | ASCII | Notes |
|---|---|---|---|
| `GIM` | `47 49 4D 00` | `GIM\0` | Texture (already known, confirmed by the real decoder in `visualizers/gim_image.py`) |
| `P3D` | `50 33 44 70` | `P3Dp` | Hardpoint/attachment table (this session) - **not** the 3-byte guess used previously |
| `ACM` | `41 43 4D 00` | `ACM\0` | Mesh chunk (this session) - **not** the 3-byte guess used previously; confirmed general-purpose (stage props *and* aircraft parts) |
| `AHM` | `41 48 4D 00` | `AHM\0` | New, previously unseen - purpose unconfirmed |

## Slot `01`: the part-geometry container

Slot `1` of an aircraft's `.dat` is a plain **NOF-based container** - byte-for-byte the same shape as `DatFile`'s own header (`u32` count, then that many `u32` offsets). Confirmed `count = 10` in both sample aircraft, and the **type sequence at each index is identical** between them:

| Index | Type | Gripen size | Draken size |
|---|---|---|---|
| 0 | `ACM` | 222,832 | 196,304 |
| 1 | `ACM` | 41,376 | 34,288 |
| 2 | `ACM` | 211,392 | 271,056 |
| 3 | `ACM` | 81,504 | 26,528 |
| 4 | **`AHM`** | 14,528 | 9,264 |
| 5 | `ACM` | 2,704 | 2,432 |
| 6 | `ACM` | 8,192 | 8,064 |
| 7 | `ACM` | 11,216 | 22,096 |
| 8 | `GIM` - **main aircraft texture** | 263,216 | 263,216 |
| 9 | `GIM` - **cockpit texture** | 17,456 | 17,456 |

Slots 8/9 confirmed by visually inspecting the decoded textures in this tool's own Image visualizer, not just by signature. Entries 8 and 9 being **exactly the same byte size in both aircraft** turned out to be a coincidence of both aircraft sharing the same fixed texture resolution/format for these slots, not shared content - slot 8 is confirmed to be the actual per-aircraft livery texture, despite the size match.

This container is modeled as the new `DatAircraftParts(DatFile)` class, with its own `ACZ_AIRCRAFT_PARTS_ASSET_LIST` sub-table (slots 0-7 still positionally named - which aircraft part each `ACM` mesh is isn't confirmed yet).

## Slot `03`: the `P3D` hardpoint table

1,056 bytes in both sample aircraft (a fixed size, unlike slot `01`). Structure:

**Header** (offsets from file start):
| Offset | Field | Notes |
|---|---|---|
| `0x00` | Signature | `50 33 44 70` = `"P3Dp"` |
| `0x06` | `u16` | 23 (Gripen) / 22 (Draken) - purpose unconfirmed, maybe a node/part count |
| `0x0A` | `u16` | 1056 in both - this `P3D` file's own total size |
| `0x0C` | `u32` | **150,160 (Gripen) / 136,656 (Draken) - exactly matches slot `04`'s byte size** in both aircraft. Slot `04` itself has no magic/self-describing header (starts all-zero), so this is very likely how a loader knows its length. |
| `0x10`-`0x32F` | 10 x 80-byte records | see below |
| `0x330`-`0x420` | trailing float block | **byte-identical between the two different aircraft** - rules out this being per-aircraft geometry; more likely shared default constants (e.g. a generic collision proxy or LOD thresholds) |

**Per-record layout** (80 bytes, relative offsets `0x00`-`0x4F`):
| Rel. offset | Field | Notes |
|---|---|---|
| `0x00` | `u16` index | 0-9, matches position |
| `0x02` | `u16` = 5 | constant |
| `0x04`-`0x0F` | 12-byte constant | `7F 64 00 01 FF FF 00 00 00 00 00 00`, identical across every record of both files |
| `0x10` | `u16` "group" tag | `0x011D` for records 0-2, `0x0119` for records 3-9 - a clean **3-vs-7 split**, plausibly matching ACZ's 3 special-weapon slots vs. 7 standard hardpoints |
| `0x12`-`0x17` | 6-byte constant | `7F 00 00 00 00 00` |
| `0x18` | `u16` ID field | one of `0x0555` / `0x0759` / `0x02AA` - a small repeating set, plausibly an attachment-point name/bone hash |
| `0x1A` | `s16` | varies per record, sometimes per aircraft |
| `0x1C` | `u16` = 0 | constant |
| `0x1E` | `u16` | varies per record; mostly (not always) identical between aircraft for the same record index |
| `0x20`-`0x23` | two `u16` | not floats (reads as IEEE-754 denormals near zero if misinterpreted as a float) |
| `0x24`-`0x2B` | 8-byte zero | constant |
| `0x2C` | `float` = 1.0 | |
| `0x30` | 4-byte constant | `FF 2E CC 5F` - identical in **every** record of **both** files; almost certainly a sentinel/marker, not measured data |
| `0x34` | `u32` = 0 | constant |
| `0x38` | `u16` | **confirmed per-aircraft varying** (direct byte diff between the two files) - the strongest candidate for an actual coordinate |
| `0x3A` | `u16` = 0 | constant |
| `0x3C` | `u16` | varies |
| `0x3E` | `u16` | varies |
| `0x40` | `float` = 1.0 | |
| `0x44` | `float` = 1.0 | |
| `0x48`-`0x4F` | 8-byte zero | constant |

Three `1.0f` constants per record (at `0x2C`, `0x40`, `0x44`) read like a 3-axis identity scale vector, alongside a mostly-constant transform and a couple of genuinely varying fields - consistent with each record being a named 3D locator/attachment point rather than raw mesh data.

## `DatAircraft` slot table (`ACZ_AIRCRAFT_DAT_ASSET_LIST`)

| Slot | Type | Notes |
|---|---|---|
| 0 | *(unresolved)* | 400 bytes, byte-identical between aircraft |
| 1 | `aircraft_parts_dat` (`DatAircraftParts`) | see above |
| 2 | *(unresolved)* | 160 bytes, byte-identical between aircraft |
| 3 | `p3d` (`P3D`) | see above |
| 4 | *(unresolved)* | size cross-referenced by slot 3's header; all-zero first bytes, no magic |
| 5 | *(unresolved)* | 6,112 bytes, byte-identical between aircraft |
| 6 | *(unresolved)* | 80 bytes; contains float-looking values (756.0, 1600.0) - possibly hangar display/pricing data |
| 7 | *(unresolved)* | 48 bytes, byte-identical between aircraft |
| 8 | *(unresolved)* | 32 bytes, byte-identical between aircraft |
| 9 | *(unresolved)* | 96 bytes, byte-identical between aircraft |
| 10 | *(unresolved)* | 96 bytes, byte-identical between aircraft, same shape as slot 9 |
| 11 | *(unresolved)* | 43,376 / 36,080 bytes - varies per aircraft; first 4 bytes look plausibly like a NOF-style count, **unconfirmed** |
| 12 | *(unresolved)* | 49,376 / 52,240 bytes - varies; same "maybe a container" caveat as slot 11, **unconfirmed** |
| 13 | `gim` (`GIM`) | 3,376 bytes, byte-identical in size between aircraft - confirmed by the user: the aircraft silhouette icon shown at the screen's lower-right corner |
| 14 | *(unresolved)* | 16 bytes, byte-identical between aircraft |
| 15 | *(unresolved)* | 8,496 bytes, byte-identical between aircraft; same "maybe a container" caveat as 11/12 |
| 16 | `gim` (`GIM`), name "Special weapon icons" | 34,032 / 34,720 bytes - varies slightly per aircraft. Confirmed via the tool's Image visualizer: depicts the 3 special-weapon icons shown in the weapon-selection menu, plus 3 more underneath showing each weapon's dynamic/type (e.g. semi-active, unguided bomb, rocket, for this aircraft) - independent confirmation of the "3 special weapons" split already suspected from `P3D`'s 3-vs-7 record grouping above |

Registered only for `DatAircraft`, not `DatAircraftHangar` - the hangar-quality variant's internal layout hasn't been checked and may differ.

## Open questions

- What `AHM` actually is (mesh variant? animation? cockpit-specific?) and its internal structure.
- Whether slots `11`, `12`, `15` are really NOF-style sub-containers, and if so what they hold.
- What the `P3D` header's `0x06` field and each record's `0x18`/`0x1A`/`0x1E`/`0x38`/`0x3C`/`0x3E` fields precisely encode (which axis is which, what unit).
- What the `FF 2E CC 5F` per-record sentinel means.
- Whether `DatAircraftHangar` shares this same slot layout.
