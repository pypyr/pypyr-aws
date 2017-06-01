"""Prepare aws arguments from the pypyr context."""
from pypyr.errors import KeyInContextHasNoValueError, KeyNotInContextError


def get_awsclient_args(context, calling_module_name):
    """Get required args from context for awsClientIn type steps.

    Args:
        context: pypyr.context.Context.
        calling_module_name: string. This is just to make a friendly error msg
                             should something go wrong.

    Returns:
        tuple(client_in, service_name, method_name)

    Raises:
        pypyr.errors.KeyNotInContextError: Required key missing in context.
        pypyr.errors.KeyInContextHasNoValueError: Required key exists but is
                                                  empty or None.
    """
    try:
        client_in = context['awsClientIn']
        service_name = client_in['serviceName']
        method_name = client_in['methodName']
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

    return client_in, service_name, method_name


def get_formatted_iterable(input_dict, field_name, context):
    """Format inputdict's field_name field against context.

    Args:
        input_dict: dict. Dictionary containing dict to format.
        field_name: str. Points at field in input_dict to format.
        context: pypyr.context.Context. Substitutes string expressions from
                 this.

    Returns:
        dict: Formatted dictionary that was at input_dict['field_name']
              Returns None if input_dict['field_name'] doesn't exist.
    """
    output = input_dict.get(field_name, None)
    if output is not None:
        output = context.get_formatted_iterable(output)

    return output
