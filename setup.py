from setuptools import setup

with open("README.md", "r") as fh:
    readme_long_description = fh.read()

setup(
    name='traffic-man',
    version='1.0.0',
    description="An application that checks for bad traffic between two points using the Google Maps API at set times and sends SMS notifications using Twilio.",
    long_description=readme_long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/shinyshoes404/traffic-man',
    author='shinyshoes',
    author_email='shinyshoes404@protonmail.com',
    license='MIT License',
    packages=['traffic_man', 'traffic_man.db', 'traffic_man.traffic_engine', 'traffic_man.google', 'traffic_man.twilio', 'traffic_man.sms_processor'],
    package_dir={'':'src'},
    entry_points = { 'console_scripts' : ['start-traffic-man=traffic_man.entrypoint:main']},
    
    install_requires=[
        'requests', 'sqlalchemy', 'pandas', 'redis', 'flask'
    ],

    extras_require={
        # To install requirements for dev work use 'pip install -e .[dev]'
        'dev': ['coverage', 'mock']
    },

    python_requires = '>=3.9.*',

    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows :: Windows 10',
        'Operating System :: POSIX :: Linux',           
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10'
    ],
)
