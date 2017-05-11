"""client.py unit tests."""
from unittest.mock import patch
from pypyr.context import Context
from pypyr.errors import KeyInContextHasNoValueError, KeyNotInContextError
import pypyraws.steps.client as client_step
import pytest


# ---------------------------- run_step -------------------------------------#

def test_aws_client_missing_awsclientin():
    """Missing awsClientIn raises"""
    context = Context({'k1': 'v1'})

    with pytest.raises(KeyNotInContextError) as err_info:
        client_step.run_step(context)

    assert repr(err_info.value) == (
        "KeyNotInContextError(\'awsClientIn not found in the pypyr "
        "context.',)")


@patch('pypyraws.aws.service.operation_exec', return_value={'rk1': 'rv1',
                                                            'rk2': 'rv2'})
def test_aws_client_pass_no_args(mock_service):
    """Successful run with no client args"""
    context = Context({
        'k1': 'v1',
        'awsClientIn': {
            'serviceName': 'service name',
            'methodName': 'method_name',
            'arbKey': 'arb_value'
        }})
    client_step.run_step(context)

    assert len(context) == 3
    assert context['k1'] == 'v1'
    assert context['awsClientIn'] == {
        'serviceName': 'service name',
        'methodName': 'method_name',
        'arbKey': 'arb_value'
    }
    assert context['awsClientOut'] == {'rk1': 'rv1', 'rk2': 'rv2'}
    mock_service.assert_called_once_with(service_name='service name',
                                         method_name='method_name',
                                         client_args=None,
                                         operation_args=None,
                                         )


@patch('pypyraws.aws.service.operation_exec', return_value={'rk1': 'rv1',
                                                            'rk2': 'rv2'})
def test_aws_client_pass_client_args(mock_service):
    """Successful run with client args"""
    context = Context({
        'k1': 'v1',
        'awsClientIn': {
            'serviceName': 'service name',
            'methodName': 'method_name',
            'arbKey': 'arb_value',
            'clientArgs': {'ck1': 'cv1', 'ck2': 'cv2'}
        }})
    client_step.run_step(context)

    assert len(context) == 3
    assert context['k1'] == 'v1'
    assert context['awsClientIn'] == {
        'serviceName': 'service name',
        'methodName': 'method_name',
        'arbKey': 'arb_value',
        'clientArgs': {'ck1': 'cv1', 'ck2': 'cv2'}
    }
    assert context['awsClientOut'] == {'rk1': 'rv1', 'rk2': 'rv2'}
    mock_service.assert_called_once_with(service_name='service name',
                                         method_name='method_name',
                                         client_args={'ck1': 'cv1',
                                                      'ck2': 'cv2'},
                                         operation_args=None,
                                         )


@patch('pypyraws.aws.service.operation_exec', return_value={'rk1': 'rv1',
                                                            'rk2': 'rv2'})
def test_aws_client_pass_method_args(mock_service):
    """Successful run with method args"""
    context = Context({
        'k1': 'v1',
        'awsClientIn': {
            'serviceName': 'service name',
            'methodName': 'method_name',
            'arbKey': 'arb_value',
            'methodArgs': {'mk1': 'mv1', 'mk2': 'mv2'}
        }})
    client_step.run_step(context)

    assert len(context) == 3
    assert context['k1'] == 'v1'
    assert context['awsClientIn'] == {
        'serviceName': 'service name',
        'methodName': 'method_name',
        'arbKey': 'arb_value',
        'methodArgs': {'mk1': 'mv1', 'mk2': 'mv2'}
    }
    assert context['awsClientOut'] == {'rk1': 'rv1', 'rk2': 'rv2'}
    mock_service.assert_called_once_with(service_name='service name',
                                         method_name='method_name',
                                         client_args=None,
                                         operation_args={'mk1': 'mv1',
                                                         'mk2': 'mv2'},
                                         )


@patch('pypyraws.aws.service.operation_exec', return_value={'rk1': 'rv1',
                                                            'rk2': 'rv2'})
