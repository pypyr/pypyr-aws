"""Prepare aws arguments from the pypyr context."""
from pypyr.errors import KeyInContextHasNoValueError, KeyNotInContextError


def get_awsclient_args(input_dict, calling_module_name):
    """Get required args from context for awsClientIn type steps.

    Doesn't do any formatting. You gotta format before you get here.

    Args:
        input_dict (dict): dict-like structure containing awsClientIn key.
        calling_module_name: string. This is just to make a friendly error msg
                             should something go wrong.

    Returns:
        tuple(service_name, method_name, client_args, method_args)

    Raises:
        pypyr.errors.KeyNotInContextError: Required key missing in context.
        pypyr.errors.KeyInContextHasNoValueError: Required key exists but is
                                                  empty or None.
    """
    try:
        service_name = input_dict['serviceName']
        method_name = input_dict['methodName']
    except KeyError as err:
        raise KeyNotInContextError(
            f"awsClientIn missing required key for {calling_module_name}: "
            f"{err}"
        ) from err

    if not (service_name and service_name.strip()):
        raise KeyInContextHasNoValueError(
            f'serviceName required in awsClientIn for {calling_module_name}')

    if not (method_name and method_name.strip()):
        raise KeyInContextHasNoValueError(
            f'methodName required in awsClientIn for {calling_module_name}')

    client_args = input_dict.get('clientArgs', None)
    method_args = input_dict.get('methodArgs', None)

    return service_name, method_name, client_args, method_args
