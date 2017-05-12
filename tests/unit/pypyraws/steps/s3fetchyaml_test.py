"""s3fetchyaml.py unit tests."""
import pypyraws.steps.s3fetchyaml  # as s3fetchyaml
from pypyr.context import Context
import ruamel.yaml as yaml
from unittest.mock import patch


@patch('pypyraws.aws.service.operation_exec')
def test_s3fetchyaml(mock_s3):
    """Success path all the way through to the mocked boto s3 object."""
    input_dict = {'newkey': 'newvalue', 'newkey2': 'newvalue2'}
    string_of_yaml = yaml.dump(input_dict, Dumper=yaml.RoundTripDumper)
    bunch_of_bytes = bytes(string_of_yaml, 'utf-8')
    mock_s3.side_effect = [{'Body': bunch_of_bytes}]

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
