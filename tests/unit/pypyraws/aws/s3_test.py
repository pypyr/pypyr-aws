"""service.py unit tests."""
import pypyraws.aws.s3 as ps3
from pypyr.context import Context
from pypyr.errors import KeyNotInContextError
import pytest
from unittest.mock import patch

# ---------------------------- get_payload ----------------------------------#


def test_get_payload_no_s3fetch():
    """Operation exec with s3Fetch raises."""
    context = Context({'k1': 'v1'})
    with pytest.raises(KeyNotInContextError) as err_info:
        ps3.get_payload(context)

    assert str(err_info.value) == ("s3Fetch not found in the pypyr context.")


def test_get_payload_no_methodargs():
    """Operation exec with s3Fetch raises."""
    context = Context({'s3Fetch': {'k1': 'v1'}})
    with pytest.raises(KeyNotInContextError) as err_info:
        ps3.get_payload(context)

    assert str(err_info.value) == ("s3Fetch missing required key for "
                                   "pypyraws.steps.s3fetch step: methodArgs")


@patch('pypyraws.aws.service.operation_exec')
def test_aws_client_pass(mock_s3):
    """Successful run with client args"""
    mock_s3.side_effect = [{'Body': b'bunchofbytes'}]

    context = Context({
        'k1': 'v1',
        's3Fetch': {
            'serviceName': 'service name',
            'methodName': 'method_name',
            'clientArgs': {'ck1': 'cv1', 'ck2': 'cv2'},
            'methodArgs': {'Bucket': 'bucket name',
                           'Key': 'key name',
                           'SSECustomerAlgorithm': 'sse alg',
                           'SSECustomerKey': 'sse key'}
        }})
    payload = ps3.get_payload(context)

    assert payload
    assert payload == b'bunchofbytes'
    assert len(context) == 2
    assert context['k1'] == 'v1'
    assert context['s3Fetch'] == {
        'serviceName': 'service name',
        'methodName': 'method_name',
        'clientArgs': {'ck1': 'cv1', 'ck2': 'cv2'},
        'methodArgs': {'Bucket': 'bucket name',
                       'Key': 'key name',
                       'SSECustomerAlgorithm': 'sse alg',
                       'SSECustomerKey': 'sse key'}
    }

    mock_s3.assert_called_once_with(service_name='s3',
                                    method_name='get_object',
                                    client_args={'ck1': 'cv1',
                                                 'ck2': 'cv2'},
                                    operation_args={
                                        'Bucket': 'bucket name',
                                        'Key': 'key name',
                                        'SSECustomerAlgorithm': 'sse alg',
                                        'SSECustomerKey': 'sse key'}
                                    )


@patch('pypyraws.aws.service.operation_exec')
def test_aws_client_pass_no_client_args(mock_s3):
    """Successful run with no client args"""
    mock_s3.side_effect = [{'Body': b'bunchofbytes'}]

    context = Context({
        'k1': 'v1',
        's3Fetch': {
            'serviceName': 'service name',
            'methodName': 'method_name',
            'methodArgs': {'Bucket': 'bucket name',
                           'Key': 'key name',
                           'SSECustomerAlgorithm': 'sse alg',
                           'SSECustomerKey': 'sse key'}
        }})
    payload = ps3.get_payload(context)

    assert payload
    assert payload == b'bunchofbytes'
    assert len(context) == 2
    assert context['k1'] == 'v1'
    assert context['s3Fetch'] == {
        'serviceName': 'service name',
        'methodName': 'method_name',
        'methodArgs': {'Bucket': 'bucket name',
                       'Key': 'key name',
                       'SSECustomerAlgorithm': 'sse alg',
                       'SSECustomerKey': 'sse key'}
    }

    mock_s3.assert_called_once_with(service_name='s3',
                                    method_name='get_object',
                                    client_args=None,
                                    operation_args={
                                        'Bucket': 'bucket name',
                                        'Key': 'key name',
                                        'SSECustomerAlgorithm': 'sse alg',
                                        'SSECustomerKey': 'sse key'}
                                    )


@patch('pypyraws.aws.service.operation_exec')
def test_aws_client_pass_substitutions(mock_s3):
    """Successful run with client args"""
    mock_s3.side_effect = [{'Body': b'bunchofbytes'}]

    context = Context({
        'k1': 'v1',
        'k2': 'v2',
        'k3': 'v3',
        'k4': 'v4',
        's3Fetch': {
            'serviceName': 'service name',
            'methodName': 'method_name',
            'clientArgs': {'ck1 {k1}': 'cv1', 'ck2': 'cv2 {k2}'},
            'methodArgs': {'Bucket': '{k3} bucket name',
                           'Key': 'key name {k4}',
                           'SSECustomerAlgorithm': 'sse alg',
                           'SSECustomerKey': 'sse key'}
        }})
    payload = ps3.get_payload(context)

    assert payload
    assert payload == b'bunchofbytes'
    assert len(context) == 5
    assert context['k1'] == 'v1'
    assert context['s3Fetch'] == {
        'serviceName': 'service name',
        'methodName': 'method_name',
        'clientArgs': {'ck1 {k1}': 'cv1', 'ck2': 'cv2 {k2}'},
        'methodArgs': {'Bucket': '{k3} bucket name',
                       'Key': 'key name {k4}',
                       'SSECustomerAlgorithm': 'sse alg',
                       'SSECustomerKey': 'sse key'}
    }

    mock_s3.assert_called_once_with(service_name='s3',
                                    method_name='get_object',
                                    client_args={'ck1 v1': 'cv1',
                                                 'ck2': 'cv2 v2'},
                                    operation_args={
                                        'Bucket': 'v3 bucket name',
                                        'Key': 'key name v4',
                                        'SSECustomerAlgorithm': 'sse alg',
                                        'SSECustomerKey': 'sse key'}
                                    )
# ---------------------------- get_payload ----------------------------------#
