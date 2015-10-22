Omgircd
=======

*Note: I'm currently trying to put this a bit up-to-date. I'm not sure it's going somewhere, please bear with me.*

This project was originally available at [programble/omgircd](https://github.com/programble/omgircd).

Omgircd is an Internet Relay Chat Daemon (IRCd) written in Python. It
is designed to be as simple as possible, while still providing a
complete IRC experience.

Usage
-----

Before running this program, you may want to create a `config.py` file which
will contain your configuration variables. Copy the `config.sample.py` file to
create your own custom configuration.

Omgircd is still in development and therefore does not have a complete
launch script. The simplest way to launch Omgircd for now is to simply
run `ircd.py`

    python ircd.py

An alternative method to run Omgircd is using the `ircdreload.py`
script. This launch script provides a means to reload the IRCd code on
the fly while it is running. This script is only recommended for use
in development.

    python ircdreload.py

In order to reload the IRCd code, type Control+c (`C-c`). You will then
be prompted with `[r/q]`. Typing `r` at this prompt will cause all
IRCd code to be reloaded and the IRCd to continue to run. Typing `q`
at this prompt will cause the IRCd to shut down and exit.

Additionally, if an unhandled exception occurs in the IRCd code, it
will be caught by the script and its traceback will be printed
out. The same prompt will then appear in order to give an opportunity
to fix the code and then reload the fixed code, without the server
going down.

Configuration
-------------

In its current state, Omgircd is not very configurable. The main focus
has been to focus on getting the IRCd to run perfectly, and then make
it more configurable afterwards. The few configuration options
available are located in `config.py`.

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
