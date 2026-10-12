from django.db import models


class PredictionRecord(models.Model):
    """One saved prediction: student info + inputs + model output."""
    # student information and input features
    student_name = models.CharField(max_length=100)
    age = models.PositiveSmallIntegerField()
    sex = models.CharField(max_length=1)
    studytime = models.PositiveSmallIntegerField()
    failures = models.PositiveSmallIntegerField()
    absences = models.PositiveSmallIntegerField()
    g1 = models.PositiveSmallIntegerField()
    g2 = models.PositiveSmallIntegerField()
    schoolsup = models.CharField(max_length=3)
    famsup = models.CharField(max_length=3)
    activities = models.CharField(max_length=3)
    internet = models.CharField(max_length=3)
    freetime = models.PositiveSmallIntegerField()
    goout = models.PositiveSmallIntegerField()
    # model output
    predicted_score = models.FloatField()                  # percentage
    category = models.CharField(max_length=30)
    risk_level = models.CharField(max_length=10)
    pass_probability = models.FloatField(null=True, blank=True)
    explanation = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student_name} - {self.predicted_score}% ({self.category})"

    @property
    def inputs(self):
        """Dict with the field names used by rules.py / ml_model.py."""
        return {f: getattr(self, f) for f in (
            "age", "sex", "studytime", "failures", "absences", "g1", "g2", "schoolsup",
            "famsup", "activities", "internet", "freetime", "goout")}
