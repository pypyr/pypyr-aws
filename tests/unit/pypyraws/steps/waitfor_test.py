"""waitfor.py unit tests."""
import logging
from pypyr.context import Context
from pypyr.errors import KeyNotInContextError
from pypyraws.errors import WaitTimeOut
import pypyraws.steps.waitfor as waitfor_step
import pytest
from unittest.mock import call, patch

# ---------------------------- run_step -------------------------------------#


def test_waitfor_missing_awswaitfor():
    """Missing awsWaitFor raises."""
    context = Context({'k1': 'v1'})

    with pytest.raises(KeyNotInContextError) as err_info:
        waitfor_step.run_step(context)

    assert str(err_info.value) == (
        "context[\'awsWaitFor\'] doesn\'t exist. It "
        "must exist for pypyraws.steps.waitfor.")


@patch('pypyraws.aws.service.operation_exec', return_value={'rk1': 'rv1',
                                                            'rk2': 'rv2'})
@patch('time.sleep')
def test_waitfor_pass_1st_time_no_client_args(mock_sleep, mock_service):
    """Successful run with no client args."""
    context = Context({
        'k1': 'v1',
        'awsWaitFor': {
            'awsClientIn': {
                'serviceName': 'service name',
                'methodName': 'method_name',
                'arbKey': 'arb_value'
            },
            'waitForField': '{rk2}',
            'toBe': 'rv2'
        }})

    logger = logging.getLogger('pypyraws.steps.waitfor')
    with patch.object(logger, 'info') as mock_logger_info:
        waitfor_step.run_step(context)

    assert mock_logger_info.mock_calls == [
        call('{rk2} in aws response is: rv2'),
        call('aws service name method_name returned rv2. '
             'Pipeline will now continue.')]

    assert len(context) == 3
    assert not context['awsWaitForTimedOut']
    assert context['k1'] == 'v1'
    assert context['awsWaitFor']['awsClientIn'] == {
        'serviceName': 'service name',
        'methodName': 'method_name',
        'arbKey': 'arb_value'
    }

    mock_sleep.assert_not_called()
    mock_service.assert_called_once_with(service_name='service name',
                                         method_name='method_name',
                                         client_args=None,
                                         operation_args=None,
                                         )


@patch('pypyraws.aws.service.operation_exec', return_value={'rk1': 'rv1',
                                                            'rk2': 'rv2'})
@patch('time.sleep')
def test_waitfor_fail_no_client_args(mock_sleep, mock_service):
    """Fail run with no client args."""
    context = Context({
        'k1': 'v1',
        'awsWaitFor': {
            'awsClientIn': {
                'serviceName': 'service name',
                'methodName': 'method_name',
                'arbKey': 'arb_value'
            },
            'waitForField': '{rk2}',
            'toBe': 'xxx'
        }})

    with pytest.raises(WaitTimeOut) as err_info:
        logger = logging.getLogger('pypyraws.steps.waitfor')
        with patch.object(logger, 'error') as mock_logger_error:
            waitfor_step.run_step(context)

    assert str(err_info.value) == ("aws service name method_name did not "
                                   "return xxx within 10 retries.")

    mock_logger_error.assert_called_once_with(
        'aws service name method_name did not return xxx within 10. '
        'errorOnWaitTimeout is True, throwing error')

    assert len(context) == 3
    assert context['awsWaitForTimedOut']
    assert context['k1'] == 'v1'
    assert context['awsWaitFor']['awsClientIn'] == {
        'serviceName': 'service name',
        'methodName': 'method_name',
        'arbKey': 'arb_value'
    }

    mock_sleep.call_count == 10
    mock_sleep.assert_called_with(30)
    mock_service.assert_called_with(service_name='service name',
                                    method_name='method_name',
                                    client_args=None,
                                    operation_args=None,
                                    )


@patch('pypyraws.aws.service.operation_exec', return_value={'rk1': 'rv1',
                                                            'rk2': 'rv2'})
