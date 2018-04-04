#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import api

try:
    import mock
except ImportError:
    from unittest import mock


def cases(data):
    def test_decorator(fn):
        def test_decorated(self, *args):
            for i in data:
                fn(self, i)
        return test_decorated
    return test_decorator


# @unittest.skip("Skip TestFields")
class TestFields(unittest.TestCase):

    @cases(['12/12/1954', ''])
    def test_bad_date_field(self, value):
        field = api.DateField()
        with self.assertRaises(Exception):
            field.clean(value)

    def test_date_field(self):
        field = api.DateField()
        self.assertEqual(
            field.clean('12.12.1954'), api.datetime(1954, 12, 12, 0, 0)
        )

    @cases([1, 's', [], ['1', 2, 3], ['1', '2', '3'], '', ()])
    def test_bad_client_ids_field(self, value):
        field = api.ClientIDsField()
        with self.assertRaises(Exception):
            field.clean(value)

    def test_client_ids_field(self):
        field = api.ClientIDsField()
        self.assertEqual(field.clean([1, 2, 3]), [1, 2, 3])
        self.assertEqual(field.clean([-1, 2, -3]), [-1, 2, -3])

    @cases(['88981231231', '1', '888981231211131'])
    def test_bad_phone_field(self, value):
        field = api.PhoneField(required=False, nullable=True)
        with self.assertRaises(Exception):
            field.clean(value)

    def test_phone_field(self):
        field = api.PhoneField(required=False, nullable=True)
        self.assertEqual(field.clean('78981231231'), '78981231231')
        self.assertEqual(field.clean(''), '')

    @cases(['edasdasasdasd', '1', 'fasdf.1131'])
    def test_bad_email_field(self, value):
        field = api.EmailField(required=False, nullable=True)
        with self.assertRaises(Exception):
            field.clean(value)

    def test_email_field(self):
        field = api.EmailField(required=False, nullable=True)
        self.assertEqual(field.clean('edasdas@asdasd'), 'edasdas@asdasd')
        self.assertEqual(field.clean(''), '')

    @cases(['12/12/1954', '12.12.1904'])
    def test_bad_birthday_field(self, value):
        field = api.BirthDayField(required=False, nullable=True)
        with self.assertRaises(Exception):
            field.clean(value)

    def test_birthday_field(self):
        field = api.BirthDayField(required=False, nullable=True)
        self.assertEqual(
            field.clean('12.12.1954'),
            api.datetime(1954, 12, 12, 0, 0)
        )
        self.assertEqual(field.clean(''), '')

    @cases([-1, 3, 2.5])
    def test_bad_gender_field(self, value):
        field = api.GenderField(required=False, nullable=True)
        with self.assertRaises(Exception):
            field.clean(value)

    @cases([(0, 0), (1, 1), (2, 2), ('', '')])
    def test_gender_field(self, value):
        field = api.GenderField(required=False, nullable=True)
        self.assertEqual(field.clean(value[0]), value[1])

    @cases(['edasdasasdasd', {}, '', ()])
    def test_bad_argument_field(self, value):
        field = api.ArgumentsField()
        with self.assertRaises(Exception):
            field.clean(value)

    def test_argument_field(self):
        field = api.ArgumentsField()
        self.assertEqual(field.clean({'a': 1}), {'a': 1})


# @unittest.skip("Skip ClientsInterestsRequest")
class TestClientsInterestsRequest(unittest.TestCase):
    @cases([
        {'date': ''},
        {'client_ids': [], 'date': ''},
        {'client_ids': ['1', 2, 3], 'date': ''},
        {'client_ids': '', 'date': ''},
    ])
    def test_bad_is_valid(self, value):
        request = api.ClientsInterestsRequest(value)
        self.assertEqual(request.is_valid(), False)

    @cases([
        {'client_ids': [1, 2, 3]},
        {'client_ids': [1, 2, 3], 'date': ''},
        {'client_ids': [1, 2, 3], 'date': '23.12.1987'},
    ])
    def test_is_valid(self, value):
        request = api.ClientsInterestsRequest(value)
        self.assertEqual(request.is_valid(), True)


