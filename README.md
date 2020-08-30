# pypyr aws plug-in

![pypyr task runner for automation pipelines](https://pypyr.io/images/2x1/pypyr-taskrunner-yaml-pipeline-automation-1200x600.1bd2401e4f8071d85bcb1301128e4717f0f54a278e91c9c350051191de9d22c0.png)

Run anything on aws. No really, anything! If the aws api supports it, the pypyr 
aws plug-in supports it.

It's a pretty easy way of invoking the aws api as a step in a series of steps 
without having to write code. 

[pypyr](https://pypyr.io/) is a cli & api to run pipelines 
defined in yaml.

All documentation for the pypyr aws plugin is here: 
https://pypyr.io/docs/plugins/aws/

Why use this when you could just use the aws-cli instead? The aws cli is all 
kinds of awesome, but I find more often than not it's not just one or two aws 
*ad hoc* cli or aws api methods you have to execute, but especially when 
automating and scripting you actually need to run a sequence of commands, where 
the output of a previous command influences what you pass to the next command.

Sure, you can bash it up, and I do that too, but running it as a pipeline via 
pypyr has actually made my life quite a bit easier because of not having to 
deal with conditionals, error traps and input validation.

[![build status](https://github.com/pypyr/pypyr-aws/workflows/lint-test-build/badge.svg)](https://github.com/pypyr/pypyr-aws/actions)
[![coverage status](https://codecov.io/gh/pypyr/pypyr-aws/branch/master/graph/badge.svg)](https://codecov.io/gh/pypyr/pypyr-aws)[![pypi version](https://badge.fury.io/py/pypyraws.svg)](https://pypi.python.org/pypi/pypyraws/)
[![apache 2.0 license](https://img.shields.io/github/license/pypyr/pypyr-aws)](https://opensource.org/licenses/Apache-2.0)


## installation
```bash
$ pip install --upgrade pypyraws
```

`pypyraws` depends on the pypyr core. The above `pip` will install it
for you if you don't have it already.

## usage
Here is some sample yaml of what a pipeline using the pypyr-aws plug-in to 
upload a file to s3 would look like:

```yaml
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
```

If you saved this yaml as `./pipelines/go-go-s3.yaml`, you can run it like this 
to upload `arb.txt` to your specified bucket:

```bash
$ pypyr go-go-s3 bucket=myuniquebucketname
```

## custom waiters
But wait, there's more! You can make a custom waiter for any aws client 
operation and wait for a specified field in the response to become the value 
you want it to be.

This is especially handy for things like Beanstalk, because Elastic
Beanstalk does not have Waiters for environment creation.

The input context looks like this:

```yaml
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
```

## Help!
Don't Panic! Check the 
[pypyraws technical docs](https://pypyr.io/docs/plugins/aws/) to begin. 
For help, community & talk, check 
[pypyr twitter](https://twitter.com/pypyrpipes/), or join the chat on 
[pypyr discord](https://discordapp.com/invite/8353JkB)!

## contribute
### developers
For information on how to help with pypyr, run tests and coverage,
please do check out the [pypyr contribution
guide](https://pypyr.io/docs/contributing/).

### bugs
Well, you know. No one's perfect. Feel free to [create an
issue](https://github.com/pypyr/pypyr-aws/issues/new).

## License
pypyr is free & open-source software distributed under the Apache 2.0 License.

Please see [LICENSE](LICENSE) in the root of the repo.

Copyright 2017 the pypyr contributors.
