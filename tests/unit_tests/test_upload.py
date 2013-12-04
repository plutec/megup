import os

from tests.utils import BaseTest
from core.mega import Mega


class TestDirectories(BaseTest):    
    def test_create_folder(self):
        os.mkdir(os.path.join(self.local_root_dir, 'dir1'))
        mega_wrapper = Mega()
        mega_wrapper.login()
        mega_wrapper.create_folder('dir1')
        remote_files = mega_wrapper.get_files()
        assert remote_files  # How the hell am I supposed to check that dir1 is there?
