# Provider schema evidence

Evidence reviewed on October 20, 2026. No NASCAR CF endpoint was requested in
this task: the cloud network policy does not allow that host. Owner-reported
browser success remains separate from field-shape references and synthetic
fixture tests. None of these establish data-use permission.

The explicitly requested third-party references were reviewed critically:

- [`TannerYohe/nascar-api` at `3ab85bb543528d76521417b5534a6eedb09dcdf3`](https://github.com/TannerYohe/nascar-api/tree/3ab85bb543528d76521417b5534a6eedb09dcdf3).
- [`ooohfascinating/NascarApi/NewEndpointsDiscovered.MD`](https://github.com/ooohfascinating/NascarApi/blob/main/NewEndpointsDiscovered.MD),
  GitHub file blob `acd3f16f485c81823d1cb6274a3ed75008bf7c73` when read.

The first reference supplies a consistent narrow parsing contract. No source
implementation or upstream dataset was copied. The second agrees with the live
field names but is not an official schema or an authorization document.

| Adapter | Narrow contract used | Pinned reference |
| --- | --- | --- |
| Global season list `/cacher/{year}/race_list_basic.json` | Object containing `series_1`, `series_2`, `series_3` lists | [`repos/historic.py`, `get_races`](https://github.com/TannerYohe/nascar-api/blob/3ab85bb543528d76521417b5534a6eedb09dcdf3/src/nascar_api/repos/historic.py) |
| Schedule row | `race_id`, `series_id`, `race_name`, `date_scheduled`, `track_name` | [`models/base_race_info.py`](https://github.com/TannerYohe/nascar-api/blob/3ab85bb543528d76521417b5534a6eedb09dcdf3/src/nascar_api/models/base_race_info.py) |
| Global live feed `/live/feeds/live-feed.json` | Object containing `race_id`, `series_id`, `lap_number`, `flag_state`, `run_type`, `time_of_day_os` | [`models/live_info.py`](https://github.com/TannerYohe/nascar-api/blob/3ab85bb543528d76521417b5534a6eedb09dcdf3/src/nascar_api/models/live_info.py) |
| Flag code | 1 green, 2 yellow, 3 red, 4 white, 5 checkered, 8 hot track, 9 cold track | [`enums/flag.py`](https://github.com/TannerYohe/nascar-api/blob/3ab85bb543528d76521417b5534a6eedb09dcdf3/src/nascar_api/enums/flag.py) |

`run_type` is a **session kind**, normalized to practice/qualifying/race using
the second reference; it does not prove that a session is currently running or
that results are final. Unknown codes remain unknown. A fresh transport response
does not prove fresh NASCAR data: the source timestamp remains separate from
the local observation time.

Only dates with an explicit timezone offset are normalized to UTC. A naive
`date_scheduled`, missing time, or invalid optional time remains unknown rather
than guessing a track timezone. Whether naive dates are actually UTC needs an
authorized real response capture and official clarification. This can limit
next-race entities with real feeds until the schema gate is resolved.

Missing series envelopes, wrong/missing identities, duplicate race IDs, and
unknown live envelopes raise a schema error; they do not become fabricated
empty schedules or zero-valued sensors. Additional optional fields are ignored.
A JSON `null` live payload is supported as an empty-provider representation for
mocked tests, **not claimed as a verified NASCAR off-season response**. Empty
objects and unrecognized off-season payloads fail explicitly pending evidence.

The experimental CF adapter is opt-in and remains unverified against a current
anonymous response. Default demonstration mode uses handmade examples, requires
no credentials, and makes no network requests. The broad endpoint inventory is
documented separately; a URL being listed does not mean an adapter exists.
