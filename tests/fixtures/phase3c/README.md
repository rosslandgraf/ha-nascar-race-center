# Synthetic event replay

`race_sequence.json` is a handmade scenario in a TEST-ONLY format, not a NASCAR
response or capture. Tests construct the existing immutable normalized models.
All times, driver IDs, ranks, flags, transitions and pit evidence are fictional.
The fixture exercises baseline/start, caution/restart, favorite lead/top-N/pits,
red/white/checkered observations. It cannot validate actual code meanings,
source-clock correctness, official scoring or live-session behavior. No runtime
provider reads this file. No endpoints or provider parsing fields were added.
