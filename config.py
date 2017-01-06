
class Config:
    DATA_PATH="/tmp/wtools"
    JSONIFY_PRETTYPRINT_REGULAR=False


class DevelopmentConfig(Config):
	DEBUG = True



config = {
        'default': DevelopmentConfig
        }
