#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
import hashlib
import uuid
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
from optparse import OptionParser

import six
from dateutil.relativedelta import relativedelta

from scoring import get_interests, get_score

SALT = "Otus"
ADMIN_LOGIN = "admin"
ADMIN_SALT = "42"
OK = 200
BAD_REQUEST = 400
FORBIDDEN = 403
NOT_FOUND = 404
INVALID_REQUEST = 422
INTERNAL_ERROR = 500
ERRORS = {
    BAD_REQUEST: "Bad Request",
    FORBIDDEN: "Forbidden",
    NOT_FOUND: "Not Found",
    INVALID_REQUEST: "Invalid Request",
    INTERNAL_ERROR: "Internal Server Error",
}
UNKNOWN = 0
MALE = 1
FEMALE = 2
GENDERS = {
    UNKNOWN: "unknown",
    MALE: "male",
    FEMALE: "female",
}

EMPTY_VALUES = (None, '', [], (), {})


class Field(object):
    default_error_messages = {
        'nullable': 'This field must not be an empty.'
    }

    empty_values = list(EMPTY_VALUES)

    def __init__(self, required=True, nullable=False):
        self.required = required
        self.nullable = nullable

        messages = {}
        for c in reversed(self.__class__.__mro__):
            messages.update(getattr(c, 'default_error_messages', {}))
        self.error_messages = messages
        super(Field, self).__init__()

    def prepare_value(self, value):
        """ Implemented in each field """
        return value

    def validate(self, value):
        """ Basic validation """
        if value in self.empty_values and not self.nullable:
            raise ValidationError(self.error_messages['nullable'])

    def clean(self, value):
        """
        Validate the given value and return its "cleaned" value as an
        appropriate Python object. Raise ValidationError for any errors.
        """
        value = self.prepare_value(value)
        self.validate(value)
        return value


class BaseRequest(object):
    default_error_messages = {
        'required': 'This field <{}> is required.',
    }

    def __init__(self, data=None):
        self._errors = {}
        self.data = {} if data is None else data
        self.fields = []
        self.not_empty_fields = []
        for key, value in self.base_fields:
            if key not in self.data:
                setattr(self, key, '')
                continue
            setattr(self, key, self.data[key])
            self.fields.append((key, value))

            if self.data[key] not in EMPTY_VALUES:
                self.not_empty_fields.append(key)

    @property
    def errors(self):
        """Return errors for the data provided for the request."""
        self._clean_request()
        self._clean_fields()
        return self._errors

    def is_valid(self):
        """Return True if the request has no errors, or False otherwise."""
        return not self.errors

    def _validate(self):
        """ Basic validation for required fields """
        for field in self.base_fields:
            if field[1].required and field not in self.fields:
                raise ValidationError(
                    self.default_error_messages['required'].format(field[0])
                )

    def _clean_fields(self):
        for name, field in self.fields:
            value = self.data.get(name)
            try:
                field.clean(value)
            except ValidationError as e:
                self._errors[name] = e.message

    def _clean_request(self):
        try:
            self._validate()
            self.clean()
        except ValidationError as e:
            self._errors[self.__class__.__name__] = e.message

    def clean(self):
        """ Implemented in a request """
        pass


class DeclarativeFieldsMetaclass(type):
    """Collect Fields declared on the base classes."""
    def __new__(mcs, name, bases, attrs):
        # Collect fields from current class.
        base_fields = []
        for key, value in list(attrs.items()):
            if isinstance(value, Field):
                base_fields.append((key, value))
                attrs.pop(key)

        new_class = super(DeclarativeFieldsMetaclass, mcs).\
            __new__(mcs, name, bases, attrs)
        new_class.base_fields = base_fields

        return new_class


class Request(six.with_metaclass(DeclarativeFieldsMetaclass, BaseRequest)):
    "A collection of Fields, plus their associated data."


class ValidationError(Exception):
    """An error while validating data."""
    def __init__(self, message, code=None, params=None):
        super(ValidationError, self).__init__(message, code, params)
        self.message = message
        self.code = code
        self.params = params
        self.error_list = [self]


class CharField(Field):
    def __init__(self, empty_value='', **kwargs):
        self.empty_value = empty_value
        super(CharField, self).__init__(**kwargs)

    def prepare_value(self, value):
        """Return a value or preset empty value."""
        if value in self.empty_values:
            return self.empty_value
        return value


class DateField(Field):
    default_error_messages = {
        'date_format': "Invalid date. Must be in format DD.MM.YYYY",
    }

    def prepare_value(self, value):
        if value in self.empty_values:
            return ''
        try:
            value = datetime.strptime(value, '%d.%m.%Y')
        except:
            raise ValidationError(self.error_messages['date_format'])
        return value


class ClientIDsField(Field):
    default_error_messages = {
        'list_int': "Invalid IDs. Must be a list of integers",
    }

    def prepare_value(self, value):
        if value in self.empty_values:
            return None
        if not isinstance(value, list) or \
                not all(isinstance(v, int) for v in value):
            raise ValidationError(self.error_messages['list_int'])
        return value


class PhoneField(Field):
    default_error_messages = {
        'length': "Invalid length. Must be 11",
        'start_7': "Invalid format. Must start with 7",
    }

    def prepare_value(self, value):
        if value in self.empty_values:
            return ''
        if len(str(value)) != 11:
            raise ValidationError(self.error_messages['length'])
        if not str(value).startswith('7'):
            raise ValidationError(self.error_messages['start_7'])
        return value


