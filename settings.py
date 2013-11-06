settings = {
    'mega_verbose':True,    
    'remote_folder':'megup'
}

#Local settings
try:
    import local_settings
    local_settings_var = local_settings.local_settings
except:
    local_settings_var = dict()

settings.update(local_settings_var)