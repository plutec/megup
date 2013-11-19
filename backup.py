import settings
import uploader
import os
import filesystem

class Backup(object):

    recursive = None
    path = None
    uploader = None
    actual_filesystem = None
    remote_filesystem = None

    def __init__(self, path):
        self.recursive = True
        self.path = path
        self.uploader = uploader.UploaderMega()
        self.now_path = path #Is it used?
        self.actual_filesystem = filesystem.FileSystem(
                                    initial_path=self.path)
        self.initial_backup_mode = False
        self.remote_home_mode = False
        self.resync_mode = False
        self.unknown_mode = False

    def detect_mode(self):
        #Initial backup, when in mega doesn't exist anything.
        #Check remote_folder and summary_file exists, else, is initial backup
        remote = self.uploader.find_folder(settings.settings['remote_folder'])
        summary = self.uploader.get_file(
                                    filename=settings.settings['summary_file'], 
                                    path=settings.settings['remote_folder'])
        if not remote or not summary:
            self.initial_backup_mode = True
            return
        #Resync, when in mega exists something and in home too.
        empty_dir = filesystem.os_empty_dir(settings.settings['sync_file'])
        if summary and not empty_dir:
            self.resync_mode = True
        #Remote-home, when mega has content and local folder is empty or doesn't exist.
        #Check if mega has sumary file (previous check is valid)
        #Check if local folder exists or is empty
            #exists_local = filesystem.os_exists_dir(settings.settings['sync_file'])
            if empty_dir:#exists_local:
                self.remote_home_mode = True
            else:
                self.unknown_mode = True
        else:
            self.unknown_mode = True


    def run(self, options=None):
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
            return
            print "1 - LOAD REMOTE FS"
            self.get_remote_fs_struct()
            print "2 - SYNC REMOTE HOME"
            self.sync_remote_home()
        elif self.resync_mode: # Reprocess
            print "RESYNC"
            return
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
        Upload a complete FileSystem
        Params:
            fs: FileSystem object
        """
        for file in self.actual_filesystem.files:
            if file.type == filesystem.FOLDER:
                if file.relative_path == '/':
                    file.relative_path = ''
                remote_folder = os.path.join(settings.settings['remote_folder'],
                                             file.relative_path,
                                             file.name)

                rem_desc = self.uploader.mkdir(remote_folder)
                file.remote_desc = rem_desc
            elif file.type == filesystem.FILE:
                remote_folder = '%s/%s' % (settings.settings['remote_folder'], 
                                           file.relative_path)
                rem_desc = self.uploader.upload(remote_folder, file.path)
                file.remote_desc = rem_desc

    def prepare_to_init_backup(self):
        self.uploader.mkdir(settings.settings['remote_folder'])

    def process_changes_in_remote(self, changes):
        print "PROCESANDO CAMBIOS EN REMOTO"
        
        print "Removing files..."
        remove_files = changes['removed_files']
        for file in remove_files:
            status = self.uploader.remove(
                path='%s/%s' % (settings.settings['remote_folder'],
                                                          file.relative_path),
                filename=file.name)
            if not status:
                pass
                #print "ERROR AL ELIMINAR ARCHIVO %s" % file
            #print file

        remove_folders = changes['removed_folders']
        #TODO
        print "Uploading new files..."
        new_files = changes['new_files']
        for file in new_files:
            remote_folder = '%s/%s' % (settings.settings['remote_folder'], file.relative_path)
            rem_desc = self.uploader.upload(remote_folder, file.path)

        print "Creating remote folders..."
        new_folders = changes['new_folders']
        for folder in new_folders:
            print folder
            remote_folder = '%s/%s' % (settings.settings['remote_folder'], 
                                       folder.name)
            rem_desc = self.uploader.mkdir(remote_folder)
        #print changes

    def upload_actual_fs_struct(self):
        #Debe reemplazar el antiguo si lo hay
        self.actual_filesystem.dump_to_file('fs.dmp')
        #remote_folder = '%s/%s' % (settings.settings['remote_folder'], 
        #                           settings.settings['summary_file'])
        #rem_desc = self.uploader.upload(remote_folder, 'fs.dmp')
        rem_desc = self.uploader.upload_raw(
                                    path=settings.settings['remote_folder'],
                                    filename=settings.settings['summary_file'], 
                                    raw=self.actual_filesystem.get_dump())
        return rem_desc
    def get_remote_fs_struct(self):
        file_desc = self.uploader.get_file(
                                filename=settings.settings['summary_file'], 
                                path=settings.settings['remote_folder'])

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
                        path=os.path.join(settings.settings['sync_file'], 
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
                actual_remote_folder = settings.settings['remote_folder']
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