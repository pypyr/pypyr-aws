"""s3 higher-level functions"""
import logging
import pypyraws.aws.service
from pypyr.errors import KeyNotInContextError

# pypyr logger means the log level will be set correctly and output formatted.
logger = logging.getLogger(__name__)


def get_payload(context):
    """Gets object from s3, reads underlying http stream, returns bytes.

    Args:
        context: pypyr.context.Context. Mandatory. Must contain key:
            - s3Fetch: dict. mandatory. Must contain:
                - methodArgs
                    - Bucket: string. s3 bucket name.
                    - Key: string. s3 key name.

    Returns:
        bytes: payload of the s3 obj in bytes

    Raises:
        KeyNotInContextError: s3Fetch or s3Fetch.methodArgs missing
    """
    logger.debug("started")

    assert context
    fetch_me = context['s3Fetch']

    try:
        operation_args = fetch_me['methodArgs']
    except KeyError as err:
        raise KeyNotInContextError(
            "s3Fetch missing required key for pypyraws.steps.s3fetch step: "
            "methodArgs") from err

    client_args = fetch_me.get('clientArgs', None)
    if client_args is not None:
        client_args = context.get_formatted_iterable(client_args)

    operation_args = context.get_formatted_iterable(operation_args)

    response = pypyraws.aws.service.operation_exec(
        service_name='s3',
        method_name='get_object',
        client_args=client_args,
        operation_args=operation_args)

    logger.debug("reading response stream")
    payload = response['Body']
    logger.debug("returning response bytes")

    logger.debug("done")
    return payload
