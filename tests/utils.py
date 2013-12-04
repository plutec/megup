import os
import shutil

from core import settings


class BaseTest(object):
    local_root_dir = settings.get_config('local', 'base_directory')

    def cleanup_local_directory(self):
        shutil.rmtree(self.local_root_dir)
        os.mkdir(self.local_root_dir)

    def cleanup_remote_directory(self):
        pass

    def setup(self):
        self.cleanup_local_directory()
        self.cleanup_remote_directory()

    def teardown(self):
        self.cleanup_local_directory()
        self.cleanup_remote_directory()
