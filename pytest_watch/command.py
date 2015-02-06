"""\
pytest_watch.command
~~~~~~~~~~~~~~~~~~~~

Implements the command-line interface for pytest-watch.


Usage:
  ptw [options] [<directory> ...]

Options:
  -h --help                Show this help.
  --version                Show version.
  -c --clear               Automatically clear the screen before each run.
  --onpass=<cmd>           Run arbitrary programs on pass.
  --onfail=<cmd>           Run arbitrary programs on failure.
  --pytest-options=<opts>  Options passed to py.test as-is
"""

import sys
from docopt import docopt
from .watcher import watch
from . import __version__


def main(argv=None):
    """The entry point of the application."""
    if argv is None:
        argv = sys.argv[1:]
    usage = '\n\n\n'.join(__doc__.split('\n\n\n')[1:])
    version = 'pytest-watch ' + __version__

    # Parse options
    args = docopt(usage, argv=argv, version=version)

    # Get options
    directories = args['<directory>'] or []
    pytest_opts = args['--pytest-options'] or ''
    clear = args['--clear']
    triggers = dict(
      onpass=args['--onpass'],
      onfail=args['--onfail'],
    )

    # Execute
    return watch(directories, pytest_opts, clear, triggers)
