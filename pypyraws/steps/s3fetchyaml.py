"""pypyr step to fetch a yaml file from s3 and put it in context."""
from collections.abc import MutableMapping
import logging
import pypyraws.aws.s3
import ruamel.yaml as yaml

# pypyr logger means the log level will be set correctly and output formatted.
logger = logging.getLogger(__name__)


def run_step(context):
    """Fetch a yaml file from s3 and put the yaml values into context.

    Args:
        - context: pypyr.context.Context. Mandatory. Should contain keys for:
            - s3Fetch: dict. mandatory. Must contain:
                - Bucket: string. s3 bucket name.
                - Key: string. s3 key name.
            - outKey. string. If exists, write yaml structure to this
                           context key. Else yaml writes to context root.

    yaml parsed from the s3 file will be merged into the
    context. This will overwrite existing values if the same keys are already
    in there. I.e if s3 yaml has {'eggs' : 'boiled'} and context
    {'eggs': 'fried'} already exists, returned context['eggs'] will be
    'boiled'.
    """
    logger.debug("started")
    response = pypyraws.aws.s3.get_payload(context)

    yaml_loader = yaml.YAML(typ='safe', pure=True)
    payload = yaml_loader.load(response)
    logger.debug("successfully parsed yaml from s3 response bytes")

    destination_key_expression = context['s3Fetch'].get('outKey', None)

    if destination_key_expression:
        destination_key = context.get_formatted_iterable(
            destination_key_expression)
        logger.debug(f"Writing yaml to context {destination_key}")
        context[destination_key] = payload
    else:
        if not isinstance(payload, MutableMapping):
            raise TypeError(
                "yaml input should describe a dictionary at the top "
                "level when outKey isn't specified. You should have "
                "something like \n'key1: value1'\n key2: value2'\n"
                "in the yaml top-level, not \n'- value1\n - value2'")
        context.update(payload)

    logger.info("loaded s3 yaml into pypyr context")

    logger.debug("done")
