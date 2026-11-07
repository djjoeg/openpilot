# Recovery log (rebuilding the design programs from the chat record)

Method: read_conversation(conversation_id="current", page_token="t<N>", max_turns=1) returns turn N with every
tool call's inputs (Write content, Edit old/new strings, Bash commands). Rebuild each file by replaying its first
write and every later change in order.

Chat: 397 turns as of 7 Nov. Turn 296 = 2 Nov ("should be done"); turn 297 = the push of v1.3.0 to GitHub;
turn 331 = 5 Nov (plate fit plan); turn 360 = 5 Nov.

pypi is blocked by the proxy (403), so manifold3d / trimesh / shapely can't be installed here: the rebuilt programs
can be saved but not run in this workspace.

## Turn map (what each turn touched)

Probed so far (human turns are even, assistant turns odd):
- 240 (Nov 1): shopping for M5 wing bolts in Chrome: the right-arm mount's design existed by then.
- 250, 252 (Nov 1): wiring questions. 256, 262 (Nov 2): plates to print; "how does it know it's in the teeth".
- 280 (Nov 2): Amazon order recorded. 296-297 (Nov 2): v1.3.0 pushed to GitHub.
- 331, 360 (Nov 5): frame plate fit plan; "what's missing".
So rightarm.py / rightcheck.py / stiffness.py / midteeth.py were first written before turn 240 and edited up to
about turn 365 (the v6 fit print 3 Nov, the plate fit test and paper template 5 Nov). The gear came from an earlier
mount's program (faceparts.py or sideparts.py), earlier still.

## 7 Nov, first pass (ten helpers)
All ten slices stopped at read_conversation's hourly cap (256 calls an hour, shared). Done: 0-23, 40-67, 80-103,
120-144, 160-165, 200-224, 240-279, 280-307, 320-336, 360-398. Still to read: 24-39, 68-79, 104-119, 145-159,
166-199, 225-239, 308-319, 337-359. Large turns were copied byte-exact by small parsers (recovery/tools,
_tools_120_159, _helpers_280_319) from the saved tool results.
549 operations indexed so far (453 shell commands, 62 full writes, 34 edits). recovery/assemble.py replays them in
order in a sandbox (running a design program is skipped, since its 3D libraries can't be installed here; ruff is
skipped, so a few unused imports it once removed may remain).