@patch('time.sleep')
def test_waitfor_fail_no_client_args_no_throw(mock_sleep, mock_service):
    """Fail run with no client args and no error thrown."""
    context = Context({
        'k1': 'v1',
        'awsWaitFor': {
            'awsClientIn': {
                'serviceName': 'service name',
                'methodName': 'method_name',
                'arbKey': 'arb_value'
            },
            'waitForField': '{rk2}',
            'toBe': 'xxx',
            'errorOnWaitTimeout': False
        }})

    logger = logging.getLogger('pypyraws.steps.waitfor')
    with patch.object(logger, 'warning') as mock_logger_warn:
        waitfor_step.run_step(context)

    mock_logger_warn.assert_called_once_with(
        'aws service name method_name did NOT return  xxx. errorOnWaitTimeout '
        'is False, so pipeline will proceed to the next step anyway.')

    assert len(context) == 3
    assert context['k1'] == 'v1'
    assert context['awsWaitFor']['awsClientIn'] == {
        'serviceName': 'service name',
        'methodName': 'method_name',
        'arbKey': 'arb_value'
    }

    assert context['awsWaitForTimedOut']

    mock_sleep.call_count == 10
    mock_sleep.assert_called_with(30)
    mock_service.assert_called_with(service_name='service name',
                                    method_name='method_name',
                                    client_args=None,
                                    operation_args=None,
                                    )


@patch('pypyraws.aws.service.operation_exec')
@patch('time.sleep')
def test_waitfor_pass_client_args(mock_sleep, mock_service):
    """Successful run with client args pass on 3."""
    mock_service.side_effect = [
        {'rk1': 'rv1',
         'rk2': 'rv2'},  # 1
        {'rk1': 'rv1',
         'rk2': 'rv2'},  # 2
        {'rk1': 'rv1',
         'rk2': 'xxx'},  # 3
        {'rk1': 'rv1',
         'rk2': 'rv2'}   # 4
    ]

    context = Context({
        'k1': 'v1',
        'awsWaitFor': {
            'awsClientIn': {
                'serviceName': 'service name',
                'methodName': 'method_name',
                'arbKey': 'arb_value',
                'clientArgs': {'ck1': 'cv1', 'ck2': 'cv2'}},
            'waitForField': '{rk2}',
            'toBe': 'xxx'
        }})
    waitfor_step.run_step(context)

    assert len(context) == 3
    assert context['k1'] == 'v1'
    assert context['awsWaitFor']['awsClientIn'] == {
        'serviceName': 'service name',
        'methodName': 'method_name',
        'arbKey': 'arb_value',
        'clientArgs': {'ck1': 'cv1', 'ck2': 'cv2'}
    }
    assert not context['awsWaitForTimedOut']

    mock_service.assert_called_with(service_name='service name',
                                    method_name='method_name',
                                    client_args={'ck1': 'cv1',
                                                 'ck2': 'cv2'},
                                    operation_args=None,
                                    )
    mock_sleep.call_count == 3
    mock_sleep.assert_called_with(30)


@patch('pypyraws.aws.service.operation_exec', return_value={'rk1': 'rv1',
                                                            'rk2': 'rv2'})
@patch('time.sleep')
def test_waitfor_pass_method_args(mock_sleep, mock_service):
    """Successful run with method args pass on 2 with int."""
    mock_service.side_effect = [
        {'rk1': 'rv1',
         'rk2': 'rv2'},  # 1
        {'rk1': 'rv1',
         'rk2': 123},  # 2
        {'rk1': 'rv1',
         'rk2': 'xxx'},  # 3
    ]

    context = Context({
        'k1': 'v1',
        'awsWaitFor': {
            'awsClientIn': {
                'serviceName': 'service name',
                'methodName': 'method_name',
                'arbKey': 'arb_value',
                'methodArgs': {'mk1': 'mv1', 'mk2': 'mv2'}
            },
            'waitForField': '{rk2}',
            'toBe': 123
        }})
    waitfor_step.run_step(context)

    assert len(context) == 3
    assert not context['awsWaitForTimedOut']
    assert context['k1'] == 'v1'
    assert context['awsWaitFor']['awsClientIn'] == {
        'serviceName': 'service name',
        'methodName': 'method_name',
        'arbKey': 'arb_value',
        'methodArgs': {'mk1': 'mv1', 'mk2': 'mv2'}
    }

    mock_service.assert_called_with(service_name='service name',
                                    method_name='method_name',
                                    client_args=None,
                                    operation_args={'mk1': 'mv1',
                                                    'mk2': 'mv2'},
                                    )
    mock_sleep.call_count == 2
    mock_sleep.assert_called_with(30)


