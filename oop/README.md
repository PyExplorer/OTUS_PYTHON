Homework for opp

Taras Shevchenko

Scoring API
=======

INSTALLATION
----------

| Directory tree    |Contents |
| --- | --- |
|  oop/             |     source code, test         |
|     api.py        |     main module               |
|     scoring.py    |     scoring functions         |
|     test.py       |     test for the future       |
|  README           |     this file                 |

REQUIREMENTS
--------
The minimum requirement is python 2.7

No external packages are needed

QUICK START
-------
At first we should go to opp/

$cd opp

Then the script can be run with the one of the next lines:

$python api.py

$python api.py -p 8090

$python api.py -p 8090 -l 'api.log'

$python api.py -l 'api.log'

Then you can make a request like:

curl -X POST -H "Content-Type: application/json" -d '{"account": "horns&hoofs", "login": "h&f",
"method": "online_score", "token": "5bb12418e7d89b6d718a9e35af3",
"arguments": {"phone": "79179987611", "email": "wwrre@gmail.com", "first_name": "John",
"last_name": "Stamp", "birthday": "01.01.1990", "gender": 1}}' http://127.0.0.1:8080/method/ 

and get response like:

{"code": 200, "response": {"score": 5.0}}


DESCRIPTION
----
API for scoring model

If we do not specify options in command line - they are taken by default:

port = 8080
log path = stdout

to be continued...

TESTS
-----

Not yet