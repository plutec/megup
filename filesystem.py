import hashlib
import os
import sys
import stat
import pickle

class FileSystem(object):

    files = None

    def __init__(self, initial_path):
        self.files = list()
        self.path = initial_path
    
    def generate(self):
        level = 0

        for root, subfolders, files in os.walk(self.path):
            #For each files
            for file_name in files:
                file_path = os.path.join(root, file_name) 
                file_obj = FileObject(path=file_path, level=level)
                self.files.append(file_obj)
            
            #For each subfolder
            for subfolder in subfolders:
                file_path = os.path.join(root,subfolder)
                file_obj = FileObject(path=file_path, level=level)
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

    def get_file(self, path):
        for file in self.files:
            if file.path == path:
                return file

    def print_in_screen(self):
        for file in self.files:
            print file


def compare_fs(actual_fs, old_fs):
    # TODO this is complicate... :P
    # Renombramientos: mismo hash, distinto path
    # First, the removed
    to_ret = dict()
    to_ret['removed_files'] = list()
    to_ret['removed_folders'] = list()
    for file in old_fs.files:
        print file.path
        res = actual_fs.find_by_path(file.path)
        if not res:
            if file.type == 'FOLDER':
                print "REMOVED FOLDER %s" % file # Running ok
                to_ret['removed_folders'].append(file)
            elif file.type == 'FILE':
                print "REMOVED FILE %s" % file # Running ok
                to_ret['removed_files'].append(file)
        elif file.hash:
            res = actual_fs.find_by_hash(file.hash)
            if res:
                if file in res:
                    print "FOUND, EXACTLY EQUAL"
                else:
                    print "NOT FOUND, pero hay uno con el mismo hash, puede ser RENOMBRAMIENTO"
            else:
                print "NO EXISTE CON EL MISMO HASH, BORRADO/RENOMBRADO"
        else:
            print "PATH OK"
                #print "ELIMINADO %s" % file
    # Then, the changes
    #for file in old_fs.files:
    #    if file.hash:
    #        res = actual_fs.find_by_hash
    #pass
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

    def __init__(self, path, level):
        self.path = path
        self.level = level#len(path.split('/'))
        self.calcule_hash()
        self.calcule_type()
        if self.type == 'FILE':
            self.name = path.split('/')[-1]
        else:
            self.name = ''

    def __str__(self):
        to_ret = dict()
        to_ret['name'] = self.name
        to_ret['path'] = self.path
        to_ret['level'] = self.level
        to_ret['hash'] = self.hash
        to_ret['type'] = self.type
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