@patch('pypyraws.aws.service.operation_exec')
@patch('time.sleep')
def test_waitfor_pass_all_args(mock_sleep, mock_service):
    """Successful run with client and method args pass on #2."""
    mock_service.side_effect = [
        {'rk1': 'rv1',
         'rk2': 'rv2'},  # 1
        {'rk1': 'rv1',
         'rk2': False},  # 2
        {'rk1': 'rv1',
         'rk2': 'rv2'},  # 3
    ]

    context = Context({
        'k1': 'v1',
        'awsWaitFor': {
            'awsClientIn': {
                'serviceName': 'service name',
                'methodName': 'method_name',
                'arbKey': 'arb_value',
                'clientArgs': {'ck1': 'cv1', 'ck2': 'cv2'},
                'methodArgs': {'mk1': 'mv1', 'mk2': 'mv2'}},
            'waitForField': '{rk2}',
            'toBe': False,
            'pollInterval': 99
        }})
    waitfor_step.run_step(context)

    assert len(context) == 3
    assert context['k1'] == 'v1'
    assert context['awsWaitFor']['awsClientIn'] == {
        'serviceName': 'service name',
        'methodName': 'method_name',
        'arbKey': 'arb_value',
        'clientArgs': {'ck1': 'cv1', 'ck2': 'cv2'},
        'methodArgs': {'mk1': 'mv1', 'mk2': 'mv2'}
    }
    assert not context['awsWaitForTimedOut']
    mock_sleep.assert_called_once_with(99)
    mock_service.assert_called_with(service_name='service name',
                                    method_name='method_name',
                                    client_args={'ck1': 'cv1',
                                                 'ck2': 'cv2'},
                                    operation_args={'mk1': 'mv1',
                                                    'mk2': 'mv2'},
                                    )

# ---------------------------- run_step -------------------------------------#

# ---------------------------- substitutions --------------------------------#


@patch('pypyraws.aws.service.operation_exec')
@patch('time.sleep')
def test_waitfor_substitute_all_args(mock_sleep, mock_service):
    """Successful substitution run with client and method args."""
    mock_service.side_effect = [
        {'rk1': 'rv1',
         'rk2': True},
        {'rk1': 'rv1',
         'rk2': False}
    ]
    context = Context({
        'k1': 'v1',
        'k2': 'v2',
        'k3': 'v3',
        'k4': 'v4',
        'k5': 'v5',
        'k6': 'v6',
        'k7': 'v7',
        'k8': False,
        'k9': 99,
        'k10': 77,
        'k11': False,
        'awsWaitFor': {
            'awsClientIn': {
                'serviceName': 'service name {k1}',
                'methodName': 'method_name {k2}',
                'arbKey': 'arb_value {k3}',
                'clientArgs': {'ck1{k4}': 'cv1{k5}', 'ck2': 'cv2'},
                'methodArgs': {'mk1': 'mv1', 'mk2{k6}': 'mv2{k7}'}},
            'waitForField': '{rk2}',
            'toBe': '{k8}',
            'pollInterval': '{k9}',
            'maxAttempts': '{k10}',
            'errorOnWaitTimeout': '{k11}'
        }})
    waitfor_step.run_step(context)

    assert len(context) == 13
    assert context['k1'] == 'v1'
    assert context['awsWaitFor']['awsClientIn'] == {
        'serviceName': 'service name {k1}',
        'methodName': 'method_name {k2}',
        'arbKey': 'arb_value {k3}',
        'clientArgs': {'ck1{k4}': 'cv1{k5}', 'ck2': 'cv2'},
        'methodArgs': {'mk1': 'mv1', 'mk2{k6}': 'mv2{k7}'}
    }
    assert not context['awsWaitForTimedOut']
    mock_sleep.assert_called_once_with(99)
    mock_service.assert_called_with(service_name='service name v1',
                                    method_name='method_name v2',
                                    client_args={'ck1v4': 'cv1v5',
                                                 'ck2': 'cv2'},
                                    operation_args={'mk1': 'mv1',
                                                    'mk2v6': 'mv2v7'},
                                    )


