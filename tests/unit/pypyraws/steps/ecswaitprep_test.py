"""ecswaitprep.py unit tests."""
from pypyr.context import Context
from pypyr.errors import KeyInContextHasNoValueError, KeyNotInContextError
import pypyraws.steps.ecswaitprep as prepstep
import pytest


def test_waitprep_awsclientout_missing():
    """Missing awsClientOut raises."""
    with pytest.raises(KeyNotInContextError) as err:
        context = Context({'blah': 'blah blah'})
        prepstep.run_step(context)

    assert repr(err.value) == (
        "KeyNotInContextError(\"context['awsClientOut'] doesn't exist. It "
        "must exist for pypyraws.steps.ecswaitprep.\",)")


def test_waitprep_awsclientout_empty():
    """Missing awsClientOut raises."""
    with pytest.raises(KeyInContextHasNoValueError) as err:
        context = Context({'awsClientOut': None})
        prepstep.run_step(context)

    assert repr(err.value) == (
        "KeyInContextHasNoValueError(\"context['awsClientOut'] must have a "
        "value for pypyraws.steps.ecswaitprep.\",)")


def test_waitprep_awsclientout_no_matches():
    """Raise if no matching keys found in awsClientOut."""
    with pytest.raises(KeyNotInContextError) as err:
        context = Context({'awsClientOut': {}})
        prepstep.run_step(context)

    assert repr(err.value) == (
        "KeyNotInContextError(\"Run ecswaitprep after an ecs method that "
        "does something with services or tasks. Couldn't find service, "
        "serviceArns, services, task, taskArns or tasks in awsClientOut.\",)")

# ------------------------------ tasks ---------------------------------------#


def test_waitprep_task_no_cluster():
    """task with cluster pass"""
    context = Context({
        'awsClientOut': {
            'task': {
                'taskArn': 'arn1',
                'clusterArn': 'cluster1',
                'taskDefinitionArn': 'string',
            }
        }})

    prepstep.run_step(context)

    assert context['awsWaitIn'] == {'waitArgs': {
                                    'cluster': 'cluster1',
                                    'tasks': ['arn1']}}


def test_waitprep_task_with_cluster():
    """service with no cluster pass"""
    context = Context({
        'awsClientOut': {
            'task': {
                'taskArn': 'arn1',
                'clusterArn': 'string',
                'taskDefinitionArn': 'string',
            }
        },
        'awsEcsWaitPrepCluster': 'arb cluster'})

    prepstep.run_step(context)

    assert context['awsWaitIn'] == {'waitArgs': {
                                    'cluster': 'arb cluster',
                                    'tasks': ['arn1']}}


def test_waitprep_tasks_with_cluster():
    """Specifying cluster overrides all other clusters."""
    context = Context({
        'awsClientOut': {'tasks': [
            {
                'taskArn': 't one',
                'clusterArn': 'c arn 1',
                'taskDefinitionArn': 'string'},
            {
                'taskArn': 't two',
                'clusterArn': 'c arn 1',
                'taskDefinitionArn': 'string'},
            {
                'taskArn': 't three',
                'clusterArn': 'c arn 1',
                'taskDefinitionArn': 'string'}
        ]},
        'awsEcsWaitPrepCluster': 'arb cluster'})

    prepstep.run_step(context)

    assert context['awsWaitIn'] == {'waitArgs': {
                                    'cluster': 'arb cluster',
                                    'tasks': ['t one', 't two', 't three']}}


def test_waitprep_tasks_no_cluster():
    """Tasks parsed. Uses 1st task cluster."""
    context = Context({
        'awsClientOut': {'tasks': [
            {
                'taskArn': 't one',
                'clusterArn': 'c arn 1',
                'taskDefinitionArn': 'string'},
            {
                'taskArn': 't two',
                'clusterArn': 'c arn 1',
                'taskDefinitionArn': 'string'},
            {
                'taskArn': 't three',
                'clusterArn': 'c arn 1',
                'taskDefinitionArn': 'string'}
        ]}})

    prepstep.run_step(context)

    assert context['awsWaitIn'] == {'waitArgs': {
                                    'cluster': 'c arn 1',
                                    'tasks': ['t one', 't two', 't three']}}


def test_waitprep_taskarns_with_no_cluster():
    """taskarns with no cluster pass"""
    context = Context({
        'awsClientOut': {'taskArns': ['one', 'two', 'three'],
                         'NextToken': 'string'}
    })

    prepstep.run_step(context)

    assert context['awsWaitIn'] == {'waitArgs': {
                                    'tasks': ['one', 'two', 'three']}}


def test_waitprep_taskarns_with_cluster():
    """taskarns with cluster pass"""
    context = Context({
        'awsClientOut': {'taskArns': ['one', 'two', 'three'],
                         'NextToken': 'string'},
        'awsEcsWaitPrepCluster': 'arb cluster'
    })

    prepstep.run_step(context)

    assert context['awsWaitIn'] == {'waitArgs': {
                                    'cluster': 'arb cluster',
                                    'tasks': ['one', 'two', 'three']}}


