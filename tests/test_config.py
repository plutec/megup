import os

from core import settings


class TestSettings:
    def setup(self):
        self.config_path = 'test_settings.conf'
        with open(self.config_path, 'w') as f:
            f.write('[global]\n'
                    'test_key = made_up')
        settings.set_config_file(self.config_path)

    def teardown(self):
        os.remove(self.config_path)

    def test_parse_custom_config(self):
        expected_value = 'made_up'
        actual_value = settings.get_config('global', 'test_key')
        assert actual_value == expected_value, (
            'Exepected to get %s, got %s' % (expected_value, actual_value))
