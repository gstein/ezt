#!/bin/bash

python2 setup.py sdist --formats=gztar

# Sometimes, on Mac OS, we get a "._setup.py" file in the tar, which holds
# resource fork data. We don't want to see such files in our tarfile.
tar tzf dist/ezt-*.tar.gz | fgrep -q ._ && echo "BAD FILE IN DISTRIBUTION"
