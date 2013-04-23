# encoding: utf-8

import unittest
import trafaret
from froshki import Froshki, validation_hook
from froshki.ext.trafaret_attr import TrafaretPoweredAttribute, trafaret_attr


class TestTrafaretIntegration(unittest.TestCase):

    def test_trafaret_powered_attribute(self):

        class Int(TrafaretPoweredAttribute):
            trafaret = trafaret.Int()
        class Email(TrafaretPoweredAttribute):
            trafaret = trafaret.Email()
        class ProductId(TrafaretPoweredAttribute):
            trafaret = trafaret.Enum('F171', 'F172', 'F173')
        class OrderVolume(TrafaretPoweredAttribute):
            trafaret = trafaret.Int(gt=0)

        import datetime
        datetime_converter = (
            trafaret.String(regex=r'^(\d{4})/(\d{2})/(\d{2})$')
            >> (lambda m: datetime.datetime(
                    *[int(num) for num in m.groups()]
                ))
        )
        class Date(TrafaretPoweredAttribute):
            trafaret = datetime_converter

        class OrderSubmit(Froshki):
            client_id = Int()
            client_email = Email()
            product_id = ProductId()
            volume = OrderVolume()
            order_date = Date()
            delivary_date = Date()
            @validation_hook
            def consistent_date(self):
                try:
                    return self.order_date < self.delivary_date
                except:
                    return False

        attr_source = dict(
            client_id=1249, client_email='drowse314@gmail.com',
            product_id='F172', volume=1,
            order_date='2013/04/16', delivary_date='2013/05/01',
        )
        order_submit = OrderSubmit(source=attr_source)
        self.assertTrue(order_submit.validate())

        failure_updates = dict(
            client_id='ymat', client_email='drowse314:gmail.com',
            product_id='F17', volume=-1,
            order_date='2013/04/5', delivary_date='2012/05/01',
        )
        for failure_key in failure_updates:
            attr_failure = attr_source.copy()
            attr_failure.update(
                {failure_key: failure_updates[failure_key]}
            )
            order_submit = OrderSubmit(
                source=attr_failure
            )
            self.assertFalse(order_submit.validate())

    def test_trafaret_attribute_shortcut(self):

        class EventEntry(Froshki):
            user_id = trafaret_attr(trafaret.Int(gt=0))()
            user_contact = trafaret_attr(trafaret.Email())()
            members = trafaret_attr(
                trafaret.String(regex=r'^\d[\d,]*$')
                >> (lambda m: [int(i) for i in m.string.split(',')])
            )(key_alias='team_members')
            team_name = trafaret_attr(trafaret.String())(nullable=True)
            @validation_hook
            def leader_in_team(self):
                try:
                    return self.user_id in self.members
                except:
                    return False

        attr_source = dict(
            user_id=3219, user_contact='jsai.ml.keeper.ymat@gmail.com',
            team_members='314,6341,3219,4418',
            team_name='Nice Middles',
        )
        event_entry = EventEntry(source=attr_source)

        failure_updates = dict(
            user_id='ymat', user_contact='y@m@a@t@example.com',
            team_members='314,6341,4418,ku',
        )
        for failure_key in failure_updates:
            attr_failure = attr_source.copy()
            attr_failure.update(
                {failure_key: failure_updates[failure_key]}
            )
            event_entry = EventEntry(
                source=attr_failure
            )
            self.assertFalse(event_entry.validate())

        # Nullable attribute.
        valid_source = attr_source.copy()
        valid_source.pop('team_name')
        event_entry = EventEntry(source=valid_source)
        self.assertTrue(event_entry.validate())
