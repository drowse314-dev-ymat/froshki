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
