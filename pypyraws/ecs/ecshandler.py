"""cd aws ecs handler.

Aws Ecs boto3 functions encapsulated here.
Registers and runs tasks in Ecs.
"""
import boto3
import pypyr.log.logger
import pypyraws.ecs.TaskDefinition

# pypyr logger means the log level will be set correctly and output formatted.
logger = pypyr.log.logger.get_logger(__name__)


def get_command_text_as_list(command_text):
    """Convert bash command "echo text" to ["echo", "text"]."""
    logger.debug("starting")
    if command_text is not None:
        logger.debug("splitting command text into list")
        command_list = command_text.split()
    else:
        logger.debug("command text empty. Initialize empty command list.")
        command_list = []

    logger.debug("done")
    return command_list


def process_failures(failures):
    """Process failures returned from aws ecs task functions."""
    if len(failures) == 0:
        logger.debug("no failures returned from aws ecs")
    else:
        logger.error("aws ecs task processing error")
        for failure in failures:
            logger.error(failure)
        logger.error(failures)


def register_task(task_definition):
    """Register ecs task for the specified container.

       Args:
        task_definition: TaskDefinition. Required.
    """
    logger.debug("starting")
    assert task_definition, "task_definition required"

    command_list = get_command_text_as_list(command_text)

    ecs = boto3.client("ecs")

    response = ecs.register_task_definition(
        family=task_definition.family,
        networkMode=task_definition.network_mode,
        containerDefinitions=task_definition.get_container_definitions
    )

    arn = response['taskDefinition']['taskDefinitionArn']
    logger.info(f"task created. Arn is: {arn}")
    logger.debug("done")
    return response


def run_task(cluster,
             task_arn,
             container_tag,
             command_text,
             count,
             started_by):
    """Run the task specified by arn on cluster."""
    logger.debug("starting")

    command_list = get_command_text_as_list(command_text)

    ecs = boto3.client("ecs")
    response = ecs.run_task(
        cluster=cluster,
        taskDefinition=task_arn,
        overrides={
            'containerOverrides': [
                {
                    'name': container_tag,
                    'command': command_list
                }
            ]
        },
        count=count,
        startedBy=started_by
    )

    for task in response['tasks']:
        logger.info(f"ecs task run arn: {task['taskArn']}: "
                    f"last status: {task['lastStatus']}")

    process_failures(response['failures'])

    logger.debug("complete")


def wait_for_task(cluster,
                  arns,
                  delay=6,
                  max_attempts=100):
    """Wait for an ecs task to stop.

    Polls every 6 seconds until a successful state. Error after 100 checks.

    Args:
        cluster: string. The short name or full Amazon Resource Name (ARN) of
                 the cluster that hosts the task to describe. If you do not
                 specify a cluster, the default cluster is assumed.
        arns: List of task IDs or full Amazon Resource Name (ARN) entries.
        delay: Int. Delay in seconds between polling intervals.
        max_attempts: Number of retries on polling for completion.

    Returns: None
    """
    ecs = boto3.client("ecs")
    waiter = ecs.get_waiter('tasks_stopped',
                            delay=delay,
                            max_attempts=max_attempts)

    waiter.wait(
        cluster=cluster,
        tasks=arns
    )
