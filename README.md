# ChatProtocol

This protocol can be used for multiple users to engage in an online chat through a command line interface.

## Get application running
Follow these instructions to get the server and client to run on your computer

### Assumptions:
* You have python 3.5 installed on your computer. If you have another version of python3 I recommend using [pyenv](https://realpython.com/intro-to-pyenv/) library to manage multiple versions of python3.
* You have virtualenv installed on your computer

### Steps to start the Chat Protocol Server:
1. In the command line create a virtual environment with python 3.5
2. Start virtualenv with Python 3.5 and run ```python server/main.py```

### Steps to start the Chat Protocol Client:
1. In the command line, in a new tab or window, start a virtual environment with python 3.5
2. Run ```python client/main.py```
3. Follow the instructions you see in the command line to use the client and interact with the server.

## Any analysis about how robust your assignment is
I do believe that this application will perform well under fuzzing.
### Implementation
On the Client side, the user input is always checked, and if client receives user input that it does not expect then a message will be returned to user.

on the server side, the client command send to the server always checks the state of the protocol before performing any function. If the state is not correct for the command, or the command does not exist a '500 bad command' error is returned. A test file was created to automate this process and continue to test as implementing protocol.

### Testing
 three actions were taken to test the protocol against fuzzing.
1. Attempt to input wrong commands into the client User Interface. If a command was unexpected than an error message would show for the user.
2. Attempt to input wrong commands that do not exist in direct contact with the client, and it will always return '500 bad command' error response.
3. Attempt to put in correct commands out of order. This will also resulted consistently with a '500 bad command' error response.

## Extra Credit was not implemented
