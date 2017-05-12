"""s3fetchjson.py unit tests."""
import json
import pypyraws.steps.s3fetchjson as s3fetchjson
from pypyr.context import Context
from unittest.mock import Mock, patch


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
