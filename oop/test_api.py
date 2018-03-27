import unittest
import api


class TestSuite(unittest.TestCase):
    def setUp(self):
        self.context = {}
        self.headers = {}
        self.store = None

    # def get_response(self, request):
    #     return api.method_handler({"body": request, "headers": self.headers},
    #                               self.context, self.store)
    #
    # def test_empty_request(self):
    #     _, code = self.get_response({})
    #     self.assertEqual(api.INVALID_REQUEST, code)

    def test_field(self):
        field = api.Field(required=False, nullable=True)
        self.assertEqual(field.clean({}), {})
        self.assertEqual(field.clean(''), '')
        self.assertEqual(field.clean([]), [])
        self.assertEqual(field.clean(None), None)

    def test_argument_field(self):
        field = api.ArgumentsField()
        self.assertEqual(field.clean({'a': 1}), {'a': 1})
        with self.assertRaises(Exception):
            field.clean('edasdasasdasd')
        with self.assertRaises(Exception):
            field.clean({})
        with self.assertRaises(Exception):
            field.clean('')

    def test_email_field(self):
        field = api.EmailField()
        self.assertEqual(field.clean('edasdas@asdasd'), 'edasdas@asdasd')
        with self.assertRaises(Exception):
            field.clean('edasdasasdasd')
        with self.assertRaises(Exception):
            field.clean('')

    def test_phone_field(self):
        field = api.PhoneField()
        self.assertEqual(field.clean('78981231231'), '78981231231')
        with self.assertRaises(Exception):
            field.clean('88981231231')
        with self.assertRaises(Exception):
            field.clean('1')
        with self.assertRaises(Exception):
            field.clean('888981231211131')
        with self.assertRaises(Exception):
            field.clean('')

    def test_date_field(self):
        field = api.DateField()
        self.assertEqual(field.clean('12.12.1954'), api.datetime(1954, 12, 12, 0, 0))
        with self.assertRaises(Exception):
            field.clean('12/12/1954')
        with self.assertRaises(Exception):
            field.clean('')

    def test_birthday_field(self):
        field = api.BirthDayField()
        self.assertEqual(field.clean('12.12.1954'), api.datetime(1954, 12, 12, 0, 0))
        with self.assertRaises(Exception):
            field.clean('12/12/1954')
        with self.assertRaises(Exception):
            field.clean('12.12.1904')
        with self.assertRaises(Exception):
            field.clean('')

    def test_gender_field(self):
        field = api.GenderField()
        self.assertEqual(field.clean(0), 0)
        self.assertEqual(field.clean(1), 1)
        self.assertEqual(field.clean(2), 2)
        with self.assertRaises(Exception):
            field.clean(-1)
        with self.assertRaises(Exception):
            field.clean(3)
        with self.assertRaises(Exception):
            field.clean('')

    def test_client_ids_field(self):
        field = api.ClientIDsField()
        self.assertEqual(field.clean([1, 2, 3]), [1, 2, 3])
        self.assertEqual(field.clean([-1, 2, -3]), [-1, 2, -3])
        with self.assertRaises(Exception):
            field.clean(1)
        with self.assertRaises(Exception):
            field.clean('s')
        with self.assertRaises(Exception):
            field.clean([])
        with self.assertRaises(Exception):
            field.clean(['1', 2, 3])
        with self.assertRaises(Exception):
            field.clean(['1', '2', '3'])
        with self.assertRaises(Exception):
            field.clean('')






if __name__ == "__main__":
    unittest.main()