# @unittest.skip("Skip TestOnlineScoreRequest")
class TestOnlineScoreRequest(unittest.TestCase):
    @cases([
        # test missing sets of fields
        {'first_name': '', 'last_name': '', 'email': '',
         'phone': '', 'birthday': '', 'gender': ''},
        {'first_name': '1', 'last_name': '', 'email': '1@1',
         'phone': '', 'birthday': '', 'gender': 1},
    ])
    def test_bad_is_valid(self, value):
        request = api.OnlineScoreRequest(value)
        self.assertEqual(request.is_valid(), False)

    @cases([
        # test sets of fields
        {'first_name': '1', 'last_name': '1', 'email': '',
         'phone': '', 'birthday': '', 'gender': ''},
        {'first_name': '', 'last_name': '', 'email': '1@1',
         'phone': '79898765432', 'birthday': '', 'gender': ''},
        {'first_name': '', 'last_name': '', 'email': '',
         'phone': '', 'birthday': '24.12.1987', 'gender': 1},
    ])
    def test_is_valid(self, value):
        request = api.OnlineScoreRequest(value)
        self.assertEqual(request.is_valid(), True)


# @unittest.skip("Skip TestMethodHandler")
class TestMethodHandler(unittest.TestCase):
        @cases([{
            "account": "horns&hoofs", "login": "h&f", "method": "online_score",
            "token": "", "arguments": {}
            },
            {
                "account": "horns&hoofs", "login": "h&f", "method":
                "online_score", "token": "sdd", "arguments": {}
            },
            {
                "account": "horns&hoofs", "login": "admin", "method":
                "online_score", "token": "", "arguments": {}
            },
        ])
        def test_bad_auth(self, request):
            self.assertEqual(
                api.method_handler(
                    {"body": request, "headers": ''},
                    '',
                    ''
                ), ('Forbidden', 403)
            )

        # Good response for clients_interests
        template_resp = {
            '1': ['books', 'pets'],
            '3': ['tv', 'travel'],
            '2': ['geek', 'books'],
            '4': ['cars', 'books']
        }

        @cases([{
            "account": "horns&hoofs", "login": "admin",
            "method": "clients_interests", "token": "",
            "arguments": {"client_ids": [1, 2, 3, 4], "date": "20.07.2017"}
         }])
        @mock.patch('api.check_auth')
        @mock.patch('api.ClientsInterestsRequest.get_response')
        def test_clients_interests(self, request, mocked_get_response,
                                   mocked_check_auth):
            mocked_get_response.return_value = (self.template_resp, 200)
            mocked_check_auth.return_value = True
            self.assertEqual(
                api.method_handler(
                    {"body": request, "headers": ''},
                    {},
                    {}
                ),
                (self.template_resp, 200)
            )

        # Bad response for clients_interests
        @cases([
            {"account": "horns&hoofs", "login": "admin",
             "method": "clients_interests", "token": "",
             "arguments": {"client_ids": [], "date": "20.07.2017"}
             }])
        @mock.patch('api.check_auth')
        def test_bad_clients_interests(self, request, mocked_check_auth):
            mocked_check_auth.return_value = True
            self.assertEqual(
                api.method_handler(
                    {"body": request, "headers": ''},
                    {},
                    {}
                ),
                ({'client_ids': 'This field must not be an empty.'}, 422)
            )

        # Good response for online_score
        @cases([{
            "account": "horns&hoofs", "login": "h&f",
            "method": "online_score", "token": '',
            "arguments": {
                "phone": "79175002040", "email": "ivan@com.com",
                "first_name": "Ivan",
                "last_name": "Ivanov",
                "birthday": "01.01.1990", "gender": 1
                }
            }
        ])
        @mock.patch('api.get_score')
        @mock.patch('api.check_auth')
        def test_online_score(
                self, request, mocked_check_auth, mocked_get_score
        ):
            mocked_check_auth.return_value = True
            mocked_get_score.return_value = 5.0
            self.assertEqual(
                api.method_handler(
                    {"body": request, "headers": ''},
                    {},
                    {}
                ),
                ({'score': 5.0}, 200)
            )

        # Bad response for online_score
        @cases([{
            "account": "horns&hoofs", "login": "h&f",
            "method": "online_score", "token": '',
            "arguments": {
                "phone": "", "email": "", "first_name": "",
                "last_name": "", "birthday": "", "gender": ''}
            }
        ])
        @mock.patch('api.get_score')
        @mock.patch('api.check_auth')
        def test_bad_online_score(
                self, request, mocked_check_auth, mocked_get_score
        ):
            mocked_check_auth.return_value = True
            mocked_get_score.return_value = 5.0
            self.assertEqual(
                api.method_handler(
                    {"body": request, "headers": ''},
                    {},
                    {}
                ),
                ({
                     'OnlineScoreRequest': {
                         'pair_not_exist': "Invalid set of fields "
                                           "(('phone', 'email'), "
                                           "('first_name', 'last_name'), "
                                           "('gender', 'birthday'))"
                     }
                  },
                 422
                 )
            )

        # wrong method
        @cases([{
            "account": "horns&hoofs", "login": "h&f",
            "method": "missing_method", "token": '',
            "arguments": {
                "phone": "", "email": "", "first_name": "",
                "last_name": "", "birthday": "", "gender": ''}
            }
        ])
        @mock.patch('api.check_auth')
        def test_bad_meth_online_score(
                self, request, mocked_check_auth):
            mocked_check_auth.return_value = True
            self.assertEqual(
                api.method_handler(
                    {"body": request, "headers": ''},
                    {},
                    {}
                ),
                ('Invalid Request', 422)
            )


