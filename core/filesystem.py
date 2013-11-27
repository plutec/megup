import hashlib
#Externals
import os
import sys
import stat
import pickle
import time

#Internals
from core.logger import log

#Statics
REMOVED = 0
NEW = 1
RENAMED = 2
THE_SAME = 3
FOLDER = 4
FILE = 5
NEWEST = 6
OLDEST = 7

class FileSystem(object):

    files = None

    def __init__(self, initial_path):
        self.files = list() #Must be a tree
        self.path = initial_path

    def _extract_relative_path(self, path):
        to_ret = ''
        if path.find(self.path) == 0:
            to_ret = path[len(self.path):]
        if not to_ret:
            to_ret = ''
        #elif to_ret[-1] != '/':
        #    to_ret = '%s/' % to_ret

        return to_ret
    
    def calculate_level(self, absolute_path):
        to_ret = 1
        if absolute_path.find(self.path) == 0:
            path = absolute_path[len(self.path):]
        len_path = len(path.split('/'))
        if path != '':
            to_ret = len_path + 1
        
        return to_ret

    def generate(self):
        #Using relative path
        for root, subfolders, files in os.walk(self.path):
            #Calculate level
            level = self.calculate_level(root)
            #For each files
            for file_name in files:
                file_path = os.path.join(root, file_name) 
                file_obj = FileObject(
                        relative_path=self._extract_relative_path(root), 
                        path=file_path, 
                        level=level)
                self.files.append(file_obj)
            
            #For each subfolder
            for subfolder in subfolders:
                file_path = os.path.join(root,subfolder)
                #print "SUBFOLDER %s" % subfolder
                file_obj = FileObject(
                        relative_path=self._extract_relative_path(root), 
                        path=file_path, 
                        level=level)
                self.files.append(file_obj)

        log.debug("Tree generated")
        #for file in self.files:
        #    log.debug(file)

    def find_by_path(self, path, filetype=None):
        #Several files
        to_ret = list()
        if filetype:
            for file in self.files:
                if path == file.relative_path and file.type == filetype:
                    to_ret.append(file)
        else:
            for file in self.files:
                if path == file.relative_path:
                    to_ret.append(file)
        return to_ret
        
    def find_by_path_name(self, path, name, filetype=None):
        to_ret = list()
        files = self.find_by_path(path=path, filetype=filetype)
        for file in files:
            if file.name == name:
                to_ret.append(file)
                #Only must be one, but not break...

        return to_ret

    def find_by_hash(self, hash):
        #Maybe more than one
        to_ret = list()
        for file in self.files:
            if hash == file.hash:
                to_ret.append(file)
        return to_ret

    def dump_to_file(self, filename):
        descriptor = open(filename, 'wb')
        pickle.dump(self, descriptor)
        descriptor.close()
        
    def get_dump(self):
        return pickle.dumps(self)

    def get_file(self, path):
        for file in self.files:
            if file.path == path:
                return file

    def print_to_screen(self):
        for file in self.files:
            print file


def compare_fs(actual_fs, old_fs):

    to_ret = dict()
    to_ret['removed_files'] = list()
    to_ret['removed_folders'] = list()
    to_ret['new_files'] = list()
    to_ret['new_folders'] = list()
    to_ret['to_upload'] = list()
    to_ret['to_download'] = list()

    #for file in old_fs.files:
    #    print file
    #print "FIN ARBOL ANTIGUO"
    #return to_ret
    #Estados diferentes:
    """
    - Folders: 
        - New, OK
        - Deleted, OK
        - The same, OK
    - Ficheros: 
        - New, OK
        - Changed, OK
        - Deleted, OK
        - The same, OK

    """
    for file in old_fs.files:
        if file.type == FOLDER:
            #Find by path only
            #print "CARPETA %s" % file
            res = actual_fs.find_by_path_name(path=file.relative_path, 
                                              name=file.name,
                                              filetype=FOLDER)
            #print res
            if res:
                #print "RES %s" % res[0]
                for folder in res:
                    if file == folder:
                        #print "Encontrada"
                        file.status = THE_SAME
                        folder.status = THE_SAME
            else: #Not res
                file.status = REMOVED
                to_ret['removed_folders'].append(file)
                
        elif file.type == FILE:
            #Find by hash/path
            res_hash = actual_fs.find_by_hash(file.hash)
            found = False
            #If hash is the same and path too, it's the same file
            for file2 in res_hash:
                if file2.relative_path == file.relative_path:
                    file.status = THE_SAME
                    file2.status = THE_SAME
                    found = True
                    #break
            if not found: #Not the same hash, maybe change or deleted
                #Find by path/name
                res_path = actual_fs.find_by_path_name(
                                                    path=file.relative_path,
                                                    name=file.name,
                                                    filetype=FILE)
                if res_path:
                    if len(res_path) > 1:
                        log.critical(
                               "More than one file with the same path/name")
                    #File changed
                    found = False
                    for file2 in res_path:
                        if file.name == file2.name: #Changed content
                            if file > file2:
                                file.status = NEWEST
                                file2.status = OLDEST
                                to_ret['to_download'].append(file)
                            elif file < file2:
                                file.status = OLDEST
                                file2.status = NEWEST
                                to_ret['to_upload'].append(file2)
                            found = True
                            #break

                if not found:
                    #Removed
                    file.status = REMOVED
                    to_ret['removed_files'].append(file)            

    #For not marked in previous loop
    for file in actual_fs.files:
        if not hasattr(file, 'status'):
            file.status = NEW
            if file.type == FOLDER:
                to_ret['new_folders'].append(file)
            elif file.type == FILE:
                #print "NUEVO: %s" % file
                to_ret['new_files'].append(file)

    return to_ret

