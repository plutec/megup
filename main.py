import path
import settings
import uploader

p = path.Path(settings.settings['sync_file'])
p.prepare_to_init_backup()
p.visit_paths()

#u = uploader.UploaderMega()
#print u.find_folder('megup/test/hola')
#u.mkdir('megup/pepito/lechuga')
