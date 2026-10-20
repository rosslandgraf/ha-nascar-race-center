"""Constants for NASCAR Race Center."""

from datetime import timedelta

from homeassistant.const import Platform

DOMAIN = "nascar_race_center"
NAME = "NASCAR Race Center"
PLATFORMS = (Platform.SENSOR, Platform.BINARY_SENSOR)

CONF_PROVIDER = "provider"
CONF_SERIES = "series"
CONF_DATA_USE_AUTHORIZED = "data_use_authorized"
CONF_LIVE_INTERVAL = "live_interval"
PROVIDER_DEMO = "demo"
PROVIDER_CF = "nascar_cf"
DEFAULT_LIVE_INTERVAL = 300
MIN_LIVE_INTERVAL = 300
MAX_LIVE_INTERVAL = 3600
DEFAULT_SERIES = ["1", "2", "3"]
SERIES_NAMES = {
    1: "NASCAR Cup Series",
    2: "NASCAR National Series 2",
    3: "NASCAR Truck Series",
}
SCHEDULE_INTERVAL = timedelta(hours=6)
LIVE_IDLE_INTERVAL = timedelta(hours=1)
LIVE_OFF_SEASON_INTERVAL = timedelta(hours=6)
LIVE_STALE_AFTER = timedelta(minutes=15)
SCHEDULE_STALE_AFTER = timedelta(days=1)
