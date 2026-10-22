# Data use and publication boundaries

The [MIT license](LICENSE) covers project code and original NRC artwork, not
NASCAR data, trademarks, photographs, logos, video or other third-party material.
This project is independent and is not an official NASCAR product.

Demonstration mode is offline. Experimental CF access requires authorization for
the user's intended use; the configuration acknowledgement does not establish
permitted polling rates, retention, redistribution or public distribution rights.
Owner-reported accessibility and passing code/HACS checks do not grant those rights.
No employee credentials, restricted Swagger access, inferred tokens, cookies,
video scraping or access-control bypass is supported.

The CF live request floor remains 300 seconds or the higher configured minimum;
server cache, Retry-After, cooldown, persisted eligibility and backoff can delay
requests further. Adaptive selection does not authorize fast CF polling. These
engineering limits are not NASCAR-approved cadence. Historical access is explicit
and on demand; an HTTP denial remains unavailable without aggressive retries.
No complete captured feeds, driver imagery or video are included in this package.

Before public publication or broader collection, establish applicable access,
cadence, storage, redistribution and attribution permissions. Approve the public
destination and original artwork, review metadata/privacy, and run the official
unskipped HACS validator there. Local original brand assets are supplied, with no
brands ignore. The current private repository's HACS job is skipped, not passed;
private HACS installation is unsupported. No release or visibility change occurs
automatically. See [installation and rollback](UPGRADE.md) and the
[current bundled update guide](REAL_CF_UPGRADE.md).
