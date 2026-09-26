from enum import Enum

class ErrorType(str, Enum):
    INVALID_CREDS = 'InvalidCreds'
    TWO_FACTOR = '2FA'
    CAPTCHA = 'Captcha'
    RATE_LIMIT = 'RateLimit'
    SESSION_TIMEOUT = 'SessionTimeout'
    NETWORK_ERROR = 'NetworkError'

class ApplicationStatus(str, Enum):
    APPLIED = 'Applied'
    SKIPPED = 'Skipped'
    QUEUED = 'Queued'
    FAILED = 'Failed'

class Phase(str, Enum):
    INIT = 'INIT'
    AUTH = 'AUTH'
    LOAD = 'LOAD'
    SCRAPE = 'SCRAPE'
    PROCESS = 'PROCESS'
    AGGREGATE = 'AGGREGATE'
    OUTPUT = 'OUTPUT'
    FAILED = 'FAILED'
