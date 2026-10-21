# Opt-in racing events and automation blueprints

Events are **off by default**, including on upgrades. In **Settings → Devices &
services → NASCAR Race Center → Configure**, enable racing events and select
individual race and favorite-driver event types. Choose the top-position threshold
(1–40) and reminder lead time (1–1440 minutes). Favorite events use the existing
saved NASCAR driver IDs. Clearing either event selector disables those types.
Existing entries and entity IDs require no migration.

The integration only publishes events. It never calls notification, light or
other device services. Import and enable an automation separately to act on them.
The offline demonstration still makes no NASCAR requests and has no active live
feed; the synthetic replay tests demonstrate transitions without real racing.

## Stable event contract

Listen to the single Home Assistant event namespace **`nascar_race_center_event`**.
All events contain `event_type`, a deterministic SHA-256 `event_id`, `series_id`,
`race_id`, `run_id`, `driver_id`, `source` (`nascar_cf` or `demo`) and ISO-offset
`source_time`. Run/driver IDs are null when inapplicable. Names, car numbers and
full feeds are absent. Live `source_time` is the normalized source content clock;
reminder `source_time` is the local deadline evaluation time and its distinct
`schedule_start` context is supplied as `scheduled_start`. No source content time
is invented for a schedule. Same-named clocks remain subject to existing provider
evidence limits; see [Phase 3B evidence](PHASE3B_EVIDENCE.md).

| Event type | Evidence and additional fields |
| --- | --- |
| `upcoming_race` | Previously watched, unchanged, offset-aware future race start crosses the reminder deadline; `scheduled_start`, `reminder_minutes`. At most one reminder per source/series/season/race even after changing lead time or rescheduling. |
| `session_started` | Same identified race run changes from observed lap zero with cold/hot/green flag to positive lap with green flag; `lap`. A first observed active race or a caution restart cannot establish the start. |
| `flag_changed` | Supported changed green/yellow/red/white/checkered flag between valid observations; `flag`, `lap`, `completion` (`observed` for checkered, otherwise `unknown`). |
| `lead_changed` | Unique position 1 changes between NASCAR-ID drivers present in both fields; new `driver_id`, `previous_driver_id`. |
| `favorite_lead` | Same evidence, new leader is a saved favorite; `previous_driver_id`. Select this instead of general lead changes to receive only favorite-lead notifications. |
| `favorite_top_n_entered` / `favorite_top_n_left` | Favorite has unambiguous ranks in both fields crossing the chosen threshold; `position`, `previous_position`, `top_n`. Disappearance is unknown, never a top-N exit. |
| `favorite_pit_observed` | New unambiguous embedded pit entry with positive reported entry clock and pit lap between the previous/current race laps; `pit_lap`. Prior pit list must be known, including known empty. Only the newest supported entry is reported after skipped updates. Exit enrichment never emits another observation for that stop. |

A checkered transition creates **one `flag_changed` event**, marking observed
session completion. There is no additional finish event. Further changes for that
completed run are suppressed. **Observed completion is not official finalized
results.** No retirement, stage-finish, championship-movement or official-result
events exist. Pit observation does not claim completed stop, on-pit-road status,
duration, tire activity or a completed-stop count.

Example payload (fictional):

```json
{"event_type":"flag_changed","event_id":"<64-character SHA-256>","series_id":1,"race_id":9001,"run_id":8,"driver_id":null,"source":"nascar_cf","source_time":"2026-10-21T16:03:30+00:00","flag":"checkered","lap":100,"completion":"observed"}
```

## Reliability and retention

Setup, options reload, restart, source recovery and race/run/series changes always
establish silent baselines. Events require a monitored race run with positive
race/run IDs, known lap/flag and healthy source time between now and 15 minutes
old. Missing, stale, future, failed, unselected or nonrace sources break continuity.
Neither HTTP success nor a cache hit refreshes source content time. Equal clocks
with conflicting data, regressing clocks/laps/elapsed progress and observation
gaps longer than 15 minutes suppress transitions and require a new baseline.
Missing driver records, invalid fields and duplicate ranks cannot fabricate
position/leader changes. No missed flag timeline or historical pit sequence is
reconstructed between polls.

