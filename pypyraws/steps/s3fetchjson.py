"""pypyr step to fetch a json file from s3 and put it in context."""
from collections.abc import MutableMapping
import json
import logging
import pypyraws.aws.s3

# pypyr logger means the log level will be set correctly and output formatted.
logger = logging.getLogger(__name__)


def run_step(context):
    """Fetch a json file from s3 and put the json values into context.

    Args:
        - context: pypyr.context.Context. Mandatory. Should contain keys for:
            - s3Fetch: dict. mandatory. Must contain:
                -methodArgs
                    - Bucket: string. s3 bucket name.
                    - Key: string. s3 key name.
                -outKey. string. If exists, write json structure to this
                               context key. Else json writes to context root.

    All inputs support formatting expressions.

    json parsed from the s3 file will be merged into the
    context. This will overwrite existing values if the same keys are already
    in there. I.e if s3 json has {'eggs' : 'boiled'} and context
    {'eggs': 'fried'} already exists, returned context['eggs'] will be
    'boiled'.
    """
    logger.debug("started")
    response = pypyraws.aws.s3.get_payload(context)

    payload = json.load(response)
    logger.debug("successfully parsed json from s3 response bytes")

    destination_key_expression = context['s3Fetch'].get('outKey', None)

    if destination_key_expression:
        destination_key = context.get_formatted_iterable(
            destination_key_expression)
        logger.debug(f"Writing json to context {destination_key}")
        context[destination_key] = payload
    else:
        if not isinstance(payload, MutableMapping):
            raise TypeError(
                'json input should describe an object at the top '
                'level when outKey isn\'t specified. You should have '
                'something like {"key1": "value1", "key2": "value2"} '
                'in the json top-level, not ["value1", "value2"]')

        context.update(payload)

    logger.info("loaded s3 json into pypyr context")

    logger.debug("done")
