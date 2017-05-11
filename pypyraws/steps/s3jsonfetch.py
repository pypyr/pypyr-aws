"""pypyr step to fetch a json file from s3 and put it in context."""
import boto3
import botocore.client
import json
import pypyr.log.logger
import pypyr.validate.asserts

# pypyr logger means the log level will be set correctly and output formatted.
logger = pypyr.log.logger.get_logger(__name__)


def run_step(context):
    """Fetch a json file from s3 and put the json values into context.

    context is a dictionary.
    context is mandatory. context should contain keys for:
    - s3bucket
    - s3key

    Returns context. json parsed from the s3 file will be merged into the
    context. This will overwrite existing values if the same keys are already
    in there. I.e if s3 json has {'eggs' : 'boiled'} and context
    {'eggs': 'fried'} already exists, returned context['eggs'] will be
    'boiled'.
    """
    logger.debug("started")
    context_validate(context)

    logger.info(f"retrieving s3 file {context['s3key']}")

    # The s3 client doesn't default signature version to 4,
    # meaning the decrypt will fail if it's not set here.
    client = boto3.client('s3',
                          config=botocore.client.Config(
                              signature_version='s3v4'))

    response = client.get_object(
        Bucket=context['s3bucket'], Key=context['s3key'])

    logger.info("retrieved s3 file")
    payload = json.load(response['Body'])

    logger.info("load json into pipeline context")
    context.update(payload)

    logger.debug("done")


def context_validate(context):
    """Asserts all required values in context."""
    required_keys = ['s3bucket', 's3jsonfetch']

    pypyr.validate.asserts.keys_in_context_has_value(context,
                                                     required_keys,
                                                     __name__)
