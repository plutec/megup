test_settings_are_overwritten_by_system_variable() {
    config_file="test.conf"
    cat >$config_file <<-EOF
[global]
dummy = foobar
EOF

    test_file="test.sh"
    cat >$test_file <<-EOF
from core import settings
assert settings.get_config('global', 'dummy') == 'foobar'
EOF

    MEGUP_CONFIG_FILE="$config_file" python $test_file
    rm $test_file $config_file
}
