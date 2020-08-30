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
    client_in, service_name, method_name = contextargs.get_awsclient_args(
        context, 'pypyraws.steps.client')

    assert client_in == {
        'serviceName': 'service name',
        'methodName': 'method_name',
        'arbKey': 'arb_value'
    }
    assert service_name == 'service name'
    assert method_name == 'method_name'


def test_get_awsclient_args_missing_awsclientin():
    """Missing awsClientIn raises."""
    context = Context({'k1': 'v1'})

    with pytest.raises(KeyNotInContextError) as err_info:
        client_in, service_name, method_name = contextargs.get_awsclient_args(
            context, 'pypyraws.steps.client')

    assert str(err_info.value) == (
        "awsClientIn missing required key for "
        "pypyraws.steps.client: awsClientIn not found in the pypyr context.")


def test_get_awsclient_args_missing_servicename():
    """Missing serviceName raises."""
    context = Context({
        'k1': 'v1',
        'awsClientIn': {
            'methodName': 'method_name',
            'arbKey': 'arb_value'
        }})

    with pytest.raises(KeyNotInContextError) as err_info:
        client_in, service_name, method_name = contextargs.get_awsclient_args(
            context, 'pypyraws.steps.client')

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
        client_in, service_name, method_name = contextargs.get_awsclient_args(
            context, 'pypyraws.steps.client')

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
        client_in, service_name, method_name = contextargs.get_awsclient_args(
            context, 'pypyraws.steps.client')

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
        client_in, service_name, method_name = contextargs.get_awsclient_args(
            context, 'pypyraws.steps.client')

    assert str(err_info.value) == ("methodName required in awsClientIn "
                                   "for pypyraws.steps.client")

# ---------------------------- get_awsclient_args-----------------------------#

# ---------------------------- get_formatted_iterable-------------------------#


def test_getformatted_iterable_pass():
    """get_formatted_iterable passes."""
    context = Context({
        'k1': 'v1',
        'k2': 'v2',
        'awsClientIn': {
            'serviceName': '',
            'methodName': 'method_name',
            'clientArgs': {
                'cak1': 'cak2',
                '{k1}': '{k2}'
            },
            'arbKey': 'arb_value'

        }})

    result = contextargs.get_formatted_iterable(
        input_dict=context['awsClientIn'],
        field_name='clientArgs',
        context=context)

    assert result == {
        'cak1': 'cak2',
        'v1': 'v2'
    }


def test_getformatted_iterable_none_pass():
    """get_formatted_iterable none returns none."""
    context = Context({
        'k1': 'v1',
        'k2': 'v2',
        'awsClientIn': {
            'serviceName': '',
            'methodName': 'method_name',
            'clientArgs': {
                'cak1': 'cak2',
                '{k1}': '{k2}'
            },
            'arbKey': 'arb_value'

        }})

    result = contextargs.get_formatted_iterable(
        input_dict=context['awsClientIn'],
        field_name='doesntexist',
        context=context)

    assert result is None

# ---------------------------- get_formatted_iterable-------------------------#
