from pytest import fixture
from omgircd3.ircd import Server, load_configuration


class MockChannel(object):
    def __init__(self, name):
        self.name = name


@fixture
def config():
    return load_configuration()


@fixture
def server(config):
    return Server(config)


def test_channel_finder(server):
    assert len(server.channels) == 0
    assert not server.find_channel('meuh')
    # Add a channel to the channel list
    channel_meuh = MockChannel('meuh')
    server.add_channel(channel_meuh)
    assert server.find_channel('meuh') == channel_meuh
    assert not server.find_channel('moo')
    # Remove meuh
    server.remove_channel(channel_meuh)
    assert not server.find_channel('meuh')
