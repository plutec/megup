import backup
import settings
import uploader
import filesystem


b = backup.Backup(settings.settings['sync_file'])
b.run()
