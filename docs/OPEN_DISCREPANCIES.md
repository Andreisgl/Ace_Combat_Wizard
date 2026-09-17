# Open Discrepancies & Contradictions

Unresolved conflicts between different sources of information about the file formats - our own reverse-engineering, death_the_d0g's documentation, and in-game/tool observation. None of these are resolved; this file exists so that if we hit an inconsistency or a roadblock somewhere later, we check here first for a possibility we already noticed but didn't chase down at the time.

Each entry: what conflicts, the evidence on each side, and why it's not resolved yet.

---

## 1. `P3D` (aircraft slot 3): hardpoints/special-weapons vs. audio playback

**Our hypothesis** (built up over most of a session's worth of hex analysis, see `docs/AIRCRAFT_FORMAT_NOTES.md`): `P3D` is a 10-record hardpoint/attachment-point table. Evidence: records split cleanly 3-vs-7 by a "group" tag, which lines up suspiciously well with ACZ's 3-special-weapon-slot system (the exact reason this investigation started - the ACZ→AC5 wingman conversion issue where AC5 aircraft only support 1 SpW).

**d0g's documentation**: describes aircraft slot `0003` as "possible audio playback parameter file, related to `0004`" - and slot `0004` is documented as the "engine sound effect file." This is a materially different theory.

**Evidence for the audio theory**: we independently (and separately from d0g's doc) confirmed that `P3D`'s own header stores slot `4`'s exact byte size - a fact that fits "P3D describes playback parameters for the sound sample in slot 4" at least as well as, if not better than, "P3D describes hardpoints" (why would a hardpoint table need to know a completely unrelated raw blob's size?). The per-record fields being mostly constants/sentinels with only a couple of genuinely varying values also fits "named sound-emission point" (e.g. front/rear engine, exhaust) plausibly.

**Why unresolved**: neither theory is confirmed. The "3 vs 7" split matching the SpW count could be coincidental. d0g's own doc hedges with "possible." Needs either: a way to correlate specific `P3D` record fields against known real-world hardpoint or sound-emitter positions on a specific aircraft, or evidence from a completely different angle (e.g. finding what actually points at slot 3's data elsewhere in the engine/game logic, if that's ever discoverable).

---

## 2. Aircraft slot 16: "Special weapon icons" vs. "SpW HUD texture (refueling mode)"

**Our finding**: directly observed via this tool's own Image visualizer - the texture depicts 6 icons: 3 for the weapon-selection menu, 3 more showing each weapon's dynamic/type (semi-active, unguided bomb, rocket, for the aircraft checked).

**d0g's documentation**: labels the same slot "SpW HUD texture (refueling mode)" - a narrower, different-sounding purpose (a single icon for a specific in-flight HUD context, not a 6-icon selection sheet).

**Why unresolved**: both could be partially right if the same texture sheet is reused across different UI contexts (selection menu and in-flight HUD alike) - not unusual for games to share icon atlases. Or one description is simply less precise than the other. Direct visual observation is strong evidence, but doesn't rule out the texture also being used the way d0g describes elsewhere in the game.

---

## 3. Aircraft slots 0 and 2: per-aircraft parameters vs. byte-identical content

**d0g's documentation**: slot `0` = "Aircraft movement stat parameter file" (implies per-aircraft data - different planes fly differently) and slot `2` = "Camera coordinate placement file" (also sounds aircraft-specific, e.g. cockpit camera position).

**Our finding**: both slots are byte-for-byte identical between the two sample aircraft checked (Gripen, Draken) - 400 bytes and 160 bytes respectively, exact same content, not just the same size.

**Why unresolved**: only two aircraft have been checked, both "STANDARD" tier. Possible explanations, none confirmed: these fields could be a shared baseline/default that's overridden elsewhere (e.g. multiplied by a per-aircraft stat elsewhere in the game), the two sample aircraft could coincidentally share base stats even though they play differently in other ways, or d0g's description could be off for these specific slots. Worth re-checking against a more different pair of aircraft (e.g. a very large vs. very small airframe) if this becomes relevant.

---

## 4. Stage/mission ace-style ordering (M/S/K vs S/M/K)

Not from d0g's new document, but the same "check here if something doesn't add up" spirit applies, so it's cross-referenced here rather than only living in code comments.

**Existing code** (`ACZ_DAT_ASSET_LIST`/`ACZ_STAGE_DAT_ASSET_LIST` in `asset_classes.py`) orders multi-style stage/mission groups (Round Table, Juggernaut, Merlon, Mayhem, Final Overture, Demon of the Round Table) as M/S/K.

**death_the_d0g's `ACZ_makepack_contents_SLUS21346.txt`** (the earlier slot-listing document, not `acz_data_struc.md`) is internally inconsistent about this across its own three separate listings - e.g. it lists Juggernaut as S/M/K in one place.

**Current handling**: every `ace_style`-tagged slot's display name is tagged `[CONFIRM ACE STYLE]` in the tree/metadata (see `Container.generate_children()`), as a standing reminder that this ordering isn't trusted from either source without independent verification (dialogue, other data).
