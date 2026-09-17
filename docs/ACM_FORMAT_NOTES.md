# `.ACM` Mesh Format Notes

Reverse-engineering log for the `ACM\0`-signed mesh format, written up from sampling real files across every category this tool currently surfaces as `type: 'acm'` or `ACM[autodetected]`, via the CLI's `hex`/`ls` commands (no exports needed). Everything below is either directly confirmed by comparing multiple real samples, or explicitly marked as an open question.

## Prior art

See [AIRCRAFT_FORMAT_NOTES.md](AIRCRAFT_FORMAT_NOTES.md)'s "Prior art" section for the AC4 `SM.cs`/`BIN_Analysis.xls` background - `SM.cs` confirms AC4's related `.SM` format uses 64-byte per-part records (position, rotation, mesh/keyframe offsets, a component-type ID), which turns out to be a strong lead for `.ACM`'s own per-record layout (see below) even though the two formats are not byte-identical.

## Samples used this pass

At least three files per category, picked directly through the CLI against `testproj` (ACZ):

| Category | Samples |
|---|---|
| Stage trees | `43/28` (Valais AFB, tree 1), `3/28` (Glacial Skies, tree 1), `4/28` (Annex, tree 1) |
| Stage props | `43/16/0`, `43/16/4`, `43/16/6` (Valais AFB's stage-props container, `DatStageProps`) |
| Aircraft airframe (flight model, full LOD) | `503/1/0` (F-15C Eagle), `500/1/0` (Typhoon), `510/1/0` (F-117A Nighthawk) |
| Other slots of one aircraft's parts container | `503/1/{1,2,3,5,6,7}` (Draken/F-15C landing gear, cockpit x2, unknown, low-poly dup, fuel tank) |
| Special Weapon LOD model | `498/11/0/1` (Draken's SpW1, LOD 0) |
| Low-poly aircraft LOD | `498/12/2` (Draken's low-poly package, LOD 1) |
| Briefing "digitized terrain" | `1430`, `1431`, `1435`, `1440`, `1445` (M01/M02/M06/M11/M16) - see correction below; `1430/2/0`-`1430/2/4` (5 real ACM meshes, found only after manually casting slot `2` as a `.dat`) |

## Confirmed: terrain itself is not `.ACM`

Checked directly against `ACZ_STAGE_DAT_ASSET_LIST` slots 0-8 (the terrain mesh/texture-tile block) via hex dump - none of these carry the `ACM\0` signature or resemble the structure below. The engine's terrain is a tile-placement/heightmap system (slot 0 = tile placement map, slot 7 = texture tile data at ~4MB, etc.), completely separate from `.ACM`. The only stage-level use of `.ACM` is **vegetation** (`ACZ_STAGE_DAT_ASSET_LIST` slots 28-30, "Tree model file 1-3") and the stage-props container (slot 16). "Terrain" and "trees" are not the same category in this format, despite both being outdoor/environment geometry.

## Correction: briefing "digitized terrain" *does* contain `.ACM` files - hidden behind an uncast `.dat` wrapper

The previous pass through this document sampled 5 `DatBriefingTerrain` dats (missions 1, 2, 6, 11, 16) via plain `ls` and found only `GIM[autodetected]` textures and small unidentified `Asset`s among their 9 children - never `ACM[autodetected]` - and concluded briefings don't use `.ACM` at all. **That conclusion was wrong.** The user manually cast child `2` (9,376 bytes, previously just an unidentified `Asset`) as a `.dat` and found it's a real nested container with **8 children**: 5 `ACM[autodetected]` meshes (752 / 1,024 / 2,336 / 2,384 / 1,216 bytes) and 3 `GIM[autodetected]` textures (240 / 624 / 752 bytes). Autodetection never saw these because they only exist once the wrapper `.dat` itself is un-hidden by a manual cast - plain signature-sniffing on the *outer* `Asset` correctly found no `ACM\0`/`GIM\0` signature (the wrapper is a `.dat`, not a mesh), so this was never a bug, just a blind spot in how the previous pass sampled the category (`ls` only one level deep, never tried casting the unidentified slots).

Child `1` (368 bytes) and child `6` (size varies per mission) were also tried as `.dat` casts and correctly **rejected** by `DatHeaderError` (implausible NOF) - i.e. they are genuinely not containers, the safety check working as intended. Children `7`/`8` cast "successfully" but report 0 children (NOF reads as 0) - inconclusive on their own, most likely just non-container raw data that happens to start with zero bytes, not further pursued.

**Revised picture:** children `0`-`5` of a `DatBriefingTerrain` are byte-identical in size across all 5 missions checked (32,880 / 368 / 9,376 / 17,456 / 66,608 / 1,056 bytes) and child `2`'s nested package is very likely a **shared, generic** set of wireframe/UI pieces reused by every mission's briefing screen (e.g. a compass rose, distance rings, or map border - not the actual per-mission terrain). Children `6`-`8` genuinely vary in size per mission and are the more likely candidates for the actual per-mission "digitized terrain" payload; child `6` isn't a `.dat` container itself, so if it holds real mission-specific terrain geometry it's either raw `.ACM`-less vector data or something not yet identified. Not fully resolved - flagged in "Open questions" below.

## Header (80 bytes, confirmed structure)

All offsets are absolute, relative to the start of the `.ACM` asset's own data.

| Offset | Field | Notes |
|---|---|---|
| `0x00` | Signature | `41 43 4D 00` = `"ACM\0"` |
| `0x04` | `u32` = 5 | Constant across every sample checked (format version?) |
| `0x08` | `float` | Varies per file - candidate: bounding-sphere radius or similar per-mesh extent |
| `0x0C` | `float` | Varies per file, generally much smaller than `0x08`'s value - candidate: LOD switch distance or epsilon |
| `0x10` | `u32` | **Node/record count** - see formula below. Confirmed by cross-checking against `0x1C` on all 9 samples (2,272-byte trees through 206,048-byte aircraft) |
| `0x14` | `u32` = `0x50` (80) | Constant on every sample - **this file's own header size**, i.e. the node table starts at this absolute offset |
| `0x18` | `u32` | Varies; close to (often exactly) `node_count - 1` for small tables, but **not a fully confirmed formula** - diverges for large aircraft tables (see below) |
| `0x1C` | `u32` | **Confirmed formula: `0x1C = 0x14 + node_count(0x10) * 64`** - i.e. the absolute offset where the node table ends. Verified exactly on all 9 samples with wildly different sizes/categories - the most solid new finding this pass |
| `0x20`-`0x4F` | Several more `u32`/offset-looking fields | Not fully decoded - see "Open questions" |
| `0x4C` | `u32` | **Confirmed formula: `0x4C = file_size - 32`** on every single sample checked (trees, props, aircraft, SpW, low-poly LOD alike) - every `.ACM` file ends with a fixed 32-byte trailer/footer block, and the header stores a direct absolute pointer to it |
| `0x48` | `u32` = 1 | Constant on every sample - likely "count = 1" for whatever the `0x4C` footer chunk is |

## Node/part table (64-byte records, starts at absolute offset `0x50`)

`node_count` (header `0x10`) consecutive 64-byte records, immediately following the header - i.e. this is the same "80-byte header then N x 64-byte record table" shape independently found in `P3D` (see [AIRCRAFT_FORMAT_NOTES.md](AIRCRAFT_FORMAT_NOTES.md)), reused here for a structurally different purpose.

**Per-record layout** (64 bytes, relative offsets `0x00`-`0x3F`):

| Rel. offset | Field | Notes |
|---|---|---|
| `0x00` | `u32` "type tag" | Observed values: `0` (stage trees), `8` (stage props, SpW LOD models, low-poly aircraft LODs, and most slots of an aircraft's parts container), `9` (all 5 briefing-terrain meshes found in `1430/2`), `10` (only the airframe and fuel-tank slots of a full-detail flight aircraft, in the one aircraft checked in full - see "Open questions") |
| `0x04` | `u32` | Varies - matches `node_count - 1` in several samples, but not the large aircraft airframe tables (there it was a distinct, smaller number - possibly a sub-count unrelated to the table itself) |
| `0x08` | `u32` | In multi-record tables, increments `0, 1, 2, ...` starting from record 1 - looks like each record's own sequential index |
| `0x0C` | `u32` = 0 | Constant in every record checked |
| `0x10` | `u32` | Varies per record; in the airframe's articulated table this looked like it could reference a parent record's own index (`0x08` value), but not confirmed |
| `0x14`,`0x18`,`0x1C` | `u32` x3 | Usually `0xFFFFFFFF` sentinels (all three), matching the "sentinel marker, not measured data" pattern already seen in `P3D`'s per-record constants |
| `0x20`,`0x24`,`0x28` | `float` x3 | Position-vector-shaped. **Confirmed non-zero and genuinely varying only in the flight aircraft's own airframe table** (tag `10` records) - every other category checked (trees, stage props, SpW models, low-poly LODs) had these three floats at exactly `0.0` in every record beyond record 0, even when `node_count > 1` |
| `0x2C` | `float` = 1.0 | Constant in every record checked - same "homogeneous coordinate / uniform scale" role as `P3D`'s equivalent field |
| `0x30` | `float` | Constant *within* a single file's own table (e.g. always `≈0.52` across all of one F-15C's airframe records), but differs between files - candidate: a per-mesh shared constant (material index encoded as a float? unlikely; more likely a shared transform/scale term) |
| `0x34`,`0x38` | `float` x2 | Small, varying, sometimes near-zero/denormal-looking values |
| `0x3C` | `u32` = 0 | Constant in every record checked |

## Interpretation: the airframe's own table looks like a real part hierarchy

Dumping records 0-4 of `503/1/0` (F-15C airframe, `node_count = 62`) shows record 0 acting as a distinct "root" entry (all-zero position, no index), while records 1+ have genuinely different, non-zero `0x20`/`0x24`/`0x28` position floats and an incrementing `0x08` index - i.e. **not** a flat list of identical placeholders. This is consistent with `SM.cs`'s AC4 precedent of a `root_part` plus a recursively-nested `sub_part.list`, and with the earlier `P3D` hypothesis that a flight aircraft needs per-part attachment/pivot points for animated components (canopy, control surfaces, landing gear doors, etc. - compare death_the_d0g's "Joint movement limit file" name for aircraft slot `6`, see [DAT_STRUCTURE_FINDINGS.md](DAT_STRUCTURE_FINDINGS.md)).

By contrast, every stage-prop, SpW-model, and low-poly-LOD table checked has all-zero position data in every record past record 0, **even when `node_count > 1`** (e.g. an 11-node stage prop with every record's position at the origin) - these look like simple multi-chunk static meshes (perhaps per-material or per-texture-page submeshes) rather than an articulated hierarchy.

**Not yet explained:** within one aircraft's own parts container, the airframe (`503/1/0`) and fuel tank (`503/1/7`) both carry the `10` type tag, while landing gear (`1`), both cockpit views (`2`,`3`), an unidentified model (`5`), and the low-poly duplicate (`6`) all carry `8` - even though landing gear visibly animates in-game (retracts) and the fuel tank does not. Whatever the tag distinguishes, it is **not** simply "this mesh moves/articulates."

**Cross-checked against a second aircraft (`498`, J35J Draken) - the `0`/`7` = tag `10` split holds exactly.** Airframe (`498/1/0`) and fuel tank (`498/1/7`) both `10`; landing gear, both cockpit views, the unknown model, and the low-poly duplicate all `8`, identical to the F-15C. This resolves the "needs a second aircraft" question above - the split is a real, reproducible rule, just not yet an explained one.

**However, the exact sub-record byte layout is *not* identical between the two aircraft's airframe tables**, even though the overall shape (record 0 = root, records 1+ = real per-part data) and record 0's own tag (`10`) match. Comparing `503/1/0` records 1-3 against `498/1/0` records 1-3:

| Rel. offset | F-15C (`503`) records 1-3 | Draken (`498`) records 1-3 |
|---|---|---|
| `0x00` (type tag) | `10` (same as record 0) | `8` (differs from record 0's `10`) |
| `0x08` | Clean incrementing index (`1`, `2`, `3`, ...) | `0xFFFFFFFF` sentinel in every record checked |
| `0x10` | Small incrementing value (`1`, `5`, `7`, ...) | A packed value with a constant low half (`0x0067`) and a varying high half (`0x000C`, `0x000B`, `0x0002`, ...) |
| `0x18` | `0` | `0xFFFFFFFF` sentinel |

So the per-record field table above (the `0x08`/`0x10`/`0x18` rows) should be read as "confirmed shape, values and even which fields are indices vs. sentinels can differ per aircraft" rather than a fixed universal layout - only record 0's role as a tag-bearing root record generalizes cleanly so far.

**Leading hypothesis for what tag `10` actually means:** landing gear, cockpit, and the low-poly duplicate are always rigidly attached to the airframe and never separate from it in-game; the airframe itself obviously is its own independently-simulated rigid body; and a fuel tank *can* become one too - both AC5 and (per the user's recollection) ACZ let aircraft jettison external fuel tanks at some mission starts, at which point the tank stops following the airframe and becomes its own free-falling object. So tag `10` may mark **"mesh that can exist as its own independent rigid body,"** rather than tag `8`'s "always a fixed sub-mesh of the parent's own body." This reading is also consistent with the hangar-package difference below: Draken's hangar package has a real, tag-`10` fuel tank mesh (matching its flight model), while the MPBM/TLS packages have no fuel tank mesh at all but *do* have a second tag-`10` mesh at slot `2` where Draken has an ordinary tag-`8` one - plausibly some other separable/droppable component of whatever MPBM and the TLS weapon mount actually are. Still a hypothesis, not a certainty - `AHM` (aircraft slot `1`/`4`, "dynamic shadow data") would be a natural place to check next, since a jettisoned tank's shadow would need to detach too if this theory is right.

**New finding: mirrored left/right attachment points.** Draken's airframe records 1 and 3 share identical `0x24`/`0x28` position floats, with `0x20` negated between them (`+10.72` vs `-10.72`) - a textbook left/right symmetric pair (e.g. mirrored wingtip or pylon attachment points). This is independent, format-internal evidence for the same "hardpoint-like attachment table" reading already suspected for `P3D` (see [AIRCRAFT_FORMAT_NOTES.md](AIRCRAFT_FORMAT_NOTES.md)) - now also visible inside `.ACM`'s own node table, in a completely different file.

## Hangar-display mesh packages, and the MPBM/TLS assets

`asset_classes.py` carried three top-level `DATA.PAC` slots marked "named but structurally unverified" - `1160` (MPBM hangar assets), `1170`/`1171` (TLS unit hangar assets, ADFX-01/ADF-01). All three were untyped generic `Asset`s in the table. Casting each as a `.dat` (and then casting its own single child `0` as a `.dat` too) revealed they all follow the **same package shape**, and that this shape is also the real structure behind every `aircraft_hangar_dat` slot (e.g. `720`, J35J Draken's hangar package) - previously only seen as one unparsed 686,064-byte blob, never cast further until now.

**Important correction: `1170`/`1171` are not alternate renders of the ADFX-01/ADF-01 aircraft.** They're the hangar-display assets for the **TLS special weapon mount those two aircraft equip** - a separate piece of hardware, not the airframe itself. Since this shape is now confirmed on at least two genuinely non-aircraft subjects (MPBM, and the TLS weapon mount), the type/class previously named `aircraft_hangar_dat`/`DatAircraftHangar` has been renamed to **`hangar_display_dat`/`DatHangarDisplay`** - a name describing the on-screen behavior (a rotating 3D object shown on a hangar-style display) rather than presupposing the object is an aircraft. All ~250 real aircraft livery slots keep using this same type; nothing else changed for them.

| Child | `1160` (MPBM) | `1170` (TLS ADFX-01) | `1171` (TLS ADF-01) | `720/0` (Draken, standard flyable) |
|---|---|---|---|---|
| `0` | ACM, tag `10` | ACM, tag `10` | ACM, tag `10` | ACM, tag `10` |
| `1` | 16-byte placeholder | 16-byte placeholder | 16-byte placeholder | 16-byte placeholder |
| `2` | ACM, tag `10` | ACM, tag `10` | ACM, tag `10` | **ACM, tag `8`** |
| `3` | ACM, tag `8` | ACM, tag `8` | ACM, tag `8` | ACM, tag `8` |
| `4` | 16-byte placeholder | 16-byte placeholder | 16-byte placeholder | 16-byte placeholder |
| `5` | 16-byte placeholder | 16-byte placeholder | 16-byte placeholder | **ACM, tag `10`** (22,096 bytes - exactly matches Draken's own flight-model fuel tank, `498/1/7`) |
| `6`-`8` | GIM x3 | GIM x3 | GIM x3 | GIM x3 |
| `9` | `Asset`, 1,888 bytes | `Asset`, 1,808 bytes | `Asset`, 224 bytes | `Asset`, 240 bytes |

Two real differences between Draken's hangar package and the MPBM/TLS ones: (1) Draken's package has a genuine 4th ACM mesh at slot `5`, sized identically to its own flight-model fuel tank - consistent with death_the_d0g's doc description of a hangar package including "a fuel tank ACM" (see [DAT_STRUCTURE_FINDINGS.md](DAT_STRUCTURE_FINDINGS.md)) - while MPBM/TLS have only a placeholder there; (2) Draken's slot `2` is tag `8` while all three MPBM/TLS entries have tag `10` at slot `2`.

**Correction: slot `5`'s fuel tank is not a "standard aircraft" thing in general - Draken is the only one that has it, out of every playable aircraft checked.** After implementing this table in code, all 36 distinct STANDARD-tier flyable aircraft were checked (every aircraft in the roster - Gripen, Typhoon, Tornado GR4, F-4E, F-15C, F-16C, F-117A, F-35C, F-14D, Mirage 2000D, MiG-31, ADF-01, ADFX-01, and every other one), and **every single one except Draken (`720`) has only a 16-byte placeholder at slot `5`.** This fits real-world aircraft behavior well: the J35 Draken is well known for carrying an external centerline drop tank, unlike most of the others checked. The slot's real rule is most likely "present only for aircraft whose hangar loadout includes an external tank" - genuinely a one-off among the 36, not a category split of any kind.

**Slot `9` is very likely inert padding, not real data.** Its first 16 bytes are zero, immediately followed by a run of `0xCC` bytes - the exact same "trailing debug-heap padding" byte pattern already diagnosed and fixed for in the GIM decoder (`visualizers/gim_image.py`) earlier this session. Sizes differ per aircraft (240/1,808/224/1,888 bytes) but that's consistent with "how much leftover padding happened to get baked in," not necessarily meaningful per-aircraft content.

None of this has been applied to `asset_classes.py` yet - `1160`/`1170`/`1171` remain untyped and `DatAircraftHangar` remains a single-blob container in code. This section only documents what casting revealed; turning it into real typed classes (a `DatHangarAircraftPackage` sub-table, say) is a follow-up step if wanted.

## Geometry and footer structure - first full byte-accounting, from a minimal sample

`1430/2/0` (752 bytes, one of the briefing-terrain meshes above) is the smallest real `.ACM` sample analyzed so far (`node_count = 1`), small enough to account for **every single byte** rather than just the header/table. That full breakdown:

| Range | Size | Content |
|---|---|---|
| `0x000`-`0x04F` | 80 bytes | Header (as above) |
| `0x050`-`0x08F` | 64 bytes | Node table, 1 record, type tag `9` |
| `0x090`-`0x0A7` | 24 bytes | Geometry-section preamble: 16 zero bytes, then `22 00 00 60 00 00 00 00` |
| `0x0A8`-`0x2C7` | 544 bytes | **4 repeating 136-byte "geometry units"** (see below) |
| `0x2C8`-`0x2CF` | 8 bytes | Zero padding/terminator after the last unit |
| `0x2D0`-`0x2EF` | 32 bytes | Footer (see below) |

`80 + 64 + 24 + 544 + 8 + 32 = 752` - exactly the file's total size, with no leftover or gap.

**The footer (32 bytes, 8 floats) is a bounding-volume descriptor.** Its first float is bit-for-bit identical to the header's own `0x08` float, confirming that field really is some kind of per-mesh extent/radius value (previously only a guess). The 8 floats form two `(-x, +x)`-style symmetric pairs plus a few singles, consistent with an axis-aligned bounding box (or a box-plus-radius) rather than random data - exact per-slot meaning (which float is which axis) not pinned down.

**Each 136-byte "geometry unit" is itself structured, not raw vertex soup:**
- An 8-byte unit header (constant across all 4 units in this sample: `05 01 00 01 00 80 01 64`).
- An 8-byte count pair: in this sample, `(3, 1)` - the `3` matches exactly what follows (see next point), strongly suggesting this is a real vertex/element count field, not coincidence.
- **4 sequential sub-packets**, each starting with a 4-byte marker: a running counter (`01`,`02`,`03`,`04`), then a near-constant 2-byte tag (`80 03` for the first three, `c0 03` for the third), then a distinguishing type byte (`0x68`, `0x69`, `0x6e`, `0x64` respectively).
  - Sub-packet 1 (tag `0x68`): 36-byte payload = 9 `float`s. With the unit's own count field reading `3`, `9 = 3 × 3` lines up exactly with **3 vertices' worth of XYZ coordinates** - the strongest lead yet for where actual mesh geometry lives in the format.
  - Sub-packets 2-4 (tags `0x69`, `0x6e`, `0x64`): shorter payloads (20, 20, 24 bytes) that do **not** decode cleanly as IEEE floats (values like `0x04fa0000` sit in denormal/near-zero exponent ranges that don't correspond to plausible coordinates). More likely packed/fixed-point data - indices, UVs, or flags - not decoded this pass.

This packet-tagged shape (running counter + type byte, several sub-blocks per unit) matches the "packet-like" description flagged as unsolved in earlier exploratory notes before this session's structured pass, and resembles PS2-era VU/GS command-stream conventions (a plausible reason ACZ's mesh format doesn't match AC4's flatter `SM.cs` layout byte-for-byte despite the shared 64-byte-record precedent). Only confirmed on this one minimal sample - **not yet cross-checked against a larger, multi-node file**, where the same 136-byte unit shape may not hold (larger files could have multiple such geometry-blocks per node, one per node, or an entirely different layout for genuinely multi-vertex meshes).

## Open questions

- Whether the "80-byte unit header + count pair + 4 tagged sub-packets" geometry shape found in the 752-byte briefing mesh generalizes to larger, multi-node files, or whether those use a different/more complex layout per node. **Needs a second small sample and one larger sample walked all the way through to confirm or refute.**
- What sub-packet tags `0x69`/`0x6e`/`0x64`'s non-float payloads actually encode (indices? UVs? flags?) - only tag `0x68`'s "3 vertices, 9 floats" is reasonably well explained.
- Which of the footer's 8 floats corresponds to which axis/quantity of the bounding volume - the structural shape (symmetric pairs, one value shared with the header) is confirmed, exact semantics aren't.
- What the two header floats at `0x08`/`0x0C` measure beyond "the footer restates `0x08`'s value exactly" - still short of a confirmed name for either.
- What header fields `0x20`-`0x44` encode - several look like `(count, offset)` pairs pointing into the file's own geometry/material data, but no clean, universally-consistent division of bytes-per-element was found this pass.
- What the record-level `0x00` type tag values (`0`/`8`/`9`/`10`) actually distinguish - leading hypothesis for `10` is "can exist as its own independent rigid body" (see above), not yet tested against `AHM`/shadow data or a jettisoned-tank scenario specifically. Tag `9` (briefing) and `0` (trees) still have no real hypothesis attached.
- Whether record `0x04`'s "usually `node_count - 1`" pattern is a real rule or coincidental for small tables - it clearly breaks for the large airframe table.
- What record field `0x10` (candidate: parent-record index) and the constant-per-file `0x30` float actually mean.
- What children `6`-`8` of a `DatBriefingTerrain` (the ones that vary in size per mission, unlike `0`-`5`) actually hold - `6` was tried as a `.dat` cast and rejected as invalid, `7`/`8` cast without error but show 0 children (inconclusive). Still the best lead for where the actual per-mission terrain wireframe data lives, if it's not simply baked into the shared `2` package.
