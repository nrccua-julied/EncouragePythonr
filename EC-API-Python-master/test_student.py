import ecqa_helpers
from ecqa_helpers import get, post, put, delete, responseTest, responseNegTest, logBody, logTestName
from loguru import logger
import psycopg2
import requests
import datetime

student_key = None
TOKEN = ecqa_helpers.AUTHTOKEN
NEW_TOKEN = None
TS = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
newuname = "nrccuadl" + TS
newuemailname = "nrccuadl" + TS + "@nrccua.org"

# newuuid = None
##########Login to get token########################
@logTestName
def test_post_login():
    logger.info("POST /login - Positive Test")

    head = {
        'Content-Type': 'application/json',
        'x-api-key': ecqa_helpers.environ
    }

    creds = {
        'userName': ecqa_helpers.uname,
        'password': ecqa_helpers.pword
    }

    response = requests.post(ecqa_helpers.envUrl +
                             '/login', headers=head, json=creds)
    for _ in range(3):
        if response.status_code != 504:
            break
        response = requests.post(
            ecqa_helpers.envUrl + '/login', headers=head, json=creds)
    print("Login Test 1st Valid Account: Expected Response Code is 200, Actual Response Code is", response.status_code)
    responseTest(response.status_code, 200)
    responseTest(type(response.json()['sessionToken']), str)

    global TOKEN
    TOKEN = response.json()['sessionToken']



@logTestName
def test_get_students():
    logger.info("GET /students - Positive Test")

    response = get('/students')

    responseTest(response.status, 200)
    global student_key
    student_key = (response.body[0]['student_key'])
    print (response.body)

@logTestName
def test_get_students_key():
    logger.info("GET /students{student_key} - Positive Test")

    response = get('/students/'+str(student_key))

    responseTest(response.status, 200)

    print (response.body)

    @logTestName
    def test_get_students_key_include_appstatus_checklist_fafsa():
        logger.info("GET /students{student_key}include application_status,checklist,fafsa  - Positive Test")

        response = get('/students/' + str(student_key)+'?include=application_status,checklist,fafsa')

        responseTest(response.status, 200)

        print(response.body)