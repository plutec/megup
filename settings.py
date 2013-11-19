
class Settings(object):
    _instance = None
    def __init__(self):
        self.settings = {
            'mega_verbose':False,
            'megup_debug':5, #0 - 10    
            'remote_folder':'megup',
            'summary_file':'.summary_megup'
        }
        try:
            import local_settings
            local_settings_var = local_settings.local_settings
        except:
            local_settings_var = dict()

        self.settings.update(local_settings_var)

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Settings, cls).__new__(
                                cls, *args, **kwargs)
        return cls._instance
    
    def get(self, key):
        if self.settings.has_key(key):
            return self.settings[key]
        return None

    def set(self, key, value):
        self.settings[key] = value
        return value