# @unittest.skip("Skip TestScoring")
class TestScoring(unittest.TestCase):
    def setUp(self):
        self.store = api.MainHTTPHandler.store

    # With server but without initial date
    @cases([
        {'phone': '79213132121',
         'email': 'qw@qw', 'birthday': api.datetime(1954, 12, 12, 0, 0),
         'gender': 1, 'first_name': 'Ivan',
         'last_name': 'Ivanovich'
         }
        ])
    def test_get_score(self, value):
        self.assertEqual(
            api.get_score(
                self.store,
                value.get('phone'),
                value.get('email'),
                value.get('birthday'),
                value.get('gender'),
                value.get('first_name'),
                value.get('last_name')
            ), 5.0
        )

    # with server and with initial data
    @cases([
        {'phone': '79213132121',
         'email': 'qw@qw', 'birthday': api.datetime(1954, 12, 12, 0, 0),
         'gender': 1, 'first_name': 'Ivan',
         'last_name': 'Ivanov', 'result': 5.0
         },
        {'phone': '',
         'email': 'qw@qw', 'birthday': api.datetime(1954, 12, 12, 0, 0),
         'gender': 1, 'first_name': 'Ivan',
         'last_name': 'Ivanov', 'result': 3.5
         }

    ])
    def test_init_get_score(self, value):
        self.store.set_init_data()
        if self.store.is_alive:
            self.assertEqual(
                api.get_score(
                    self.store,
                    value.get('phone'),
                    value.get('email'),
                    value.get('birthday'),
                    value.get('gender'),
                    value.get('first_name'),
                    value.get('last_name')
                ), 10.0
            )
        else:
            if self.store.is_alive:
                self.assertEqual(
                    api.get_score(
                        self.store,
                        value.get('phone'),
                        value.get('email'),
                        value.get('birthday'),
                        value.get('gender'),
                        value.get('first_name'),
                        value.get('last_name')
                    ), value.get('result')
                )


class TestInterests(unittest.TestCase):
    def setUp(self):
        self.store = api.MainHTTPHandler.store
        self.store.set_init_data()

    @cases([
        {'cid': 1, 'result': {u'i:1': [u'auto', u'books']}},
        {'cid': 2, 'result': {u'i:2': [u'garden', u'birds']}},
        {'cid': 3, 'result': {u'i:3': [u'forest', u'airplane']}}
        ])
    def test_get_interests(self, value):
        if self.store.is_alive:
            self.assertEqual(
                api.get_interests(
                    self.store,
                    value.get('cid')
                ),
                value.get('result')
            )
        else:
            with self.assertRaises(Exception):
                self.assertEqual(
                    api.get_interests(
                        self.store,
                        value.get('cid')
                    ),
                    value.get('result')
                )


if __name__ == "__main__":
    unittest.main()
