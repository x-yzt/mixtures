from django.test import TestCase

from drugcombinator.models import Drug, Interaction
from utils.serializers import StructureSerializer


class BaseDrugSerializerTestCase(TestCase):
    drug_a = Drug(name="Drug A", slug='drug-a')
    drug_b = Drug(name="Drug B", slug='drug-b')
    drug_c = Drug(name="Drug C", slug='drug-c')

    inter_a_b = Interaction(
        from_drug=drug_a,
        to_drug=drug_b,
    )
    inter_a_c = Interaction(
        from_drug=drug_a,
        to_drug=drug_c,
    )

    def setUp(self):
        self.drug_a.save()
        self.drug_b.save()
        self.drug_c.save()
        self.inter_a_b.save()
        self.inter_a_c.save()


class DrugStructureSerializerTestCase(BaseDrugSerializerTestCase):
    serializer_key = StructureSerializer((
        'name',
        ('interactions', 'slug')
    ))

    serializer_nested = StructureSerializer((
        'name',
        ('interactions', 'slug', ('interactants',))
    ))

    serializer_nested_no_key = StructureSerializer((
        'name',
        ('interactions', None, ('interactants',))
    ))

    def testSerialize(self):
        for (serializer, result) in {
            'serializer_key': {
                'name': 'Drug A',
                'interactions': ('drug-a_drug-b', 'drug-a_drug-c')
            },
            'serializer_nested': {
                'name': 'Drug A',
                'interactions': {
                    'drug-a_drug-b': {
                        'interactants': ('Drug A', 'Drug B'),
                    },
                    'drug-a_drug-c': {
                        'interactants': ('Drug A', 'Drug C'),
                    },
                }
            },
            'serializer_nested_no_key': {
                'name': 'Drug A',
                'interactions': (
                    {'interactants': ('Drug A', 'Drug B')},
                    {'interactants': ('Drug A', 'Drug C')},
                )
            }
        }.items():
            with self.subTest(serializer=serializer):
                serializer = getattr(self, serializer)
                self.assertEqual(
                    serializer.serialize(self.drug_a), result
                )

    def testSerializeMany(self):
        for (serializer, result) in {
            'serializer_key': ({
                'name': 'Drug A',
                'interactions': ('drug-a_drug-b', 'drug-a_drug-c')
            }, {
                'name': 'Drug B',
                'interactions': ('drug-a_drug-b',)
            }),
            'serializer_nested': ({
                'name': 'Drug A',
                'interactions': {
                    'drug-a_drug-b': {
                        'interactants': ('Drug A', 'Drug B')
                    },
                    'drug-a_drug-c': {
                        'interactants': ('Drug A', 'Drug C')
                    },
                }
            }, {
                'name': 'Drug B',
                'interactions': {
                    'drug-a_drug-b': {
                        'interactants': ('Drug A', 'Drug B')
                    },
                }
            }),
            'serializer_nested_no_key': ({
                'name': 'Drug A',
                'interactions': (
                    {'interactants': ('Drug A', 'Drug B')},
                    {'interactants': ('Drug A', 'Drug C')},
                )
            }, {
                'name': 'Drug B',
                'interactions': (
                    {'interactants': ('Drug A', 'Drug B')},
                )
            }),
        }.items():
            with self.subTest(serializer=serializer):
                serializer = getattr(self, serializer)
                self.assertEqual(
                    serializer.serialize_many((self.drug_a, self.drug_b)),
                    result
                )

    def testSerializeSingleKey(self):
        self.assertEqual(
            self.serializer_nested.serialize_single_key(
                (self.drug_a, self.drug_b),
                key='name'
            ),
            ('Drug A', 'Drug B')
        )

    def testSerializeSingleForeignKey(self):
        self.assertEqual(
            self.serializer_nested.serialize_single_key(
                (self.inter_a_b, self.inter_a_c),
                key='interactants'
            ),
            (('Drug A', 'Drug B'), ('Drug A', 'Drug C'))
        )
