from __future__ import print_function

import os
import time
import subprocess

from colorama import Fore
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


DEFAULT_EXTENSIONS = ['.py']
CLEAR_COMMAND = 'cls' if os.name == 'nt' else 'clear'
BEEP_CHARACTER = '\a'


class ChangeHandler(FileSystemEventHandler):
    """Listens for changes to files and re-runs tests after each change."""
    def __init__(self, directories=[], auto_clear=False, beep_on_failure=True,
                 onpass=None, onfail=None, extensions=[]):
        super(ChangeHandler, self).__init__()
        self.directories = directories
        self.auto_clear = auto_clear
        self.beep_on_failure = beep_on_failure
        self.onpass = onpass
        self.onfail = onfail
        self.extensions = extensions or DEFAULT_EXTENSIONS

    def on_any_event(self, event):
        if event.is_directory:
            return
        ext = os.path.splitext(event.src_path)[1].lower()
        is_watch_target = self.is_watch_target(event)
        if ext in self.extensions and is_watch_target:
            self.run(event.src_path)

    def is_watch_target(self, event):
        relpath = os.path.relpath(event.src_path)
        if not self.directories:  # if directories not specified,
            return True           # any changed files are target
        else:
            for directory in self.directories:
                directory = os.path.relpath(directory + os.sep)
                if directory == '.' or \
                   relpath.startswith(os.path.relpath(directory + os.sep)):
                    return True
            return False

    def run(self, filename=None):
        """Called when a file is changed to re-run the tests with nose."""
        if self.auto_clear:
            subprocess.call(CLEAR_COMMAND, shell=True)
        elif filename:
            print()
            print(Fore.CYAN + 'Change detected in ' + filename + Fore.RESET)
        print()
        print('Running unit tests...')
        if self.auto_clear:
            print()
        pytest_cmd = 'py.test %s' % ' '.join(self.directories)
        exit_code = subprocess.call(pytest_cmd, shell=True)
        passed = exit_code == 0

        # Beep if failed
        if not passed and self.beep_on_failure:
            print(BEEP_CHARACTER, end='')

        # Run custom commands
        if passed and self.onpass:
            os.system(self.onpass)
        elif not passed and self.onfail:
            os.system(self.onfail)


def watch(directories=[], auto_clear=False, beep_on_failure=True,
          onpass=None, onfail=None, extensions=[]):
    """
    Starts a server to render the specified file or directory
    containing a README.
    """
    for directory in directories:
        if not os.path.isdir(directory):
            raise ValueError('Directory not found: ' + directory)

    # Initial run
    event_handler = ChangeHandler(directories, auto_clear, beep_on_failure,
                                  onpass, onfail, extensions)
    event_handler.run()

    # Setup watchdog
    observer = Observer()
    observer.schedule(event_handler, path=os.getcwd(), recursive=True)
    observer.start()

    # Watch and run tests until interrupted by user
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
