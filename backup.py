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


    def run(self):
        self.actual_filesystem = filesystem.FileSystem(
                                    initial_path=self.path)
        print "1 - LOAD REMOTE FS"
        self.get_remote_fs_struct()
        return
        print "GENERA ACTUAL FS"
        self.actual_filesystem.generate()
        #self.actual_filesystem.dump_to_file('fs.dmp')
        print "PREPARA BACKUP"
        self.prepare_to_init_backup()
        #self.visit_path()
        return

        print "GENERA CAMBIOS"
        print ('*'*80)
        changes = filesystem.compare_fs(actual_fs=self.actual_filesystem,
                                        old_fs=self.remote_filesystem)
        #print changes
        self.process_changes_in_remote(changes)

    def prepare_to_init_backup(self):
        self.uploader.mkdir(settings.settings['remote_folder'])

    def process_changes_in_remote(self, changes):
        print "PROCESANDO CAMBIOS EN REMOTO"
        print changes

    def upload_actual_fs_struct(self):
        pass

    def get_remote_fs_struct(self):
        file_desc = self.uploader.get_file(
                                filename=settings.settings['summary_file'], 
                                path=settings.settings['remote_folder'])

        a = self.uploader.mega.download(file=file_desc, in_descriptor=True) #Make with a function
        #print "DESCARGADO"
        self.remote_filesystem = filesystem.load_filesystem_descriptor(a)
        print self.remote_filesystem.print_in_screen()
        print "DESCARGADO FS REMOTO"

    def visit_path(self):
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
                print "SUBO %s a %s" % (fil ,actual_remote_folder)
                file_path = os.path.join(root, fil) 
                print "ORIGEN %s" % file_path
                #print file_path
                rem_desc = self.uploader.upload(actual_remote_folder, file_path)
                
            #For each subfolder
            for subfolder in subfolders:
                print "CREO carpeta %s" % actual_remote_folder+'/'+subfolder
                folder = os.path.join(actual_remote_folder, subfolder)
                rem_desc = self.uploader.mkdir(folder)
            level += 1
            print ('*'*80)

            #print root
            #print files
            #print subfolders