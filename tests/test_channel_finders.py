from pytest import fixture
from omgircd3.ircd import Channel


class MockUser(object):
    def __init__(self, nickname, *args, **kwargs):
        self.nickname = nickname


@fixture
def channel():
    return Channel("test")


def test_channel_finder(channel):
    assert len(channel.users) == 0
    assert not channel.find_user('meuh')
    # Add a user to the user list
    user_meuh = MockUser('meuh')
    channel.add_user(user_meuh)
    assert channel.find_user('meuh') == user_meuh
    assert not channel.find_user('moo')
    # Remove meuh
    channel.remove_user(user_meuh)
    assert not channel.find_user('meuh')