def load_filesystem(filename):
    """
    Load a FileSystem object from a file
    Params:
        - filename, str with the complete path of object. This maybe contains 
            a FileSystem serialized with pickle
    Return:
        FileSystem object in memory.
    """
    descriptor = open(filename, 'rb')
    obj = pickle.load(descriptor)
    descriptor.close()
    return obj

def load_filesystem_descriptor(descriptor):
    """
    Load a FileSystem object from a descriptor
    Params:
        - descriptor, File object with FileSystem object serialized with pickle
    Return:
        FileSystem object in memory.
    """
    obj = pickle.load(descriptor)
    return obj

class FileObject(object):

    path = None
    relative_path = None
    name = None
    remote_desc = None
    level = None
    hash = None
    type = None
    change_time = None

    def __init__(self, path, relative_path, level):
        self.path = path
        self.relative_path = relative_path
        self.level = level
        self.calcule_hash()
        self.calcule_type()
        self.name = path.split('/')[-1]
        self.last_modified = os.stat(self.path).st_mtime

    def __str__(self):
        to_ret = dict()
        to_ret['name'] = self.name
        to_ret['path'] = self.path
        to_ret['level'] = self.level
        to_ret['relative_path'] = self.relative_path
        to_ret['remote_desc'] = self.remote_desc
        to_ret['hash'] = self.hash
        to_ret['type'] = self.type
        to_ret['last_modified'] = self.last_modified
        if hasattr(self, 'status'):
            to_ret['STATUS'] = self.status

        return str(to_ret)
    def __gt__(self, other):
        if self.last_modified > other.last_modified:
            return True
        return False

    def __lt__(self, other):
        if self.last_modified < other.last_modified:
            return True
        return False
        
    def __eq__(self, other):
        if self.name != other.name:
            return False
        if self.relative_path != other.relative_path:
            return False
        if self.level != other.level:
            return False
        if self.hash != other.hash:
            return False
        if self.type != other.type:
            return False
        #if self.last_modified != other.last_modified:
        #    return False
        return True

    def calcule_hash(self):
        """
        Calcule md5 hash of file
        """
        try:
            descriptor = open(os.path.join(self.path), 'rb')
            m = hashlib.md5()
            for content in descriptor.read(256):
                m.update(content)
            
            self.hash = m.hexdigest()
        except:
            self.hash = None


    def calcule_type(self):

        mode = os.stat(os.path.join(self.path)).st_mode
        if stat.S_ISDIR(mode):
            self.type = FOLDER
        else:
            self.type = FILE


def os_exists_dir(path):
    return os.path.lexists(path)

def os_empty_dir(path):
    try:
        to_ret = os.listdir(path)
    except:
        return True
    if not to_ret:
        return True
    return False

def os_mkdir(path):
    log.debug("MKDIR: %s" % path)
    try:
        os.makedirs(path)
    except:
        log.debug("Directory already exists, do nothing")
        pass

def create_file(path, name, content):
    try:
        os.makedirs(path) #First, directory
    except:
        log.debug("Already exists, do nothing with dir %s" % path)
        pass

    try:
        #print "CREANDO %s" % name
        #print "PATH %s NAME %s" % (path, name)
        desc = open(os.path.join(path,name), 'wb')
        desc.write(content)
        desc.close()
    except Exception, why:
        log.critical("Error saving file %s. Reason %s" % (name, why))
        