"""ecstaskwait.py unit tests."""
from unittest.mock import patch
import pypyraws.ecs.ecshandler
import pypyraws.steps.ecstaskwait
import pytest


def test_ecscluster_mandatory():
    """No 'ecsCluster'  in context should throw assert error."""
    with pytest.raises(AssertionError):
        context = {'blah': 'blah blah'}
        context = pypyraws.steps.ecstaskwait.context_validate(context)


def test_ecscluster_has_value():
    """Key 'ecsCluster'  in context should throw assert error if None."""
    with pytest.raises(AssertionError):
        context = {'ecsCluster': None}
        context = pypyraws.steps.ecstaskwait.context_validate(context)


def test_arn_mandatory():
    """No 'ecsTaskArn'  in context should throw assert error."""
    with pytest.raises(AssertionError):
        context = {'ecsCluster': 'blah blah'}
        context = pypyraws.steps.ecstaskwait.run_step(context)


def test_arn_has_value():
    """Key 'ecsTaskArn' in context should throw assert error if None."""
    with pytest.raises(AssertionError):
        context = {'ecsCluster': 'blah blah', 'ecsTaskArns': None}
        context = pypyraws.steps.ecstaskwait.context_validate(context)


def test_ecstaskwait_validate_pass():
    """Success."""
    context = {'ecsCluster': 'blah blah', 'ecsTaskArns': ['arn blah']}
    context = pypyraws.steps.ecstaskwait.context_validate(context)


def test_ecstask_wait_correct_default_params():
    """Parameters should pass through to ecshandler correctly."""
    context = {'ecsCluster': 'blah blah',
               'ecsTaskArns': ['arn blah'],
               'ecsTaskWaitDelay': 3,
               'ecsTaskWaitMaxAttempts': 33}

    with patch('pypyraws.ecs.ecshandler.wait_for_task',
               return_value=None) as mock_wait:
        context = pypyraws.steps.ecstaskwait.run_step(context)

    mock_wait.assert_called_once_with(cluster='blah blah',
                                      arns=['arn blah'],
                                      delay=3,
                                      max_attempts=33)