@patch('pypyraws.aws.service.operation_exec', return_value={'rk1': 'rv1',
                                                            'rk2': 123})
@patch('time.sleep')
def test_waitfor_substitute_no_client_meth_args(mock_sleep, mock_service):
    """Successful substitution run with no client and no method args."""
    context = Context({
        'k1': 'v1',
        'k2': 'v2',
        'k3': 'v3',
        'k4': 'v4',
        'k5': 'v5',
        'k6': 'v6',
        'k7': 'v7',
        'k8': 66,
        'k9': 1,
        'k10': False,
        'awsWaitFor': {
            'awsClientIn': {
                'serviceName': 'service name {k1}',
                'methodName': 'method_name {k2}',
                'arbKey': 'arb_value {k3}'
            },
            'waitForField': '{rk2}',
            'toBe': 123,
            'pollInterval': '{k8}',
            'maxAttempts': '{k9}',
            'errorOnWaitTimeout': '{k10}'
        }})
    waitfor_step.run_step(context)

    assert len(context) == 12
    assert context['k1'] == 'v1'
    assert context['awsWaitFor']['awsClientIn'] == {
        'serviceName': 'service name {k1}',
        'methodName': 'method_name {k2}',
        'arbKey': 'arb_value {k3}'
    }
    assert not context['awsWaitForTimedOut']
    mock_sleep.assert_not_called()
    mock_service.assert_called_once_with(service_name='service name v1',
                                         method_name='method_name v2',
                                         client_args=None,
                                         operation_args=None
                                         )


@patch('pypyraws.aws.service.operation_exec', return_value={'rk1': 'rv1',
                                                            'rk2': 'rv2'})
@patch('time.sleep')
def test_aws_waitfor_substitute_no_client_args(mock_sleep, mock_service):
    """Successful run with no client but method args."""
    context = Context({
        'k1': 'v1',
        'k2': 'v2',
        'k3': 'v3',
        'k4': 'v4',
        'k5': 'v5',
        'k6': 'v6',
        'k7': 'v7',
        'k8': 66,
        'k9': 1,
        'k10': False,
        'awsWaitFor': {
            'awsClientIn': {
                'serviceName': 'service name {k1}',
                'methodName': 'method_name {k2}',
                'arbKey': 'arb_value {k3}',
                'methodArgs': {'mk1': 'mv1', 'mk2{k6}': 'mv2{k7}'}},
            'waitForField': '{rk2}',
            'toBe': 123,
            'pollInterval': '{k8}',
            'maxAttempts': '{k9}',
            'errorOnWaitTimeout': '{k10}'
        }})
    waitfor_step.run_step(context)

    assert len(context) == 12
    assert context['k1'] == 'v1'
    assert context['awsWaitFor']['awsClientIn'] == {
        'serviceName': 'service name {k1}',
        'methodName': 'method_name {k2}',
        'arbKey': 'arb_value {k3}',
        'methodArgs': {'mk1': 'mv1', 'mk2{k6}': 'mv2{k7}'}
    }
    assert context['awsWaitForTimedOut']
    mock_sleep.assert_not_called()
    mock_service.assert_called_once_with(service_name='service name v1',
                                         method_name='method_name v2',
                                         client_args=None,
                                         operation_args={'mk1': 'mv1',
                                                         'mk2v6': 'mv2v7'},
                                         )


@patch('pypyraws.aws.service.operation_exec', return_value={'rk1': 'rv1',
                                                            'rk2': 123.4})
