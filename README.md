Omgircd
=======

[![Travis Build Status](https://travis-ci.org/brunobord/omgircd.svg?branch=master)](https://travis-ci.org/brunobord/omgircd)

This is a revamped version of [programble/omgircd](https://github.com/programble/omgircd).

It looks like the original project is not supported anymore. As an exercise and
because we love so much to reinvent the wheel, I've tried to port this sweet
IRC server to Python3 and to improve it in a way or another.

To see the changes between upstream and this version, please read the
[CHANGES.md](CHANGES.md) document. This document also contains a mini-roadmap
of the things I'd like to improve in the future.

**WARNING: This version is Python 3 only ; tested with Python 3.6.**

Omgircd is an Internet Relay Chat Daemon (IRCd) written in Python. It
is designed to be as simple as possible, while still providing a
complete IRC experience.

Usage
-----

Omgircd is still in development and therefore does not have a complete
launch script. The simplest way to launch Omgircd for now is to simply
run `ircd.py`

    python omgircd3/ircd.py

Optionally,you may want to create a `config.ini` file which will contain your
configuration variables. Copy the `config.sample.ini` file to create your own
custom configuration, and run the following:

    python omgircd3/ircd.py --config=path/to/your/config.ini

An alternative method to run Omgircd is using the `ircdreload.py`
script. This launch script provides a means to reload the IRCd code on
the fly while it is running. This script is only recommended for use
in development.

    python omgircd3/ircdreload.py

In order to reload the IRCd code, type Control+c (`C-c`). You will then
be prompted with `[r/q]`. Typing `r` at this prompt will cause all
IRCd code to be reloaded and the IRCd to continue to run. Typing `q`
at this prompt will cause the IRCd to shut down and exit.

Additionally, if an unhandled exception occurs in the IRCd code, it
will be caught by the script and its traceback will be printed
out. The same prompt will then appear in order to give an opportunity
to fix the code and then reload the fixed code, without the server
going down.

As for the `ircd.py` script, you can also use your configuration file:

    python omgircd3/ircdreload.py --config=path/to/your/config.ini


Configuration
-------------

In its current state, Omgircd is not very configurable. The main focus
has been to focus on getting the IRCd to run perfectly, and then make
it more configurable afterwards. The few configuration options
available are located in `config.sample.ini`. Use this file as a template to
configure it your own way.

Progress
--------

For documentation on development progress, see `progress.md`.

License
-------

Copyright © 2011, Curtis McEnroe <curtis@cmcenroe.me>
Copyright © 2015, Bruno Bord <bruno@jehaisleprintemps.net>

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
