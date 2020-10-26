import unittest
import requests
import joblib
import hassbrainapi.algorithm as api
from hassbrainapi.settings import *

class TestFile(object):
    def __init__(self, num):
        self._num = num

class AlgorithmTest(unittest.TestCase):

    def setUp(self):
        pass


    def test_download_model(self):
        link = "134.2.56.118:8000/media/HMM"
        file = api.download_model(link)
        #model = joblib.load(file)

    def test_get_full_ip(self):
        response = api.get(
            "http://134.2.56.118:8000/api/v1/algorithms/1/",
            USER,
            PASSWORD
        )
        print(response)
        print(response.text)


    def test_get(self):
        response = api.get(SERVER_ADDRESS,USER,PASSWORD)
        self.assertIsNotNone(response)
        #print(response)
        id = response[0]['id']
        response = api.get_by_id(SERVER_ADDRESS, USER, PASSWORD, id)
        #print(response)
        self.assertIsNotNone(response)
        response = api.get_by_address(SERVER_ADDRESS + "/api/v1/activities/%s/"%(id),
                                  USER, PASSWORD)
        #print(response)
        self.assertIsNotNone(response)

    def test_create(self):
        # CREATE
        name = "test_activity"
        api.create(
            url=SERVER_ADDRESS,
            user_name=USER,
            password=PASSWORD,
            name=name
        )
        response = requests.get(
            SERVER_ADDRESS + "/api/v1/activities/",
            auth=(USER, PASSWORD)
        ).json()


    def test_put(self):
        # PUT
        obs_pred = 'asdf'
        resp = api.put(
            url=SERVER_ADDRESS,
            user_name=USER,
            password=PASSWORD,
            id=2,
            obs_pred=obs_pred
        )
        print(resp)
        print(resp.reason)
        #response = requests.put(
        #    SERVER_ADDRESS + "/api/v1/algorithms/",
        #    auth=(USER, PASSWORD)
        #).json()
        #print(response)



    def test_put_file(self):
        # PUT
        obj = TestFile(2)
        joblib.dump(obj, "asdf.joblib")

        #files = {'file': open('asdf.joblib', 'rb')}
        #files = {'model': open('asdf.joblib', 'rb'), 'description' : 'asdf'}
        #res = api.put(
        #    url=SERVER_ADDRESS,
        #    user_name=USER,
        #    password=PASSWORD,
        #    id=1,
        #    model_file=files
        #)
        #print(res.reason)
        res = api.send_request(
            url=SERVER_ADDRESS,
            user_name=USER,
            password=PASSWORD,
            id=2,
            model_file='asdffiles'
        )
        print(res.reason)
        print(res.text)
    def test_get_csrf_cookie6(self):
        import logging
        import requests
        import re
        url = SERVER_ADDRESS

        s = requests.session()
        r = s.get(url, verify=False)
        print(s.cookies)
        print(r.headers)
        matchme = 'meta content =”(.*)” name =”csrf - token” / '
        csrf = re.search(matchme, str(r.text))
        print(csrf)
        s.close()

    def test_get_csrf_cooki4(self):
        auth = (USER, PASSWORD)
        login_url = SERVER_ADDRESS + "/api/v1/auth/login/"


        client = requests.session()
        logindata = {
                     'user[email]': 'your@loginemail.com',
                     'user[password]': 'yourpassword',
                     'user[remember_me]': '0'}
        login = client.post(login_url, data=logindata,
                             auth=auth)  # this should log in in, i don't have an account there to test.
        client.get(SERVER_ADDRESS, auth=auth)  # sets cookie
        print(client.auth)
        print(client.cookies)
        #data = dict('person_first_name' = 'Morgan')
        #url = 'https://app.greenhouse.io/people/new?hiring_plan_id=24047'
        #r = session.post(url,
        #                 data=data)  # unless you need to set a user agent or referrer address you may not need the header to be added.

    def test_get_csrf_cookie2(self):
        import sys
        import requests


        client = requests.session()
        auth = (USER, PASSWORD)
        # Retrieve the CSRF token first
        client.get(SERVER_ADDRESS + "/api/v1/locations", auth=auth)  # sets cookie
        print(client.cookies)
        if 'csrftoken' in client.cookies:
            # Django 1.6 and up
            csrftoken = client.cookies['csrftoken']
        else:
            # older versions
            csrftoken = client.cookies['csrf']
        #print(csrftoken)
        #login_data = dict(username=EMAIL, password=PASSWORD, csrfmiddlewaretoken=csrftoken, next='/')
        #r = client.post(URL, data=login_data, headers=dict(Referer=URL))


    def test_get_csrf_cookie3(self):
        import sys

        import django
        from django.middleware.csrf import CsrfViewMiddleware, get_token
        from django.test import Client

        django.setup()
        csrf_client = Client(enforce_csrf_checks=True)


        # Retrieve the CSRF token first
        csrf_client.get(SERVER_ADDRESS)  # sets cookie
        csrftoken = csrf_client.cookies['csrftoken']

    def test_get_csrf_cookie(self):
        import requests

        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
        }
        user_name = USER
        password = PASSWORD
        auth=(user_name, password)
        response = requests.get(SERVER_ADDRESS, headers=headers, auth=auth, verify=False)
        #print(response.text)
        #headers['cookie'] = '; '.join([x.name + '=' + x.value for x in response.cookies])
        #headers['content-type'] = 'application/x-www-form-urlencoded'
        #print(headers['cookie'])
        #payload = {
        #    'username': 'user_name',
        #    'password': 'randompass123'
        #}
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, 'lxml')

        #csrf_token = soup.select_one('meta[name="csrf-token"]')['content']
        #print(csrf_token)
        #response = requests.post(SERVER_ADDRESS, data=payload, headers=headers, verify=False)
        #headers['cookie'] = '; '.join([x.name + '=' + x.value for x in response.cookies])

    def test_get_csrf_cookie8(self):
        sess = requests.Session()
        r = sess.get(SERVER_ADDRESS+"/api/v1/", auth=(USER, PASSWORD))
        print(r.cookies)
        print(r.headers)
        print(r.request)
        print(r.elapsed)
        print(r.content)
        print(r.links)
        print(r.apparent_encoding)
        print(r.url)
        print(r.content)
        #my_csrf_token = r.cookies['csrftoken']

    def test_delete(self):
        ide=3
        # DELETE
        api.delete(
            url=SERVER_ADDRESS,
            user_name=USER,
            password=PASSWORD,
            pk=ide,
        )
        response = requests.get(
            SERVER_ADDRESS + "/api/v1/activities/%s/"%(ide),
            auth=(USER, PASSWORD)
        ).json()
        self.assertEqual(response['detail'], "Not found.")

    def tearDown(self):
        pass

if __name__ == "__main__":
    unittest.main()