"""Version information."""

import platform

__version__ = '1.3.0'


def get_version():
    """Return package-name __version__ python python_version."""
    return (f'pypyraws {__version__} '
            f'python {platform.python_version()}')


if __name__ == '__main__':
    """Entry point for script execution.

    Makes it easy to get version number from cli from outside the package.
    """
    print(__version__)
