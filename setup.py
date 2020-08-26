#!/usr/bin/env python

from setuptools import setup, find_packages

from gullveig import GULLVEIG_VERSION

with open('README.md') as f:
    readme = f.read()

setup(
    name='gullveig',
    version=GULLVEIG_VERSION,
    description='Distributed systems and service monitoring',
    long_description=readme,
    long_description_content_type='text/markdown',
    author='Matiss Treinis',
    author_email='matiss@hub256.com',
    url='https://github.com/Addvilz/gullveig',
    download_url='https://github.com/Addvilz/gullveig',
    license='Apache 2.0',
    platforms='UNIX',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'psutil>=5.6.7',
        'cryptography>=3.0',
        'aiohttp>=3.6.2',
        'aiosqlite>=0.14.0',
        'aiosmtplib>=1.1.2',
        'pyjwt>=1.7.1',
        'pyyaml>=5.1.1'
    ],
    entry_points={
        'console_scripts': [
            'gullveig-agent = gullveig.agent.agent:main',
            'gullveig-util = gullveig.util.util:main',
            'gullveig-server = gullveig.server.server:main',
            'gullveig-web = gullveig.web.web:main',
        ]
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: System :: Monitoring',
        'Topic :: System :: Networking :: Monitoring'
    ],
)
