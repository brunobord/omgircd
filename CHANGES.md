# Changes

## Changelog

Changes from [upstream](https://github.com/programble/omgircd).

* PEP8 support ; tested using `flake8`.
* refactored several methods/functions (`handle_recv`, nickname check, `handle_PRIVMSG`, `handle_NOTICE`, `handle_JOIN`).
* Added logging messages (still WIP).
* Ported `ircd.py` and `ircreload.py` to Python 3 (only tested using python 3.6 at the moment).
* Better `find_channel` and `find_user` functions (cleaner and optimized).
* Better nickname validation and channel name validation functions (cleaner and optimized).
* Changed the configuration loading (using the good'ol' `ConfigParser` module).
* Now the `PING` timeout time a configurable parameter.

## Roadmap

* test infrastructure.
* Add tests for... everything? (the goal is to cover at least the `User` + `Channel` + `Server` classes).
* Python3 test grid to test against different Python versions.
* Log more things more seriously (that helps so much for debugging).
* Changes channels and users properties and make them faster (dicts over lists).
* Build a package and upload it on PyPI. Maybe rename this as `omgircd3`?
* Take the [progress.md](progress.md) document and try to work on the missing commands.

### Things that WON'T change

* Stick to using only the standard library.
