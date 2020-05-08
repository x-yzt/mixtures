from django.test import TestCase
from django.db.utils import IntegrityError
from drugcombinator.utils import normalize
from drugcombinator.models import Drug, Interaction


class UtilsTestCase(TestCase):

    def test_normalize(self):

        self.assertEqual(
            normalize("Je bois du café. Ça vous va ?"),
            "je bois du cafe. ca vous va ?"
        )


    def test_normalize_noop(self):

        data = "c'est vraiment pas de bol !"
        self.assertEqual(normalize(data), data)


class InteractionModelTestCase(TestCase):

    drug_a = Drug(name="DrugA", slug='drug-a')
    drug_b = Drug(name="DrugB", slug='drug-b')


    def setUp(self):

        self.drug_a.save()
        self.drug_b.save()
        

    def test_interactants_inequals(self):

        with self.assertRaises(IntegrityError):
            Interaction(
                from_drug=self.drug_a,
                to_drug=self.drug_a
            ).save()
        

    def test_interactants_unique_together(self):

        with self.assertRaises(IntegrityError):
            Interaction(
                from_drug=self.drug_a,
                to_drug=self.drug_b
            ).save()
            Interaction(
                from_drug=self.drug_b,
                to_drug=self.drug_a
            ).save()
        

    def test_interactants_ordering(self):

        inter = Interaction(
            from_drug=self.drug_b,
            to_drug=self.drug_a
        )
        inter.save()
        self.assertSequenceEqual(
            inter.interactants,
            sorted(inter.interactants, key=lambda d: d.name)
        )
