#################
pypyr aws plug-in
#################

.. image:: https://cdn.345.systems/wp-content/uploads/2017/03/pypyr-logo-small.png
    :alt: pypyr-logo
    :align: left

*pypyr*
  pronounce how you like, but I generally say *piper* as in "piping down the
  valleys wild"

  `pypyr <https://github.com/pypyr/pypyr-cli>`__ is a command line interface to
  run pipelines defined in yaml.

*the pypyr aws plug-in*
  Run anything on aws. No really, anything. If the aws api supports it, the
  pypyr aws plug-in supports it.

  It's a pretty easy way of invoking the aws api as a step
  in a series of steps.
  Why use this when you could just use the aws-cli instead? The aws cli is all
  kinds of awesome, but I find more often than not it's not just one or two aws
  *ad hoc* cli or aws api methods you have to execute, but especially when
  automating and scripting you actually need to run a sequence of commands,
  where the output of a previous command influences what you pass to the next
  command.

  Sure, you can bash it up, and I do that too, but running it as a pipeline
  via pypyr has actually made my life quite a bit easier in terms of not having
  to deal with conditionals, error traps and input validation.

|build-status| |coverage| |pypi|

.. contents::

.. section-numbering::

************
Installation
************

pip
===
.. code-block:: bash

  # pip install --upgrade pypyraws

pypyraws depends on the ``pypyr`` cli. The above ``pip`` will install it for
you if you don't have it already.

Python version
==============
Tested against Python >=3.6

********
Examples
********
If you prefer reading code to reading words, https://github.com/pypyr/pypyr-example

*****
steps
*****
+-------------------------------+-------------------------------------------------+------------------------------+
| **step**                      | **description**                                 | **input context properties** |
+-------------------------------+-------------------------------------------------+------------------------------+
| `pypyraws.steps.client`_      | Execute any low-level aws client method         | awsClientIn (dict)           |
+-------------------------------+-------------------------------------------------+------------------------------+
| `pypyraws.steps.ecswaitprep`_ | Run me after an ecs task run or stop to prepare | awsClientOut (dict)          |
|                               | an ecs waiter.                                  |                              |
|                               |                                                 | awsEcsWaitPrepCluster (str)  |
+-------------------------------+-------------------------------------------------+------------------------------+
| `pypyraws.steps.s3fetchjson`_ | Fetch a json file from s3 into the pypyr        | s3Fetch (dict)               |
|                               | context.                                        |                              |
+-------------------------------+-------------------------------------------------+------------------------------+
| `pypyraws.steps.s3fetchyaml`_ | Fetch a yaml file from s3 into the pypyr        | s3Fetch (dict)               |
|                               | context.                                        |                              |
+-------------------------------+-------------------------------------------------+------------------------------+
| `pypyraws.steps.wait`_        | Wait for an aws client waiter method to         | awsWaitIn (dict)             |
|                               | complete.                                       |                              |
+-------------------------------+-------------------------------------------------+------------------------------+
| `pypyraws.steps.waitfor`_     | Wait for any aws client method to complete,     | awsWaitFor (dict)            |
|                               | even when it doesn't have an official waiter.   |                              |
+-------------------------------+-------------------------------------------------+------------------------------+

pypyraws.steps.client
=====================
What can I do with pypyraws.steps.client?
-----------------------------------------
This step provides an easy way of getting at the low-level AWS api from the
pypyr pipeline runner. So in short, pretty much anything you can do with the
AWS api, you got it, as the Big O might have said.

This step lets you specify the service name and the service method you want to
execute dynamically. You can also control the service header arguments and the
method arguments themselves.

The arguments you pass to the service and its methods are exactly as given by
the AWS help documentation. So you do not have to learn yet another
configuration based abstraction on top of the AWS api that might not even
support all the methods you need.

You can actually pretty much just grab the json as written from the excellent
AWS help docs, paste it into some json that pypyr consumes and tadaaa!
Alternatively, grab the samples from the boto3 python documentation to include
in some yaml - the python dictionary structures map to yaml without too much
faff.

