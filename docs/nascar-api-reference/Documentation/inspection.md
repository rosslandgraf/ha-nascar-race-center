# Source inspection and access dependencies

The entire uploaded Markdown brief was read. It supplies 28 literal anonymous HTTPS URLs, project architecture and acceptance gates. It contains no executable code, API library, credentials, tokens or access-grant mechanism. No uploaded code was executed. Paths encode season, series and race IDs; no query parameters are required by the supplied examples. Network connectivity is required; session authentication was not used.

Path sets: live/feeds has five global feeds with no explicit series selector; cacher/{season}/{series}/schedule-feed.json and race_list_basic.json take season and series; cacher/{season}/{series}/{race}/... and loopstats/prod/{season}/{series}/{race}.json take a race context. Legacy paths encode series_1/5170; practice lap averages additionally encode a session in the filename. Drive config paths encode series only. These path interpretations come from the supplied URLs, not a verified API contract.

Reference repositories, Home Assistant and HACS documentation were listed in the brief but were not needed to capture or describe the responses. The development repository and its synthetic fixtures were not supplied or inspected. No implementation or PR changes were made. Public accessibility does not settle permission to poll or redistribute. No video, logos, photos, cookies or credentials are included.
