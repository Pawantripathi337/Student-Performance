from django import forms

YES_NO = [("yes", "Yes"), ("no", "No")]
STUDY_CHOICES = [(1, "Under 2 hours / week"), (2, "2 to 5 hours / week"),
                 (3, "5 to 10 hours / week"), (4, "Over 10 hours / week")]
LEVEL_CHOICES = [(i, str(i)) for i in range(1, 6)]
NUM = {"class": "form-control"}
SEL = {"class": "form-select"}


def _int(label, lo, hi, help_text="", **kw):
    return forms.IntegerField(
        label=label, min_value=lo, max_value=hi, help_text=help_text,
        widget=forms.NumberInput(attrs={**NUM, "min": lo, "max": hi}),
        error_messages={"required": f"{label} is required.",
                        "invalid": f"{label} must be a whole number.",
                        "min_value": f"{label} cannot be below {lo}.",
                        "max_value": f"{label} cannot be above {hi}."}, **kw)


class PredictionForm(forms.Form):
    student_name = forms.CharField(
        label="Student name", max_length=100,
        widget=forms.TextInput(attrs={**NUM, "placeholder": "e.g. Riya Sharma"}),
        error_messages={"required": "Student name is required."})
    age = _int("Age", 15, 22, "15 to 22 years")
    sex = forms.ChoiceField(label="Gender", choices=[("F", "Female"), ("M", "Male")],
                            widget=forms.Select(attrs=SEL))
    studytime = forms.TypedChoiceField(label="Weekly study time", choices=STUDY_CHOICES,
                                       coerce=int, widget=forms.Select(attrs=SEL))
    failures = _int("Previous failures", 0, 3, "Number of past class failures (0 to 3)")
    absences = _int("Absences", 0, 93, "Classes missed this term")
    g1 = _int("Period 1 marks", 0, 20, "Out of 20")
    g2 = _int("Period 2 marks", 0, 20, "Out of 20")
    schoolsup = forms.ChoiceField(label="Extra school support", choices=YES_NO,
                                  widget=forms.Select(attrs=SEL))
    famsup = forms.ChoiceField(label="Family academic support", choices=YES_NO,
                               widget=forms.Select(attrs=SEL))
    activities = forms.ChoiceField(label="Extracurricular activities", choices=YES_NO,
                                   widget=forms.Select(attrs=SEL))
    internet = forms.ChoiceField(label="Internet at home", choices=YES_NO,
                                 widget=forms.Select(attrs=SEL))
    freetime = forms.TypedChoiceField(label="Free time after school (1-5)",
                                      choices=LEVEL_CHOICES, coerce=int,
                                      widget=forms.Select(attrs=SEL))
    goout = forms.TypedChoiceField(label="Going out with friends (1-5)",
                                   choices=LEVEL_CHOICES, coerce=int,
                                   widget=forms.Select(attrs=SEL))

    def clean_student_name(self):
        name = self.cleaned_data["student_name"].strip()
        if not any(ch.isalpha() for ch in name):
            raise forms.ValidationError("Please enter a valid name (letters required).")
        return name
