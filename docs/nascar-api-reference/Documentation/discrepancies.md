# Discrepancies and assumption limits

No repository schemas or synthetic fixtures were attached, so a field-by-field diff against the earlier 91 synthetic paths is unavailable. Do not claim those assumptions were verified or corrected. The source brief provides feature wishes rather than a concrete response schema. The following are comparisons against its access observations and implementation expectations:

* Owner reported 24 working and four error/login URLs. Here those 24 returned populated JSON, driver recap returned an empty successful article envelope, and only the three Drive endpoints returned HTTP 403. These results are time/network specific.
* Prior conversation reported proxy CONNECT 403 for all URLs. That is not the result in this run: 25 origin-path HTTP 200 JSON responses and three MissingKey XML responses were observed.
* Global feeds do not share verified event context: leaderboard race 5633 versus stages 5168; points series/race/run IDs zero. HTTP success does not establish coherent current race data.
* Historical and live field shapes differ: numeric versus string lap speed, differing driver identity spellings, misspelled embedded pit positions_gained_lossed, and differing average-lap wrappers.
* Schedule strings do not carry timezone offsets, even *_utc. Live time_of_day_os does. Numeric time_of_day must not be assumed epoch seconds.
* Schedule/reference data and a driver directory are present, but team/manufacturer display values, car numbers and annotated names must not substitute for stable identity.
* 999 lap-average values, null ranks and -1 pit durations need unknown/sentinel handling; default zero conversion would fabricate facts.
* Exact Phase 3A/3B/3C definitions are absent from the attached brief; compatibility mapping is provisional.
