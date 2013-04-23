# encoding: utf-8

import unittest
from  voluptuous import Schema, All, Length, Range, Any
from froshki import Froshki, validation_hook
from froshki.ext.voluptuous_attr import VoluptuousPoweredAttribute, voluptuous_attr


class TestVoluptuousIntegration(unittest.TestCase):

    def test_voluptuous_powered_attribute(self):

        class QueryKey(VoluptuousPoweredAttribute):
            schema = Schema(All(str, Length(min=3)))
        class ItemFetchSize(VoluptuousPoweredAttribute):
            schema = Schema(All(int, Range(min=1, max=50)))
        class PageOffset(VoluptuousPoweredAttribute):
            schema = Schema(All(int, Range(min=0)))
        class ResultFields(VoluptuousPoweredAttribute):
            schema = Schema(['document', 'line_no', 'surroundings', 'hit_count'])

        class SearchText(Froshki):
            query = QueryKey()
            items_per_page = ItemFetchSize()
            page_offset = PageOffset()
            result_fields = ResultFields()

        attr_source = dict(
            query='monday morning',
            items_per_page=30, page_offset=0,
            result_fields=['document', 'surroundings', 'hit_count'],
        )
        search_text = SearchText(source=attr_source)
        self.assertTrue(search_text.validate())
        self.assertEqual(search_text.query, 'monday morning')
        self.assertEqual(search_text.items_per_page, 30)
        self.assertEqual(search_text.page_offset, 0)
        self.assertEqual(
            search_text.result_fields,
            [
                'document', 'surroundings', 'hit_count',
            ]
        )

        failure_updates = dict(
            query='aa',
            items_per_page=80, page_offset=-1,
            result_fields=['doc', 'surroundings'],
        )
        for failure_key in failure_updates:
            attr_failure = attr_source.copy()
            attr_failure.update(
                {failure_key: failure_updates[failure_key]}
            )
            search_text = SearchText(
                source=attr_failure
            )
            self.assertFalse(search_text.validate())

    def test_voluptuous_attribute_shortcut(self):

        import datetime
        def timestamp(time_repr):
            return datetime.datetime.strptime(
                time_repr,
                '%Y-%m-%d-%H:%M',
            )

        class POS(Froshki):
            item_id = voluptuous_attr(Schema(All(int, Range(min=1))))(key_alias='item')
            shop_id = voluptuous_attr(Schema(All(int, Range(min=1))))(key_alias='shop')
            time_stamp = voluptuous_attr(Schema(timestamp))()
            buyer_gender = voluptuous_attr(Schema(Any('male', 'female')))(nullable=True)
            buyer_age_looking = voluptuous_attr(
                Schema(Any('5-20', '20-30', '30-40', '40-50', '50-60', '60-70', '70-'))
            )(nullable=True)

        attr_source = dict(
            item=8231, shop=319,
            time_stamp='2014-04-26-12:28',
        )
        pos = POS(source=attr_source)
        self.assertTrue(pos.validate())

        attr_source.update(dict(
            buyer_gender='male', buyer_age_looking='40-50',
        ))
        pos = POS(source=attr_source)
        self.assertTrue(pos.validate())

        failure_updates = dict(
            item='kabayaki', shop='Shinjuku-Sanchome',
            time_stamp='2012/08/01 05:16',
            buyer_gender='hideyoshi', buyer_age_looking='0-5',
        )
        for failure_key in failure_updates:
            attr_failure = attr_source.copy()
            attr_failure.update(
                {failure_key: failure_updates[failure_key]}
            )
            pos = POS(
                source=attr_failure
            )
            self.assertFalse(pos.validate())
