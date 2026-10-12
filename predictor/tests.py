"""Run with:  python manage.py test"""
from django.test import TestCase
from django.urls import reverse

from .models import PredictionRecord
from . import rules

VALID = {"student_name": "Test Student", "age": 17, "sex": "F", "studytime": 2,
         "failures": 0, "absences": 3, "g1": 12, "g2": 13, "schoolsup": "no",
         "famsup": "yes", "activities": "yes", "internet": "yes", "freetime": 3,
         "goout": 2}


class RulesTests(TestCase):
    def test_category_boundaries(self):
        self.assertEqual(rules.categorize(90), "Excellent")
        self.assertEqual(rules.categorize(75), "Good")
        self.assertEqual(rules.categorize(60), "Average")
        self.assertEqual(rules.categorize(40), "Needs Improvement")
        self.assertEqual(rules.categorize(39.9), "Poor")


class ViewTests(TestCase):
    def test_pages_load(self):
        for name in ("home", "predict", "dashboard", "students"):
            self.assertEqual(self.client.get(reverse(name)).status_code, 200, name)

    def test_valid_prediction_is_saved(self):
        response = self.client.post(reverse("predict"), VALID)
        self.assertEqual(PredictionRecord.objects.count(), 1)
        record = PredictionRecord.objects.first()
        self.assertRedirects(response, reverse("result", args=[record.pk]))
        self.assertEqual(self.client.get(reverse("student_detail", args=[record.pk])).status_code, 200)

    def test_invalid_inputs_are_rejected(self):
        bad_cases = [{"absences": 500}, {"absences": -1}, {"g1": 25}, {"g2": ""},
                     {"age": "abc"}, {"student_name": ""}]
        for change in bad_cases:
            response = self.client.post(reverse("predict"), {**VALID, **change})
            self.assertEqual(response.status_code, 200, change)
        self.assertEqual(PredictionRecord.objects.count(), 0)

    def test_search_and_filter(self):
        self.client.post(reverse("predict"), VALID)
        self.assertContains(self.client.get(reverse("students"), {"q": "Test"}), "Test Student")
        self.assertNotContains(self.client.get(reverse("students"), {"q": "Nobody"}), "Test Student")

    def test_unknown_record_returns_404(self):
        self.assertEqual(self.client.get(reverse("result", args=[9999])).status_code, 404)
