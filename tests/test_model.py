# encoding: utf-8

import unittest
from froshki import Froshki, validation_hook, Attribute

try:
    import clr
    is_ipy = True
except ImportError:
    is_ipy = False


class TestAttributeModeling(unittest.TestCase):

    def test_attribute_access(self):

        # Attach Attribute instance to Froshki object.
        class RegisterFormInput(Froshki):
            user_id = Attribute()
            user_name = Attribute()
            user_age=Attribute()
            password = Attribute()

        # Instantiation with names.
        registration = RegisterFormInput(
            user_id='drowse314',
            user_age=24,
            password='ijk2355',
        )
        # Accessible as instance attributes.
        self.assertEqual(registration.user_id, 'drowse314')
        self.assertEqual(registration.user_name, None)
        self.assertEqual(registration.user_age, 24)
        self.assertEqual(registration.password, 'ijk2355')
        with self.assertRaises(AttributeError):
            assert registration.user_gender == 'male'
        # Allows assignments.
        registration.user_name = 'ymat'
        self.assertEqual(registration.user_name, 'ymat')

        # Class attributes are accessible even after __new__.
        self.assertIsInstance(RegisterFormInput.user_id, Attribute)
        self.assertIsInstance(RegisterFormInput.user_name, Attribute)
        self.assertIsInstance(RegisterFormInput.user_age, Attribute)
        self.assertIsInstance(RegisterFormInput.password, Attribute)

        # Froshki.data property.
        self.assertEqual(
            registration.data,
            {
                'user_id': 'drowse314',
                'user_name': 'ymat',
                'user_age': 24,
                'password': 'ijk2355',
            }
        )

    def test_attribute_source_hooks(self):

        # Default settings.
        class AdminLogin(Froshki):
            user_id = Attribute()
            password = Attribute()
            default_values = {
                'user_id': 'root',
            }
        admin_login = AdminLogin(password='KDalyAwytT7d;I')
        self.assertEqual(admin_login.user_id, 'root')

        # From source dict.
        class OrderSubmit(Froshki):
            order_id = Attribute()
            order_date = Attribute()
            order_owner = Attribute()
            address = Attribute()
            billing_to =Attribute()
            item_ids = Attribute()
            item_volumes = Attribute()
        source_dict = {
            'order_id': 2355,
            'order_date': '2013-08-07',
            'order_owner': 'ymat',
            'address': 'Saitama, Japan',
            'item_ids': [13, 27, 3, 48],
            'item_volumes': [1, 1, 3, 1],
        }
        order_submit = OrderSubmit(source=source_dict)
        self.assertEqual(order_submit.order_id, 2355)
        self.assertEqual(order_submit.order_date, '2013-08-07')
        self.assertEqual(order_submit.order_owner, 'ymat')
        self.assertEqual(order_submit.address, 'Saitama, Japan')
        self.assertEqual(order_submit.billing_to, None)
        self.assertEqual(order_submit.item_ids, [13, 27, 3, 48])
        self.assertEqual(order_submit.item_volumes, [1, 1, 3, 1])

    def test_attribute_transform(self):

        class IntAttribute(Attribute):
            @classmethod
            def transform(klass, input_value):
                return int(input_value)

        class TextAttribute(Attribute):
            @classmethod
            def transform(klass, input_value):
                return str(input_value)

        class User(Froshki):
            id = IntAttribute()
            user_id = TextAttribute()
            user_fname = TextAttribute()
            user_lname = TextAttribute()

        # With initialization.
        user = User(
            id='1231', user_id=213511,
            user_fname='y', user_lname='mat',
        )
        self.assertTrue(user.validate())  # Must be called to transform.
        self.assertEqual(user.id, 1231)
        self.assertEqual(user.user_id, '213511')
        self.assertEqual(user.user_fname, 'y')
        self.assertEqual(user.user_lname, 'mat')
        # With assignment.
        user.id = '2142'
        user.user_id = 73894
        self.assertTrue(user.validate())  # Even after assignments.
        self.assertEqual(user.id, 2142)
        self.assertEqual(user.user_id, '73894')
        # Conversion error behaviour.
        user.id = object
        self.assertFalse(user.validate())
        self.assertEqual(user.id, object)

    def test_model_subclassing(self):

        class Like(Froshki):
            uri = Attribute()
            user = Attribute()
            date_liked = Attribute()

        like = Like(
            uri='http://github.com',
            user='ymat',
            date_liked='2013/05/13',
        )
        self.assertTrue(like.validate())
        self.assertEqual(like.uri, 'http://github.com')
        self.assertEqual(like.user, 'ymat')
        self.assertEqual(like.date_liked, '2013/05/13')

        class LikeSwitch(Like):
            like_on = Attribute()

        like_switch = LikeSwitch(
            uri='http://github.com',
            user='ymat',
            date_liked='2013/05/13',
            like_on=True,
        )
        self.assertTrue(like_switch.validate())
        self.assertEqual(like_switch.uri, 'http://github.com')
        self.assertEqual(like_switch.user, 'ymat')
        self.assertEqual(like_switch.date_liked, '2013/05/13')
        self.assertEqual(like_switch.like_on, True)

    def test_model_as_base_class(self):

        # ! Never instantiate before subclassing !
        class Like(Froshki):
            uri = Attribute()
            user = Attribute()
            date_liked = Attribute()

        class LikeSwitch(Like):
            like_on = Attribute()

        like_switch = LikeSwitch(
            uri='http://github.com',
            user='ymat',
            date_liked='2013/05/13',
            like_on=True,
        )
        self.assertTrue(like_switch.validate())
        self.assertEqual(like_switch.uri, 'http://github.com')
        self.assertEqual(like_switch.user, 'ymat')
        self.assertEqual(like_switch.date_liked, '2013/05/13')
        self.assertEqual(like_switch.like_on, True)

    def test_attribute_mixin(self):

        class Switch(object):
            on = Attribute()

        class LikeSwitch(Froshki, Switch):
            uri = Attribute()
            user = Attribute()
            date_liked = Attribute()

        like_switch = LikeSwitch(
            uri='http://github.com',
            user='ymat',
            date_liked='2013/05/13',
            on=True,
        )
        self.assertTrue(like_switch.validate())
        self.assertEqual(like_switch.uri, 'http://github.com')
        self.assertEqual(like_switch.user, 'ymat')
        self.assertEqual(like_switch.date_liked, '2013/05/13')
        self.assertEqual(like_switch.on, True)


