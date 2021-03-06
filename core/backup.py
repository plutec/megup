from core import settings, uploader, filesystem
from core.logger import log
import os


class Backup(object):
    """
    Class used to make a backup, in other words, the "kernel".
    """
    def __init__(self, backup_path):
        """
        Constructor. It used settings file
        """
        self.recursive = True
        self.backup_path = backup_path
        self.uploader = uploader.UploaderMega()
        self.actual_filesystem = filesystem.FileSystem(
                              initial_path=backup_path)
        self.remote_filesystem = None
        # Modes
        self.initial_backup_mode = False
        self.remote_home_mode = False
        self.resync_mode = False
        self.unknown_mode = False

    def detect_mode(self):
        """
        This method, depends of remote repository, and local folder, decides 
        the backup mode
        """
        #Initial backup, when in mega doesn't exist anything.
        #Resync, when in mega exists something and in home too.
        #Remote-home, when mega has content and local folder is empty 
            #or doesn't exist.
        remote = self.uploader.find_folder(
                                        settings.get_config('remote', 'folder'))
        summary = self.uploader.get_file(
                        filename=settings.get_config('remote','summary_file'),
                        path=settings.get_config('remote', 'folder'))
        empty_dir = filesystem.os_empty_dir(self.backup_path)
        
        if remote and summary and empty_dir: #(000)
            log.debug("REMOTE HOME 1")
            self.remote_home_mode = True
        elif remote and summary and not empty_dir: #(001)
            log.debug("RESYNC 1")
            self.resync_mode = True
        elif remote and not summary and empty_dir: #(010)
            log.debug("UNKNOWN MODE 1")
            self.unknown_mode = True
        elif remote and not summary and not empty_dir: #(011)
            log.debug("INITIAL BACKUP 1")
            self.initial_backup_mode = True
        elif not remote and summary and empty_dir: #(100)
            #Impossible
            log.debug("UNKNOWN MODE 2")
            self.unknown_mode = True
        elif not remote and summary and not empty_dir: #(101)
            #Impossible
            log.debug("UNKNOWN MODE 3")
            self.unknown_mode = True
        elif not remote and not summary and empty_dir: #(110)
            log.critical("Local directory doesn't exist and remote neither")
            print "Local directory doesn't exist & remote neither, existing..."
            log.debug("UNKNOWN MODE 4")
            self.unknown_mode = True
        elif not remote and not summary and not empty_dir: #(111)
            log.debug("INITIAL BACKUP 2")
            self.initial_backup_mode = True
        

    def run(self, options=None):
        """
        This method is the main function in this class.
        Pre:
            - Previous execution of detect_mode() method.
        Return:
            None
        """
        if self.initial_backup_mode:
            log.info("INITIAL BACKUP MODE")

            log.debug("0 - READY BACKUP")
            self.prepare_to_init_backup()

            log.debug("2 - GENERATE ACTUAL FS")
            self.actual_filesystem.generate()

            log.debug("5.5 - UPLOAD ALL LOCAL FS")
            self.upload_all()

            log.debug("6 - UPDATE REMOTE FS")
            self.upload_actual_fs_struct()

        elif self.remote_home_mode:
            log.info("REMOTE_HOME MODE")

            log.debug("1 - LOAD REMOTE FS")
            self.get_remote_fs_struct()
            log.debug("2 - SYNC REMOTE HOME")
            self.sync_remote_home()
        elif self.resync_mode: # Reprocess
            log.info("RESYNC")

            log.debug("1 - LOAD REMOTE FS")
            self.get_remote_fs_struct()

            log.debug("2 - GENERATE ACTUAL FS")
            self.actual_filesystem.generate()

            log.debug("3,4 - CALCULATE CHANGES")
            changes = filesystem.compare_fs(actual_fs=self.actual_filesystem,
                                            old_fs=self.remote_filesystem)
     
            log.debug("5 - APPLY DIFERENCES (DELETE/DOWNLOAD AND UPLOAD)")
            self.process_changes_in_remote(changes)
        
            log.debug("6 - UPDATE REMOTE FS")
            self.upload_actual_fs_struct()
        else:
            log.critical("UNKNOWN MODE, existing...")

            
    def upload_all(self):
        """
        Upload a complete local FileSystem
        Pre:
            - self.actual_filesystem is set. This is possible, calling the 
              method filesystem.generate()
        Return:
            None            
        """

        for file in self.actual_filesystem.files:
            if file.type == filesystem.FOLDER:
                if file.relative_path == '/':
                    file.relative_path = ''
                remote_folder = os.path.join(
                                        settings.get_config('remote', 'folder'),
                                        file.relative_path,
                                        file.name)

                rem_desc = self.uploader.mkdir(remote_folder)
                file.remote_desc = rem_desc
            elif file.type == filesystem.FILE:
                remote_folder = '%s/%s' % (
                                        settings.get_config('remote', 'folder'), 
                                        file.relative_path)
                rem_desc = self.uploader.upload(remote_folder, file.path)
                file.remote_desc = rem_desc

    def prepare_to_init_backup(self):
        """
        This method is used to prepare remote folder (in Mega) to make a backup
        """
        self.uploader.mkdir(settings.get_config('remote', 'folder'))


    def process_changes_in_remote(self, changes):
        """
        This method is used to changes changes in Mega (synchronize).
        """

        log.debug("Processing changes in remote")
        
        remove_files = changes['removed_files']
        for file in remove_files:
            log.debug("Removing file %s" % file)
            status = self.uploader.remove(
                path='%s/%s' % (settings.get_config('remote', 'folder'),
                                file.relative_path),
                filename=file.name)

            if not status:
                log.error("ERROR DELETING REMOTE FILE %s" % file)


        remove_folders = changes['removed_folders']
        for folder in remove_folders:
            log.debug("Removing folder %s" % folder)
            status = self.uploader.remove(
            path='%s/%s' % (settings.get_config('remote', 'folder'),
                            folder.relative_path),
            filename=folder.name)
            if not status:
                log.error("Folder not deleted correctly in remote %s" % folder)

        new_folders = changes['new_folders']
        for folder in new_folders:
            log.debug("Creating remote folder %s" % folder)
            remote_folder = '%s/%s/%s' % (
                                        settings.get_config('remote', 'folder'), 
                                        folder.relative_path,
                                        folder.name)
            rem_desc = self.uploader.mkdir(remote_folder)
        
        new_files = changes['new_files']
        for file in new_files:
            log.debug("New file %s" % file)
            remote_folder = '%s/%s' % (settings.get_config('remote', 'folder'), 
                                       file.relative_path)
            rem_desc = self.uploader.upload(remote_folder, file.path)


        to_download = changes['to_download']
        for file in to_download:
            log.debug("Download modified %s" % file)
            path = '%s/%s' % (settings.get_config('remote', 'folder'),
                                                        file.relative_path)
            content = self.uploader.get_content_by_path(path=path,
                                                        filename=file.name)
            filesystem.create_file(
                    path=os.path.join(
                           self.backup_path,
                           file.relative_path),
                    name=file.name, 
                    content=content)
        
        new_files = changes['to_upload']
        for file in new_files:
            log.debug("Uploading file %s" % file)
            remote_folder = '%s/%s' % (settings.get_config('remote', 'folder'),
                                file.relative_path)
            rem_desc = self.uploader.upload(remote_folder, file.path)


    def upload_actual_fs_struct(self):
        self.actual_filesystem.dump_to_file('fs.dmp')
        
        rem_desc = self.uploader.upload_raw(
                        path=settings.get_config('remote', 'folder'),
                        filename=settings.get_config('remote', 'summary_file'),
                        raw=self.actual_filesystem.get_dump())
        return rem_desc
    def get_remote_fs_struct(self):
        file_desc = self.uploader.get_file(
                        filename=settings.get_config('remote', 'summary_file'), 
                        path=settings.get_config('remote', 'folder'))

        fs_descriptor = self.uploader.get_content_descriptor(
                                                        file_info=file_desc)
        #print "DESCARGADO"
        self.remote_filesystem = filesystem.load_filesystem_descriptor(
                                                                fs_descriptor)

    def sync_remote_home(self):
        #We have remote FS, then...
        for file in self.remote_filesystem.files:
            if file.relative_path == '/':
                file.relative_path = ''
            
            if file.type == filesystem.FILE: #Else, folder
                path = '%s/%s' % (settings.get_config('remote', 'folder'),
                                     file.relative_path)
                content = self.uploader.get_content_by_path(path=path,
                                                            filename=file.name)
                filesystem.create_file(
                        path=os.path.join(
                               self.backup_path,
                               file.relative_path),
                        name=file.name, 
                        content=content)
            elif file.type == filesystem.FOLDER:
                path = os.path.join(self.backup_path,
                                     file.relative_path,
                                     file.name)
                filesystem.os_mkdir(path)
                
    def visit_path(self):
        #Deprecated?
        """
        Visit path and create summary file in binary
        """
        log.critical("RUNNING, DEPRECATED")
        level = 0
        for root, subfolders, files in os.walk(self.path):
            #print root
            if not level:
                actual_remote_folder = settings.get_config('remote', 'folder')
            else:
                actual_remote_folder = '%s/%s' % \
                    (actual_remote_folder, root.split('/')[-1])

            #For each files
            for fil in files:
                #print "SUBO %s a %s" % (fil ,actual_remote_folder)
                file_path = os.path.join(root, fil) 
                #print "ORIGEN %s" % file_path
                #print file_path
                rem_desc = self.uploader.upload(actual_remote_folder, file_path)
                
            #For each subfolder
            for subfolder in subfolders:
                #print "CREO carpeta %s" % actual_remote_folder+'/'+subfolder
                folder = os.path.join(actual_remote_folder, subfolder)
                rem_desc = self.uploader.mkdir(folder)
            level += 1
            

            #print root
            #print files
            #print subfolders