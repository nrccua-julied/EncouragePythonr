import ecqa_helpers
from ecqa_helpers import get, post, put, delete, responseTest, responseNegTest, logBody, logTestName
from loguru import logger
import psycopg2
import requests
import datetime

UID = '39217eab-2478-435f-86eb-e9052cc7bdb4'
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


##########Creates a user##########################
@logTestName
def test_post_signup():
    logger.info("POST /users - Positive Test")
    #    responseTest(type(TOKEN), str)

    head = {
        'Content-Type': 'application/json',
        'x-api-key': ecqa_helpers.environ,
        'Authorization': 'JWT ' + TOKEN
    }

    creds = {
        'firstName': "PythonFirstName",
        'lastName': "PythonLastName",
        'userName': newuname,
        'password': ecqa_helpers.pword2,
        "status": "Active",
        'email': newuemailname
    }

    response = requests.post(ecqa_helpers.envUrl +
                             '/users', headers=head, json=creds)
    for _ in range(3):
        if response.status_code != 504:
            break
        response = requests.post(
            ecqa_helpers.envUrl + '/users', headers=head, json=creds)
    print("Create New User: Expected Response Code is 201, Actual Response Code is", response.status_code)
    print("New Username: ", newuname)
    print("New User Email: ", newuemailname)
    assert response.status_code == 201


########## Verification Code found in the DB query####################
@logTestName
def test_db():
    logger.info("Querying the DB")
    global userid
    global verificationcode
    global emailaddress

    try:
        connection = psycopg2.connect(user=ecqa_helpers.pguser,
                                      password=ecqa_helpers.pgpassword,
                                      host=ecqa_helpers.pghost,
                                      port=ecqa_helpers.pgport,
                                      database=ecqa_helpers.pgdatabase)

        cursor = connection.cursor()
        # Print PostgreSQL Connection properties
        print(connection.get_dsn_parameters(), "\n")

        # Print PostgreSQL version
        cursor.execute("SELECT version();")
        record = cursor.fetchone()
        print("You are connected to - ", record, "\n")

        cursor.execute("""SELECT * FROM public."User" where "UserName" = %s;""", [newuname, ])
        query_results = cursor.fetchall()
        print(query_results)
        for x in query_results:
            print(x[0])
            print(x[2])
            print(x[7])
            userid = (x[0])
            verificationcode = (x[2])
            emailaddress = (x[7])

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)

    finally:
        # closing database connection.
        if (connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")


@logTestName
def test_get_users():
    logger.info("GET /users - Positive Test")

    response = get('/users')

    responseTest(response.status, 200)

    print (response.body)



@logTestName
def test_get_users_uid():
    logger.info("GET /users/{ userUid } - Positive Test")

    response = get('/users/' + userid)

    responseTest(response.status, 200)



@logTestName
def test_put_users_uid():
    logger.info("PUT /users/{ userUid } - Positive Test")

    payload = {
    "firstName": "PythonFirstNameUpdated",
    "lastName": "PythonLastName",
    "userName": newuname,
    "status": "Active",
    "email": newuemailname
}

    response = put('/users/' + userid, payload)

    responseTest(response.status, 200)
    responseTest(response.body['uid'], userid)
    responseTest(response.body['status'], 'Active')


@logTestName
def test_verify_fname_db():
    logger.info("Verifying Updated FirstName")

    try:
        connection = psycopg2.connect(user=ecqa_helpers.pguser,
                                      password=ecqa_helpers.pgpassword,
                                      host=ecqa_helpers.pghost,
                                      port=ecqa_helpers.pgport,
                                      database=ecqa_helpers.pgdatabase)

        cursor = connection.cursor()
        # Print PostgreSQL Connection properties
        print(connection.get_dsn_parameters(), "\n")

        # Print PostgreSQL version
        cursor.execute("SELECT version();")
        record = cursor.fetchone()
        print("You are connected to - ", record, "\n")

        cursor.execute("""SELECT * FROM public."User" where "UserName" = %s;""", [newuname, ])
        query_results = cursor.fetchall()
        print(query_results)
        for x in query_results:
            print(x[4])

        responseTest ((x[4]), "PythonFirstNameUpdated")

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)

    finally:
        # closing database connection.
        if (connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")


@logTestName
def test_post_users_uid_impersonate():
    logger.info("POST /users/{ userUid }/impersonate - Positive Test")

    response = post('/users/' + userid + '/impersonate', {})

    responseTest(response.status, 200)
    responseTest(response.body, 'sessionToken')

    ecqa_helpers.AUTHTOKEN = response.body['sessionToken']


@logTestName
def test_delete_users_uid_impersonate():
    logger.info("DELETE /users/{ userUid }/impersonate - Positive Test")

    response = delete('/users/' + userid + '/impersonate')

    responseTest(response.status, 200)
    responseTest(response.body, 'sessionToken')

##########Login to get token########################
@logTestName
def test_post_login2():
    logger.info("POST /login2 - Positive Test")

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

    ecqa_helpers.AUTHTOKEN = response.json()['sessionToken']

@logTestName
def test_delete_users_uid():
    logger.info("DELETE /users/{ userUid } - Positive Test")
    print(userid)
    response = delete('/users/' + userid)
    print (response.body)
    responseTest(response.body['message'], 'Success')
    responseTest(response.status, 200)