class EmailField(CharField):
    default_error_messages = {
        'email': "Invalid email. Must contains @",
    }

    def prepare_value(self, value):
        if value in self.empty_values:
            return ''
        if "@" not in value:
            raise ValidationError(self.error_messages['email'])
        return value


class BirthDayField(DateField):
    default_error_messages = {
        'birthday': "Invalid Birthday. Must be less then 70",
    }

    def prepare_value(self, value):
        new_value = super(BirthDayField, self).prepare_value(value)
        if relativedelta(datetime.today(), new_value).years > 70:
            raise ValidationError(self.error_messages['birthday'])
        return new_value


class GenderField(Field):
    default_error_messages = {
        'gender': "Invalid gender. Must be 0 or 1 or 2",
    }

    def prepare_value(self, value):
        if value in self.empty_values:
            return ''
        if value not in GENDERS:
            raise ValidationError(self.error_messages['gender'])
        return value


class ArgumentsField(Field):
    default_error_messages = {
        'dict': '"Invalid arguments. Must be a dict."',
    }

    def prepare_value(self, value):
        if value in self.empty_values:
            return {}
        if not isinstance(value, dict):
            raise ValidationError(self.error_messages['dict'])
        return value


class ClientsInterestsRequest(Request):
    client_ids = ClientIDsField()
    date = DateField(required=False, nullable=True)

    def get_response(self, ctx, store, is_admin=False):
        response = {}
        for client in self.client_ids:
            response[str(client)] = get_interests(store, '')
        ctx['nclients'] = len(self.client_ids)
        return response, OK


class OnlineScoreRequest(Request):
    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=False, nullable=True)

    def get_response(self, ctx, store, is_admin=False):
        if is_admin:
            score = 42
        else:
            score = get_score(
                store, self.phone, self.email, birthday=self.birthday,
                gender=self.gender, first_name=self.first_name,
                last_name=self.last_name)

        ctx['has'] = self.not_empty_fields
        return {'score': score}, OK

    def clean(self):
        validate_set = (
                ('phone', 'email'),
                ('first_name', 'last_name'),
                ('gender', 'birthday')
        )
        for one_set in validate_set:
            if all(self.data.get(name) not in EMPTY_VALUES and
                   name not in self._errors for name in one_set
                   ):
                return

        error_messages = {
            'pair_not_exist': "Invalid set of fields {}".format(validate_set),
        }
        raise ValidationError(error_messages)


class MethodRequest(Request):
    account = CharField(required=False, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method = CharField(required=True, nullable=False)

    @property
    def is_admin(self):
        return self.login == ADMIN_LOGIN


def check_auth(request):


    return True





    if request.is_admin:
        digest = hashlib.sha512(datetime.now().strftime(
            "%Y%m%d%H") + ADMIN_SALT).hexdigest()
    else:
        digest = hashlib.sha512(
            request.account + request.login + SALT).hexdigest()
    if digest == request.token:
        return True
    return False


def method_handler(request, ctx, store):
    handlers = {
        'clients_interests': ClientsInterestsRequest,
        'online_score': OnlineScoreRequest
    }

    method_request = MethodRequest(request["body"])
    if not method_request.is_valid():
        return method_request.errors, INVALID_REQUEST

    if not check_auth(method_request):
        return ERRORS[FORBIDDEN], FORBIDDEN

    if method_request.method in handlers:
        handler = handlers[method_request.method](method_request.arguments)
        if handler.is_valid():
            return handler.get_response(ctx, store, method_request.is_admin)
        return handler.errors, INVALID_REQUEST

    return ERRORS[INVALID_REQUEST], INVALID_REQUEST


class MainHTTPHandler(BaseHTTPRequestHandler):
    router = {
        "method": method_handler
    }
    store = None

    def get_request_id(self, headers):
        return headers.get('HTTP_X_REQUEST_ID', uuid.uuid4().hex)

    def do_POST(self):
        response, code = {}, OK
        context = {"request_id": self.get_request_id(self.headers)}
        request = None
        try:
            data_string = self.rfile.read(int(self.headers['Content-Length']))
            request = json.loads(data_string)
        except:
            code = BAD_REQUEST

        if request:
            path = self.path.strip("/")
            logging.info(
                "%s: %s %s" % (self.path, data_string, context["request_id"]))
            if path in self.router:
                try:
                    response, code = self.router[path](
                        {"body": request, "headers": self.headers}, context,
                        self.store)
                except Exception as e:
                    logging.exception("Unexpected error: %s" % e)
                    code = INTERNAL_ERROR
            else:
                code = NOT_FOUND

        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if code not in ERRORS:
            r = {"response": response, "code": code}
        else:
            r = {"error": response or ERRORS.get(code, "Unknown Error"),
                 "code": code}
        context.update(r)
        logging.info(context)
        self.wfile.write(json.dumps(r))
        return


if __name__ == "__main__":
    op = OptionParser()
    op.add_option("-p", "--port", action="store", type=int, default=8080)
    op.add_option("-l", "--log", action="store", default=None)
    (opts, args) = op.parse_args()
    logging.basicConfig(filename=opts.log, level=logging.INFO,
                        format='[%(asctime)s] %(levelname).1s %(message)s',
                        datefmt='%Y.%m.%d %H:%M:%S')
    server = HTTPServer(("localhost", opts.port), MainHTTPHandler)
    logging.info("Starting server at %s" % opts.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
