"""aws ecs functions.

aws ecs task runner.
Schedules and runs tasks on ecs. Writes outputs to logging database.
"""
from cd.ecs.ecshandler import register_task
from cd.ecs.ecshandler import run_task

import pypyr.log.logger

# pypyr logger means the log level will be set correctly and output formatted.
logger = pypyr.log.logger.get_logger(__name__)


def register_cd_task(pipeline_state, region):
    """Register cd container task."""
    logger.debug("starting")

    container_tag = ''  # get_container_tag(pipeline_state.build_no, 'devops')

    logger.debug("container name is: %s", container_tag)

    family = 'cloco-ecs-cd-deploy-stage-task-definition-{0}' \
        .format(container_tag)

    arn = register_task(region=region,
                        family=family,
                        container_tag=container_tag,
                        command_text=None,
                        build_no=pipeline_state.build_no)

    pipeline_state.set_devops_task_registered_complete(arn=arn)
    logger.debug("done")


def register_e2e_task(pipeline_state, region):
    """Register e2e container task."""
    logger.debug("starting")

    container_tag = ''  # get_container_tag(pipeline_state.build_no, 'e2e')

    logger.debug("container name is: %s", container_tag)

    family = 'cloco-ecs-e2e-task-definition-{0}' \
        .format(container_tag)

    arn = register_task(region=region,
                        family=family,
                        container_tag=container_tag,
                        command_text=None,
                        build_no=pipeline_state.build_no)

    pipeline_state.set_e2e_task_registered_complete(arn=arn)
    logger.debug("done")

    return arn


def run_cd_task(pipeline_state):
    """Run cd container task.

    Runs the deployment pipeline inside the container.
    """
    logger.info("starting")

    logger.info("starting task %s", pipeline_state.devops_task_definition_arn)

    cluster = 'ecs-cloco-stage-cd-cluster'

    container_tag = 'T'  # get_container_tag(pipeline_state.build_no, 'devops')

    # this is the path inside the container. Container's root dir is ops.
    command_text = 'cloco-cd-pipeline --commit {0} --buildNo {1}' \
        .format(pipeline_state.commit_hash, pipeline_state.build_no)

    run_task(cluster=cluster,
             task_arn=pipeline_state.devops_task_definition_arn,
             container_tag=container_tag,
             command_text=command_text,
             started_by='shippable-ci')

    logger.info("done")
