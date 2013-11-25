settings = {
    'mega_verbose':False,
    'megup_debug':5, #0 - 10    
    'remote_folder':'megup',
    'summary_file':'.summary_megup'
}

#Local settings
try:
    import local_settings
    local_settings_var = local_settings.local_settings
except:
    local_settings_var = dict()

settings.update(local_settings_var)