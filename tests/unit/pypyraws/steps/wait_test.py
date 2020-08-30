"""wait.py unit tests."""
from unittest.mock import patch
from pypyr.context import Context
from pypyr.errors import KeyInContextHasNoValueError, KeyNotInContextError
import pypyraws.steps.wait as wait
import pytest


# ---------------------------- run_step -------------------------------------#

def test_aws_wait_missing_awswaitin():
    """Missing awsClientIn raises."""
    context = Context({'k1': 'v1'})

    with pytest.raises(KeyNotInContextError) as err_info:
        wait.run_step(context)

    assert str(err_info.value) == (
        "awsWaitIn missing required key for pypyraws.steps.wait: "
        "awsWaitIn not found in the pypyr context.")


@patch('pypyraws.aws.service.waiter')
def test_aws_wait_pass_no_args(mock_waiter):
    """Successful run with no client args."""
    context = Context({
        'k1': 'v1',
        'awsWaitIn': {
            'serviceName': 'service name',
            'waiterName': 'waiter_name',
            'arbKey': 'arb_value'
        }})
    wait.run_step(context)

    assert len(context) == 2
    assert context['k1'] == 'v1'
    assert context['awsWaitIn'] == {
        'serviceName': 'service name',
        'waiterName': 'waiter_name',
        'arbKey': 'arb_value'
    }

    mock_waiter.assert_called_once_with(service_name='service name',
                                        waiter_name='waiter_name',
                                        waiter_args=None,
                                        wait_args=None,
                                        )


@patch('pypyraws.aws.service.waiter')
def test_aws_wait_pass_waiter_args(mock_waiter):
    """Successful run with waiter args."""
    context = Context({
        'k1': 'v1',
        'awsWaitIn': {
            'serviceName': 'service name',
            'waiterName': 'waiter_name',
            'arbKey': 'arb_value',
            'waiterArgs': {'ck1': 'cv1', 'ck2': 'cv2'}
        }})
    wait.run_step(context)

    assert len(context) == 2
    assert context['k1'] == 'v1'
    assert context['awsWaitIn'] == {
        'serviceName': 'service name',
        'waiterName': 'waiter_name',
        'arbKey': 'arb_value',
        'waiterArgs': {'ck1': 'cv1', 'ck2': 'cv2'}
    }

    mock_waiter.assert_called_once_with(service_name='service name',
                                        waiter_name='waiter_name',
                                        waiter_args={'ck1': 'cv1',
                                                     'ck2': 'cv2'},
                                        wait_args=None,
                                        )


@patch('pypyraws.aws.service.waiter')
def test_aws_waiter_pass_wait_args(mock_waiter):
    """Successful run with wait args."""
    context = Context({
        'k1': 'v1',
        'awsWaitIn': {
            'serviceName': 'service name',
            'waiterName': 'waiter_name',
            'arbKey': 'arb_value',
            'waitArgs': {'mk1': 'mv1', 'mk2': 'mv2'}
        }})
    wait.run_step(context)

    assert len(context) == 2
    assert context['k1'] == 'v1'
    assert context['awsWaitIn'] == {
        'serviceName': 'service name',
        'waiterName': 'waiter_name',
        'arbKey': 'arb_value',
        'waitArgs': {'mk1': 'mv1', 'mk2': 'mv2'}
    }

    mock_waiter.assert_called_once_with(service_name='service name',
                                        waiter_name='waiter_name',
                                        waiter_args=None,
                                        wait_args={'mk1': 'mv1',
                                                    'mk2': 'mv2'},
                                        )


@patch('pypyraws.aws.service.waiter')
def test_aws_client_pass_all_args(mock_waiter):
    """Successful run with waiter and wait args."""
    context = Context({
        'k1': 'v1',
        'awsWaitIn': {
            'serviceName': 'service name',
            'waiterName': 'waiter_name',
            'arbKey': 'arb_value',
            'waiterArgs': {'ck1': 'cv1', 'ck2': 'cv2'},
            'waitArgs': {'mk1': 'mv1', 'mk2': 'mv2'}
        }})
    wait.run_step(context)

    assert len(context) == 2
    assert context['k1'] == 'v1'
    assert context['awsWaitIn'] == {
        'serviceName': 'service name',
        'waiterName': 'waiter_name',
        'arbKey': 'arb_value',
        'waiterArgs': {'ck1': 'cv1', 'ck2': 'cv2'},
        'waitArgs': {'mk1': 'mv1', 'mk2': 'mv2'}
    }

    mock_waiter.assert_called_once_with(service_name='service name',
                                        waiter_name='waiter_name',
                                        waiter_args={'ck1': 'cv1',
                                                     'ck2': 'cv2'},
                                        wait_args={'mk1': 'mv1',
                                                    'mk2': 'mv2'},
                                        )


