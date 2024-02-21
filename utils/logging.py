
import functools
import logging
import os
import sys
import threading
from logging import (
    CRITICAL,
    DEBUG,
    ERROR,
    FATAL,
    INFO,
    NOTSET,
    WARN,
    WARNING,
)
from typing import Optional
from logging import _nameToLevel as log_levels

# this lock is used to setup root logger and lock the other logger threads while doing this
_lock = threading.Lock()
_default_handler: Optional[logging.Handler] = None

_default_log_level = WARNING


def _get_default_logging_level():
    """
    check if a default log level has been set, if it has not been set, we will use default '_default_log_level'
    NOTE: We use MATRIX_ prefix to distinguish the ENV vars
    """

    env_level_str = os.getenv("MATRIX_LOGLEVEL", None)
    if env_level_str:
        if env_level_str in log_levels:
            return log_levels[env_level_str]
        else:
            logging.getLogger().warning(
                f"Unknown option MATRIX_LOGLEVEL={env_level_str}, "
                f"the options are: { ', '.join(log_levels.keys()) }"
            )
    return _default_log_level


def _get_library_name() -> str:
    return __name__.split(".")[0]


def _get_library_root_logger() -> logging.Logger:
    return logging.getLogger(_get_library_name())


def _setup_library_root_logger() -> None:
    global _default_handler

    with _lock:
        if _default_handler:
            # root logger has been setup already
            return
        _default_handler = logging.StreamHandler()  # Set sys.stderr as stream.
        _default_handler.flush = sys.stderr.flush

        # Setup root logger with default configs 
        library_root_logger = _get_library_root_logger()
        library_root_logger.addHandler(_default_handler)
        library_root_logger.setLevel(_get_default_logging_level())
        library_root_logger.propagate = False


def _reset_library_root_logger() -> None:
    global _default_handler

    with _lock:
        if not _default_handler:
            return

        library_root_logger = _get_library_root_logger()
        library_root_logger.removeHandler(_default_handler)
        library_root_logger.setLevel(logging.NOTSET)
        _default_handler = None


def get_log_levels_dict():
    return log_levels


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Return a logger with the given name
    you can use this inside the AbstractPipeline instances
    """

    if name is None:
        name = _get_library_name()

    _setup_library_root_logger()
    return logging.getLogger(name)


def get_loglevel() -> int:
    """
    Return the current loglevel for the root logger as an int.

    Returns:
        The log level as an int number, refer to logging module
    """

    _setup_library_root_logger()
    return _get_library_root_logger().getEffectiveLevel()


def set_loglevel(level: int) -> None:
    """
    Set the log level for the root logger.

    Args:
        level (`int`): one of the log_levels, or LEVELS specified inside logging module
        
    """

    _setup_library_root_logger()
    _get_library_root_logger().setLevel(level)


def set_loglevel_info():
    """
    Set the loglevel to the logging.INFO level.
    """
    return set_loglevel(INFO)


def set_loglevel_warning():
    """
     Set the loglevel to the logging.WARNING level.
    """
    return set_loglevel(WARNING)


def set_loglevel_debug():
    """
    Set the loglevel to the logging.DEBUG level.
    """
    return set_loglevel(DEBUG)


def set_loglevel_error():
    """
    Set the loglevel to the logging.ERROR level.
    """
    return set_loglevel(ERROR)


def disable_default_handler() -> None:
    """
    Disable the default handler set for the root logger
    """

    _setup_library_root_logger()

    assert _default_handler is not None
    _get_library_root_logger().removeHandler(_default_handler)


def enable_default_handler() -> None:
    """
    Enable the default handler of the root logger.
    """

    _setup_library_root_logger()

    assert _default_handler is not None
    _get_library_root_logger().addHandler(_default_handler)


def add_handler(handler: logging.Handler) -> None:
    """
    adds a handler to the root logger
    """

    _setup_library_root_logger()

    assert handler is not None
    _get_library_root_logger().addHandler(handler)


def remove_handler(handler: logging.Handler) -> None:
    """
    removes given handler from the root logger
    """

    _setup_library_root_logger()

    assert handler is not None and handler not in _get_library_root_logger().handlers
    _get_library_root_logger().removeHandler(handler)


def disable_propagation() -> None:
    """
    Disable propagation of the library log outputs. 
    NOTE: the log propagation is disabled by default.
    """

    _setup_library_root_logger()
    _get_library_root_logger().propagate = False


def enable_propagation() -> None:
    """
    Enable propagation of the library log outputs. 
    """

    _setup_library_root_logger()
    _get_library_root_logger().propagate = True


def enable_explicit_format() -> None:
    """
    Enable explicit formatting:
        [LEVELNAME|FILENAME|LINE NUMBER] TIME >> MESSAGE
    """
    handlers = _get_library_root_logger().handlers

    for handler in handlers:
        formatter = logging.Formatter("[%(levelname)s|%(filename)s:%(lineno)s] %(asctime)s >> %(message)s")
        handler.setFormatter(formatter)


def reset_format() -> None:
    """
    Resets the formatting to default logging format
    """
    handlers = _get_library_root_logger().handlers

    for handler in handlers:
        handler.setFormatter(None)


def warning_advice(self, *args, **kwargs):
    """
    This method is identical to `logger.warning()`, but if env var MATRIX_DISABLE_ADVICE=1 is set, this
    warning will not be printed
    """
    no_advisory_warnings = os.getenv("MATRIX_DISABLE_ADVICE", False)
    if no_advisory_warnings:
        return
    self.warning(*args, **kwargs)

"""
HINT:
def warning(self, msg, *args, **kwargs):
    if self.isEnabledFor(WARNING):
        self._log(WARNING, msg, args, **kwargs)
"""

logging.Logger.warning_advice = warning_advice


@functools.lru_cache(None)
def warning_once(self, *args, **kwargs):
    """
    This method is identical to `logger.warning()`, but will emit the warning with the same message only once

    Note: The cache is for the function arguments, so 2 different callers using the same arguments will hit the cache.
    The assumption here is that all warning messages are unique across the code. If they aren't then need to switch to
    another type of cache that includes the caller frame information in the hashing function.
    """
    self.warning(*args, **kwargs)


logging.Logger.warning_once = warning_once
