import ecqa_helpers
from ecqa_helpers import get, post, put, delete, responseTest, responseNegTest, logBody, logTestName
from loguru import logger
import requests
import psycopg2
import datetime
TS = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
newuname = "nrccuadl" + TS
newuemailname = "nrccuadl" + TS + "@nrccua.org"

TOKEN = None


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



##########Activates the user based on the Verification Code found in the DB query####################
@logTestName
def test_post_activate():
    logger.info("POST /activate-user - Positive Test")
    global userid
    global verificationcode
    global emailaddress

    try:
        connection = psycopg2.connect(user = ecqa_helpers.pguser,
                                  password = ecqa_helpers.pgpassword,
                                  host = ecqa_helpers.pghost,
                                  port = ecqa_helpers.pgport,
                                  database = ecqa_helpers.pgdatabase)

        cursor = connection.cursor()
        # Print PostgreSQL Connection properties
        print ( connection.get_dsn_parameters(),"\n")

        # Print PostgreSQL version
        cursor.execute("SELECT version();")
        record = cursor.fetchone()
        print("You are connected to - ", record,"\n")

        cursor.execute("""SELECT * FROM public."User" where "UserName" = %s;""",[newuname,])
        query_results = cursor.fetchall()
        print(query_results)
        for x in query_results:
            print(x[0])
            print(x[2])
            print(x[7])
            userid = (x[0])
            verificationcode =(x[2])
            emailaddress = (x[7])

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)

    finally:
    #closing database connection.
        if (connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

    head = {
        'Content-Type': 'application/json',
        'x-api-key': ecqa_helpers.environ,
        'Authorization': 'JWT ' + TOKEN
    }

    creds = {
        'verificationCode': verificationcode ,
        'userName': newuname,
        'password': ecqa_helpers.pword2,
        'acceptedTerms': 'true'
    }

##########Post to Activate the User#########################
    response = requests.post(ecqa_helpers.envUrl +
                             '/activate-user', headers=head, json=creds)
    for _ in range(3):
        if response.status_code != 504:
            break
        response = requests.post(
            ecqa_helpers.envUrl + '/login', headers=head, json=creds)
    print("Login Test 1st Valid Account: Expected Response Code is 200, Actual Response Code is", response.status_code)
    responseTest(response.status_code, 200)




@logTestName
def test_get_refresh_token():
    logger.info("GET /refresh-token - Positive Test")

    responseTest(type(TOKEN),str)

    head = {
        'Content-Type': 'application/json',
        'x-api-key': ecqa_helpers.environ,
        'Authorization': 'JWT ' + TOKEN
    }

    response = requests.get(ecqa_helpers.envUrl + '/refresh-token', headers=head)
    print("Refresh Token Test: Expected Response Code is 200, Actual Response Code is", response.status_code)
    responseTest(response.status_code, 200)
    responseTest(type(response.json()['sessionToken']), str)
    responseNegTest(response.json()['sessionToken'], TOKEN)


@logTestName
def test_post_forgot_password():
    logger.info("POST /forgot-password - Positive Test")

    head = {
        'Content-Type': 'application/json',
        'x-api-key': ecqa_helpers.environ
    }

    creds = {
        'credential': newuemailname
    }

    response = requests.post(ecqa_helpers.envUrl +
                             '/forgot-password', headers=head, json=creds)
    for _ in range(3):
        if response.status_code != 504:
            break
        response = requests.post(
            ecqa_helpers.envUrl + '/forgot-password', headers=head, json=creds)
    print("Forgot Password Test: Expected Response Code is 200, Actual Response Code is", response.status_code)
    responseTest(response.status_code, 200)

@logTestName
def test_get_module_access_yes_access():
    logger.info("GET /authorize-module - No Access to ReadUsers Module Test")

    responseTest(type(TOKEN),str)

    head = {
        'Content-Type': 'application/json',
        'x-api-key': ecqa_helpers.environ,
        'Authorization': 'JWT ' + TOKEN
    }

    response = requests.get(ecqa_helpers.envUrl + '/authorize-module/encourage.users.readlist', headers=head)
    print("Read User Module No Access Test: Expected Response Code is 200, Actual Response Code is", response.status_code)
    responseTest(response.status_code, 200)


@logTestName
def test_post_validate_email():
    logger.info("POST /validate-email - Positive Test (Exists)")

    payload = {'email': newuemailname}

    response = post('/validate-email', payload)

    responseTest(response.status, 200)
    responseTest(response.body['isEmailUnique'], False)

    logger.info("POST /validate-email - Positive Test (Does Not Exist)")

    payload = {'email': 'nrccuadl.bademailaddress@nrccua.org'}

    response = post('/validate-email', payload)

    responseTest(response.status, 200)
    responseTest(response.body['isEmailUnique'], True)


@logTestName
def test_post_validate_username():
    logger.info("POST /validate-username - Positive Test (Exists)")

    payload = {'userName': newuname}

    response = post('/validate-username', payload)

    responseTest(response.status, 200)
    responseTest(response.body['isUserNameUnique'], False)
    responseTest(response.body['isUserNameValid'], True)

    logger.info("POST /validate-username - Positive Test (Does Not Exist)")

    payload = {'userName': 'qa_auto_target_bad'}

    response = post('/validate-username', payload)

    responseTest(response.status, 200)
    responseTest(response.body['isUserNameUnique'], True)
    responseTest(response.body['isUserNameValid'], True)

    logger.info("POST /validate-username - Positive Test (Invalid)")

    payload = {'userName': 'qa_auto_target_!!!'}

    response = post('/validate-username', payload)

    responseTest(response.status, 200)
    responseTest(response.body['isUserNameUnique'], True)
    responseTest(response.body['isUserNameValid'], False)

@logTestName
def test_post_reset_password1():
    logger.info("POST /reset-password - Positive Test (Exists)")

    payload = {
        "uid": userid,
        "email": emailaddress,
        "newPassword": "password1",
        "verificationCode": verificationcode
        }

    response = post('/reset-password', payload)

    responseTest(response.status, 200)
    responseTest(response.body['message'], "Success")

@logTestName
def test_post_reset_password2():
        logger.info("POST /reset-password - Positive Test (Exists)")

        payload = {
         "newPassword": "password2",
        "verificationCode": verificationcode
        }

        response = post('/reset-password', payload)

        responseTest(response.status, 200)
        responseTest(response.body['message'], "Success")

@logTestName
def test_post_reset_password3():
        logger.info("POST /reset-password - Positive Test (Exists)")

        payload = {
            "uid": userid,
            "newPassword": "password3"
        }

        response = post('/reset-password', payload)

        responseTest(response.status, 200)
        responseTest(response.body['message'], "Success")

##########Login to get token########################
@logTestName
def test_post_login2():
            logger.info("POST /login - Positive Test")

            head = {
                'Content-Type': 'application/json',
                'x-api-key': ecqa_helpers.environ
            }

            creds = {
                'userName': emailaddress,
                'password': "password3"
            }

            response = requests.post(ecqa_helpers.envUrl +
                                     '/login', headers=head, json=creds)
            for _ in range(3):
                if response.status_code != 504:
                    break
                response = requests.post(
                    ecqa_helpers.envUrl + '/login', headers=head, json=creds)
            print("Login Test 1st Valid Account: Expected Response Code is 200, Actual Response Code is",
                  response.status_code)
            responseTest(response.status_code, 200)
            responseTest(type(response.json()['sessionToken']), str)

            global TOKEN
            TOKEN = response.json()['sessionToken']


@logTestName
def test_post_reset_password4():
        logger.info("POST /reset-password - Positive Test (Exists)")

        head = {
            'Content-Type': 'application/json',
            'x-api-key': ecqa_helpers.environ,
            'Authorization': 'JWT ' + TOKEN
        }

        creds = {
            "newPassword": "password4"
        }

        response = requests.post(ecqa_helpers.envUrl +'/reset-password', headers=head, json=creds)

        responseTest(response.status_code, 200)
        #responseTest(response.body['message'], "Success")



