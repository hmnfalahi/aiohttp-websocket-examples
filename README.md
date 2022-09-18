# aiohttp websocket examples

## Getting started
#### Create a virtual environment and install dependencies:

- python3 -m venv env
- source env/bin/activate
- pip install -r requirements.txt


## Run the worker
- python worker.py

also, in the worker you can replace the other apps with the default app. 


## [WSCAT](https://www.npmjs.com/package/wscat)
##### wscat is a tool for connecting to and communicating with a WebSockets server.

after running the worker you can communicate with server using wscat by: 
##### $ wscat -c ws://0.0.0.0:8080
