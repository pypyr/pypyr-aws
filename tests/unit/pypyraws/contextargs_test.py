"""contextargs.py unit tests."""
from pypyr.context import Context
from pypyr.errors import KeyInContextHasNoValueError, KeyNotInContextError
import pypyraws.contextargs as contextargs
import pytest

# ---------------------------- get_awsclient_args-----------------------------#


def test_get_awsclient_args_pass():
    """get_awsclient_args pass."""
    context = Context({
        'k1': 'v1',
        'awsClientIn': {
            'serviceName': 'service name',
            'methodName': 'method_name',
            'arbKey': 'arb_value'
        }})
    (service_name,
     method_name,
     client_args,
     method_args) = contextargs.get_awsclient_args(context['awsClientIn'],
                                                   'pypyraws.steps.client')

    assert service_name == 'service name'
    assert method_name == 'method_name'
    assert client_args is None
    assert method_args is None


def test_get_awsclient_args_missing_servicename():
    """Missing serviceName raises."""
    context = Context({
        'k1': 'v1',
        'awsClientIn': {
            'methodName': 'method_name',
            'arbKey': 'arb_value'
        }})

    with pytest.raises(KeyNotInContextError) as err_info:
        contextargs.get_awsclient_args(context['awsClientIn'],
                                       'pypyraws.steps.client')

    assert str(err_info.value) == ("awsClientIn missing required key for "
                                   "pypyraws.steps.client: 'serviceName'")


def test_get_awsclient_args_missing_methodname():
    """Missing methodName raises."""
    context = Context({
        'k1': 'v1',
        'awsClientIn': {
            'serviceName': 'service name',
            'arbKey': 'arb_value'
        }})

    with pytest.raises(KeyNotInContextError) as err_info:
        contextargs.get_awsclient_args(context['awsClientIn'],
                                       'pypyraws.steps.client')

    assert str(err_info.value) == ("awsClientIn missing required key for "
                                   "pypyraws.steps.client: 'methodName'")


def test_get_awsclient_args_servicename_empty():
    """Empty serviceName raises."""
    context = Context({
        'k1': 'v1',
        'awsClientIn': {
            'serviceName': '',
            'methodName': 'method_name',
            'arbKey': 'arb_value'
        }})

    with pytest.raises(KeyInContextHasNoValueError) as err_info:
        contextargs.get_awsclient_args(context['awsClientIn'],
                                       'pypyraws.steps.client')

    assert str(err_info.value) == ("serviceName required in awsClientIn "
                                   "for pypyraws.steps.client")


def test_get_awsclient_args_methodname_empty():
    """Whitespace serviceName raises."""
    context = Context({
        'k1': 'v1',
        'awsClientIn': {
            'serviceName': 'service name',
            'methodName': ' ',
            'arbKey': 'arb_value'
        }})

    with pytest.raises(KeyInContextHasNoValueError) as err_info:
        contextargs.get_awsclient_args(context['awsClientIn'],
                                       'pypyraws.steps.client')

    assert str(err_info.value) == ("methodName required in awsClientIn "
                                   "for pypyraws.steps.client")

# ---------------------------- get_awsclient_args-----------------------------#
