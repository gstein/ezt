#!/bin/bash

python setup.py sdist --formats=bztar,zip

# Sometimes, on Mac OS, we get a "._setup.py" file in the tar, which holds
# resource fork data. We don't want to see such files in our tarfile.
tar tjf dist/ezt-*.tar.bz2 | fgrep -q ._ && echo "BAD FILE IN DISTRIBUTION"
