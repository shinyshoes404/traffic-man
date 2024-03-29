from setuptools import setup

with open("README.md", "r") as fh:
    readme_long_description = fh.read()

setup(
    name='traffic-man',
    version='1.1.1',
    description="traffic-man is a dockerized application that checks for bad traffic conditions between two points using Google's Distance Matrix API on set days and times and sends SMS notifications to users when traffic conditions exceed a configurable threshold using Twilio. Users authenticate and setup their profile via SMS. traffic-man uses Google's Places API to search for addresses and place ids based on user provided search terms.",
    long_description=readme_long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/shinyshoes404/traffic-man',
    author='shinyshoes',
    author_email='shinyshoes404@protonmail.com',
    license='MIT License',
    packages=['traffic_man', 'traffic_man.db', 'traffic_man.traffic_engine', 'traffic_man.google', 'traffic_man.twilio', 'traffic_man.sms_processor', 'traffic_man.api'],
    package_dir={'':'src'},
    entry_points = { 'console_scripts' : ['start-traffic-man=traffic_man.entrypoint:main']},
    
    install_requires=[
        'requests', 'sqlalchemy==1.4.41', 'pandas', 'redis', 'flask', 'flask_cors'
    ],

    extras_require={
        # To install requirements for dev work use 'pip install -e .[dev]'
        'dev': ['coverage', 'mock']
    },

    python_requires = '>=3.9',

    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',           
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10'
    ],
)