class TestAttrValidation(unittest.TestCase):

    def test_attr_validation(self):

        class ResourceId(Attribute):
            @classmethod
            def transform(klass, input_value):
                return int(input_value)
            @classmethod
            def validate(klass, input_value):
                if input_value in (1,5,7,9):
                    return True, input_value
                else:
                    return False, 'resource id not found'

        class Filetype(Attribute):
            @classmethod
            def validate(klass, input_value):
                if input_value in ('pdf', 'txt', 'mobi'):
                    return True, input_value
                else:
                    return False, 'filetype unavailable'

        class Download(Froshki):
            resource_id = ResourceId()
            filetype = Filetype()

        # Valid inputs.
        download = Download(resource_id='9', filetype='pdf')
        self.assertTrue(download.validate())
        self.assertTrue(download.validate())  # Consistent validation.
        self.assertEqual(download.resource_id, 9)
        self.assertEqual(download.filetype, 'pdf')
        download.resource_id = '99'  # Invalidate by assignment.
        self.assertFalse(download.validate())
        self.assertFalse(download.validate())  # Consistent validation.
        self.assertEqual(
            download.errors,
            {'resource_id': 'resource id not found'}
        )
        self.assertEqual(
            download.data,
            {'filetype': 'pdf', 'resource_id': '99'}  # Keeps value even in error.
        )
        download.resource_id = '9'  # Valid data again.
        self.assertTrue(download.validate())
        self.assertTrue(download.validate())  # Consistent validation.
        # Invalid inputs.
        invalid_dl_request = Download(resource_id='34', filetype='doc')
        self.assertFalse(invalid_dl_request.validate())
        self.assertFalse(invalid_dl_request.validate())  # Consistent validation.
        self.assertEqual(
            invalid_dl_request.errors,
            {'resource_id': 'resource id not found',
             'filetype': 'filetype unavailable'}
        )

    def test_nullable_attribute(self):

        import re
        class Nickname(Attribute):
            pattern = re.compile('\w+')
            @classmethod
            def validate(klass, input_value):
                if klass.pattern.match(input_value):
                    return True, input_value
                else:
                    return False, 'invalid nickname'

        class IntAttribute(Attribute):
            @classmethod
            def transform(klass, input_value): return int(input_value)

        class TextAttribute(Attribute):
            @classmethod
            def transform(klass, input_value): return str(input_value)

        class RegisterUser(Froshki):
            id = IntAttribute()
            user_id = TextAttribute()
            nickname = Nickname(nullable=True)

        register_user = RegisterUser(id='1988', user_id='omikoshi')
        self.assertTrue(register_user.validate())
        self.assertEqual(register_user.id, 1988)
        self.assertEqual(register_user.user_id, 'omikoshi')
        self.assertEqual(register_user.nickname, None)
        register_user.nickname = 'mksh'
        self.assertTrue(register_user.validate())
        self.assertEqual(register_user.nickname, 'mksh')


