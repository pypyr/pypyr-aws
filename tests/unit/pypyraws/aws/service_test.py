"""service.py unit tests."""
from unittest.mock import patch
import pypyraws.aws.service as paws
import pytest
from unittest.mock import MagicMock, Mock


# ---------------------------- operation_exec --------------------------------#
@patch('boto3.client')
def test_op_exec_no_client_args(mock_boto):
    """Operation exec with no client args pass."""
    mock_boto.return_value.arbmethod.return_value = {
        'arbreturnk1': 'arbreturnv1'}

    response = paws.operation_exec(service_name='test svc',
                                   method_name='arbmethod',
                                   operation_args={'k1': 'v1', 'k2': 'v2'})

    assert response
    mock_boto.assert_called_once_with('test svc')
    mock_boto.return_value.arbmethod.assert_called_once_with(
        k1='v1', k2='v2')
    assert response == {'arbreturnk1': 'arbreturnv1'}


@patch('boto3.client')
def test_op_exec_with_client_args(mock_boto):
    """Operation exec with client args pass."""
    mock_boto.return_value.arbmethod.return_value = {
        'arbreturnk1': 'arbreturnv1'}

    response = paws.operation_exec(service_name='test svc',
                                   method_name='arbmethod',
                                   client_args={'ck1': 'cv1', 'ck2': 'cv2'},
                                   operation_args={'k1': 'v1', 'k2': 'v2'})

    assert response
    mock_boto.assert_called_once_with('test svc', ck1='cv1', ck2='cv2')
    mock_boto.return_value.arbmethod.assert_called_once_with(
        k1='v1', k2='v2')
    assert response == {'arbreturnk1': 'arbreturnv1'}


@patch('boto3.client', return_value=Mock(spec=int))
def test_op_exec_method_doesnt_exist(mock_boto):
    """Operation exec calling non existent method gets AttributeError."""
    # somewhat arbitrarily using an int as spec for client, since it
    # won't have an arbmethod.
    with pytest.raises(AttributeError) as err_info:
        paws.operation_exec(service_name='test svc',
                            method_name='arbmethod',
                            operation_args={'k1': 'v1', 'k2': 'v2'})

    assert str(err_info.value) == "Mock object has no attribute 'arbmethod'"

# ---------------------------- operation_exec --------------------------------#

# ---------------------------- waiter --------------------------------#


@patch('boto3.client')
def test_waiter_no_client_args(mock_boto):
    """waiter with no client args pass."""
    mock_waiter = MagicMock()
    mock_boto.return_value.get_waiter = mock_waiter

    paws.waiter(service_name='test svc',
                waiter_name='arbwaiter',
                wait_args={'k1': 'v1', 'k2': 'v2'})

    mock_boto.assert_called_once_with('test svc')
    mock_waiter.assert_called_once_with('arbwaiter')
    mock_waiter.return_value.wait.assert_called_once_with(k1='v1', k2='v2')


@patch('boto3.client')
def test_waiter_with_client_args(mock_boto):
    """waiter with client args pass."""
    mock_waiter = MagicMock()
    mock_boto.return_value.get_waiter = mock_waiter

    paws.waiter(service_name='test svc',
                waiter_name='arbwaiter',
                waiter_args={'wk1': 'wv1', 'wk2': 'wv2'},
                wait_args={'k1': 'v1', 'k2': 'v2'})

    mock_boto.assert_called_once_with('test svc')
    mock_waiter.assert_called_once_with('arbwaiter', wk1='wv1', wk2='wv2')
    mock_waiter.return_value.wait.assert_called_once_with(k1='v1', k2='v2')

# ---------------------------- waiter --------------------------------#
