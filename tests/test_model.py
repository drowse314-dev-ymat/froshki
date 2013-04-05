# encoding: utf-8

import unittest
from froshki import Froshki
from froshki.model import Attribute


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
        self.assertEqual(user.id, 1231)
        self.assertEqual(user.user_id, '213511')
        self.assertEqual(user.user_fname, 'y')
        self.assertEqual(user.user_lname, 'mat')
        # With assignment.
        user.id = '2142'
        user.user_id = 73894
        self.assertEqual(user.id, 2142)
        self.assertEqual(user.user_id, '73894')