Supported AWS services
----------------------
Clients provide a low-level interface to AWS whose methods map close to 1:1
with the AWS REST service APIs. All service operations are supported by clients.

Run any method on any of the following aws low-level client services:

  acm, apigateway, application-autoscaling, appstream, autoscaling,
  batch, budgets, clouddirectory, cloudformation, cloudfront, cloudhsm,
  cloudsearch, cloudsearchdomain, cloudtrail, cloudwatch, codebuild, codecommit,
  codedeploy, codepipeline, codestar, cognito-identity, cognito-idp,
  cognito-sync, config, cur, datapipeline, devicefarm, directconnect, discovery,
  dms, ds, dynamodb, dynamodbstreams, ec2, ecr, ecs, efs, elasticache,
  elasticbeanstalk, elastictranscoder, elb, elbv2, emr, es, events, firehose,
  gamelift, glacier, health, iam, importexport, inspector, iot, iot-data,
  kinesis, kinesisanalytics, kms, lambda, lex-models, lex-runtime, lightsail,
  logs, machinelearning, marketplace-entitlement, marketplacecommerceanalytics,
  meteringmarketplace, mturk, opsworks, opsworkscm, organizations, pinpoint,
  polly, rds, redshift, rekognition, resourcegroupstaggingapi, route53,
  route53domains, s3, sdb, servicecatalog, ses, shield, sms, snowball, sns, sqs,
  ssm, stepfunctions, storagegateway, sts, support, swf, waf, waf-regional,
  workdocs, workspaces, xray

You can find full details for the supported services and what methods you can
run against them here:  http://boto3.readthedocs.io/en/latest/reference/services/

With the speed of new features and services AWS introduces, it's pretty
unlikely I'll get round to updating the list each and every time.

pypyr-aws will automatically support new services AWS releases for the boto3
client, in case the list above gets out of date. So while the document might
not update, the code already will dynamically use new features and services on
the boto3 client.

pypyr context
-------------
Requires the following context items:

.. code-block:: yaml

  awsClientIn:
    serviceName: 'aws service name here'
    methodName: 'execute this method of the aws service'
    clientArgs: # optional
      arg1Name: arg1Value
      arg2Name: arg2Value
    methodArgs: # optional
      arg1Name: arg1Value
      arg2Name: arg2Value

The *awsClientIn* context supports text `Substitutions`_.

AWS response
------------
After this step completes the full response is available to subsequent steps
in the pypyr context in the *awsClientOut* key.

Sample pipeline
---------------
Here is some sample yaml of what a pipeline using the pypyr-aws plug-in *client*
step could look like:

.. code-block:: yaml

  context_parser: pypyr.parser.keyvaluepairs
  steps:
    - name: pypyraws.steps.client
      description: upload a file to s3
      in:
        awsClientIn:
          serviceName: s3
          methodName: upload_file
          methodArgs:
            Filename: ./testfiles/arb.txt
            Bucket: '{bucket}'
            Key: arb.txt

If you saved this yaml as ``./pipelines/go-go-s3.yaml``, you can run
from ./ the following to upload *arb.txt* to your specified bucket:

.. code-block:: bash

  $ pypyr go-go-s3 "bucket=myuniquebucketname"


See a worked example for `pypyr aws s3 here
<https://github.com/pypyr/pypyr-example/blob/master/pipelines/aws-s3.yaml>`__.

pypyraws.steps.ecswaitprep
==========================
Run me after an ecs task run or stop to prepare an ecs waiter.

Prepares the awsWaitIn context key for pypyraws.steps.wait

Available ecs waiters are:

- ServicesInactive
- ServicesStable
- TasksRunning
- TasksStopped

Full details here: http://boto3.readthedocs.io/en/latest/reference/services/ecs.html#waiters

Use this step after any of the following ecs client methods if you want to use
one of the ecs waiters to wait for a specific state:

- describe_services
- describe_tasks
- list_services - specify awsEcsWaitPrepCluster if you don't want default
- list_tasks - specify awsEcsWaitPrepCluster if you don't want default
- run_task
- start_task
- stop_task
- update_service

You don't have to use this step, you could always just construct the awsWaitIn
dictionary in context yourself. It just so happens this step saves you some
legwork to do so.

