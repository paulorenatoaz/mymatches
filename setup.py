from setuptools import setup, find_packages

setup(
    name='mymatches',
    version='0.1.0',
    description='Fetch football match data and update Google Calendar',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Paulo Renato Azevedo',
    author_email='paulorenatoaz@dcc.ufrj.br',
    url='https://github.com/paulorenatoaz/mymatches',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'requests',
        'google-auth',
        'google-auth-oauthlib',
        'google-auth-httplib2',
        'google-api-python-client',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
