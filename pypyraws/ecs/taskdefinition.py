"""TaskDefinition class."""
import pypyr.validation.asserts as asserts


class TaskDefinition(object):
    """Encapsulate properties and validation for ecs tasks.

    These properties end up in passed to AWS boto3. For more info on what each
    parameter means:
    http://boto3.readthedocs.io/en/latest/reference/services/ecs.html#ECS.Client.register_task_definition

    Attributes:
        region: A boolean indicating if we like SPAM or not.
        family: An integer count of the eggs we have laid.
        image: The image used to start a container.
        container_name: string. 255 characters. The name of a container.
        command_text: The command that is passed to the container.
                      Cf. docker cmd.
        cpu: integer. Number of cpu units reserved for container.
        memory: integer. Hard limit in MiB for container memory.
        network_mode: string. bridge'|'host'|'none'. You prob want bridge.
        log_driver: string. Logdriver to use for container. Only awslogs
                    supported if specified.
        log_group: string. Region for logs if awslogs.
        log_prefix: string. Prefix for logstream if awslogs. Log format is:
                    prefix-name/container-name/ecs-task-id
    """

    def __init__(self, context):
        """Inits TaskDefinition.

           Args:
               context:
                   Dictionary. Mandatory.
                   Expected context keys:
                       - ecsCluster (required). string. The short name or arn
                         of the cluster that hosts the task
                       - ecsTaskArns (required) list. Task Id or Arn.
                       - ecsTaskWaitDelay (optional). int. Seconds.
                       - ecsTaskWaitMaxAttempts (optional). int.
        """
        self.context_validate(context)

        self.region = context['awsRegion']
        self.family = context['ecsTaskFamily']
        self.image = context['ecsTaskImage']
        self.container_name = context['ecsTaskContainerName']
        self.command_text = context['ecsCommandText']
        self.cpu = context['ecsTaskCpu']
        self.memory = context['ecsTaskMemory']
        self.network_mode = context['ecsNetworkMode']
        self.log_driver = context['ecsLogDriver']
        self.log_group = context['ecsLogGroup']
        self.log_prefix = context['ecsLogPrefix']

    def context_validate(self, context):
        """Validates context contains what it should."""
        required_keys = ['ecsTaskContainerName', 'ecsTaskImage']

        asserts.keys_in_context_has_value(context,
                                          required_keys,
                                          self.__class__.__name__)

    def get_awslogs_definition(self):
        """Returns logConfiguration if log_driver awslogs"""
        if self.log_driver == 'awslogs':
            return {
                'logDriver': self.log_driver,
                'options': {
                    'awslogs-group': self.log_group,
                    'awslogs-region': self.region,
                    'awslogs-stream-prefix': self.log_prefix
                }
            }
        else:
            return None

    def get_container_definitions(self):
        """Returns container definition dictionary.

        Returns:
            Dictionary in ecs container definition format
        """
        container_definitions = [
            {
                'name': self.container_name,
                'image': self.image,
                'cpu': self.cpu,
                'memory': self.memory,
                'essential': True,
                'command': self.command_list
            }
        ]

        log_definition = self.get_awslogs_definition()

        if log_definition is not None:
            container_definitions['logConfiguration'] = log_definition

        return container_definitions
