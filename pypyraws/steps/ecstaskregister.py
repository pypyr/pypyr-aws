"""pypyr step to register ecs task."""
import pypyraws.ecs.ecshandler
import pypyr.log.logger
import pypyr.validate.asserts

# pypyr logger means the log level will be set correctly and output formatted.
logger = pypyr.log.logger.get_logger(__name__)


def run_step(context):
    """Register ecs task.

    Args:
        context:
            Dictionary.
            context is mandatory. accepts these context keys for:
                - ecsCluster (mandatory). string. The short name or arn of the
                  cluster that hosts the task
                - ecsTaskArns (mandatory) list. Task Id or Arn.
                - ecsTaskWaitDelay (optional). int. Seconds.
                - ecsTaskWaitMaxAttempts (optional). int.

    Returns:
        context as passed in, plus context keys for:
            - ecsTaskArns. Dictionary of created task definition arns.

    Raises:
        ecs error if failure state or too many attempts retrying the waiter.
        TODO FailureStateError
        TODO TooManyAttemptsError
    """
    logger.debug("started")
    context_validate(context)

    logger.debug(
        f"waiting on arn {context['ecsTaskArns']} on cluster "
        f"{context['ecsCluster']}")

    # default delay to 6 - this is what it is by default for boto3
    delay = context['ecsTaskWaitDelay'] if 'ecsTaskWaitDelay' in context else 6
    # default max attempts to 100 - also default for boto
    max_attempts = context[
        'ecsTaskWaitMaxAttempts'] if (
            'ecsTaskWaitMaxAttempts' in context) else 100

    pypyraws.ecs.ecshandler.register_task(cluster=context['ecsCluster'],
                                          arns=context['ecsTaskArns'],
                                          delay=delay,
                                          max_attempts=max_attempts)
    logger.info(f"task arn {context['ecsTaskArns']} complete")

    logger.debug("done")
    return context


def context_validate(context):
    """Validate the context contains what it should. Raises AssertionError."""
    pypyr.validate.asserts.key_in_context_has_value(context,
                                                    'ecsCluster',
                                                    'ecstaskwait')
    pypyr.validate.asserts.key_in_context_has_value(context,
                                                    'ecsTaskArns',
                                                    'ecstaskwait')