class TestComplexFunctions(unittest.TestCase):

    def test_attr_name_alias(self):

        class ResouceKey(Attribute):
            @classmethod
            def transform(klass, input_value):
                return input_value.lower()
            @classmethod
            def validate(klass, input_value):
                if input_value == 'vxfpf93':
                    return True, input_value
                else:
                    return False, 'invalid resource key'

        class ResourceAccess(Froshki):
            resource_id = Attribute()
            user_id = Attribute()
            resource_key = ResouceKey(key_alias='password')

        access = ResourceAccess(
            resource_id='1276',
            user_id='ymat', password='VXFPF93',
        )
        self.assertTrue(access.validate())
        self.assertEqual(access.resource_id, '1276')
        self.assertEqual(access.user_id, 'ymat')
        self.assertEqual(access.resource_key, 'vxfpf93')
        with self.assertRaises(AttributeError):
            access.password
        self.assertEqual(
            access.data,
            {'resource_id': '1276', 'user_id': 'ymat',
             'resource_key': 'vxfpf93'}
        )

        access.resource_key = 'fxfPf93'
        self.assertFalse(access.validate())
        self.assertEqual(
            access.errors,
            {'resource_key': 'invalid resource key'}
        )

    def test_attr_modification(self):

        class Search(Froshki):
            search_key = Attribute(key_alias='key')

        search = Search(key='japanese furoshiki')  # __new__ called for the first time.
        self.assertTrue(search.validate())

        # Append attribute.
        Search.search_type = Attribute(key_alias='type')
        search = Search(
            key='japanese furoshiki',
            type='image',
        )
        self.assertTrue(search.validate())
        self.assertEqual(search.search_key, 'japanese furoshiki')
        self.assertEqual(search.search_type, 'image')
        # Redefine attribute.
        if is_ipy:
            del Search.search_type
        Search.search_type = Attribute()
        with self.assertRaises(TypeError):
            search = Search(type='movie')
        search = Search(
            search_key='japanese furoshiki',
            search_type='movie',
        )
        self.assertTrue(search.validate())
        self.assertEqual(search.search_key, 'japanese furoshiki')
        self.assertEqual(search.search_type, 'movie')
        # Delete attribute.
        del Search.search_type
        with self.assertRaises(TypeError):
            search = Search(search_type='news')
        search = Search(search_key='russian pirozhki')
        self.assertTrue(search.validate())
        self.assertEqual(search.search_key, 'russian pirozhki')

    def test_froshki_validation_hooks(self):

        class ModifyPassword(Froshki):
            user_id = Attribute()
            old_password = Attribute()
            new_password = Attribute()
            confirm_new_password = Attribute()
            @validation_hook
            def confirm_password(self):
                if self.new_password == self.confirm_new_password:
                    return True
                else:
                    return False

        modify_password = ModifyPassword(
            user_id='ymat', old_password='vxf',
            new_password='f8a73', confirm_new_password='f8a73',
        )
        self.assertTrue(modify_password.validate())
        modify_password.confirm_new_password = 'fffff'
        self.assertFalse(modify_password.validate())

    def test_extended_validation_hooks(self):

        class CreateEvent(Froshki):
            event_name = Attribute()
            event_start = Attribute()
            event_end = Attribute()
            @validation_hook.extend(error='event must start before the end')
            def check_event_duration(self):
                if self.event_start < self.event_end:
                    return True
                else:
                    return False

        import datetime
        create_event = CreateEvent(
            event_name='Hack your forms',
            event_start=datetime.time(hour=17, minute=30),
            event_end=datetime.time(hour=20, minute=0),
        )
        self.assertTrue(create_event.validate())

        create_event.event_end = datetime.time(hour=16, minute=0)
        self.assertFalse(create_event.validate())
        self.assertEqual(
            create_event.errors,
            dict(check_event_duration='event must start before the end')
        )

    def test_ignore_unknown_keys(self):

        class Configuration(Froshki):
            filter_level = Attribute()
            prediction = Attribute()
            items_per_page = Attribute()

        attr_source = {
            'filter_level': 'high',
            'prediction': True,
            'items_per_page': 40,
            'lang': 'ja',
        }
        with self.assertRaises(TypeError):
            config = Configuration(source=attr_source)

        Configuration.ignore_unknown_keys = True
        config = Configuration(source=attr_source)
        self.assertTrue(config.validate())

        # Overwrite on instance.
        with self.assertRaises(TypeError):
            config = Configuration(
                source=attr_source,
                ignore_unknown_keys=False,
            )
        self.assertTrue(Configuration.ignore_unknown_keys)