@patch('pypyraws.aws.service.waiter')
def test_aws_client_pass_all_args_substitutions(mock_waiter):
    """Successful run with waiter and wait args substitutions."""
    context = Context({
        'k1': 'v1',
        'k2': 'v2',
        'k3': 'v3',
        'k4': 'v4',
        'k5': 'v5',
        'awsWaitIn': {
            'serviceName': 'service name {k1}',
            'waiterName': '{k2} waiter_name',
            'arbKey': 'arb_value',
            'waiterArgs': {'ck1 {k3}': 'cv1', 'ck2': '{k4} cv2'},
            'waitArgs': {'mk1': 'mv1', '{k5} mk2': 'mv2'}
        }})
    wait.run_step(context)

    assert len(context) == 6
    assert context['k1'] == 'v1'
    assert context['awsWaitIn'] == {
        'serviceName': 'service name {k1}',
        'waiterName': '{k2} waiter_name',
        'arbKey': 'arb_value',
        'waiterArgs': {'ck1 {k3}': 'cv1', 'ck2': '{k4} cv2'},
        'waitArgs': {'mk1': 'mv1', '{k5} mk2': 'mv2'}
    }

    mock_waiter.assert_called_once_with(service_name='service name v1',
                                        waiter_name='v2 waiter_name',
                                        waiter_args={'ck1 v3': 'cv1',
                                                     'ck2': 'v4 cv2'},
                                        wait_args={'mk1': 'mv1',
                                                    'v5 mk2': 'mv2'},
                                        )


@patch('pypyraws.aws.service.waiter')
def test_aws_client_pass_no_waiterargs_substitutions(mock_waiter):
    """Successful run with no waiter, but with wait args substitutions."""
    context = Context({
        'k1': 'v1',
        'k2': 'v2',
        'k3': 'v3',
        'k4': 'v4',
        'k5': 'v5',
        'awsWaitIn': {
            'serviceName': 'service name {k1}',
            'waiterName': '{k2} waiter_name',
            'arbKey': 'arb_value',
            'waitArgs': {'mk1': 'mv1', '{k5} mk2': 'mv2'}
        }})
    wait.run_step(context)

    assert len(context) == 6
    assert context['k1'] == 'v1'
    assert context['awsWaitIn'] == {
        'serviceName': 'service name {k1}',
        'waiterName': '{k2} waiter_name',
        'arbKey': 'arb_value',
        'waitArgs': {'mk1': 'mv1', '{k5} mk2': 'mv2'}
    }

    mock_waiter.assert_called_once_with(service_name='service name v1',
                                        waiter_name='v2 waiter_name',
                                        waiter_args=None,
                                        wait_args={'mk1': 'mv1',
                                                    'v5 mk2': 'mv2'},
                                        )


@patch('pypyraws.aws.service.waiter')
def test_aws_client_pass_no_waitargs_substitutions(mock_waiter):
    """Successful run with waiter but no wait args substitutions."""
    context = Context({
        'k1': 'v1',
        'k2': 'v2',
        'k3': 'v3',
        'k4': 'v4',
        'k5': 'v5',
        'awsWaitIn': {
            'serviceName': 'service name {k1}',
            'waiterName': '{k2} waiter_name',
            'arbKey': 'arb_value',
            'waiterArgs': {'ck1 {k3}': 'cv1', 'ck2': '{k4} cv2'}
        }})
    wait.run_step(context)

    assert len(context) == 6
    assert context['k1'] == 'v1'
    assert context['awsWaitIn'] == {
        'serviceName': 'service name {k1}',
        'waiterName': '{k2} waiter_name',
        'arbKey': 'arb_value',
        'waiterArgs': {'ck1 {k3}': 'cv1', 'ck2': '{k4} cv2'}
    }

    mock_waiter.assert_called_once_with(service_name='service name v1',
                                        waiter_name='v2 waiter_name',
                                        waiter_args={'ck1 v3': 'cv1',
                                                     'ck2': 'v4 cv2'},
                                        wait_args=None
                                        )


