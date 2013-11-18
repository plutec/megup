import settings
import mega as mega_library

class UploaderMega(object):
    """
    This class is use for managing files and folders with mega
    """

    mega = None
    def __init__(self):
        """
        Constructor
        """
        self.mega = mega_library.Mega({'verbose':
                                            settings.settings['mega_verbose']})
        self.mega.login(email=settings.settings['mega_mail'],
                            password=settings.settings['mega_passw'])

    def upload(self, path, filename):
        """
        Upload a file to Mega
        Params:
            self, the object
            path, string with remote path
            filename, string with path and filename in local
        Return:
            Nothing
        """
        # Save in mega in folder 'path' with the original name
        folder = self.mega.find_path_descriptor(path)
        if not folder:
            folder = self.mkdir(path)
            
        data = self.mega.upload(filename=filename, dest=folder)
        #print data
        return data['f'][0]['h']
    
    def upload_raw(self, path, filename, raw):
        """
        Upload raw data to mega
        Params:
            self, the object
            path, string with remote path
            filename, string with the desire remote name
            raw, str with bytes
        """
        folder = self.mega.find_path_descriptor(path)
        if not folder:
            folder = self.mkdir(path)

        data = self.mega.upload_raw(raw=raw, raw_name=filename, dest=folder)
        return data['f'][0]['h']

    def remove(self, path, filename):
        #First, find file
        desc = self.get_file(path=path, filename=filename)
        if desc:
            print path
            print filename
            print desc
            self.mega.destroy(desc)
            return True
        else:
            #print "FILE %s/%s NOT FOUND FOR DELETE" % (path, filename)
            return False
    def get_file(self, filename, path):
        #Find parent
        parent_desc = self.mega.find_path_descriptor(path=path)
        #Find filename in parent
        to_ret = self.mega.find(filename=filename, parent=parent_desc)
        return to_ret

    def get_user_info(self):
        """
        Obtain mega user information in json format
        """
        details = self.mega.get_user() #Make up this data. :)
        return details

    def find_folder(self, foldername):
        """
        Find a folder in mega.
        Params:
            self, the object
            foldername, string with the name of folder
        Return:
            dictionary with information about the folder
        """
        return self.mega.find_folder(foldername)
        
    def mkdir(self, dirname):
        """
        Create a remote folder
        Params:
            dirname: string with the complete path (i.e.: pepito/lechuga/fria)
        Returns:
            dirname descriptor
        """
        folders = dirname.split('/')
        parent_desc = self.mega.get_root_descriptor()
        for folder in folders:
            #Exists folder with this parent?
            exists = self.mega.find_folder(folder, parent=parent_desc)
            if not exists:
                data = self.mega.create_folder(folder, parent_desc)
                parent_desc = data['f'][0]['h']
            else:
                parent_desc = exists[0]
        return parent_desc

    def get_content(self, remote_descriptor):
        file_desc = self.mega.download_by_desc(file=remote_descriptor, 
                                                            in_descriptor=True)
        return file_desc.read()
    def exists_dir(self, dirname):
        """
        Check if a directory exists in mega
        Params:
            self, the object
            dirname, string with complete remote path
        TODO:
            check if running properly
        """
        if self.mega.find_path_descriptor(dirname):
            return True
        return False

    def free_space(self):
        """
        Obtain the remote space left in Mega
        """
        return self.mega.get_storage_space()#bytes=True)

