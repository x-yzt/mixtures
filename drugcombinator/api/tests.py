from django.test import TestCase

from drugcombinator.models import Drug, Interaction
from utils.serializers import StructureSerializer


class DrugSerializerTestCase(TestCase):
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

    serializer = StructureSerializer((
        'name',
        'slug',
        ('interactions', 'slug', (
            'interactants',
            'is_draft',
        ))
    ))

    def setUp(self):
        self.drug_a.save()
        self.drug_b.save()
        self.drug_c.save()
        self.inter_a_b.save()
        self.inter_a_c.save()

    def testStructureSerializerSimple(self):
        self.assertEquals(
            self.serializer.serialize(self.drug_a),
            {
                'interactions': {
                    'drug-a_drug-b': {
                        'interactants': ('Drug A', 'Drug B'),
                        'is_draft': True
                    },
                    'drug-a_drug-c': {
                        'interactants': ('Drug A', 'Drug C'),
                        'is_draft': True
                    }
                },
                'name': 'Drug A',
                'slug': 'drug-a'
            }
        )
