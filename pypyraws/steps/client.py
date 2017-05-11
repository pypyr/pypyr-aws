"""pypyr step that runs any boto3 low-level client method."""
import logging
import pypyraws.aws.service
from pypyr.errors import KeyInContextHasNoValueError, KeyNotInContextError


# pypyr logger means the log level will be set correctly and output formatted.
logger = logging.getLogger(__name__)


def run_step(context):
    """Execute any low-level boto3 client method.

    All of the awsClientIn descendant valuies support {key}
    string interpolation.

    Args:
        context:
            Dictionary. Mandatory.
            Requires the following context keys in context:
                - awsClientIn. dict. mandatory. Contains keys:

            The awsClientIn dictionary should contain:
                - serviceName: mandatory. String for service name.
                               Available services here:
                  http://boto3.readthedocs.io/en/latest/reference/services/
                - methodName: mandatory. String. Name of method to execute.
                - clientArgs: optional. Dict. kwargs for the boto client ctor.
                - methodArgs: optional. Dict. kwargs for the client method call

    Returns: None. Although there is no return, this does add awsClientOut to
             context.

             Adds key to context for response from aws client:
                - awsClientOut. Dictionary containing the full aws response.

    Raises:
        botocore.exceptions.ClientError: Anything inside boto went wrong.
        pypyr.errors.KeyNotInContextError: awsClientIn missing in context.
        pypyr.errors.KeyInContextHasNoValueError: awsClientIn exists but is
                                                  None.
    """
    logger.debug("started")
    client_in, service_name, method_name = get_service_args(context)

    client_args = client_in.get('clientArgs', None)
    if client_args is not None:
        client_args = context.get_formatted_iterable(client_args)

    method_args = client_in.get('methodArgs', None)
    if method_args is not None:
        method_args = context.get_formatted_iterable(method_args)

    context['awsClientOut'] = pypyraws.aws.service.operation_exec(
        service_name=context.get_formatted_string(service_name),
        method_name=context.get_formatted_string(method_name),
        client_args=client_args,
        operation_args=method_args)

    logger.debug("aws response in context['awsClientOut']")
    logger.info(f"Executed {method_name} on aws {service_name}.")

    logger.debug("done")


def get_service_args(context):
    """Gets required args from context for this step.

    Args:
        context - dict. context.

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
            "awsClientIn missing required key for pypyraws.steps.client: "
            f"{err}"
        ) from err

    # of course, if They went and made it a bool and True this will pass.
    if not (service_name and service_name.strip()):
        raise KeyInContextHasNoValueError(
            'serviceName required in awsClientIn for pypyraws.steps.client')

    if not (method_name and method_name.strip()):
        raise KeyInContextHasNoValueError(
            'methodName required in awsClientIn for pypyraws.steps.client')

    return client_in, service_name, method_name
