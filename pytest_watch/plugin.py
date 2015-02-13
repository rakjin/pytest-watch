

def pytest_addoption(parser):
    """Add options to watch."""

    group = parser.getgroup('watch directories and run testing continually')
    group.addoption('--watch', action='store_true', default=False,
                    dest='watch',
                    help='enable watching')
    group.addoption('--watch-dir', action='append',
                    dest='watch-dir',
                    help='watch specified directory')


def pytest_configure(config):
    """Activate watch plugin if appropriate."""
    watch_dirs = []
    if config.getoption('watch'):
        watch_dirs.append(config.getoption('file_or_dir'))
    if config.getoption('watch-dir'):
        watch_dirs.append(config.getoption('watch-dir'))
    print(watch_dirs)

