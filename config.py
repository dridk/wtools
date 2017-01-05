
class Config:
    DATA_PATH="/tmp/wtools"



class DevelopmentConfig(Config):
    pass



config = {
        'default': DevelopmentConfig
        }
