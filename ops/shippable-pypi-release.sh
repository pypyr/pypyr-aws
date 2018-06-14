#!/usr/bin/env bash
# Runs on shippable. Releases to pypi.

# stop processing on any statement return != 0
set -e

# Use deploy switch on setup.py to install deploy deps.
pip install -q -e .[deploy]

# version.py will return "pypyr x.y.z python a.b.c" - get everything after the
# space for the bare version number.
NEW_VERSION=`python pypyraws/version.py`
echo "New version is: ${NEW_VERSION}"
TAG_NAME="v${NEW_VERSION}"

# all done, clean-up
pip uninstall -y pypyraws

# Build wheel in dist/
python setup.py bdist_wheel

# Deploy wheel
twine upload --username ${PYPI_USERNAME} --password ${PYPI_PASSWORD} dist/pypyraws-${NEW_VERSION}-py3-none-any.whl

echo "----------Done with twine upload-------------------------------------"

# smoke test
echo "----------Deploy to pypi complete. Testing in new virtual env.-------"

pip install pypyraws -q
# pypyr --v will return "pypyr x.y.z" - get everything after the space for the
# bare version number.
TEST_DEPLOY_VERSION=`python pypyraws/version.py`
if [ "${TEST_DEPLOY_VERSION}" =  "${NEW_VERSION}" ]; then
  echo "Deployed version is ${TEST_DEPLOY_VERSION}. Smoke test passed OK."
else
  echo "Something went wrong. Deployed version is ${TEST_DEPLOY_VERSION}, but expected ${NEW_VERSION}" >&2
  exit 1
fi;
