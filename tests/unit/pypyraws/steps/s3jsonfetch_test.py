"""s3jsonfetch.py unit tests."""
import pypyraws.steps.s3jsonfetch
import pytest


def test_bucket_mandatory():
    """No 'bucket'  in context should throw assert error."""
    with pytest.raises(AssertionError):
        context = {'blah': 'blah blah'}
        context = pypyraws.steps.s3jsonfetch.context_validate(context)


def test_bucket_has_value():
    """Key 'bucket'  in context should throw assert error if None."""
    with pytest.raises(AssertionError):
        context = {'s3bucket': None}
        context = pypyraws.steps.s3jsonfetch.context_validate(context)


def test_key_mandatory():
    """No 'key'  in context should throw assert error."""
    with pytest.raises(AssertionError):
        context = {'s3bucket': 'blah blah'}
        context = pypyraws.steps.s3jsonfetch.run_step(context)


def test_key_has_value():
    """Key 's3key' in context should throw assert error if None."""
    with pytest.raises(AssertionError):
        context = {'s3bucket': 'blah blah', 's3key': None}
        context = pypyraws.steps.s3jsonfetch.context_validate(context)


def test_validate_pass():
    """All context values provided pass."""
    context = {'s3bucket': 'bucket value here', 's3key': 'key value here'}
    context = pypyraws.steps.s3jsonfetch.context_validate(context)
