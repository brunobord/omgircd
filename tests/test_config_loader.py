from os.path import abspath, dirname, join
from omgircd3.ircd import load_configuration


def test_no_args():
    config = load_configuration()
    assert config.get('server', 'hostname') == 'localhost'
    assert config.get('server', 'name') == 'omgircd3'
    assert config.getint('server', 'creation') == 2017
    assert config.get('server', 'bind_host') == ''
    assert config.getint('server', 'bind_port') == 6667
    assert config.get('server', 'motd') == (
        'Hello and welcome to this IRC server')
    assert config.getfloat('server', 'ping_timeout') == 250.


def test_config_file():
    config_path = join(abspath(dirname(__file__)), 'test_config.ini')
    config = load_configuration(config_path)
    assert config.get('server', 'hostname') == 'test-hostname'
    assert config.get('server', 'name') == 'test-name'
    assert config.getint('server', 'creation') == 1974
    assert config.get('server', 'bind_host') == 'test-host'
    assert config.getint('server', 'bind_port') == 66667
    assert config.get('server', 'motd') == 'test-motd'
    assert config.getfloat('server', 'ping_timeout') == 200.
