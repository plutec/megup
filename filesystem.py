import hashlib
import os
import sys
import stat
import pickle

#Statics
REMOVED = 0
NEW = 1
RENAMED = 2
THE_SAME = 3
FOLDER = 'FOLDER' #TODO Change to number
FILE = 'FILE' #TODO Change to number

class FileSystem(object):

    files = None

    def __init__(self, initial_path):
        self.files = list() #Must be a tree
        self.path = initial_path

    def _convert_to_relative_path(self, path):
        to_ret = '/'
        if path.find(self.path) == 0:
            to_ret = path[len(self.path):]
        if to_ret == '':
            to_ret = '/'
        return to_ret
    
    def generate(self):
        level = 0
        #Using relative path
        for root, subfolders, files in os.walk(self.path):
            #For each files
            for file_name in files:
                file_path = os.path.join(root, file_name) 
                file_obj = FileObject(
                        relative_path=self._convert_to_relative_path(root), 
                        path=file_path, 
                        level=level)
                self.files.append(file_obj)
            
            #For each subfolder
            for subfolder in subfolders:
                file_path = os.path.join(root,subfolder)
                #print "SUBFOLDER %s" % subfolder
                file_obj = FileObject(
                        relative_path=self._convert_to_relative_path(root), 
                        path=file_path, 
                        level=level)
                self.files.append(file_obj)
            level += 1

    def find_by_path(self, path):
        #Only one
        for file in self.files:
            if path == file.path:
                return file
        return None

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
    # TODO this is complicate... :P
    # Renombramientos: mismo hash, distinto path
    # First, the removed
    to_ret = dict()
    to_ret['removed_files'] = list()
    to_ret['removed_folders'] = list()
    to_ret['new_files'] = list()
    to_ret['new_folders'] = list()
    for file in old_fs.files:
        #print file.path
        res = actual_fs.find_by_path(file.path)
        if not res:
            if file.type == 'FOLDER':
                #print "REMOVED FOLDER %s" % file # Running ok
                to_ret['removed_folders'].append(file)
                file.status = REMOVED
            elif file.type == 'FILE':
                #print "REMOVED FILE %s" % file # Running ok
                to_ret['removed_files'].append(file)
                file.status = REMOVED
        elif file.hash:
            res = actual_fs.find_by_hash(file.hash)
            if res:
                file2 = None
                for file2 in res:
                    if file == file2:
                        res = file2
                if file2:
                    #print "FOUND, EXACTLY EQUAL"
                    file.status = THE_SAME
                    res.status = THE_SAME
                else:
                    pass
                    #print "NOT FOUND, pero hay uno con el mismo hash, puede ser RENOMBRAMIENTO"
            else:
                pass
                #print "NO EXISTE CON EL MISMO HASH, BORRADO/RENOMBRADO, PASANDO"
        else:
            #print "PATH CHECK"
            if file.type == 'FOLDER':
                res = actual_fs.find_by_path(file.path)
                if res:
                    #print "FOLDER FOUND"
                    file.status = THE_SAME
                    res.status = THE_SAME
                else:
                    pass
                    #print "FOLDER NOT FOUND AGAIN, NO DEBE SALIR"


                #print "ELIMINADO %s" % file
    for file in actual_fs.files:
        if not hasattr(file, 'status'):
            file.status = NEW
            if file.type == 'FOLDER':
                to_ret['new_folders'].append(file)
            elif file.type == 'FILE':
                #print "NUEVO: %s" % file
                to_ret['new_files'].append(file)

    return to_ret

def load_filesystem(filename):
    descriptor = open(filename, 'rb')
    obj = pickle.load(descriptor)
    descriptor.close()
    return obj

def load_filesystem_descriptor(descriptor):
    #descriptor = open(filename, 'rb')
    obj = pickle.load(descriptor)
    #descriptor.close()
    return obj

class FileObject(object):

    path = None
    name = None
    remote_desc = None
    level = None
    hash = None
    type = None

    def __init__(self, path, relative_path, level):
        self.path = path
        self.relative_path = relative_path
        self.level = level#len(path.split('/'))
        self.calcule_hash()
        self.calcule_type()
        #if self.type == 'FILE':
        self.name = path.split('/')[-1]
        #else:
        #    self.name = ''

    def __str__(self):
        to_ret = dict()
        to_ret['name'] = self.name
        to_ret['path'] = self.path
        to_ret['level'] = self.level
        to_ret['relative_path'] = self.relative_path
        to_ret['remote_desc'] = self.remote_desc
        to_ret['hash'] = self.hash
        to_ret['type'] = self.type
        if hasattr(self, 'status'):
            to_ret['STATUS'] = self.status

        return str(to_ret)

    def __eq__(self, other):
        if self.name != other.name:
            return False
        if self.path != other.path:
            return False
        if self.level != other.level:
            return False
        if self.hash != other.hash:
            return False
        if self.type != other.type:
            return False
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
            self.type = 'FOLDER'
        else:
            self.type = 'FILE'


def os_exists_dir(path):
    return os.path.lexists(path)

def os_empty_dir(path):
    try:
        to_ret = os.listdir(path)
    except:
        return False
    if not to_ret:
        return True
    return False

def os_mkdir(path):
    print "MKDIR: %s" % path
    try:
        os.makedirs(path)
    except:
        print "Ya existe el directorio, pasando"
        pass

def create_file(path, name, content):
    print "FOR FILE %s in path %s" % (name, path)
    try:
        os.makedirs(path) #First, directory
    except:
        print "Already exists, do nothing with dir %s" % path
        pass

    try:
        #print "CREANDO %s" % name
        desc = open(os.path.join(path,name), 'wb')
        desc.write(content)
        desc.close()
    except:
        print "Error saving file %s" % name
        pass
    print "FIN"