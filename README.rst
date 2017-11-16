Omgircd3
========

|Travis Build Status|

This is a revamped version of
`programble/omgircd <https://github.com/programble/omgircd>`__.

It looks like the original project is not supported anymore. As an
exercise and because we love so much to reinvent the wheel, I've tried
to port this sweet IRC server to Python3 and to improve it in a way or
another.

To see the changes between upstream and this version, please read the
`CHANGES.md <CHANGES.md>`__ document. This document also contains a
mini-roadmap of the things I'd like to improve in the future.

**WARNING: This version is Python 3 only ; tested with Python 3.6.**

Omgircd3 is an Internet Relay Chat Daemon (IRCd) written in Python. It is
designed to be as simple as possible, while still providing a complete
IRC experience.

Usage
-----

As of the version ``1.0.0``, you can install ``omgircd3`` using pip::

    pip install omgircd3

It installs a console script you may want to use to instanciate your IRC
server::

    omgircd3

Optionally,you may want to create a ``config.ini`` file which will
contain your configuration variables. Copy the ``config.sample.ini``
file to create your own custom configuration, and run the following:

::

    omgircd3 --config=path/to/your/config.ini

Development mode
----------------

Once you've cloned the repository, you can use the main scripts directly,
so you don't have to pip install the source code.

::

    python omgircd3/ircd.py

Any option available for the "binary" script will also be available for the
direct scripts.


An alternative method to run Omgircd3 is using the ``ircdreload.py``
script. This launch script provides a means to reload the IRCd code on
the fly while it is running. This script is only recommended for use in
development.

::

    python omgircd3/ircdreload.py

In order to reload the IRCd code, type Control+c (``C-c``). You will
then be prompted with ``[r/q]``. Typing ``r`` at this prompt will cause
all IRCd code to be reloaded and the IRCd to continue to run. Typing
``q`` at this prompt will cause the IRCd to shut down and exit.

Additionally, if an unhandled exception occurs in the IRCd code, it will
be caught by the script and its traceback will be printed out. The same
prompt will then appear in order to give an opportunity to fix the code
and then reload the fixed code, without the server going down.

As for the ``ircd.py`` script, you can also use your configuration file:

::

    python omgircd3/ircdreload.py --config=path/to/your/config.ini

Configuration
-------------

In its current state, Omgircd3 is not very configurable. The main focus
has been to focus on getting the IRCd to run perfectly, and then make it
more configurable afterwards. The few configuration options available
are located in ``config.sample.ini``. Use this file as a template to
configure it your own way.

Logging level
"""""""""""""

By default, the logging level is set to ``INFO``. You can change this using the
``LOGGING_LEVEL`` environment variable, like this:

::

    LOGGING_LEVEL=DEBUG python omgircd3/ircd.py


Progress
--------

For documentation on development progress, see ``progress.md``.

License
-------

Copyright © 2011, Curtis McEnroe curtis@cmcenroe.me + Copyright © 2015-2017, Bruno Bord bruno@jehaisleprintemps.net

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

.. |Travis Build Status| image:: https://travis-ci.org/brunobord/omgircd3.svg?branch=master
   :target: https://travis-ci.org/brunobord/omgircd3
