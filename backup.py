import settings
import uploader
import os
import filesystem

class Backup(object):
    """
    Class used to make a backup, in other words, the "kernel".
    """
    def __init__(self):
        """
        Constructor. It used settings file
        """
        self.recursive = True
        self.uploader = uploader.UploaderMega()
        self.actual_filesystem = filesystem.FileSystem(
                              initial_path=settings.Settings().get('sync_file'))
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
        remote = self.uploader.find_folder(settings.Settings().get('remote_folder'))
        summary = self.uploader.get_file(
                                    filename=settings.Settings().get('summary_file'),
                                    path=settings.Settings().get('remote_folder'))
        empty_dir = filesystem.os_empty_dir(settings.Settings().get('sync_file'))
        
        if remote and summary and empty_dir: #(000)
            print "REMOTE HOME 1"
            self.remote_home_mode = True
        elif remote and summary and not empty_dir: #(001)
            print "RESYNC 1"
            self.resync_mode = True
        elif remote and not summary and empty_dir: #(010)
            print "UNKNOWN MODE 1"
            self.unknown_mode = True
        elif remote and not summary and not empty_dir: #(011)
            print "INITIAL BACKUP 1"
            self.initial_backup_mode = True
        elif not remote and summary and empty_dir: #(100)
            #Impossible
            print "UNKNOWN MODE 2"
            self.unknown_mode = True
        elif not remote and summary and not empty_dir: #(101)
            #Impossible
            print "UNKNOWN MODE 3"
            self.unknown_mode = True
        elif not remote and not summary and empty_dir: #(110)
            print "UNKNOWN MODE 4"
            self.unknown_mode = True
        elif not remote and not summary and not empty_dir: #(111)
            print "INITIAL BACKUP 2"
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
            print "INITIAL BACKUP MODE"

            print "0 - PREPARA BACKUP"
            self.prepare_to_init_backup()

            print "2 - GENERA ACTUAL FS"
            self.actual_filesystem.generate()

            print "5.5 - UPLOAD ALL LOCAL FS"
            self.upload_all()

            print "6 - ACTUALIZA FS REMOTO"
            self.upload_actual_fs_struct()

        elif self.remote_home_mode:
            print "REMOTE_HOME MODE"

            print "1 - LOAD REMOTE FS"
            self.get_remote_fs_struct()
            print "2 - SYNC REMOTE HOME"
            self.sync_remote_home()
        elif self.resync_mode: # Reprocess
            print "RESYNC"

            print "1 - LOAD REMOTE FS"
            self.get_remote_fs_struct()

            print "2 - GENERA ACTUAL FS"
            self.actual_filesystem.generate()

            print "3,4 - CALCULA CAMBIOS"
            #print ('*'*80)
            changes = filesystem.compare_fs(actual_fs=self.actual_filesystem,
                                            old_fs=self.remote_filesystem)
     
            print "5 - APLICA DIFERENCIAS (BORRA Y SUBE NUEVOS)"
            self.process_changes_in_remote(changes)
        
            print "6 - ACTUALIZA FS REMOTO"
            self.upload_actual_fs_struct()
        else:
            print "UNKNOWN MODE, existing..."
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
                remote_folder = os.path.join(settings.Settings().get('remote_folder'),
                                             file.relative_path,
                                             file.name)

                rem_desc = self.uploader.mkdir(remote_folder)
                file.remote_desc = rem_desc
            elif file.type == filesystem.FILE:
                remote_folder = '%s/%s' % (settings.Settings().get('remote_folder'),
                                           file.relative_path)
                rem_desc = self.uploader.upload(remote_folder, file.path)
                file.remote_desc = rem_desc

    def prepare_to_init_backup(self):
        """
        This method is used to prepare remote folder (in Mega) to ake a backup
        """

        self.uploader.mkdir(settings.Settings().get('remote_folder'))

    def process_changes_in_remote(self, changes):
        """
        This method is used to changes changes in Mega (synchronize).
        """

        print "PROCESANDO CAMBIOS EN REMOTO"
        
        remove_files = changes['removed_files']
        for file in remove_files:
            print "Removing file %s" % file
            status = self.uploader.remove(
                path='%s/%s' % (settings.Settings().get('remote_folder'), #TODO changes for os.path.join
                                file.relative_path),
                filename=file.name)
            if not status:
                pass
                #print "ERROR AL ELIMINAR ARCHIVO %s" % file
            #print file

        remove_folders = changes['removed_folders']
        #TODO

        new_files = changes['new_files']
        for file in new_files:
            print "Uploading file %s" % file
            remote_folder = '%s/%s' % (settings.Settings().get('remote_folder'),
                                file.relative_path)
            rem_desc = self.uploader.upload(remote_folder, file.path)

        new_folders = changes['new_folders']
        for folder in new_folders:
            print "Creating remote folder %s" % folder
            print folder
            remote_folder = '%s/%s' % (settings.Settings().get('remote_folder'),
                                       folder.name)
            rem_desc = self.uploader.mkdir(remote_folder)
        
        to_download = changes['to_download']
        for file in to_download:
            print "TO DOWNLOAD %s" % file

        to_upload = changes['to_upload']
        for file in to_upload:
            print "TO UPLOAD %s" % file


    def upload_actual_fs_struct(self):
        #Debe reemplazar el antiguo si lo hay
        self.actual_filesystem.dump_to_file('fs.dmp')
        #remote_folder = '%s/%s' % (settings.settings['remote_folder'], 
        #                           settings.settings['summary_file'])
        #rem_desc = self.uploader.upload(remote_folder, 'fs.dmp')
        rem_desc = self.uploader.upload_raw(
                                    path=settings.Settings().get('remote_folder'),
                                    filename=settings.Settings().get('summary_file'),
                                    raw=self.actual_filesystem.get_dump())
        return rem_desc
    def get_remote_fs_struct(self):
        file_desc = self.uploader.get_file(
                                filename=settings.Settings().get('summary_file'),
                                path=settings.Settings().get('remote_folder'))

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
                content = self.uploader.get_content(
                                            remote_descriptor=file.remote_desc)
                filesystem.create_file(
                        path=os.path.join(settings.Settings().get('sync_file'),
                                                            file.relative_path),
                        name=file.name, 
                        content=content)
            
    def visit_path(self):
        #Deprecated?
        """
        Visit path and create summary file in binary
        """
        level = 0
        for root, subfolders, files in os.walk(self.path):
            #print root
            if not level:
                actual_remote_folder = settings.Settings().get('remote_folder')
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
            print ('*'*80)

            #print root
            #print files
            #print subfolders