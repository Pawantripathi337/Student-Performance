from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Avg
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from ml.preprocessing import DatasetError

from . import analytics, ml_model, rules
from .forms import PredictionForm
from .models import PredictionRecord

SORTS = {"newest": "-created_at", "oldest": "created_at", "name": "student_name",
         "score_high": "-predicted_score", "score_low": "predicted_score"}


def home(request):
    return render(request, "home.html", {
        "stats": analytics.home_stats(),
        "records_count": PredictionRecord.objects.count()})


def predict_view(request):
    if request.method == "POST":
        form = PredictionForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            inputs = {k: v for k, v in data.items() if k != "student_name"}
            try:
                score, pass_prob = ml_model.predict(inputs)
            except ml_model.ModelUnavailable as exc:
                messages.error(request, str(exc))
                return render(request, "predict.html", {"form": form})
            category = rules.categorize(score)
            risk, _ = rules.assess_risk(score, inputs)
            record = PredictionRecord.objects.create(
                student_name=data["student_name"], **inputs,
                predicted_score=score, category=category, risk_level=risk,
                pass_probability=pass_prob,
                explanation=rules.explanation(score, category, inputs))
            return redirect("result", pk=record.pk)
        messages.error(request, "Please correct the highlighted fields and try again.")
    else:
        form = PredictionForm(initial={"age": 17, "studytime": 2, "failures": 0,
                                       "absences": 4, "g1": 10, "g2": 10,
                                       "freetime": 3, "goout": 3, "sex": "F",
                                       "schoolsup": "no", "famsup": "yes",
                                       "activities": "no", "internet": "yes"})
    return render(request, "predict.html", {"form": form})


def _detail_context(record):
    inputs = record.inputs
    _, reasons = rules.assess_risk(record.predicted_score, inputs)
    charts = {"gauge": {"data": [{
        "type": "indicator", "mode": "gauge+number", "value": record.predicted_score,
        "number": {"suffix": "%"},
        "gauge": {"axis": {"range": [0, 100]}, "bar": {"color": "#4f46e5"},
                  "steps": [{"range": [0, 40], "color": "#fecaca"},
                            {"range": [40, 60], "color": "#fde68a"},
                            {"range": [60, 75], "color": "#bfdbfe"},
                            {"range": [75, 100], "color": "#bbf7d0"}]}}],
        "layout": analytics.base_layout("Predicted final score", height=280)}}
    try:
        avg = analytics.class_average()
        charts["compare"] = {"data": [
            {"type": "bar", "name": "This student", "marker": {"color": "#4f46e5"},
             "x": ["Period 1", "Period 2", "Predicted final"],
             "y": [record.g1 * 5, record.g2 * 5, record.predicted_score]},
            {"type": "bar", "name": "Dataset average", "marker": {"color": "#94a3b8"},
             "x": ["Period 1", "Period 2", "Predicted final"],
             "y": [avg["g1"], avg["g2"], avg["g3"]]}],
            "layout": analytics.base_layout("Student vs dataset average (%)", barmode="group",
                                            yaxis={"range": [0, 100]})}
    except DatasetError:
        pass                                  # the comparison chart is optional
    return {"record": record, "reasons": reasons, "charts": charts,
            "tips": rules.recommendations(record.predicted_score, inputs),
            "study_label": rules.STUDY_BANDS.get(record.studytime, "")}


def result(request, pk):
    return render(request, "result.html", _detail_context(get_object_or_404(PredictionRecord, pk=pk)))


def student_detail(request, pk):
    return render(request, "student_detail.html",
                  _detail_context(get_object_or_404(PredictionRecord, pk=pk)))


@require_POST
def student_delete(request, pk):
    record = get_object_or_404(PredictionRecord, pk=pk)
    record.delete()
    messages.success(request, "Record deleted.")
    return redirect("students")


def dashboard(request):
    ctx = {"records_count": PredictionRecord.objects.count(),
           "records_avg": PredictionRecord.objects.aggregate(a=Avg("predicted_score"))["a"]}
    try:
        stats, charts, metrics = analytics.build_dashboard()
        ctx.update(stats=stats, charts=charts, metrics=metrics)
    except DatasetError as exc:
        messages.error(request, f"Analytics unavailable: {exc}")
    return render(request, "dashboard.html", ctx)


def students(request):
    qs = PredictionRecord.objects.all()
    q = request.GET.get("q", "").strip()
    category = request.GET.get("category", "")
    risk = request.GET.get("risk", "")
    sort = request.GET.get("sort", "newest")
    if q:
        qs = qs.filter(student_name__icontains=q)
    if category in rules.CATEGORY_ORDER:
        qs = qs.filter(category=category)
    if risk in rules.RISK_ORDER:
        qs = qs.filter(risk_level=risk)
    qs = qs.order_by(SORTS.get(sort, SORTS["newest"]))
    page = Paginator(qs, 10).get_page(request.GET.get("page"))
    params = request.GET.copy()
    params.pop("page", None)
    return render(request, "students.html", {
        "page": page, "q": q, "category": category, "risk": risk, "sort": sort,
        "categories": rules.CATEGORY_ORDER, "risks": rules.RISK_ORDER,
        "querystring": params.urlencode()})