def test_waitprep_dont_overwrite_existing_waitin():
    """Doesn't overwrite existing waitin, just overwrites waitArgs."""
    context = Context({
        'awsClientOut': {'taskArns': ['one', 'two', 'three'],
                         'NextToken': 'string'},
        'awsEcsWaitPrepCluster': 'arb cluster',
        'awsWaitIn': {
            'key1': 'value1'
        }
    })

    prepstep.run_step(context)

    assert context['awsWaitIn'] == {
        'key1': 'value1',
        'waitArgs': {
            'cluster': 'arb cluster',
            'tasks': ['one', 'two', 'three']}}


def test_waitprep_overwrite_existing_waitargs():
    """Doesn't overwrite existing waitin, just overwrites waitArgs."""
    context = Context({
        'awsClientOut': {'taskArns': ['one', 'two', 'three'],
                         'NextToken': 'string'},
        'awsEcsWaitPrepCluster': 'arb cluster',
        'awsWaitIn': {
            'key1': 'value1',
            'waitArgs': {'k1': 'v1'}
        }
    })

    prepstep.run_step(context)

    assert context['awsWaitIn'] == {
        'key1': 'value1',
        'waitArgs': {
            'cluster': 'arb cluster',
            'tasks': ['one', 'two', 'three']}}

# ------------------------------ tasks ---------------------------------------#

# ------------------------------ services-------------------------------------#


def test_waitprep_service_no_cluster():
    """service with cluster pass"""
    context = Context({
        'awsClientOut': {
            'service': {
                'serviceArn': 'arn1',
                'serviceName': 'string',
                'clusterArn': 'cluster1'
            }
        }})

    prepstep.run_step(context)

    assert context['awsWaitIn'] == {'waitArgs': {
                                    'cluster': 'cluster1',
                                    'services': ['arn1']}}


def test_waitprep_service_with_cluster():
    """service with no cluster pass"""
    context = Context({
        'awsClientOut': {
            'service': {
                'serviceArn': 'arn1',
                'serviceName': 'string',
                'clusterArn': 'cluster1'
            }
        },
        'awsEcsWaitPrepCluster': 'arb cluster'})

    prepstep.run_step(context)

    assert context['awsWaitIn'] == {'waitArgs': {
                                    'cluster': 'arb cluster',
                                    'services': ['arn1']}}


def test_waitprep_servicearns_with_no_cluster():
    """taskarns with no cluster pass"""
    context = Context({
        'awsClientOut': {'serviceArns': ['one', 'two', 'three'],
                         'NextToken': 'string'}
    })

    prepstep.run_step(context)

    assert context['awsWaitIn'] == {'waitArgs': {
                                    'services': ['one', 'two', 'three']}}


def test_waitprep_servicearns_with_cluster():
    """taskarns with cluster pass"""
    context = Context({
        'awsClientOut': {'serviceArns': ['one', 'two', 'three'],
                         'NextToken': 'string'},
        'awsEcsWaitPrepCluster': 'arb cluster'
    })

    prepstep.run_step(context)

    assert context['awsWaitIn'] == {'waitArgs': {
                                    'cluster': 'arb cluster',
                                    'services': ['one', 'two', 'three']}}


def test_waitprep_services_with_cluster():
    """Specifying cluster overrides all other clusters for services."""
    context = Context({
        'awsClientOut': {'services': [
            {
                'serviceArn': 's one',
                'serviceName': 'string',
                'clusterArn': 'c arn 1'},
            {
                'serviceArn': 's two',
                'serviceName': 'string',
                'clusterArn': 'c arn 2'},
            {
                'serviceArn': 's three',
                'serviceName': 'string',
                'clusterArn': 'c arn 3'}
        ]},
        'awsEcsWaitPrepCluster': 'arb cluster'})

    prepstep.run_step(context)

    assert context['awsWaitIn'] == {'waitArgs': {
                                    'cluster': 'arb cluster',
                                    'services': ['s one', 's two', 's three']}}


def test_waitprep_services_no_cluster():
    """services parsed. Uses 1st task cluster."""
    context = Context({
        'awsClientOut': {'services': [
            {
                'serviceArn': 's one',
                'serviceName': 'string',
                'clusterArn': 'c arn 1'},
            {
                'serviceArn': 's two',
                'serviceName': 'string',
                'clusterArn': 'c arn 2'},
            {
                'serviceArn': 's three',
                'serviceName': 'string',
                'clusterArn': 'c arn 3'}
        ]}})

    prepstep.run_step(context)

    assert context['awsWaitIn'] == {'waitArgs': {
                                    'cluster': 'c arn 1',
                                    'services': ['s one', 's two', 's three']}}
# ------------------------------ services-------------------------------------#
