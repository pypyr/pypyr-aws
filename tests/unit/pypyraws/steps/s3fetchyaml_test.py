"""s3fetchyaml.py unit tests."""
import io
import pytest
import pypyraws.steps.s3fetchyaml  # as s3fetchyaml
from pypyr.context import Context
import ruamel.yaml as yaml
from unittest.mock import patch


@patch('pypyraws.aws.service.operation_exec')
def test_s3fetchyaml(mock_s3):
    """Success path all the way through to the mocked boto s3 object."""
    input_dict = {'newkey': 'newvalue', 'newkey2': 'newvalue2'}
    yaml_loader = yaml.YAML()
    string_stream = io.StringIO()
    yaml_loader.dump(input_dict, string_stream)
    mock_s3.side_effect = [{'Body': string_stream.getvalue()}]

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
    pypyraws.steps.s3fetchyaml.run_step(context)
    assert len(context) == 4
    assert context['k1'] == 'v1'
    assert context['newkey'] == 'newvalue'
    assert context['newkey2'] == 'newvalue2'


@patch('pypyraws.aws.service.operation_exec')
def test_s3fetchyaml_with_destination(mock_s3):
    """Yaml writes to destination key."""
    input = [1, 2, 3]
    yaml_loader = yaml.YAML()
    string_stream = io.StringIO()
    yaml_loader.dump(input, string_stream)
    mock_s3.side_effect = [{'Body': string_stream.getvalue()}]

    context = Context({
        'k1': 'v1',
        's3Fetch': {
            'clientArgs': {'ck1': 'cv1', 'ck2': 'cv2'},
            'methodArgs': {'Bucket': 'bucket name',
                           'Key': 'key name',
                           'SSECustomerAlgorithm': 'sse alg',
                           'SSECustomerKey': 'sse key'},
            'outKey': 'writehere'
        }})

    pypyraws.steps.s3fetchyaml.run_step(context)

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
            'outKey': 'writehere'},
        'writehere': [1, 2, 3]
    }


@patch('pypyraws.aws.service.operation_exec')
def test_s3fetchyaml_with_destination_int(mock_s3):
    """Yaml overwrites destination key that's not a string."""
    input = [1, 2, 3]
    yaml_loader = yaml.YAML()
    string_stream = io.StringIO()
    yaml_loader.dump(input, string_stream)
    mock_s3.side_effect = [{'Body': string_stream.getvalue()}]

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

    pypyraws.steps.s3fetchyaml.run_step(context)

    assert context[99] == [1, 2, 3]
    assert len(context) == 3


@patch('pypyraws.aws.service.operation_exec')
def test_s3fetchyaml_with_destination_formatting(mock_s3):
    """Yaml writes to destination key found by formatting expression."""
    input = {'1': 2, '2': 3}
    yaml_loader = yaml.YAML()
    string_stream = io.StringIO()
    yaml_loader.dump(input, string_stream)
    mock_s3.side_effect = [{'Body': string_stream.getvalue()}]

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

    pypyraws.steps.s3fetchyaml.run_step(context)

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
def test_s3fetchyaml_list_fails(mock_s3):
    """Yaml describing a list rather than a dict should fail if no outkey."""
    input = [1, 2, 3]
    yaml_loader = yaml.YAML()
    string_stream = io.StringIO()
    yaml_loader.dump(input, string_stream)
    mock_s3.side_effect = [{'Body': string_stream.getvalue()}]

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
        pypyraws.steps.s3fetchyaml.run_step(context)