Required context:

- awsClientOut

  - dict. mandatory.
  - This is the context key that any ecs command executed by
    pypyraws.steps.service adds. Chances are pretty good you don't want to
    construct this by hand yourself - the idea is to use the output as
    generated by one of the supported ecs methods.

- awsEcsWaitPrepCluster

  - string. optional.
  - The short name or full arn of the cluster that hosts the task to
    describe. If you do not specify a cluster, the default cluster is
    assumed. For most of the ecs methods the code automatically deduces the
    cluster from awsClientOut, so don't worry about it.
  - But, when following list_services and list_tasks, you have to specify
    this parameter.
  - Specifying this parameter will override any automatically deduced cluster arn

See a worked example for `pypyr aws ecs here
<https://github.com/pypyr/pypyr-example/blob/master/pipelines/aws-ecs.yaml>`__.

pypyraws.steps.s3fetchjson
==========================
Fetch a json file from s3 and put the json values into context.

Required input context is:

.. code-block:: yaml

  s3Fetch:
    clientArgs: # optional
      arg1Name: arg1Value
    methodArgs:
      Bucket: '{bucket}'
      Key: arb.json
    outKey: 'destination pypyr context key' # optional

- *clientArgs* are passed to the aws s3 client constructor. These are optional.
- *methodArgs* are passed the the s3 ``get_object`` call. The minimum required
  values are:

  - Bucket
  - Key

- Check here for all available arguments (including SSE server-side encryption):
  http://boto3.readthedocs.io/en/latest/reference/services/s3.html#S3.Client.get_object
- *outKey* writes fetched json to this context key. If not specified, json
  writes directly to context root.

Json parsed from the file will be merged into the pypyr context. This will
overwrite existing values if the same keys are already in there.

I.e if file json has ``{'eggs' : 'boiled'}``, but context ``{'eggs': 'fried'}``
already exists, returned ``context['eggs']`` will be 'boiled'.

If *outKey* is not specified, the json should not be an Array [] at the root
level, but rather an Object {}.

The *s3Fetch* input context supports text `Substitutions`_.

See a worked example for `pypyr aws s3fetch here
<https://github.com/pypyr/pypyr-example/blob/master/pipelines/aws-s3fetch.yaml>`__.

pypyraws.steps.s3fetchyaml
==========================
Fetch a yaml file from s3 and put the yaml structure into context.

Required input context is:

.. code-block:: yaml

  s3Fetch:
    clientArgs: # optional
      arg1Name: arg1Value
    methodArgs:
      Bucket: '{bucket}'
      Key: arb.yaml

- clientArgs are passed to the aws s3 client constructor. These are optional.
- methodArgs are passed the the s3 ``get_object`` call. The minimum required
  values are:

  - Bucket
  - Key

- Check here for all available arguments (including SSE server-side encryption):
  http://boto3.readthedocs.io/en/latest/reference/services/s3.html#S3.Client.get_object

The *s3Fetch* context supports text `Substitutions`_.

Yaml parsed from the file will be merged into the pypyr context. This will
overwrite existing values if the same keys are already in there.

I.e if file yaml has

.. code-block:: yaml

  eggs: boiled

but context ``{'eggs': 'fried'}`` already exists, returned ``context['eggs']``
will be 'boiled'.

The yaml should not be a list at the top level, but rather a mapping.

So the top-level yaml should not look like this:

.. code-block:: yaml

  - eggs
  - ham

but rather like this:

.. code-block:: yaml

  breakfastOfChampions:
    - eggs
    - ham

See a worked example for `pypyr aws s3fetch here
<https://github.com/pypyr/pypyr-example/blob/master/pipelines/aws-s3fetch.yaml>`__.

pypyraws.steps.wait
===================
Wait for things in AWS to complete before continuing pipeline.

Run any low-level boto3 client wait() from get_waiter.

Waiters use a client's service operations to poll the status of an AWS resource
and suspend execution until the AWS resource reaches the state that the waiter
is polling for or a failure occurs while polling.

http://boto3.readthedocs.io/en/latest/guide/clients.html#waiters

