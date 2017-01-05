
class Config:
    DATA_PATH="/tmp/wtools"



class DevelopmentConfig(Config):
	DEBUG = True



config = {
        'default': DevelopmentConfig
        }
