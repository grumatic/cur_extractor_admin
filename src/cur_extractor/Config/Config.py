# Interval to run extracte
# Equivalent of cron schedule notation '0 * * * *'
BEAT_MINUTE = '0'
BEAT_HOUR = '*'
BEAT_DAY_OF_WEEK = '*'
BEAT_MONTH_OF_YEAR = '*'
BEAT_DAY_OF_MONTH = '*'

# Path for CUR data download
DOWNLOAD_PATH = './tmp'
# Default prefix added to the upload key file
DEFAULT_PREFIX= 'grumatic-cur'
# Remove temp folder after extract
NEED_REMOVE_TEMP = True

CHUNK_SIZE = 1e5

