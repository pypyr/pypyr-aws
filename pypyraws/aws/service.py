"""aws service client.

This works with the boto low-level service client object.
"""
import boto3
import logging

# pypyr logger means the log level will be set correctly and output formatted.
logger = logging.getLogger(__name__)


def operation_exec(service_name,
                   method_name,
                   client_args=None,
                   operation_args=None):
    """Execute operation on boto low-level service client.

    Args:
        service_name: String. Name of service. Available services here:
                      http://boto3.readthedocs.io/en/latest/reference/services/
        method_name: String. Execute this method against the service_name
                     client. Check boto3 docs for available methods for
                     service_name.
        client_args: dict. Passed to the kwargs of the
                     boto3.client(*args, **kwargs) function.
        operation_args: dict. These are passed as kwargs to the method_name
                        when executing it.

    Returns:
        dict. Response from
                    service_name(client_args).method_name(operation_args)
              Be aware this could well be None if the service operation doesn't
              have a return.
              Code safe: use the default 2nd args on dict.get(key, default)
              to specify a default value where there is a chance of the value
              not existing. Don't bother if you're cheerful about KeyError.
    """
    logger.debug("started")
    if client_args is None:
        client = boto3.client(service_name)
        logger.debug(f"boto client instantiated {service_name} with no "
                     "constructor args")
    else:
        client = boto3.client(service_name, **client_args)
        logger.debug(f"boto client instantiated {service_name} with "
                     "constructor args")

    # dynamically executing method_name against the client and passing it
    # operation_args while it's at it.
    response = getattr(client, method_name)(**operation_args)
    logger.debug(f"Executed {method_name} on {service_name}.")
    logger.debug("done")
    return response


def waiter(service_name, waiter_name, waiter_args=None, wait_args=None):
    """Wait for an aws low-level client operation to reach poll state.

    Waiters use a client's service operations to poll the status of an AWS
    resource and suspend execution until the AWS resource reaches the state
    that the waiter is polling for or a failure occurs while polling.

    Default polls every 6 seconds until a successful state.
    Error after 100 polls.

    Args:
        service_name: String. Name of service. Available services here:
                      http://boto3.readthedocs.io/en/latest/reference/services/
        waiter_name: String. Get this waiter from the service_name
                     client. Check boto3 docs for available waiters for
                     service_name.
        waiter_args: dict. Passed to the kwargs of the
                     boto3.get_waiter(*args, **kwargs) function.
        wait_args: dict. These are passed as kwargs to the waiter's wait method
                   get_waiter(waiter_name).wait(**kwargs)

    Returns: None

    Raises:
        botocore.exceptions.WaiterError: General error.
        botocore.exceptions.FailureStateError: Status changed to a different
                                               state
        botocore.exceptions.TooManyAttemptsError: Timed out waiting for desired
                                                  state.
    """
    logger.debug("started")

    client = boto3.client(service_name)

    if waiter_args is None:
        waiter = client.get_waiter(waiter_name)
        logger.debug(f"boto client got waiter {waiter_name} on {service_name} "
                     "with no waiter args")
    else:
        waiter = client.get_waiter(waiter_name, **waiter_args)
        logger.debug(f"boto client got waiter {waiter_name} on {service_name} "
                     "with waiter args")

    waiter.wait(**wait_args)
    logger.debug("done")
