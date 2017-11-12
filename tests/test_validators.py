from omgircd3.ircd import is_valid_channel_name, is_valid_nickname


def test_valid_channel_name():
    # lowercase
    assert is_valid_channel_name('meuh')
    # with numbers
    assert is_valid_channel_name('meuh42')
    # uppercase
    assert is_valid_channel_name('MEUH42')
    # lowercase with sign
    assert is_valid_channel_name('meuh!')
    # 50 chars is the limit
    assert is_valid_channel_name('a' * 50)


def test_invalid_channel_name():
    # too long
    assert not is_valid_channel_name('a' * 51)
    # too short
    assert not is_valid_channel_name('')
    # invalid character
    assert not is_valid_channel_name('méuh')


def test_valid_nickname():
    # lowercase
    assert is_valid_nickname('meuh')
    # with numbers
    assert is_valid_nickname('meuh42')
    # uppercase
    assert is_valid_nickname('MEUH42')
    # lowercase with sign
    assert is_valid_channel_name('meuh`')
    # 16 chars is the limit
    assert is_valid_nickname('a' * 16)


def test_invalid_nickname():
    # too long
    assert not is_valid_nickname('a' * 17)
    # too short
    assert not is_valid_nickname('')
    # invalid character
    assert not is_valid_nickname('méuh')
    # invalid character, bis
    assert not is_valid_nickname('meu!h')
