from setuptools import setup, find_packages

setup(
    name='matches_update',
    version='0.1',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'requests',
        'google-api-python-client',
        'google-auth',
        'google-auth-oauthlib',
        'google-auth-httplib2',
    ],
    entry_points={
        'console_scripts': [
            'fetch_matches=scripts.run_fetch_and_store_matches:main',
            'update_calendar=scripts.run_update_calendar:main',
        ],
    },
)