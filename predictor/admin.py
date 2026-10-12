from django.contrib import admin

from .models import PredictionRecord


@admin.register(PredictionRecord)
class PredictionRecordAdmin(admin.ModelAdmin):
    list_display = ("student_name", "predicted_score", "category", "risk_level", "created_at")
    list_filter = ("category", "risk_level", "sex", "created_at")
    search_fields = ("student_name",)
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)