def test_aws_client_pass_all_args(mock_service):
    """Successful run with client and method args"""
    context = Context({
        'k1': 'v1',
        'awsClientIn': {
            'serviceName': 'service name',
            'methodName': 'method_name',
            'arbKey': 'arb_value',
            'clientArgs': {'ck1': 'cv1', 'ck2': 'cv2'},
            'methodArgs': {'mk1': 'mv1', 'mk2': 'mv2'}
        }})
    client_step.run_step(context)

    assert len(context) == 3
    assert context['k1'] == 'v1'
    assert context['awsClientIn'] == {
        'serviceName': 'service name',
        'methodName': 'method_name',
        'arbKey': 'arb_value',
        'clientArgs': {'ck1': 'cv1', 'ck2': 'cv2'},
        'methodArgs': {'mk1': 'mv1', 'mk2': 'mv2'}
    }
    assert context['awsClientOut'] == {'rk1': 'rv1', 'rk2': 'rv2'}
    mock_service.assert_called_once_with(service_name='service name',
                                         method_name='method_name',
                                         client_args={'ck1': 'cv1',
                                                      'ck2': 'cv2'},
                                         operation_args={'mk1': 'mv1',
                                                         'mk2': 'mv2'},
                                         )
# ---------------------------- run_step -------------------------------------#

# ---------------------------- get_service_args------------------------------#


def test_get_service_args_pass():
    """get_service_args pass"""
    context = Context({
        'k1': 'v1',
        'awsClientIn': {
            'serviceName': 'service name',
            'methodName': 'method_name',
            'arbKey': 'arb_value'
        }})
    client_in, service_name, method_name = client_step.get_service_args(
        context)

    assert client_in == {
        'serviceName': 'service name',
        'methodName': 'method_name',
        'arbKey': 'arb_value'
    }
    assert service_name == 'service name'
    assert method_name == 'method_name'


def test_get_service_args_missing_awsclientin():
    """Missing awsClientIn raises"""
    context = Context({'k1': 'v1'})

    with pytest.raises(KeyNotInContextError) as err_info:
        client_in, service_name, method_name = client_step.get_service_args(
            context)

    assert repr(err_info.value) == (
        "KeyNotInContextError(\'awsClientIn not found in the pypyr "
        "context.',)")


def test_get_service_args_missing_servicename():
    """Missing serviceName raises"""
    context = Context({
        'k1': 'v1',
        'awsClientIn': {
            'methodName': 'method_name',
            'arbKey': 'arb_value'
        }})

    with pytest.raises(KeyNotInContextError) as err_info:
        client_in, service_name, method_name = client_step.get_service_args(
            context)

    assert repr(err_info.value) == (
        "KeyNotInContextError(\"awsClientIn missing required key for "
        "pypyraws.steps.client: 'serviceName'\",)")


def test_get_service_args_missing_methodname():
    """Missing methodName raises"""
    context = Context({
        'k1': 'v1',
        'awsClientIn': {
            'serviceName': 'service name',
            'arbKey': 'arb_value'
        }})

    with pytest.raises(KeyNotInContextError) as err_info:
        client_in, service_name, method_name = client_step.get_service_args(
            context)

    assert repr(err_info.value) == (
        "KeyNotInContextError(\"awsClientIn missing required key for "
        "pypyraws.steps.client: 'methodName'\",)")


def test_get_service_args_servicename_empty():
    """Empty serviceName raises"""
    context = Context({
        'k1': 'v1',
        'awsClientIn': {
            'serviceName': '',
            'methodName': 'method_name',
            'arbKey': 'arb_value'
        }})

    with pytest.raises(KeyInContextHasNoValueError) as err_info:
        client_in, service_name, method_name = client_step.get_service_args(
            context)

    assert repr(err_info.value) == (
        "KeyInContextHasNoValueError('serviceName required in awsClientIn "
        "for pypyraws.steps.client',)")


def test_get_service_args_methodname_empty():
    """Whitespace serviceName raises"""
    context = Context({
        'k1': 'v1',
        'awsClientIn': {
            'serviceName': 'service name',
            'methodName': ' ',
            'arbKey': 'arb_value'
        }})

    with pytest.raises(KeyInContextHasNoValueError) as err_info:
        client_in, service_name, method_name = client_step.get_service_args(
            context)

    assert repr(err_info.value) == (
        "KeyInContextHasNoValueError('methodName required in awsClientIn "
        "for pypyraws.steps.client',)")

# ---------------------------- get_service_args------------------------------#
