#!/bin/bash
virtualenv --no-site-packages --distribute example
source example/bin/activate

pip install -r ../requirements.txt

echo ''
echo ''
echo 'Please run `source example/bin/activate` to activate the virtual environment for this example'
echo 'You may then run python run_example.py to run the example'