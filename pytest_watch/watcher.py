import os
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


default_extensions = ['.py']


class ChangeHandler(FileSystemEventHandler):
    """Listens for changes to files and re-runs tests after each change."""
    def __init__(self, directories, options):
        super(ChangeHandler, self).__init__()
        self.directories = directories
        self.options = options

    def on_any_event(self, event):
        if event.is_directory:
            return
        ext = os.path.splitext(event.src_path)[1].lower()
        relpath = os.path.relpath(event.src_path)
        is_target = False
        for directory in self.directories:
            if relpath.startswith(directory + os.sep):
                is_target = True
                break
        if ext in self.options.get('extensions') and is_target:
            self.run()

    def run(self):
        """Called when a file is changed to re-run the tests with pytest."""
        banner = 'Running unit tests...'
        if self.options.get('clear'):
            os.system('cls' if os.name == 'nt' else 'clear')
            print(banner, '\n')
        else:
            print(banner)
        pytest_opts = self.options.get('pytest_opts')
        directories = ' '.join(self.directories)
        pytest_cmd = 'py.test %s %s' % (pytest_opts, directories)
        returncode = subprocess.call(pytest_cmd, shell=True)
        passed = (returncode == 0)

        onpass = self.options.get('triggers').get('onpass')
        onfail = self.options.get('triggers').get('onfail')
        if passed and onpass:
            os.system(onpass)
        elif not passed and onfail:
            os.system(onfail)


def watch(directories, pytest_opts, clear, triggers, extensions=[]):
    """Starts an observer as watcher"""

    options = dict(
        pytest_opts=pytest_opts,
        clear=clear,
        triggers=triggers,
        extensions=extensions or default_extensions,
    )

    # Initial run
    event_handler = ChangeHandler(directories, options)
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
