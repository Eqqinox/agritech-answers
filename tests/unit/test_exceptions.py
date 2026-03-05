"""Tests unitaires pour les exceptions métier."""

from src.api.exceptions import (
    AgritechException,
    CultureInconnue,
    ModeleNonCharge,
    PaysInconnu,
    ValeurNegative,
)


class TestCultureInconnue:
    def test_message(self):
        exc = CultureInconnue("Culture inconnue : Fraises")
        assert "Fraises" in exc.message

    def test_heritage(self):
        exc = CultureInconnue("test")
        assert isinstance(exc, AgritechException)
        assert isinstance(exc, Exception)


class TestPaysInconnu:
    def test_message(self):
        exc = PaysInconnu("Pays inconnu : Narnia")
        assert "Narnia" in exc.message

    def test_heritage(self):
        exc = PaysInconnu("test")
        assert isinstance(exc, AgritechException)


class TestValeurNegative:
    def test_message(self):
        exc = ValeurNegative("pesticides_tonnes ne peut pas être négatif.")
        assert "pesticides_tonnes" in exc.message

    def test_heritage(self):
        exc = ValeurNegative("test")
        assert isinstance(exc, AgritechException)


class TestModeleNonCharge:
    def test_instanciation(self):
        exc = ModeleNonCharge("Le pipeline n'est pas chargé.")
        assert isinstance(exc, Exception)

    def test_heritage(self):
        exc = ModeleNonCharge("test")
        assert isinstance(exc, AgritechException)
