"""Constants for NASCAR Race Center."""

from datetime import timedelta

from homeassistant.const import Platform

DOMAIN = "nascar_race_center"
NAME = "NASCAR Race Center"
PLATFORMS = (Platform.SENSOR, Platform.BINARY_SENSOR, Platform.CALENDAR)

CONF_PROVIDER = "provider"
CONF_SERIES = "series"
CONF_DATA_USE_AUTHORIZED = "data_use_authorized"
CONF_LIVE_INTERVAL = "live_interval"
CONF_FAVORITE_DRIVERS = "favorite_drivers"
CONF_POLLING_POLICY = "live_polling_policy"
CONF_APPROACHING_INTERVAL = "approaching_interval"
DEFAULT_POLLING_POLICY = "conservative"
DEFAULT_APPROACHING_INTERVAL = 60
PROVIDER_DEMO = "demo"
PROVIDER_CF = "nascar_cf"
DEFAULT_LIVE_INTERVAL = 300
MIN_LIVE_INTERVAL = 300
MAX_LIVE_INTERVAL = 3600
DEFAULT_SERIES = ["1", "2", "3"]
SERIES_NAMES = {
    1: "NASCAR Cup Series",
    2: "NASCAR O'Reilly Auto Parts Series",
    3: "NASCAR Craftsman Truck Series",
}
SCHEDULE_INTERVAL = timedelta(hours=6)
LIVE_IDLE_INTERVAL = timedelta(hours=1)
LIVE_OFF_SEASON_INTERVAL = timedelta(hours=6)
LIVE_STALE_AFTER = timedelta(minutes=15)
SCHEDULE_STALE_AFTER = timedelta(days=1)
REFERENCE_INTERVAL = timedelta(days=1)
REFERENCE_STALE_AFTER = timedelta(days=7)

# Only position is enabled by default; users opt into additional timing history.
FAVORITE_LIVE_METRICS = (
    "position",
    "last_lap",
    "best_lap",
    "gap",
    "running_status",
    "position_change",
)

FAVORITE_SCORING_METRICS = ("pit_lap", "stage_position", "championship_position")