@patch('time.sleep')
def test_aws_waitfor_substitute_no_method_args(mock_sleep, mock_service):
    """Successful run with client but no method args."""
    context = Context({
        'k1': 'v1',
        'k2': 'v2',
        'k3': 'v3',
        'k4': 'v4',
        'k5': 'v5',
        'k6': 'v6',
        'k7': 'v7',
        'awsWaitFor': {
            'awsClientIn': {
                'serviceName': 'service name {k1}',
                'methodName': 'method_name {k2}',
                'arbKey': 'arb_value {k3}',
                'clientArgs': {'ck1{k4}': 'cv1{k5}', 'ck2': 'cv2'}},
            'waitForField': '{rk2}',
            'toBe': 123.4,
            'pollInterval': 1,
            'maxAttempts': 1,
        }})
    waitfor_step.run_step(context)

    assert len(context) == 9
    assert context['k1'] == 'v1'
    assert context['awsWaitFor']['awsClientIn'] == {
        'serviceName': 'service name {k1}',
        'methodName': 'method_name {k2}',
        'arbKey': 'arb_value {k3}',
        'clientArgs': {'ck1{k4}': 'cv1{k5}', 'ck2': 'cv2'}
    }
    assert not context['awsWaitForTimedOut']
    mock_sleep.assert_not_called()
    mock_service.assert_called_once_with(service_name='service name v1',
                                         method_name='method_name v2',
                                         client_args={'ck1v4': 'cv1v5',
                                                      'ck2': 'cv2'},
                                         operation_args=None
                                         )
# ---------------------------- substitutions --------------------------------

# ----------------------execute_aws_client_method ---------------------------


@patch('pypyraws.aws.service.operation_exec', return_value={'rk1': 'rv1',
                                                            'rk2': [
                                                                123.4,
                                                                123,
                                                                'string here',
                                                                True,
                                                                {'rks1': 'rks2'
                                                                 }
                                                            ]})
def test_execute_awsclientmethod_parse_response_top_string(mock_service):
    """Successful response parsing."""
    assert waitfor_step.execute_aws_client_method(service_name='service name',
                                                  method_name='method name',
                                                  client_args={
                                                      'ck1': 'cv1',
                                                      'ck2': 'cv2'},
                                                  method_args={
                                                      'mk1': 'mv1',
                                                      'mk2': 'mv2'},
                                                  wait_for_field='{rk1}',
                                                  to_be='rv1')

    mock_service.assert_called_once_with(service_name='service name',
                                         method_name='method name',
                                         client_args={'ck1': 'cv1',
                                                      'ck2': 'cv2'},
                                         operation_args={'mk1': 'mv1',
                                                         'mk2': 'mv2'}
                                         )


@patch('pypyraws.aws.service.operation_exec', return_value={'rk1': 'rv1',
                                                            'rk2': [
                                                                123.4,
                                                                123,
                                                                'string here',
                                                                True,
                                                                {'rks1':
                                                                 'rks2'
                                                                 }
                                                            ]})
def test_execute_awsclientmethod_parse_response_path_float(mock_service):
    """Successful response parsing to complex path with float type."""
    assert waitfor_step.execute_aws_client_method(service_name='service name',
                                                  method_name='method name',
                                                  client_args={
                                                      'ck1': 'cv1',
                                                      'ck2': 'cv2'},
                                                  method_args={
                                                      'mk1': 'mv1',
                                                      'mk2': 'mv2'},
                                                  wait_for_field='{rk2[0]}',
                                                  to_be=123.4)

    mock_service.assert_called_once_with(service_name='service name',
                                         method_name='method name',
                                         client_args={'ck1': 'cv1',
                                                      'ck2': 'cv2'},
                                         operation_args={'mk1': 'mv1',
                                                         'mk2': 'mv2'})


@patch('pypyraws.aws.service.operation_exec', return_value={'rk1': 'rv1',
                                                            'rk2': [
                                                                123.4,
                                                                123,
                                                                'string here',
                                                                True,
                                                                {'rks1':
                                                                 'rks2'
                                                                 }
                                                            ]})
