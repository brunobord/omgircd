# Changelog

## master (unreleased)

- Added a test to make sure the README.rst is syntactically correct.

## 1.0.0 (2017-11-16)

Here's a list of the changes made from [upstream](https://github.com/programble/omgircd).

* PEP8 support ; tested using `flake8`.
* refactored several methods/functions (`handle_recv`, nickname check, `handle_PRIVMSG`, `handle_NOTICE`, `handle_JOIN`).
* Added logging messages (still WIP).
* Ported `ircd.py` and `ircreload.py` to Python 3 (only tested using python 3.6 at the moment).
* Better `find_channel` and `find_user` functions (cleaner and optimized).
* Better nickname validation and channel name validation functions (cleaner and optimized).
* Changed the configuration loading (using the good'ol' `ConfigParser` module).
* Now the `PING` timeout time a configurable parameter.
* test infrastructure & adding tests (WIP).
* Travis CI setup.
* Rename this fork omgircd3
* Build a package and upload it on PyPI.
* Logging level is now configurable (via an environment variable)
* Added debug messages for User events.
