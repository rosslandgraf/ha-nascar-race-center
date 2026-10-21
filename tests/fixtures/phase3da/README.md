# Phase 3D-A synthetic contracts

These five small handmade JSON files contain fictional IDs, labels, dates,
measurements and codes. They are not NASCAR captures or copies of the redacted
structural examples. No redacted scalar is used as an identity/date/fact.

Keys and JSON types follow the observed package's exhaustive field profiles:
`live.json` → endpoint 01; `schedule.json` → 06; `sessions.json` → 09;
`drivers.json` → 07; `tracks.json` → 08. The tests check every fixture path/type
against those profiles. Unknown-slug and unequal race-date examples exercise
uncertainty; they do not establish a series mapping or postponement. Fictional
race 99059 models the documented unmatched schedule race (without reusing it).
The seven-digit offset timestamp models the documented format, not its value.
Numeric Team text remains uninterpreted; Driver_ID differs from NASCAR identity.

Existing Phase 3B synthetic fixtures remain the standalone pits/stages/points
contracts. No fixture grants time units, timezone semantics for naive dates,
status meanings, scoring formulas, cross-endpoint run associations or data rights.
