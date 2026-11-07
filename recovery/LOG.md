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

## 7 Nov, second pass and replay
Eight more helpers read the rest (24-39, 68-79, 104-119, 145-159, 166-199, 225-239, 308-319, 337-359): all 399 turns
are now covered. 791 operations indexed in all. Replay fixes in assemble.py: a stand-in for manifold3d (on the
chat's own library path, /home/claude/pylib) ends any run of a design program at its import with exit 0, so commands
chained after a run still happen; ruff is a no-op at both paths the chat used; folders a command cds into are made;
paths inside helper scripts point into the sandbox too (undone on read-back); every tracked file is read back after
a command whatever its type (the 3D page template was being lost); a command whose folder was guessed wrong is
re-run in the cad folder; overrides/ holds hand-made stand-ins (one: T316 S169, whose CHANGELOG half, run first,
stopped its rightarm.py half).
Result: 39 programs plus the 3D page template in hardware/cad, all valid Python. Every remaining replay failure was
checked: each is a run of a program, a read of an output that isn't here (logs, pictures, reports), a scratch
script's data (photo-matching pickles), or T088 S36, whose failed assert the chat itself re-applied in S38 and S39.
Checks: platefit2.py identical to the surviving copy; platefit.py's fit-test plate matches plate-15's mesh in size
(166 x 147 x 6) and volume (64.9 cm3). The other parts are not yet re-made: manifold3d can't be installed here.