The input context requires:

.. code-block:: yaml

  awsWaitIn:
    serviceName: 'service name' # Available services here: http://boto3.readthedocs.io/en/latest/reference/services/
    waiterName: 'waiter name' # Check service docs for available waiters for each service
    waiterArgs:
      arg1Name: arg1Value # optional. Dict. kwargs for get_waiter
    waitArgs:
      arg1Name: arg1Value #optional. Dict. kwargs for wait

The *awsWaitIn* context supports text `Substitutions`_.

pypyraws.steps.waitfor
======================
Custom waiter for any aws client operation. Where `pypyraws.steps.wait`_ uses
the official AWS waiters from the low-level client api, this step allows you to
execute *any* aws low-level client method and wait for a specified field in
the response to become the value you want it to be.

This is especially handy for things like Beanstalk, because Elastic Beanstalk
does not have Waiters for environment creation.

The input context looks like this:

.. code-block:: yaml

  awsWaitFor:
    awsClientIn: # required. awsClientIn allows the same arguments as pypyraws.steps.client.
      serviceName: elasticbeanstalk
      methodName: describe_environments
      methodArgs:
          ApplicationName: my wonderful beanstalk default application
          EnvironmentNames:
            - my-wonderful-environment
          VersionLabel: v0.1
    waitForField: '{Environments[0][Status]}' # required. format expression for field name to check in awsClient response
    toBe: Ready # required. Stop waiting when waitForField equals this value
    pollInterval: 30 # optional. Seconds to wait between polling attempts. Defaults to 30 if not specified.
    maxAttempts: 10 # optional. Defaults to 10 if not specified.
    errorOnWaitTimeout: True # optional. Defaults to True if not specified. Stop processing if maxAttempts exhausted without reaching toBe value.

See `pypyraws.steps.client`_ for a full listing of available arguments under
*awsClientIn*.

If ``errorOnWaitTimeout`` is True and ``max_attempts`` exhaust before reaching
the desired target state, pypyr will stop processing with a
``pypyraws.errors.WaitTimeOut`` error.

Once this step completes it adds ``awsWaitForTimedOut`` to the pypyr context.
This is a boolean value with values:

+--------------------------+---------------------------------------------------+
| awsWaitForTimedOut       | Description                                       |
+--------------------------+---------------------------------------------------+
| True                     | ``errorOnWaitTimeout=False`` and ``max_attempts`` |
|                          | exhausted without reaching ``toBe``.              |
+--------------------------+---------------------------------------------------+
| False                    | ``waitForField``'s value becomes ``toBe`` within  |
|                          | ``max_attempts``.                                 |
+--------------------------+---------------------------------------------------+


The *awsWaitFor* context supports text `Substitutions`_. Do note that while
``waitForField`` uses substitution style format strings, the substitutions are
made against the response object that returns from the aws client call specified
in *awsClientIn*, and not from the pypyr context itself.

See a worked example for an `elastic beanstalk custom waiter for environmment
creation here
<https://github.com/pypyr/pypyr-example/blob/master/pipelines/aws-beanstalk-waitfor.yaml>`__.

*************
Substitutions
*************
You can use substitution tokens, aka string interpolation, where specified for
context items. This substitutes anything between {curly braces} with the
context value for that key. This also works where you have dictionaries/lists
inside dictionaries/lists. For example, if your context looked like this:

.. code-block:: yaml

  bucketValue: the.bucket
  keyValue: dont.kick
  moreArbText: wild
  awsClientIn:
    serviceName: s3
    methodName: get_object
    methodArgs:
      Bucket: '{bucketValue}'
      Key: '{keyValue}'

This will run s3 get_object to retrieve file *dont.kick* from *the.bucket*.

- *Bucket: '{bucketValue}'* becomes *Bucket: the.bucket*
- *Key: '{keyValue}'* becomes *Key: dont.kick*

In json & yaml, curlies need to be inside quotes to make sure they parse as
strings.

Escape literal curly braces with doubles: {{ for {, }} for }

See a worked example `for substitutions here
<https://github.com/pypyr/pypyr-example/tree/master/pipelines/substitutions.yaml>`__.


