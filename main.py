import path
import settings
import uploader
"""
p = path.Path(settings.settings['sync_file'])
p.prepare_to_init_backup()
p.visit_paths()
"""
u = uploader.UploaderMega()
u.find_folder()
#u.mkdir('megup/pepito/lechuga')
