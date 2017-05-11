"""version.py unit tests."""
import pypyraws.version
import platform


def test_get_version():
    actual = pypyraws.version.get_version()
    expected = (f'pypyraws {pypyraws.version.__version__} '
                f'python {platform.python_version()}')
    assert actual == expected, "version not returning correctly"