******************
aws authentication
******************
Configuring credentials
=======================
pypyr-aws pretty much just uses the underlying boto3 authentication mechanisms.
More info here: http://boto3.readthedocs.io/en/latest/guide/configuration.html

This means any of the following will work:

- If you are running inside of AWS - on EC2 or inside an ECS container, it will
  automatically use IAM role credentials if it does not find credentials in any
  of the other places listed below.
- In the pypyr context

  .. code-block:: python

    context['awsClientIn']['clientArgs'] = {
        aws_access_key_id: ACCESS_KEY,
        aws_secret_access_key: SECRET_KEY,
        aws_session_token: SESSION_TOKEN,
      }

- $ENV variables

  - AWS_ACCESS_KEY_ID
  - AWS_SECRET_ACCESS_KEY
  - AWS_SESSION_TOKEN

- Credentials file at *~/.aws/credentials* or *~/.aws/config*

  - If you have the aws-cli installed, run ``aws configure`` to get these
    configured for you automatically.

Tip: On dev boxes I generally don't bother with credentials, because chances
are pretty good that I have the aws-cli installed already anyway, so pypyr
will just re-use the aws shared configuration files that are there anyway.

Ensure secrets stay secret
==========================
Be safe! Don't hard-code your aws credentials. Don't check credentials into a
public repo.

Tip: if you're running pypyr inside of aws - e.g in an ec2 instance or an ecs
container that is running under an IAM role, you don't actually *need*
explicitly to configure credentials for pypyr-aws.

Do remember not to fling your key & secret around as shell arguments - it could
very easily leak that way into logs or expose via a ``ps``. I generally use one
of the pypyr built-in context parsers like *pypyr.parser.jsonfile* or
*pypyr.parser.yamlfile*, see
`here for details <https://github.com/pypyr/pypyr-cli#built-in-context-parsers>`__.

Do remember also that $ENV variables are not a particularly secure place to
keep your secrets.

*******
Testing
*******
Testing without worrying about dependencies
===========================================
Run from tox to test the packaging cycle inside a virtual env, plus run all
tests:

.. code-block:: bash

    # just run tests
    $ tox -e dev -- tests
    # run tests, validate README.rst, run flake8 linter
    $ tox -e stage -- tests

If tox is taking too long
=========================
The test framework is pytest. If you only want to run tests:

.. code-block:: bash

  $ pip install -e .[dev,test]

Day-to-day testing
==================
- Tests live under */tests* (surprising, eh?). Mirror the directory structure of
  the code being tested.
- Prefix a test definition with *test_* - so a unit test looks like

  .. code-block:: python

    def test_this_should_totally_work():

- To execute tests, from root directory:

  .. code-block:: bash

    pytest tests

- For a bit more info on running tests:

  .. code-block:: bash

    pytest --verbose [path]

- To execute a specific test module:

  .. code-block:: bash

    pytest tests/unit/arb_test_file.py

*****
Help!
*****
Don't Panic! For help, community or talk, join the chat on |discord|!

**********
Contribute
**********
Developers
==========
For information on how to help with pypyr, run tests and coverage, please do
check out the `contribution guide <https://github.com/pypyr/pypyr-cli/blob/master/CONTRIBUTING.rst>`_.

Bugs
====
Well, you know. No one's perfect. Feel free to `create an issue
<https://github.com/pypyr/pypyr-aws/issues/new>`_.


.. |build-status| image:: https://api.shippable.com/projects/58efdfe130eb380700e559a4/badge?branch=master
                    :alt: build status
                    :target: https://app.shippable.com/github/pypyr/pypyr-aws

.. |coverage| image:: https://api.shippable.com/projects/58efdfe130eb380700e559a4/coverageBadge?branch=master
                :alt: coverage status
                :target: https://app.shippable.com/github/pypyr/pypyr-aws

.. |pypi| image:: https://badge.fury.io/py/pypyraws.svg
                :alt: pypi version
                :target: https://pypi.python.org/pypi/pypyraws/
                :align: bottom

.. |discord| replace:: `discord <https://discordapp.com/invite/8353JkB>`__
