import setuptools


setuptools.setup(
    name = 'thematic_sdk',
    version = '1.0.0',
    author='Thematic Ltd',
    author_email='contact@getthematic.com',
    url='http://getthematic.com/',
    description = '',
    packages=setuptools.find_packages(),
    package_data = {},
    install_requires=[
        "requests>=2.18",
        "requests[security]"
    ]
)
