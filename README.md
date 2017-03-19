# Wifi Probe Mapper

## What is this thing?
This is a tool for collecting and mapping SSIDs from wifi access point beacons and client probe requests. It was put together as a demo for high school students to show how leaving Wifi turned on on a device can leak information about where that device has been.

## How does it work?
There are two main parts to this tool; A Python backend server and a HTML page acting as the front end. The Python server uses Tornado to manage web socket connections and the Scapy framework to sniff for beacons and client probes. Coordinates for SSIDs caught in the beacons and probes are gotten using the Wigle (https://www.wigle.net) API. The front end web page connects back to the server using a web socket, and once it's connection it'll start getting information on captures SSIDs. The Google Maps JavaScript API is used to show the location of each SSID on a map.

Note: Wigle uses information from war drivers for locations of networks. There may or may not be a location available for a given SSID and the location may not be accurate. SSIDs which are not unique (i.e. "Starbucks Wifi", "Free Wifi", "Airport Wifi") may have several locations associated with them.

## Installation
### Requirements
A Python version > 3 is needed to run the backend server.
```
sudo apt-get install python3
```
Pip can take care of the required Python modules (Tornado and scapy-python3)
```
pip3 install -r requirments.txt 
```
### Configuration
Before launching the tool, items need to be set in the configuration file.
```
$cat config.js

var config = {
                "serverIp": "127.0.0.1",
                "serverPort": "8888",
                "defaultLat": "40.7128",
                "defaultLong": "74.0059",
                "defaultZoom": 8,
                "wigleAuthToken": "<WIGLE_API_TOKEN_IN_BASE64>",
                "googleMapsAPIKey": "<GOOGLE_MAPS_API_KEY>"
              }
```

1. By default the map will conter on New York. This can be changed by adjecting the "defaultLat" and "defaultLong" variables in the config.js file.

1. An API token must be provided for the Wigle API. This token is the base64 encoded combination of the Wigle API user and Key. The token can be gotten by signing up at [https://wigle.org/] and generating it in the 
[https://wigle.net/account] page.

1. An API key is needed for the Google maps API. This can be gotten from [https://developers.google.com/maps/documentation/javascript/get-api-key]

## Usage

```
$./WPMServer.py --help
usage: WPMServer.py [-h] [-i INTERFACE] [-w WRITE]

DESCRIPTION

optional arguments:
  -h, --help            show this help message and exit
  -i INTERFACE, --interface INTERFACE
                        interface to capture on
  -w WRITE, --write WRITE
                        Write data to file
```

Once the API keys have been added to the configuration file the backend server can be started. An interface must be passed in using the `-i` option. This interface should first be put into monitoring mode.
Put interface into monitoring mode.
```
$airmon-ng start <INTERFACE>
```

Start the server.
```
$./WPMServer.py -i <INTERFACE IN MONITORING MODE>
``` 

Once the server is running the index.html file can be opened with a browser. If any issues occur try restarting the backend server and refreshing the browser.



