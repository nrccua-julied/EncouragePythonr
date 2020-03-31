import requests
import json
import os
import configparser
from loguru import logger
from notifiers import get_notifier
from datetime import datetime

# retrieve environment label
ENVNAME = os.getenv('ENV', 'stage')
USRTYPE = os.getenv('USR', 'stage')

# instantiate ConfigParser
config = configparser.ConfigParser()
config.sections()
config.read('envconfig.ini')

# assign environment and user variables
environ = config[ENVNAME]['xApiKey']
# orgUid = config[ENVNAME]['orgUid']
envUrl = config[ENVNAME]['baseUrl']
uname = config[USRTYPE]['uname']
uname2 = config[USRTYPE]['uname2']
pword = config[USRTYPE]['pword']
pword2 = config[USRTYPE]['pword2']
email = config[USRTYPE]['email']
pguser = config[USRTYPE]['dbuser']
pgpassword = config[USRTYPE]['dbpassword']
pghost =config[USRTYPE]['dbhost']
pgport =config[USRTYPE]['dbport']
pgdatabase =config[USRTYPE]['dbdatabase']

# name of test in progress
TESTNAME = ''

# checks/creates ResponseLogs directory
if not os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ResponseLogs')):
    os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ResponseLogs'))

# checks/creates RunLogs directory
if not os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'TestLogs')):
    os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'TestLogs'))

# instantiate slack
#slackNotifier = get_notifier('slack')


# slack messaging
#def slack(text):
#    slackNotifier.notify(message=text,
#                         webhook_url='https://hooks.slack.com/services/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')


# json pretty printing
def prettyPrint(obj):
    return json.dumps(obj, indent=4)


# writes json to file in log directory
def logBody(name, body):
    f = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ResponseLogs/log_' + name + '.txt'), 'w')
    f.write('log_' + name + '\n' + str(datetime.now()) + '\n\n' + prettyPrint(body))
    f.close()


# decorator that captures the test name
def logTestName(func):
    def inner1():
        global TESTNAME
        TESTNAME = func.__name__
        func()

    return inner1


# logs an error and sends a slack alert
def logAlert(name, text):
   if ENVNAME == 'DEFAULT':
        env = 'dev'
   else:
        env = ENVNAME
#    slack('[TEST FAIL] -- Encourage API -- ' + env + ' -- ' + name + ':\n• ' + text)
   logger.warning(name + ' -- ' + env + ': ' + text)


# authorization request
def authRequest():
    head = {
        'Content-Type': 'application/json',
        'x-api-key': environ
    }

    creds = {
        'userName': uname,
        'password': pword
    }

    response = requests.post(envUrl + '/login', headers=head, json=creds)
    for _ in range(3):
        if response.status_code != 504:
            break
        response = requests.post(envUrl + '/login', headers=head, json=creds)
    return response.json()['sessionToken']


# stores the session token
AUTHTOKEN = authRequest()


# builds the header (w/auth request)
def heads():
    return {
        'Content-Type': 'application/json',
        'x-api-key': environ,
        'Authorization': 'JWT ' + AUTHTOKEN
    }


# ResponseData class for auto-collecting the json
class ResponseData:
    def __init__(self, status, body):
        self.status = status
        self.body = body


# shortcut for GET
def get(url):
    response = requests.get(envUrl + url, headers=heads())
    for _ in range(3):
        if response.status_code != 504:
            break
        response = requests.get(envUrl + url, headers=heads())
    try:
        resp = ResponseData(response.status_code, response.json())
    except:
        resp = ResponseData(response.status_code, {})
    return resp


# shortcut for POST
def post(url, payload):
    response = requests.post(envUrl + url, headers=heads(), json=payload)
    for _ in range(3):
        if response.status_code != 504:
            break
        response = requests.post(envUrl + url, headers=heads(), json=payload)
    try:
        resp = ResponseData(response.status_code, response.json())
    except:
        resp = ResponseData(response.status_code, {})
    return resp


# shortcut for PUT
def put(url, payload):
    response = requests.put(envUrl + url, headers=heads(), json=payload)
    for _ in range(3):
        if response.status_code != 504:
            break
        response = requests.put(envUrl + url, headers=heads(), json=payload)
    try:
        resp = ResponseData(response.status_code, response.json())
    except:
        resp = ResponseData(response.status_code, {})
    return resp


# shortcut for DELETE
def delete(url, payload={}):
    response = requests.delete(envUrl + url, headers=heads())
    for _ in range(3):
        if response.status_code != 504:
            break
        reressponse = requests.delete(envUrl + url, headers=heads())
    try:
        resp = ResponseData(response.status_code, response.json())
    except:
        resp = ResponseData(response.status_code, {})
    return resp


# responseTest can be used to test attributes of the response multiple ways
# pass obj as int for status code, dict or list for response body
# if obj is int it will assert obj == key
# if obj is dict, if value is left empty it will check if key exists in obj
# if obj is dict, if value exists it will check for key:value pair in obj
# if obj is list, if value is left empty it will search through obj's list elements for existing key
# if obj is list, if value exists it will search through obj's list elements for key:value pair
def responseTest(obj, key, value=None):
    if type(obj) == int:
        assert obj == key, logAlert(TESTNAME, "Return code not what was expected: " + str(obj) + ' != ' + str(key))
    elif type(obj) == dict:
        if value == None:
            assert key in obj, logAlert(TESTNAME, "Key not found in object")
        else:
            assert obj[key] == value, logAlert(TESTNAME, "Value not found in obj[key]")
    elif type(obj) == list:
        if value == None:
            val = False
            for i in obj:
                if key in i:
                    val = True
                    break
            assert val, logAlert(TESTNAME, "Value is empty or Value not found in object")
        else:
            val = ''
            for i in obj:
                if key in i:
                    val = i[key]
                    break
            assert value == val, logAlert(TESTNAME, "Value not what was expected: " + str(value) + ' != ' + str(val))
    elif type(obj) == str:
        assert obj == key, logAlert(TESTNAME, "Strings do not match")
    elif type(obj) == type:
        assert obj == key, logAlert(TESTNAME, "Datatype mismatch")
    elif type(obj) == bool:
        assert obj == key, logAlert(TESTNAME, str(obj) + " when should be " + str(key))
    else:
        assert False, logAlert(TESTNAME, "No conditions met")


def responseNegTest(obj, key, value=None):
    if type(obj) == int:
        assert obj != key, logAlert(TESTNAME, "Return codes unexpectedly match: " + str(obj) + ' == ' + str(key))
    elif type(obj) == dict:
        if value == None:
            assert key not in obj, logAlert(TESTNAME, "Key was unexpectedly found")
        else:
            assert obj[key] != value, logAlert(TESTNAME, "Value was unexpectedly found in obj[key]")
    elif type(obj) == list:
        if value == None:
            val = False
            for i in obj:
                if key in i:
                    val = True
                    break
            assert not val, logAlert(TESTNAME, "Value is not empty or Value unexpectedly found in object")
        else:
            val = ''
            for i in obj:
                if key in i:
                    val = i[key]
                    break
            assert value != val, logAlert(TESTNAME, "Value match unexpectedly: " + str(value) + ' == ' + str(val))
    elif type(obj) == str:
        assert obj != key, logAlert(TESTNAME, "Strings unexpectedly match")
    elif type(obj) == type:
        assert obj != key, logAlert(TESTNAME, "Unexpected datatype match")
    elif type(obj) == bool:
        assert obj != key, logAlert(TESTNAME, str(obj) + " when shouldn't be " + str(key))
    else:
        assert False, logAlert(TESTNAME, "No conditions met")
