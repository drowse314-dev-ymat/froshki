# encoding: utf-8

import unittest
from froshki import Froshki
from froshki.model import Attribute


class TestModel(unittest.TestCase):

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
