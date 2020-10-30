"""pypyr step that runs any boto3 low-level client method."""
import logging
import pypyraws.aws.service
import pypyraws.contextargs as contextargs


# pypyr logger means the log level will be set correctly and output formatted.
logger = logging.getLogger(__name__)


def run_step(context):
    """Execute any low-level boto3 client method.

    All of the awsClientIn descendant values support {key}
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
    context.assert_key_has_value('awsClientIn', __name__)
    client_in = context.get_formatted('awsClientIn')

    (service_name,
     method_name,
     client_args,
     method_args) = contextargs.get_awsclient_args(client_in, __name__)

    context['awsClientOut'] = pypyraws.aws.service.operation_exec(
        service_name=service_name,
        method_name=method_name,
        client_args=client_args,
        operation_args=method_args)

    logger.debug("aws response in context['awsClientOut']")
    logger.info(f"Executed {method_name} on aws {service_name}.")

    logger.debug("done")
