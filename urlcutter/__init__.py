from .normalization import normalize_url, _url_fingerprint
from .protection import (
    AppState, internet_ok, circuit_blocked, cooldown_left,
    record_failure, record_success, rate_limit_allow,
    _get_state, _reset_state,
    CLIENT_RPM_LIMIT, CB_FAIL_THRESHOLD, CB_COOLDOWN_SEC,
    CIRCUIT_FAIL_THRESHOLD, CIRCUIT_COOLDOWN_SEC, RATE_LIMIT_WINDOW_SEC,
)
from .shorteners import shorten_via_tinyurl_core
from .logging_utils import setup_logging


__all__ = ["normalize_url", "_url_fingerprint"]
__version__ = "0.1.0"