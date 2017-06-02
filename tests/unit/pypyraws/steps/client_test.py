"""client.py unit tests."""
from unittest.mock import patch
from pypyr.context import Context
from pypyr.errors import KeyNotInContextError
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

# ---------------------------- substitutions --------------------------------#


@patch('pypyraws.aws.service.operation_exec', return_value={'rk1': 'rv1',
                                                            'rk2': 'rv2'})
def test_aws_client_substitute_all_args(mock_service):
    """Successful substitution run with client and method args"""
    context = Context({
        'k1': 'v1',
        'k2': 'v2',
        'k3': 'v3',
        'k4': 'v4',
        'k5': 'v5',
        'k6': 'v6',
        'k7': 'v7',
        'awsClientIn': {
            'serviceName': 'service name {k1}',
            'methodName': 'method_name {k2}',
            'arbKey': 'arb_value {k3}',
            'clientArgs': {'ck1{k4}': 'cv1{k5}', 'ck2': 'cv2'},
            'methodArgs': {'mk1': 'mv1', 'mk2{k6}': 'mv2{k7}'}
        }})
    client_step.run_step(context)

    assert len(context) == 9
    assert context['k1'] == 'v1'
    assert context['awsClientIn'] == {
        'serviceName': 'service name {k1}',
        'methodName': 'method_name {k2}',
        'arbKey': 'arb_value {k3}',
        'clientArgs': {'ck1{k4}': 'cv1{k5}', 'ck2': 'cv2'},
        'methodArgs': {'mk1': 'mv1', 'mk2{k6}': 'mv2{k7}'}
    }
    assert context['awsClientOut'] == {'rk1': 'rv1', 'rk2': 'rv2'}
    mock_service.assert_called_once_with(service_name='service name v1',
                                         method_name='method_name v2',
                                         client_args={'ck1v4': 'cv1v5',
                                                      'ck2': 'cv2'},
                                         operation_args={'mk1': 'mv1',
                                                         'mk2v6': 'mv2v7'},
                                         )


@patch('pypyraws.aws.service.operation_exec', return_value={'rk1': 'rv1',
                                                            'rk2': 'rv2'})
def test_aws_client_substitute_no_client_method_args(mock_service):
    """Successful substitution run with no client and no method args"""
    context = Context({
        'k1': 'v1',
        'k2': 'v2',
        'k3': 'v3',
        'k4': 'v4',
        'k5': 'v5',
        'k6': 'v6',
        'k7': 'v7',
        'awsClientIn': {
            'serviceName': 'service name {k1}',
            'methodName': 'method_name {k2}',
            'arbKey': 'arb_value {k3}'
        }})
    client_step.run_step(context)

    assert len(context) == 9
    assert context['k1'] == 'v1'
    assert context['awsClientIn'] == {
        'serviceName': 'service name {k1}',
        'methodName': 'method_name {k2}',
        'arbKey': 'arb_value {k3}'
    }
    assert context['awsClientOut'] == {'rk1': 'rv1', 'rk2': 'rv2'}
    mock_service.assert_called_once_with(service_name='service name v1',
                                         method_name='method_name v2',
                                         client_args=None,
                                         operation_args=None
                                         )


@patch('pypyraws.aws.service.operation_exec', return_value={'rk1': 'rv1',
                                                            'rk2': 'rv2'})
def test_aws_client_substitute_no_client_args(mock_service):
    """Successful run with no client but method args"""
    context = Context({
        'k1': 'v1',
        'k2': 'v2',
        'k3': 'v3',
        'k4': 'v4',
        'k5': 'v5',
        'k6': 'v6',
        'k7': 'v7',
        'awsClientIn': {
            'serviceName': 'service name {k1}',
            'methodName': 'method_name {k2}',
            'arbKey': 'arb_value {k3}',
            'methodArgs': {'mk1': 'mv1', 'mk2{k6}': 'mv2{k7}'}
        }})
    client_step.run_step(context)

    assert len(context) == 9
    assert context['k1'] == 'v1'
    assert context['awsClientIn'] == {
        'serviceName': 'service name {k1}',
        'methodName': 'method_name {k2}',
        'arbKey': 'arb_value {k3}',
        'methodArgs': {'mk1': 'mv1', 'mk2{k6}': 'mv2{k7}'}
    }
    assert context['awsClientOut'] == {'rk1': 'rv1', 'rk2': 'rv2'}
    mock_service.assert_called_once_with(service_name='service name v1',
                                         method_name='method_name v2',
                                         client_args=None,
                                         operation_args={'mk1': 'mv1',
                                                         'mk2v6': 'mv2v7'},
                                         )


@patch('pypyraws.aws.service.operation_exec', return_value={'rk1': 'rv1',
                                                            'rk2': 'rv2'})
def test_aws_client_substitute_no_method_args(mock_service):
    """Successful run with client but no method args"""
    context = Context({
        'k1': 'v1',
        'k2': 'v2',
        'k3': 'v3',
        'k4': 'v4',
        'k5': 'v5',
        'k6': 'v6',
        'k7': 'v7',
        'awsClientIn': {
            'serviceName': 'service name {k1}',
            'methodName': 'method_name {k2}',
            'arbKey': 'arb_value {k3}',
            'clientArgs': {'ck1{k4}': 'cv1{k5}', 'ck2': 'cv2'}
        }})
    client_step.run_step(context)

    assert len(context) == 9
    assert context['k1'] == 'v1'
    assert context['awsClientIn'] == {
        'serviceName': 'service name {k1}',
        'methodName': 'method_name {k2}',
        'arbKey': 'arb_value {k3}',
        'clientArgs': {'ck1{k4}': 'cv1{k5}', 'ck2': 'cv2'}
    }
    assert context['awsClientOut'] == {'rk1': 'rv1', 'rk2': 'rv2'}
    mock_service.assert_called_once_with(service_name='service name v1',
                                         method_name='method_name v2',
                                         client_args={'ck1v4': 'cv1v5',
                                                      'ck2': 'cv2'},
                                         operation_args=None
                                         )
# ---------------------------- substitutions --------------------------------#
