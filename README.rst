#################
pypyr aws plug-in
#################

.. image:: https://cdn.345.systems/wp-content/uploads/2017/03/pypyr-logo-small.png
    :alt: pypyr-logo
    :align: left

*pypyr*
    pronounce how you like, but I generally say *piper* as in "piping down the
    valleys wild"

Run anything on the aws. The easiest way to invoke the aws api.
Send messages to `slack <https://slack.com/>`__ from pypyr. This is useful for
sending notifications on success or failure conditions in your pipelines. Or
for sending a message just because you can.

`pypyr <https://github.com/pypyr/pypyr-cli>`__ is a command line interface to
run pipelines defined in yaml.

|build-status| |coverage| |pypi|

.. contents::

.. section-numbering::

************
Installation
************

pip
===
.. code-block:: bash

  # pip install --upgrade pypyr-aws

pypyr-slack depends on pypyr-cli. The above ``pip`` will install it for you if
you don't have it already.

Python version
==============
Tested against Python 3.6

*****
steps
*****
pypyrslack.steps.client
=======================
Run any method on any of the following aws services:
  acm, apigateway, application-autoscaling, appstream, autoscaling, batch, budgets, clouddirectory, cloudformation, cloudfront, cloudhsm, cloudsearch, cloudsearchdomain, cloudtrail, cloudwatch, codebuild, codecommit, codedeploy, codepipeline, codestar, cognito-identity, cognito-idp, cognito-sync, config, cur, datapipeline, devicefarm, directconnect, discovery, dms, ds, dynamodb, dynamodbstreams, ec2, ecr, ecs, efs, elasticache, elasticbeanstalk, elastictranscoder, elb, elbv2, emr, es, events, firehose, gamelift, glacier, health, iam, importexport, inspector, iot, iot-data, kinesis, kinesisanalytics, kms, lambda, lex-models, lex-runtime, lightsail, logs, machinelearning, marketplace-entitlement, marketplacecommerceanalytics, meteringmarketplace, mturk, opsworks, opsworkscm, organizations, pinpoint, polly, rds, redshift, rekognition, resourcegroupstaggingapi, route53, route53domains, s3, sdb, servicecatalog, ses, shield, sms, snowball, sns, sqs, ssm, stepfunctions, storagegateway, sts, support, swf, waf, waf-regional, workdocs, workspaces, xray

Required Context
----------------

Requires the following context items:

- slackToken

  - your slack api token. Keep this secure.
- slackChannel

  - send to this slack channel (include # in front)
- slackText

  - the body of your message. Use your usual slack formatting chars.

Text substitutions
------------------
For both slackChannel and slackText you can use substitution tokens, aka string
interpolation. This substitutes anything between curly braces with the context
value for that key. For example, if your context looked like this:

.. code-block:: yaml

  arbitraryValue: pypyrchannel
  arbitraryText: down the
  moreArbText: wild
  slackChannel: "#{arbitraryValue}"
  slackText: "piping {arbitraryText} valleys {moreArbText}"

This will result in sending a message to *#pypyrchannel* with text:

*piping down the values wild*

Escape literal curly braces with doubles: {{ for {, }} for }

See a worked example `for substitions here
<https://github.com/pypyr/pypyr-example/tree/master/pipelines/substitutions.yaml>`__.

Sample pipeline
---------------
Here is some sample yaml of what a pipeline using the pypyr-slack plug-in
could look like:

.. code-block:: yaml

  steps:
    - name: pypyrslack.steps.echo
      in:
        echoMe: "just an arb step that may or may not fail."
    - name: pypyrslack.steps.send
      in:
        slackToken: supersecurevaluegoeshere
        slackChannel: "#channelnamehere"
        slackText: "pypyr is busy doing things :construction:"

  # The slackToken and slackChannel have already been set in steps
  # on_success and on_failure are just changing the text for the message.
  on_success:
    - name: pypyrslack.steps.send
      in:
        slackText: "that went well! :hotdog:"

  on_failure:
    - name: pypyrslack.steps.send
      in:
        slackText: "whoops! :rage1:"

If you saved this yaml as ``./pipelines/hoping-for-a-hotdog.yaml``, you can run

.. code-block:: bash

  ./pypyr hoping-for-a-hotdog --log 20


See a worked example for `pypyr slack here
<https://github.com/pypyr/pypyr-example/tree/master/pipelines/slack.yaml>`__.

******************
aws authentication
******************
Configuring credentials
=======================
pypyr-aws pretty much just uses the underlying boto3 authentication mechanisms.
More info here: http://boto3.readthedocs.io/en/latest/guide/configuration.html

This means any of the following will work:

- In the pypyr context

  .. code-block:: python

    context['awsClientIn']['clientArgs'] = {
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        aws_session_token=SESSION_TOKEN,
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

**********
Contribute
**********
Bugs
====
Well, you know. No one's perfect. Feel free to `create an issue
<https://github.com/pypyr/pypyr-aws/issues/new>`_.

Contribute to the pypyr project
===============================
The usual jazz - create an issue, fork, code, test, PR. It might be an idea to
discuss your idea via the Issues list first before you go off and write a
huge amount of code - you never know, something might already be in the works,
or maybe it's not quite right for this plug-in (you're still welcome to fork
and go wild regardless, of course, it just mightn't get merged back in here).

Get in touch anyway, would love to hear from you at
https://www.345.systems/contact.

.. |build-status| image:: https://api.shippable.com/projects/58efdfe130eb380700e559a4/badge?branch=master
                    :alt: build status
                    :target: https://app.shippable.com/github/pypyr/pypyr-aws

.. |coverage| image:: https://api.shippable.com/projects/58efdfe130eb380700e559a4/coverageBadge?branch=master
                :alt: coverage status
                :target: https://app.shippable.com/github/pypyr/pypyr-aws

.. |pypi| image:: https://badge.fury.io/py/pypyr-aws.svg
                :alt: pypi version
                :target: https://pypi.python.org/pypi/pypyr-aws/
                :align: bottom