def test_execute_awsclientmethod_parse_response_path_int(mock_service):
    """Successful response parsing to a complex path with int type."""
    assert waitfor_step.execute_aws_client_method(service_name='service name',
                                                  method_name='method name',
                                                  client_args={
                                                      'ck1': 'cv1',
                                                      'ck2': 'cv2'},
                                                  method_args={
                                                      'mk1': 'mv1',
                                                      'mk2': 'mv2'},
                                                  wait_for_field='{rk2[1]}',
                                                  to_be=123)

    mock_service.assert_called_once_with(service_name='service name',
                                         method_name='method name',
                                         client_args={'ck1': 'cv1',
                                                      'ck2': 'cv2'},
                                         operation_args={'mk1': 'mv1',
                                                         'mk2': 'mv2'})


@patch('pypyraws.aws.service.operation_exec', return_value={'rk1': 'rv1',
                                                            'rk2': [
                                                                123.4,
                                                                123,
                                                                'string here',
                                                                True,
                                                                {'rks1':
                                                                 'rks2'
                                                                 }
                                                            ]})
def test_execute_awsclientmethod_parse_response_path_bool_true(mock_service):
    """Successful response parsing to a complex path with bool type True."""
    assert waitfor_step.execute_aws_client_method(service_name='service name',
                                                  method_name='method name',
                                                  client_args={
                                                      'ck1': 'cv1',
                                                      'ck2': 'cv2'},
                                                  method_args={
                                                      'mk1': 'mv1',
                                                      'mk2': 'mv2'},
                                                  wait_for_field='{rk2[3]}',
                                                  to_be=True)

    mock_service.assert_called_once_with(service_name='service name',
                                         method_name='method name',
                                         client_args={'ck1': 'cv1',
                                                      'ck2': 'cv2'},
                                         operation_args={'mk1': 'mv1',
                                                         'mk2': 'mv2'})


@patch('pypyraws.aws.service.operation_exec', return_value={'rk1': 'rv1',
                                                            'rk2': [
                                                                123.4,
                                                                123,
                                                                'string here',
                                                                False,
                                                                {'rks1':
                                                                 'rks2'
                                                                 }
                                                            ]})
def test_execute_awsclientmethod_parse_response_path_bool_false(mock_service):
    """Successful response parsing to a complex path with bool type False."""
    assert waitfor_step.execute_aws_client_method(service_name='service name',
                                                  method_name='method name',
                                                  client_args={
                                                      'ck1': 'cv1',
                                                      'ck2': 'cv2'},
                                                  method_args={
                                                      'mk1': 'mv1',
                                                      'mk2': 'mv2'},
                                                  wait_for_field='{rk2[3]}',
                                                  to_be=False)

    mock_service.assert_called_once_with(service_name='service name',
                                         method_name='method name',
                                         client_args={'ck1': 'cv1',
                                                      'ck2': 'cv2'},
                                         operation_args={'mk1': 'mv1',
                                                         'mk2': 'mv2'})


@patch('pypyraws.aws.service.operation_exec', return_value={'rk1': 'rv1',
                                                            'rk2': [
                                                                123.4,
                                                                123,
                                                                'string here',
                                                                False,
                                                                {'rks1':
                                                                 'rks2'
                                                                 }
                                                            ]})
def test_execute_awsclientmethod_parse_false_path_bool_false(mock_service):
    """Fail response parsing to a complex path with bool type False."""
    assert not waitfor_step.execute_aws_client_method(
        service_name='service name',
        method_name='method name',
        client_args={
            'ck1': 'cv1',
            'ck2': 'cv2'},
        method_args={
            'mk1': 'mv1',
            'mk2': 'mv2'},
        wait_for_field='{rk2[3]}',
        to_be=True)

    mock_service.assert_called_once_with(service_name='service name',
                                         method_name='method name',
                                         client_args={'ck1': 'cv1',
                                                      'ck2': 'cv2'},
                                         operation_args={'mk1': 'mv1',
                                                         'mk2': 'mv2'})


@patch('pypyraws.aws.service.operation_exec', return_value={'rk1': 'rv1',
                                                            'rk2': [
                                                                123.4,
                                                                123,
                                                                'string here',
                                                                True,
                                                                {'rks1':
                                                                 'rks2'
                                                                 }
                                                            ]})
