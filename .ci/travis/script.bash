#!/bin/bash

PYJUXA_ROOT="$(cd "$(dirname ${BASH_SOURCE[0]})" ; cd ../../ ; pwd -P )"
cd "${PYJUXA_ROOT}"

# any failure here should fail the whole test
set -e

# most of these should be baked into the docker image already
sudo pip install -r requirements.txt
#sudo pip install -r requirements-travis.txt
#sudo pip install -r requirements-optional.txt || echo "Some optional modules failed to install"


#python setup.py build_ext -i
PYJUXA_VERSION=$(python -c 'import pyjuxa;print(pyjuxa.__version__)')
# this runs in pytest in a fake, auto numbered, X Server
xvfb-run -a py.test -r sxX --junitxml=test_results_${PYJUXA_VERSION}.xml
#COVERALLS_REPO_TOKEN=${COVERALLS_TOKEN} coveralls
