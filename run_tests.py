import backup
import settings

#backup module
def test_detect_mode_from_backup():
    #3 vars: local_folder, remote_folder, summary
    
    #exists local_folder, exists remote_folder, exists summary (000)
    settings.Settings().set('sync_file', 'tests/sync_dir_full/')
    settings.Settings().set('remote_folder', 'test_folder')
    settings.Settings().set('summary_file', '.summary_file')
    to_test = backup.Backup()
    to_test.detect_mode()
    assert to_test.initial_backup_mode == False
    assert to_test.resync_mode == True
    assert to_test.remote_home_mode == False
    assert to_test.unknown_mode == False

    #exists local_folder, exists remote_folder, not exists summary (001)

    #exists local_folder, not exists remote_folder, exists summary (010)

    #exists local_folder, not exists remote_folder, not exists summary (011)

    #not exists local_folder, exists remote_folder, exists summary (100)

    #not exists local_folder, exists remote_folder, not exists summary (101)

    #not exists local_folder, not exists remote_folder, exists summary (110)

    #not exists local_folder, not exists remote_folder, not exists summary (111)


    assert backup.func() == 5