"""pypyr step that creates a custom waiter for any aws client operation."""
import logging
from pypyr.utils.poll import wait_until_true
import pypyraws.aws.service
import pypyraws.contextargs as contextargs
from pypyraws.errors import WaitTimeOut

# pypyr logger means the log level will be set correctly and output formatted.
logger = logging.getLogger(__name__)


def run_step(context):
    """Custom waiter for any aws client operation.

    All of the awsWaitFor descendant values support {key}
    string interpolation, except waitForField.

    Args:
        context:
            Dictionary. Mandatory.
            Requires the following context keys in context:
                - awsWaitFor. dict. mandatory. Contains keys:
                    - awsClientIn. dict. mandatory. This is the same as for the
                      pypyraws.steps.client in step. Contains keys:
                      - serviceName: mandatory. String for service name.
                                       Available services here:
                        http://boto3.readthedocs.io/en/latest/reference/services/
                      - methodName: mandatory. String. Name of method to
                                    execute.
                      - clientArgs: optional. Dict. kwargs for the boto client
                                    ctor.
                      - methodArgs: optional. Dict. kwargs for the client
                                    method call
                    - waitForField: mandatory. string. format expression for
                                    field name to check in awsClient response.
                    - toBe: mandatory. string. string. Stop waiting when
                            waitForField equals this value.
                    - pollInterval: optional. int. In seconds. Default to 30.
                    - maxAttempts: optional. int. Default 10.
                    - errorOnWaitTimeout: optional. Default True. Throws error
                                          if maxAttempts exhausted without
                                          reaching toBe value. If false,
                                          step completes without raising
                                          error.

    Returns: None
             Adds key to context:
            - awsWaitForTimedOut: bool. Adds key with value True if
              errorOnWaitTimeout=False and max_attempts exhausted without
              reaching toBe. If steps completes successfully and waitForField's
              value becomes toBe, awsWaitForTimedOut == False.

    Raises:
        pypyr.errors.KeyNotInContextError: awsWaitFor missing in context.
        pypyr.errors.KeyInContextHasNoValueError: awsWaitFor exists but is
                                                None.
        pypyraws.errors.WaitTimeOut: maxAttempts exceeded without waitForField
                                  changing to toBe.
    """
    logger.debug("started")
    context.assert_key_has_value('awsWaitFor', __name__)
    wait_for = context['awsWaitFor']

    client_in, service_name, method_name = contextargs.get_awsclient_args(
        wait_for, __name__)

    service_name = context.get_formatted_string(service_name)
    method_name = context.get_formatted_string(method_name)

    client_args = contextargs.get_formatted_iterable(input_dict=client_in,
                                                     field_name='clientArgs',
                                                     context=context)

    method_args = contextargs.get_formatted_iterable(input_dict=client_in,
                                                     field_name='methodArgs',
                                                     context=context)

    (wait_for_field,
     to_be,
     poll_interval,
     max_attempts,
     error_on_wait_timeout) = get_poll_args(wait_for, context)

    wait_response = wait_until_true(interval=poll_interval,
                                    max_attempts=max_attempts)(
        execute_aws_client_method)(
        service_name=service_name,
        method_name=method_name,
        client_args=client_args,
        method_args=method_args,
        wait_for_field=wait_for_field,
        to_be=to_be
    )

    if wait_response:
        context['awsWaitForTimedOut'] = False
        logger.info(f"aws {service_name} {method_name} returned {to_be}. "
                    "Pipeline will now continue.")
    else:
        if error_on_wait_timeout:
            context['awsWaitForTimedOut'] = True
            logger.error(f"aws {service_name} {method_name} did not return "
                         f"{to_be} within {max_attempts}. errorOnWaitTimeout "
                         "is True, throwing error")
            raise WaitTimeOut(f"aws {service_name} {method_name} did not "
                              f"return {to_be} within {max_attempts} retries.")
        else:
            context['awsWaitForTimedOut'] = True
            logger.warn(f"aws {service_name} {method_name} did NOT return "
                        f" {to_be}. errorOnWaitTimeout is False, so pipeline "
                        "will proceed to the next step anyway.")

    logger.debug("done")


def execute_aws_client_method(service_name,
                              method_name,
                              client_args,
                              method_args,
                              wait_for_field,
                              to_be):
    """Execute method_name on service_name.

    Args:
        service_name: string. Name of aws service.
        method_name: method to execute.
        client_args: aws client constructor args.
        method_args: method args
        wait_for_field: look for this field in the aws response
        to_be: return True if wait_for_field's value equals this.

    Return:
        True if value of wait_for_field == to_be, False if not.
    """
    logger.debug("started")
    response = pypyraws.aws.service.operation_exec(
        service_name=service_name,
        method_name=method_name,
        client_args=client_args,
        operation_args=method_args)

    wait_for_this_value = wait_for_field.format(**response)
    logger.info(f"{wait_for_field} in aws response is: {wait_for_this_value}")
    if wait_for_this_value == str(to_be):
        logger.debug("Required status reached. The wait is so over.")
        logger.debug("done")
        return True
    else:
        logger.debug("Required status not reached, keep waiting.")
        logger.debug("done")
        return False


def get_poll_args(waitfor_dict, context):
    """Gets polling arguments from waitfor_dict.

    Args:
        waitfor_dict: The awsWaitFor dict
        context: the pypyr context

    Returns:
    tuple(wait_for_field,
          to_be,
          poll_interval,
          max_attempts,
          error_on_wait_timeout)
    """
    logger.debug("started")
    wait_for_field = waitfor_dict['waitForField']

    to_be = context.get_formatted_string(str(waitfor_dict['toBe']))

    poll_interval = context.get_formatted_as_type(
        waitfor_dict.get('pollInterval', 30),
        out_type=float)

    max_attempts = context.get_formatted_as_type(
        waitfor_dict.get('maxAttempts', 10),
        out_type=int)

    error_on_wait_timeout = context.get_formatted_as_type(
        waitfor_dict.get('errorOnWaitTimeout', True),
        out_type=bool)

    logger.debug("done")

    return (wait_for_field,
            to_be,
            poll_interval,
            max_attempts,
            error_on_wait_timeout)
