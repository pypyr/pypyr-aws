"""s3 higher-level functions."""
import logging
import pypyraws.aws.service
from pypyr.errors import KeyNotInContextError

# pypyr logger means the log level will be set correctly and output formatted.
logger = logging.getLogger(__name__)


def get_payload(fetch_me):
    """Get object from s3, reads underlying http stream, returns bytes.

    Args:
        fetch_me (dict): Mandatory. Must contain key:
            - methodArgs
                - Bucket: string. s3 bucket name.
                - Key: string. s3 key name.

    Returns:
        bytes: payload of the s3 obj in bytes

    Raises:
        KeyNotInContextError: s3Fetch or s3Fetch.methodArgs missing
    """
    logger.debug("started")

    try:
        operation_args = fetch_me['methodArgs']
    except KeyError as err:
        raise KeyNotInContextError(
            "s3Fetch missing required key for pypyraws.steps.s3fetch step: "
            "methodArgs") from err

    client_args = fetch_me.get('clientArgs', None)

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


def get_fetch_input(context, caller):
    """Get s3Fetch formatted context.

    Args:
        context (pypyr.context.Context(): Mandatory. Must contain:
            - s3Fetch: dict. mandatory. Must contain:
                - methodArgs
                    - Bucket: string. s3 bucket name.
                    - Key: string. s3 key name.
        caller (string): Mandatory. __name__ of caller.

    Returns:
        Formatted dict under the context['s3Fetch']

    Raises:
       KeyNotInContextError: s3Fetch or s3Fetch.methodArgs missing
       KeyInContextHasNoValueError: s3Fetch doesn't have a value.
    """
    context.assert_key_has_value(key='s3Fetch', caller=caller)
    return context.get_formatted('s3Fetch')
