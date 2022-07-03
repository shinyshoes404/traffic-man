# traffic-man

traffic man is an application that checks for bad traffic conditions between two points using the Google Maps API on set days and times and sends SMS notifications when traffic conditions exceed a configurable threshold using Twilio.

## How it works

__Process diagram__  

 <img src="./docs/images/process_diagram.jpg" width="800px"/>  
 &nbsp;

 __Data model__  
 <img src="./docs/images/data_model.jpg" width="800px"/>  
 &nbsp;


## Development and testing

### Setting up your dev environment

#### Envirionment variables
 - In the root of this project create a .env file by copying and renaming the provided .env-template file. 
 - Edit your .env file changing out the example values for yours
 - Change the TRAFFIC_MAN_ENV variable to `dev`, so that the log and db file will be stored in the project directory
 - Before running traffic man, you need to export all of the variables you just set into your environment
     - If you are using using bash (or gitbash) `export $(grep -v '^#' .env | xargs)`  
__Note:__ Never put your real API keys and phone numbers in the .env-template file. The .env file is included in our .gitignore file, and will not be committed to our git history. .env-template is part of the poject and will be commited to git history.

### Testing
 - Run the suite of unit tests and record test coverage for reporting with `coverage run --source=src -m unittest discover -v -s tests/unit`
 - Generate an html coverage report to see which modules and lines have test coverage using `coverage html`