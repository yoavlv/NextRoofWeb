import logging
import os.path
from pathlib import Path

from split_settings.tools import include, optional

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

ENVVAR_SETTINGS_PREFIX = 'NextRoofWeb_CORESETTING_'

LOCAL_SETTINGS_PATH = os.getenv(f'{ENVVAR_SETTINGS_PREFIX}LOCAL_SETTINGS_PATH')

if not LOCAL_SETTINGS_PATH:
    LOCAL_SETTINGS_PATH = 'local/settings.dev.py'

if not os.path.isabs(LOCAL_SETTINGS_PATH):
    LOCAL_SETTINGS_PATH = str(BASE_DIR / LOCAL_SETTINGS_PATH)

# yapf: disable
include(
    'base.py',
    'custom.py',
    'envvars.py',
    'docker.py',
    'logging.py',
    optional(LOCAL_SETTINGS_PATH),
)
# yapf: enable

logging.captureWarnings(True)
