"""s3fetchjson.py unit tests."""
import json
import pytest
from unittest.mock import Mock, patch
import pypyraws.steps.s3fetchjson as s3fetchjson
from pypyr.context import Context


@patch('pypyraws.aws.service.operation_exec')
def test_s3fetchjson(mock_s3):
    """Success path all the way through to the mocked boto s3 object."""
    mock_body = Mock()
    bunch_of_bytes = bytes(json.dumps(
        {'newkey': 'newvalue', 'newkey2': 'newvalue2'}), 'utf-8')

    mock_body.read.return_value = bunch_of_bytes
    mock_s3.side_effect = [{'Body': mock_body}]

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
    s3fetchjson.run_step(context)
    assert len(context) == 4
    assert context['k1'] == 'v1'
    assert context['newkey'] == 'newvalue'
    assert context['newkey2'] == 'newvalue2'


@patch('pypyraws.aws.service.operation_exec')
def test_fetchjson_with_destination(mock_s3):
    """Json writes to destination key."""
    mock_body = Mock()
    bunch_of_bytes = bytes(json.dumps([1, 2, 3]), 'utf-8')

    mock_body.read.return_value = bunch_of_bytes
    mock_s3.side_effect = [{'Body': mock_body}]

    context = Context({
        'k1': 'v1',
        's3Fetch': {
            'clientArgs': {'ck1': 'cv1', 'ck2': 'cv2'},
            'methodArgs': {'Bucket': 'bucket name',
                           'Key': 'key name',
                           'SSECustomerAlgorithm': 'sse alg',
                           'SSECustomerKey': 'sse key'},
            'key': 'writehere'
        }})

    s3fetchjson.run_step(context)

    assert context['writehere'] == [1, 2, 3]
    assert len(context) == 3
    assert context == {
        'k1': 'v1',
        's3Fetch': {
            'clientArgs': {'ck1': 'cv1', 'ck2': 'cv2'},
            'methodArgs': {'Bucket': 'bucket name',
                           'Key': 'key name',
                           'SSECustomerAlgorithm': 'sse alg',
                           'SSECustomerKey': 'sse key'},
            'key': 'writehere'},
        'writehere': [1, 2, 3]
    }


@patch('pypyraws.aws.service.operation_exec')
def test_fetchjson_with_destination_int(mock_s3):
    """Json overwrites destination key that's not a string."""
    mock_body = Mock()
    bunch_of_bytes = bytes(json.dumps([1, 2, 3]), 'utf-8')

    mock_body.read.return_value = bunch_of_bytes
    mock_s3.side_effect = [{'Body': mock_body}]

    context = Context({
        'k1': 'v1',
        's3Fetch': {
            'clientArgs': {'ck1': 'cv1', 'ck2': 'cv2'},
            'methodArgs': {'Bucket': 'bucket name',
                           'Key': 'key name',
                           'SSECustomerAlgorithm': 'sse alg',
                           'SSECustomerKey': 'sse key'},
            'key': 99},
        99: 'blah'
    })

    s3fetchjson.run_step(context)

    assert context[99] == [1, 2, 3]
    assert len(context) == 3


@patch('pypyraws.aws.service.operation_exec')
def test_fetchjson_with_destination_int_old(mock_s3):
    """Test outKey still works for backwards compatibility."""
    mock_body = Mock()
    bunch_of_bytes = bytes(json.dumps([1, 2, 3]), 'utf-8')

    mock_body.read.return_value = bunch_of_bytes
    mock_s3.side_effect = [{'Body': mock_body}]

    context = Context({
        'k1': 'v1',
        's3Fetch': {
            'clientArgs': {'ck1': 'cv1', 'ck2': 'cv2'},
            'methodArgs': {'Bucket': 'bucket name',
                           'Key': 'key name',
                           'SSECustomerAlgorithm': 'sse alg',
                           'SSECustomerKey': 'sse key'},
            'outKey': 99},
        99: 'blah'
    })

    s3fetchjson.run_step(context)

    assert context[99] == [1, 2, 3]
    assert len(context) == 3


