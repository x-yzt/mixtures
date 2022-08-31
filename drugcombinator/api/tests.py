from django.test import TestCase
from django.urls import NoReverseMatch, reverse
from django.utils import translation

from drugcombinator.models import Drug, Interaction
from utils.serializers import StructureSerializer


TEST_HOST = 'http://testserver/'


translation.activate('fr')


class BaseAPITestCase(TestCase):
    drug_a = Drug(name="Drug A", slug='drug-a', aliases=["Other"])
    drug_b = Drug(name="Drug B", slug='drug-b')
    drug_c = Drug(name="Drug C", slug='drug-c')

    inter_a_b = Interaction(
        from_drug=drug_a,
        to_drug=drug_b,
        names=["Inter A+B"],
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

    def assertContainsSubset(self, set, subset, *args, **kwargs):
        return self.assertEqual(set, set | subset, *args, **kwargs)


class DrugStructureSerializerTestCase(BaseAPITestCase):
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

    serializer_nested_callback = StructureSerializer((
        'name',
        ('interactions', 'slug', (
            lambda o: ('custom', str(o).upper()),
        ))
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

    def testSerializerCallable(self):
        self.assertEqual(
            self.serializer_nested_callback.serialize(self.drug_a),
            {
                'name': 'Drug A',
                'interactions': {
                    'drug-a_drug-b': {'custom': 'DRUG A + DRUG B'},
                    'drug-a_drug-c': {'custom': 'DRUG A + DRUG C'}
                }
            }
        )


class APIViewTestCase(BaseAPITestCase):
    def testAliases(self):
        response = self.client.get(reverse('api:aliases'))

        self.assertContainsSubset(
            response.json(),
            {
                'Drug A': {
                    'slug': 'drug-a',
                    'url': TEST_HOST + 'fr/api/v1/substance/drug-a/'
                },
                'Other': {
                    'slug': 'drug-a',
                    'url': TEST_HOST + 'fr/api/v1/substance/drug-a/'
                },
            }
        )

    def testSearch(self):
        for field, query in (
            ('slug', "drug-a"),
            ('name', "Drug A"),
            ('alias', "Other"),
        ):
            with self.subTest(field=field):
                response = self.client.get(
                    reverse('api:search', kwargs={'name': query})
                )

                self.assertEqual(
                    response.json(),
                    {
                        'slug': 'drug-a',
                        'url': TEST_HOST + 'fr/api/v1/substance/drug-a/'
                    }
                )

    def testSearchNoResult(self):
        response = self.client.get(
            reverse('api:search', kwargs={'name': "Unknown"})
        )

        self.assertEqual(response.status_code, 404)

    def testDrug(self):
        response = self.client.get(
            reverse('api:drug', kwargs={'slug': "drug-a"})
        )

        self.assertEqual(
            response.json(),
            {
                'name': "Drug A",
                'slug': 'drug-a',
                'aliases': ["Other"],
                'site_url': TEST_HOST + 'fr/substance/drug-a/',
                'category': None,
                'common': True,
                'description': "",
                'risks': "",
                'effects': "",
                'interactions': {
                    'drug-a_drug-b': {
                        'interactants': ["Drug A", "Drug B"],
                        'is_draft': True,
                        'url': TEST_HOST + 'fr/api/v1/combo/drug-a+drug-b/',
                        'site_url': TEST_HOST + 'fr/combo/drug-a+drug-b/',
                        'risk': 0,
                        'synergy': 0,
                        'risk_reliability': 0,
                        'effects_reliability': 0,
                        'risk_description': "",
                        'effect_description': "",
                    },
                    'drug-a_drug-c': {
                        'interactants': ["Drug A", "Drug C"],
                        'is_draft': True,
                        'url': TEST_HOST + 'fr/api/v1/combo/drug-a+drug-c/',
                        'site_url': TEST_HOST + 'fr/combo/drug-a+drug-c/',
                        'risk': 0,
                        'synergy': 0,
                        'risk_reliability': 0,
                        'effects_reliability': 0,
                        'risk_description': "",
                        'effect_description': "",
                    },
                }
            }
        )

    def testDrugNoResult(self):
        response = self.client.get(
            reverse('api:drug', kwargs={'slug': 'unknown'})
        )

        self.assertEqual(response.status_code, 404)

    def testCombine(self):
        response = (
            self.client
            .get(reverse(
                'api:combine',
                kwargs={'slugs': ['drug-a', 'drug-b', 'drug-c']})
            )
            .json()
        )

        self.assertEqual(response['unknown_interactions'], 1)
        self.assertEqual(
            tuple(response['interactions']),
            ('drug-a_drug-b', 'drug-a_drug-c')
        )
        self.assertContainsSubset(
            response['interactions'],
            {
                'drug-a_drug-b': {
                    'names': ["Inter A+B"],
                    'is_draft': True,
                    'site_url': TEST_HOST + 'fr/combo/drug-a+drug-b/',
                    'risk': 0,
                    'synergy': 0,
                    'risk_reliability': 0,
                    'effects_reliability': 0,
                    'risk_description': '',
                    'effect_description': '',
                    'interactants': {
                        'drug-a': {
                            'name': 'Drug A',
                            'slug': 'drug-a',
                            'url': TEST_HOST + 'fr/api/v1/substance/drug-a/',
                            'site_url': TEST_HOST + 'fr/substance/drug-a/',
                            'risks': '',
                            'effects': ''
                        },
                        'drug-b': {
                            'name': 'Drug B',
                            'slug': 'drug-b',
                            'url': TEST_HOST + 'fr/api/v1/substance/drug-b/',
                            'site_url': TEST_HOST + 'fr/substance/drug-b/',
                            'risks': '',
                            'effects': ''
                        }
                    }
                }
            }
        )

    def testCombineEmpty(self):
        with self.assertRaises(NoReverseMatch):
            self.client.get(reverse('api:combine'), kwargs={'slugs': []})

    def testCombineReturnCode(self):
        for slugs, code in (
            (['drug-a'],                     400),
            (['drug-a', 'drug-a'],           400),
            (['drug-x'],                     400),
            ([str(x) for x in range(6)],     400),
            (['drug-a', 'drug-x'],           404),
            (['drug-a', 'drug-b', 'drug-x'], 404),
            (['drug-x', 'drug-y'],           404),
            (['drug-a', 'drug-b'],           200),
        ):
            url = reverse('api:combine', kwargs={'slugs': slugs})

            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, code)
