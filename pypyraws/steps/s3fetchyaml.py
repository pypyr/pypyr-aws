"""pypyr step to fetch a json file from s3 and put it in context."""
import logging
import pypyraws.aws.s3
import ruamel.yaml as yaml

# pypyr logger means the log level will be set correctly and output formatted.
logger = logging.getLogger(__name__)


def run_step(context):
    """Fetch a json file from s3 and put the json values into context.

    Args:
        - context: pypyr.context.Context. Mandatory. Should contain keys for:
            - s3Fetch: dict. mandatory. Must contain:
                - Bucket: string. s3 bucket name.
                - Key: string. s3 key name.

    json parsed from the s3 file will be merged into the
    context. This will overwrite existing values if the same keys are already
    in there. I.e if s3 json has {'eggs' : 'boiled'} and context
    {'eggs': 'fried'} already exists, returned context['eggs'] will be
    'boiled'.
    """
    logger.debug("started")
    response = pypyraws.aws.s3.get_payload(context)

    payload = yaml.safe_load(response)
    logger.debug("successfully parsed yaml from s3 response bytes")
    context.update(payload)
    logger.info("loaded s3 yaml into pypyr context")

    logger.debug("done")
