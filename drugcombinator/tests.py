from operator import attrgetter

from django.db.utils import IntegrityError
from django.test import TestCase

from drugcombinator.forms import ContribForm
from drugcombinator.modelfields import ListField
from drugcombinator.models import Drug, Interaction
from drugcombinator.utils import normalize


class UtilsTestCase(TestCase):
    def test_normalize(self):
        self.assertEqual(
            normalize("Je bois du café. Ça vous va ?"),
            "je bois du cafe. ca vous va ?"
        )

    def test_normalize_noop(self):
        data = "c'est vraiment pas de bol !"
        self.assertEqual(normalize(data), data)


class ListFieldTestCase(TestCase):
    def test_list_field_deconstruct(self):
        list_field = ListField(sep=',', default=['a'], help_text="Foo")
        _, _, args, kwargs = list_field.deconstruct()
        reconstructed_list_field = ListField(*args, **kwargs)

        ag = attrgetter('sep', 'default', 'help_text')
        self.assertEqual(ag(list_field), ag(reconstructed_list_field))


class InteractionModelTestCase(TestCase):
    drug_a = Drug(name="DrugA", slug='drug-a')
    drug_b = Drug(name="DrugB", slug='drug-b')
    drug_c = Drug(name="DrugC", slug='drug-c')

    inter_a_b = Interaction(
        from_drug=drug_a,
        to_drug=drug_b,
        names=["First name", "Second name"]
    )
    inter_b_c = Interaction(
        from_drug=drug_b,
        to_drug=drug_c
    )

    def setUp(self):
        self.drug_a.save()
        self.drug_b.save()
        self.drug_c.save()
        self.inter_a_b.save()
        self.inter_b_c.save()

    def test_interactants_inequals(self):
        with self.assertRaises(IntegrityError):
            Interaction(
                from_drug=self.drug_a,
                to_drug=self.drug_a
            ).save()

    def test_interactants_unique_together(self):
        with self.assertRaises(IntegrityError):
            Interaction(
                from_drug=self.drug_b,
                to_drug=self.drug_a
            ).save()

    def test_interactants_ordering(self):
        inter = Interaction(
            from_drug=self.drug_c,
            to_drug=self.drug_a
        )
        inter.save()
        self.assertSequenceEqual(
            inter.interactants,
            sorted(inter.interactants, key=lambda d: d.slug)
        )

    def test_interactants_fetching(self):
        self.assertEqual(
            self.drug_b.all_interactants.count(),
            self.drug_b.interactions.count(),
        )

    def test_interactants_fetching_django_not_fixed(self):
        self.assertNotEqual(
            self.drug_b.all_interactants.count(),
            self.drug_b.interactants.count(),
            "The Django framework now seems to support recursive M2M "
            "fields better. The Drug.all_interactants tweak is maybe "
            "not needed anymore."
        )

    def test_other_interactant(self):
        self.assertIs(
            self.inter_a_b.other_interactant(self.drug_a),
            self.drug_b
        )

    def test_other_interactant_invalid(self):
        with self.assertRaises(ValueError):
            self.inter_a_b.other_interactant(self.drug_c)

    def test_interaction_names(self):
        self.assertEqual(
            self.inter_a_b.names, ["First name", "Second name"]
        )

    def test_interaction_names_blank(self):
        self.assertEqual(self.inter_b_c.names, [])


class ComboViewTestCase(TestCase):
    drug_a = Drug(name="DrugA", slug='a')
    drug_b = Drug(name="DrugB", slug='b')

    def setUp(self):
        self.drug_a.save()
        self.drug_b.save()

    def test_return_code(self):
        for url, code in (
            ('/combo/', 404),
            ('/combo/a/', 400),
            ('/combo/x/', 400),
            ('/combo/a+x/', 404),
            ('/combo/a+b+x/', 404),
            ('/combo/x+y/', 404),
            ('/combo/a+b/', 200),
        ):
            with self.subTest(url=url):
                self.assertEqual(
                    self.client.get(url, follow=True).status_code,
                    code
                )


class ContribFormTestCase(TestCase):
    data = {
        'message_field': "Hello!",
        'email_field': "me@example.com"
    }

    def test_no_interaction(self):
        form = ContribForm(data={
            **self.data,
            'combination_name_field': "A + B"
        })
        self.assertTrue(form.is_valid())

    def test_no_interaction_no_name(self):
        form = ContribForm(data=self.data)
        self.assertFalse(form.is_valid())
