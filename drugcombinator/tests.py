from django.test import TestCase
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
        