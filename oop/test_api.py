import unittest
import api


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
        self.assertEqual(field.clean('12.12.1954'), api.datetime(1954, 12, 12, 0, 0))
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

    # @cases([
    #     {'client_ids': [1, 2, 3]},
    #     # {'client_ids': [1, 2, 3], 'date': ''},
    #     # {'client_ids': [1, 2, 3], 'date': '23.12.1987'},
    # ])
    # def test_get_response(self, value):
    #     request = api.ClientsInterestsRequest(value)
    #     self.assertEqual(request.get_response({}, ''), True)


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









if __name__ == "__main__":
    unittest.main()