def test_execute_awsclientmethod_parse_false_path_bool_true(mock_service):
    """Fail response parsing to a complex path with bool type False."""
    assert not waitfor_step.execute_aws_client_method(
        service_name='service name',
        method_name='method name',
        client_args={
            'ck1': 'cv1',
            'ck2': 'cv2'},
        method_args={
            'mk1': 'mv1',
            'mk2': 'mv2'},
        wait_for_field='{rk2[3]}',
        to_be=False)

    mock_service.assert_called_once_with(service_name='service name',
                                         method_name='method name',
                                         client_args={'ck1': 'cv1',
                                                      'ck2': 'cv2'},
                                         operation_args={'mk1': 'mv1',
                                                         'mk2': 'mv2'})


@patch('pypyraws.aws.service.operation_exec', return_value={'rk1': 'rv1',
                                                            'rk2': [
                                                                123.4,
                                                                123,
                                                                'string here',
                                                                True,
                                                                {'rks1': 'rkv2'
                                                                 }
                                                            ]})
def test_execute_awsclientmethod_parse_response_path_dict(mock_service):
    """Successful response parsing."""
    assert waitfor_step.execute_aws_client_method(
        service_name='service name',
        method_name='method name',
        client_args={
            'ck1': 'cv1',
            'ck2': 'cv2'},
        method_args={
            'mk1': 'mv1',
            'mk2': 'mv2'},
        wait_for_field='{rk2[4][rks1]}',
        to_be='rkv2')

    mock_service.assert_called_once_with(service_name='service name',
                                         method_name='method name',
                                         client_args={'ck1': 'cv1',
                                                      'ck2': 'cv2'},
                                         operation_args={'mk1': 'mv1',
                                                         'mk2': 'mv2'}
                                         )
# ----------------------execute_aws_client_method ------------------------

# ----------------------get_poll_args ------------------------------------


def test_get_poll_args_defaults():
    """All defaults assigned."""
    context = Context({
        'waitFor': {
            'waitForField': 'field name',
            'toBe': 'value here'}
    })

    waitfor_dict = context['waitFor']
    (wait_for_field,
     to_be,
     poll_interval,
     max_attempts,
     error_on_wait_timeout) = waitfor_step.get_poll_args(waitfor_dict, context)

    assert wait_for_field == 'field name'
    assert to_be == 'value here'
    assert poll_interval == 30
    assert max_attempts == 10
    assert error_on_wait_timeout


def test_get_poll_args_all():
    """All args assigned."""
    context = Context({
        'waitFor': {
            'waitForField': 'field name',
            'toBe': 'value here',
            'pollInterval': 99,
            'maxAttempts': 66,
            'errorOnWaitTimeout': False}
    })

    waitfor_dict = context['waitFor']
    (wait_for_field,
     to_be,
     poll_interval,
     max_attempts,
     error_on_wait_timeout) = waitfor_step.get_poll_args(waitfor_dict, context)

    assert wait_for_field == 'field name'
    assert to_be == 'value here'
    assert poll_interval == 99
    assert max_attempts == 66
    assert not error_on_wait_timeout


def test_get_poll_args_substitutions():
    """All args assigned and substituted."""
    context = Context({
        'k1': 123.4,
        'k2': 99,
        'k3': 66,
        'k4': False,
        'waitFor': {
            'waitForField': 'field name',
            'toBe': '{k1}',
            'pollInterval': '{k2}',
            'maxAttempts': '{k3}',
            'errorOnWaitTimeout': '{k4}'}
    })

    waitfor_dict = context['waitFor']
    (wait_for_field,
     to_be,
     poll_interval,
     max_attempts,
     error_on_wait_timeout) = waitfor_step.get_poll_args(waitfor_dict, context)

    assert wait_for_field == 'field name'
    assert to_be == 123.4
    assert poll_interval == 99
    assert max_attempts == 66
    assert not error_on_wait_timeout
# ----------------------get_poll_args ------------------------------------
