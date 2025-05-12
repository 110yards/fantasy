# Install Python development tools
pip install autopep8==1.5.7
pip install flake8==3.9.2
pip install pytest==6.2.4
pip install pytest-mock==3.5.1

# Install project dependencies
$servicePath = $args[0]
pip install -r "$servicePath\requirements.txt"
pip install -e .