One entry-owned listener processes the **single global live observation** once;
selected series/favorites add no requests or events for copied data. No endpoint,
minimum polling interval or standalone-scoring eligibility changed. Reminders
use one local timer and fresh usable schedules (at most one day old). Installation
inside a reminder window, rescheduling into an elapsed window, canceled/unknown
starts, schedule failures and deadlines missed by more than one minute do not
produce catch-up notifications. Very distant reminders need an existing healthy
schedule refresh; they never trigger a new fetch.

The private versioned Home Assistant Store ledger contains at most 64 session
high-water marks, 2,048 event-ID hashes and 300 sent-reminder identities. A bounded
32-observation queue and one worker serialize persistence. Session and reminder
evictions advance durable clock floors so old observations/deadlines cannot be
replayed after retention. Completed-session tombstones outlive event-ID eviction.
The ledger stores no raw JSON, leaderboard, driver names or pit arrays. No full
feed enters Recorder. Removing the integration deletes its ledger; disabling
and re-enabling events keeps it. Diagnostics expose `disabled`, `ready`,
`ledger_error` or `stopped` and selected event types, without dumping the ledger.

Replay barriers are saved **before** publishing and checked through the public Store read-back API. HA can log a failed write without raising it; a mismatched read-back disables events. A save/load/schema error disables
events for that load while schedules/entities remain usable. Inspect HA logs and
restore a valid ledger from backup before reloading; do not delete it to retry
notifications. Delivery favors **at-most-once** behavior: a crash after saving but
before publishing can omit an event. There is no catch-up outbox. Deleting storage,
restoring an older HA backup or a source falsifying its own advancing clock cannot
provide an absolute all-time delivery guarantee. Restarts still create silent
baselines even if no prior ledger exists.

## Notification blueprint

Copy [race_notifications.yaml](../blueprints/automation/nascar_race_center/race_notifications.yaml)
to `config/blueprints/automation/nascar_race_center/` (or use HA's blueprint import
with its reviewed GitHub file URL). Under **Settings → Automations & scenes →
Blueprints**, create an automation. Choose series and event types, then use the
notification-action selector to choose your own notification service. For example:

```yaml
action: notify.mobile_app_your_phone
data:
  title: '{{ racing_title }}'
  message: '{{ racing_message }}'
```

The action selector also accepts other standard user-chosen actions. The blueprint
provides `racing_title`, `racing_message` and the small `racing_event` mapping.
Notification actions default to empty. Demo events are ignored unless separately
enabled in the blueprint. Select either `favorite_lead` or `lead_changed` when
you want one notification per lead change; selecting both intentionally asks for
two different event subscriptions. Event IDs are available for downstream systems.

## Optional flag lights

Copy/import [flag_lights.yaml](../blueprints/automation/nascar_race_center/flag_lights.yaml)
the same way. Choose color-capable lights, one series and a 1–10 second effect.
Green/yellow/red use their corresponding colors; white and checkered use neutral
white. There is no brand requirement, flashing/strobing or automatic installation.

Every run captures an HA scene before changing a light, uses ordinary
`light.turn_on`, waits briefly (or ends early for a newer matching flag), restores
with `scene.turn_on`, then deletes the temporary scene. `queued` execution
(maximum 10) lets restoration finish before another effect snapshots anything;
queued events older than the effect duration are discarded. An effect-command
failure still reaches restoration. A restoration failure leaves the scene for
manual recovery and aborts that run. Use one automation per light group and avoid
other controllers changing those lights during the effect; HA can restore only
the state the devices expose (including on/off, brightness and reported color).
Unavailable lights are excluded. Device/network failures, disabling/reloading
an active automation or stopping HA can interrupt restoration; no automation can
command an unreachable device or continue while HA is stopped. Restore the
retained scene manually if needed. Physical bulbs and production HA were not used. A retained recovery scene blocks further effects until it is recovered and removed, preserving the original snapshot.

The test suite loads both blueprints through HA's real blueprint schema and
executes notification filtering plus light effects, rapid transitions, on/off
restoration and failed color commands with local test lights/services. It makes
no calls to external notification services or real devices. Source enum meanings,
clock behavior and real active-session transitions remain unverified; see
[Phase 3C validation](PHASE3C_VALIDATION.md).
