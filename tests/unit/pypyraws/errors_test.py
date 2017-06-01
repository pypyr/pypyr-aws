"""errors.py unit tests."""
from pypyr.errors import Error as PypyrError
from pypyr.errors import PlugInError
from pypyraws.errors import Error as PypyrAwsError
from pypyraws.errors import WaitTimeOut
import pytest


def test_base_error_raises():
    """Pypyr root Error raises with correct message."""
    with pytest.raises(PypyrAwsError) as err_info:
        raise PypyrAwsError("this is error text right here")

    assert repr(err_info.value) == ("Error('this is error text "
                                    "right here',)")


def test_wait_timeout_raises():
    """Aws WaitTimeOut error raises with correct message."""
    with pytest.raises(WaitTimeOut) as err_info:
        raise WaitTimeOut("this is error text right here")

    assert repr(err_info.value) == ("WaitTimeOut('this is error "
                                    "text right here',)")


def test_wait_timeout_inheritance():
    """WaitTimeOut should inherit all the way up to pypyr Error."""
    # confirm subclassed from pypyr root error
    err = WaitTimeOut()
    assert isinstance(err, PypyrAwsError)
    assert isinstance(err, PlugInError)
    assert isinstance(err, PypyrError)
