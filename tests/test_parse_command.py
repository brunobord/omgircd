from omgircd3.ircd import parse_command


def test_parse_command_basic():
    assert parse_command('CAP LS') == ['CAP', 'LS']
    assert parse_command('NICK bruno') == ['NICK', 'bruno']


def test_parse_command_colon():
    assert parse_command('USER bruno bruno 127.0.0.1 :Bruno Bord') \
        == ['USER', 'bruno', 'bruno', '127.0.0.1', 'Bruno Bord']
    assert parse_command('PRIVMSG #meuh :hello how are you?') \
        == ['PRIVMSG', '#meuh', "hello how are you?"]
    assert parse_command('PRIVMSG #meuh :do you think there is a ":"?') \
        == ['PRIVMSG', '#meuh', 'do you think there is a ":"?']
