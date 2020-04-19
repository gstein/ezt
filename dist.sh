#!/bin/bash

python2 setup.py sdist --formats=gztar

# Sometimes, on Mac OS, we get a "._setup.py" file in the tar, which holds
# resource fork data. We don't want to see such files in our tarfile.
tar tzf dist/ezt-*.tar.gz | fgrep -q ._ && echo "BAD FILE IN DISTRIBUTION"

# DOCCO
#
# Ensure that ~/.pypirc contains [pypi] and [testpypi] locations.
# The latter should have the correct repository: value. Each
# section should have username=__token__ with the associated API
# token that was generated for that service.
#
# Ensure that twine installed:
# $ pip3 install twine
#
# Test upload:
# $ python3 -m twine upload --repository testpypi dist/ezt-1.1.tar.gz
#
# Test that it worked correctly:
# $ mkdir piptest
# $ pip3 install --target piptest --index-url https://test.pypi.org/simple/ --no-deps ezt
# $ cd piptest
# $ python2 -c 'import ezt;print(ezt.__version__)'
# $ python3 -c 'import ezt;print(ezt.__version__)'
#
# Final upload:
# $ python3 -m twine upload dist/ezt-1.1.tar.gz 
#