@patch('pypyraws.aws.service.operation_exec')
def test_fetchjson_with_destination_formatting_old(mock_s3):
    """Test deprecated outKey still works for backwards compatibility."""
    mock_body = Mock()
    bunch_of_bytes = bytes(json.dumps({'1': 2, '2': 3}), 'utf-8')

    mock_body.read.return_value = bunch_of_bytes
    mock_s3.side_effect = [{'Body': mock_body}]

    context = Context({
        'keyhere': {'sub': ['outkey', 2, 3]},
        's3Fetch': {
            'clientArgs': {'ck1': 'cv1', 'ck2': 'cv2'},
            'methodArgs': {'Bucket': 'bucket name',
                           'Key': 'key name',
                           'SSECustomerAlgorithm': 'sse alg',
                           'SSECustomerKey': 'sse key'},
            'outKey': '{keyhere[sub][0]}'},
    })

    s3fetchjson.run_step(context)

    assert len(context) == 3
    assert context['outkey'] == {'1': 2, '2': 3}
    assert context['keyhere'] == {'sub': ['outkey', 2, 3]}
    assert context['s3Fetch'] == {
        'clientArgs': {'ck1': 'cv1', 'ck2': 'cv2'},
        'methodArgs': {'Bucket': 'bucket name',
                       'Key': 'key name',
                       'SSECustomerAlgorithm': 'sse alg',
                       'SSECustomerKey': 'sse key'},
        'outKey': '{keyhere[sub][0]}'}


@patch('pypyraws.aws.service.operation_exec')
def test_fetchjson_with_destination_formatting(mock_s3):
    """Json writes to destination key found by formatting expression."""
    mock_body = Mock()
    bunch_of_bytes = bytes(json.dumps({'1': 2, '2': 3}), 'utf-8')

    mock_body.read.return_value = bunch_of_bytes
    mock_s3.side_effect = [{'Body': mock_body}]

    context = Context({
        'keyhere': {'sub': ['outkey', 2, 3]},
        's3Fetch': {
            'clientArgs': {'ck1': 'cv1', 'ck2': 'cv2'},
            'methodArgs': {'Bucket': 'bucket name',
                           'Key': 'key name',
                           'SSECustomerAlgorithm': 'sse alg',
                           'SSECustomerKey': 'sse key'},
            'key': '{keyhere[sub][0]}'},
    })

    s3fetchjson.run_step(context)

    assert len(context) == 3
    assert context['outkey'] == {'1': 2, '2': 3}
    assert context['keyhere'] == {'sub': ['outkey', 2, 3]}
    assert context['s3Fetch'] == {
        'clientArgs': {'ck1': 'cv1', 'ck2': 'cv2'},
        'methodArgs': {'Bucket': 'bucket name',
                       'Key': 'key name',
                       'SSECustomerAlgorithm': 'sse alg',
                       'SSECustomerKey': 'sse key'},
        'key': '{keyhere[sub][0]}'}


@patch('pypyraws.aws.service.operation_exec')
def test_fetchjson_list_fails(mock_s3):
    """Json describing a list rather than a dict should fail if no outkey."""
    mock_body = Mock()
    bunch_of_bytes = bytes(json.dumps([1, 2, 3]), 'utf-8')

    mock_body.read.return_value = bunch_of_bytes
    mock_s3.side_effect = [{'Body': mock_body}]

    context = Context({
        'k1': 'v1',
        's3Fetch': {
            'clientArgs': {'ck1': 'cv1', 'ck2': 'cv2'},
            'methodArgs': {'Bucket': 'bucket name',
                           'Key': 'key name',
                           'SSECustomerAlgorithm': 'sse alg',
                           'SSECustomerKey': 'sse key'}
        }})

    with pytest.raises(TypeError):
        s3fetchjson.run_step(context)