@patch('pypyraws.aws.service.waiter')
def test_aws_client_pass_no_opt_args_substitutions(mock_waiter):
    """Successful run with no optional args substitutions."""
    context = Context({
        'k1': 'v1',
        'k2': 'v2',
        'k3': 'v3',
        'k4': 'v4',
        'k5': 'v5',
        'awsWaitIn': {
            'serviceName': 'service name {k1}',
            'waiterName': '{k2} waiter_name',
            'arbKey': 'arb_value'
        }})
    wait.run_step(context)

    assert len(context) == 6
    assert context['k1'] == 'v1'
    assert context['awsWaitIn'] == {
        'serviceName': 'service name {k1}',
        'waiterName': '{k2} waiter_name',
        'arbKey': 'arb_value'
    }

    mock_waiter.assert_called_once_with(service_name='service name v1',
                                        waiter_name='v2 waiter_name',
                                        waiter_args=None,
                                        wait_args=None
                                        )

# ---------------------------- run_step -------------------------------------#

# ---------------------------- get_waiter_args------------------------------#


def test_get_waiter_args_pass():
    """get_service_args pass."""
    context = Context({
        'k1': 'v1',
        'awsWaitIn': {
            'serviceName': 'service name',
            'waiterName': 'waiter_name',
            'arbKey': 'arb_value'
        }})
    client_in, service_name, waiter_name = wait.get_waiter_args(
        context)

    assert client_in == {
        'serviceName': 'service name',
        'waiterName': 'waiter_name',
        'arbKey': 'arb_value'
    }
    assert service_name == 'service name'
    assert waiter_name == 'waiter_name'


def test_get_waiter_args_missing_awswaitin():
    """Missing awsWaiterIn raises."""
    context = Context({'k1': 'v1'})

    with pytest.raises(KeyNotInContextError) as err_info:
        client_in, service_name, waiter_name = wait.get_waiter_args(
            context)

    assert str(err_info.value) == (
        "awsWaitIn missing required key for pypyraws.steps.wait: "
        "awsWaitIn not found in the pypyr context.")


def test_get_waiter_args_missing_servicename():
    """Missing serviceName raises."""
    context = Context({
        'k1': 'v1',
        'awsWaitIn': {
            'waiterName': 'method_name',
            'arbKey': 'arb_value'
        }})

    with pytest.raises(KeyNotInContextError) as err_info:
        client_in, service_name, waiter_name = wait.get_waiter_args(
            context)

    assert str(err_info.value) == ("awsWaitIn missing required key for "
                                   "pypyraws.steps.wait: 'serviceName'")


def test_get_waiter_args_missing_waitername():
    """Missing waiterName raises."""
    context = Context({
        'k1': 'v1',
        'awsWaitIn': {
            'serviceName': 'service name',
            'arbKey': 'arb_value'
        }})

    with pytest.raises(KeyNotInContextError) as err_info:
        client_in, service_name, waiter_name = wait.get_waiter_args(
            context)

    assert str(err_info.value) == ("awsWaitIn missing required key for "
                                   "pypyraws.steps.wait: 'waiterName'")


def test_get_waiter_args_servicename_empty():
    """Empty serviceName raises."""
    context = Context({
        'k1': 'v1',
        'awsWaitIn': {
            'serviceName': '',
            'waiterName': 'method_name',
            'arbKey': 'arb_value'
        }})

    with pytest.raises(KeyInContextHasNoValueError) as err_info:
        client_in, service_name, waiter_name = wait.get_waiter_args(
            context)

    assert str(err_info.value) == ("serviceName required in awsWaitIn "
                                   "for pypyraws.steps.wait")


def test_get_waiter_args_waitername_empty():
    """Whitespace serviceName raises."""
    context = Context({
        'k1': 'v1',
        'awsWaitIn': {
            'serviceName': 'service name',
            'waiterName': ' ',
            'arbKey': 'arb_value'
        }})

    with pytest.raises(KeyInContextHasNoValueError) as err_info:
        client_in, service_name, waiter_name = wait.get_waiter_args(
            context)

    assert str(err_info.value) == ("waiterName required in awsWaitIn "
                                   "for pypyraws.steps.wait")

# ---------------------------- get_waiter_args------------------------------#
