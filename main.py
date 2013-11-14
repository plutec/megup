import backup
import settings
import uploader
import filesystem


def main():
	b = backup.Backup(settings.settings['sync_file'])
	#b.is_initial_backup()
	b.run()

if __name__ == '__main__':
	main()