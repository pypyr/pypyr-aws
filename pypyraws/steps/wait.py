"""pypyr step that runs any boto3 low-level client waiter."""
import logging
import pypyraws.aws.service
from pypyr.errors import KeyInContextHasNoValueError, KeyNotInContextError


# pypyr logger means the log level will be set correctly and output formatted.
logger = logging.getLogger(__name__)


def run_step(context):
    """Run any low-level boto3 client wait from get_waiter.

    All of the awsWaitIn descendant values support {key}
    string interpolation.

    Args:
        context:
            Dictionary. Mandatory.
            Requires the following context keys in context:
                - awsWaitIn. dict. mandatory. Contains keys:

                  The awsWaitIn dictionary should contain:
                    - serviceName: mandatory. String for service name.
                      Available services here:
                      http://boto3.readthedocs.io/en/latest/reference/services/
                    - waiterName: mandatory. String. Name of waiter.
                    - waiterArgs: optional. Dict. kwargs for get_waiter
                    - waitArgs: optional. Dict. kwargs for wait

    Returns: None

    Raises:
        botocore.exceptions.ClientError: Anything inside boto went wrong.
        botocore.exceptions.WaiterError: General error.
        botocore.exceptions.FailureStateError: Status changed to a different
                                               state
        botocore.exceptions.TooManyAttemptsError: Timed out waiting for desired
                                                  state.
        pypyr.errors.KeyNotInContextError: awsClientIn missing in context.
        pypyr.errors.KeyInContextHasNoValueError: awsClientIn exists but is
                                                None.
    """
    logger.debug("started")
    client_in, service_name, waiter_name = get_waiter_args(context)

    waiter_args = client_in.get('waiterArgs', None)
    if waiter_args is not None:
        waiter_args = context.get_formatted_iterable(waiter_args)

    wait_args = client_in.get('waitArgs', None)
    if wait_args is not None:
        wait_args = context.get_formatted_iterable(wait_args)

    waiter_name = context.get_formatted_string(waiter_name)
    service_name = context.get_formatted_string(service_name)

    logger.info(f"Waiting for {waiter_name} on aws {service_name}.")

    pypyraws.aws.service.waiter(
        service_name=service_name,
        waiter_name=waiter_name,
        waiter_args=waiter_args,
        wait_args=wait_args)

    logger.debug("done")


def get_waiter_args(context):
    """Gets required args from context for this step.

    Args:
        context - dict. context.

    Returns:
        tuple(client_in, service_name, waiter_name)

    Raises:
        pypyr.errors.KeyNotInContextError: Required key missing in context.
        pypyr.errors.KeyInContextHasNoValueError: Required key exists but is
                                                  empty or None.
    """
    try:
        client_in = context['awsWaitIn']
        service_name = client_in['serviceName']
        waiter_name = client_in['waiterName']
    except KeyError as err:
        raise KeyNotInContextError(
            "awsWaitIn missing required key for pypyraws.steps.wait: "
            f"{err}"
        ) from err

    # of course, if They went and made it a bool and True this will pass.
    if not (service_name and service_name.strip()):
        raise KeyInContextHasNoValueError(
            'serviceName required in awsWaitIn for pypyraws.steps.wait')

    if not (waiter_name and waiter_name.strip()):
        raise KeyInContextHasNoValueError(
            'waiterName required in awsWaitIn for pypyraws.steps.wait')

    return client_in, service_name, waiter_name
