from django.contrib import admin

# Register your models here.

from .models import Baby, GuardianMapping

@admin.register(Baby)
class BabyAdmin(admin.ModelAdmin):
    list_display = ["id"]
    readonly_fields = ["id", "name"]

@admin.register(GuardianMapping)
class GuardianMappingAdmin(admin.ModelAdmin):
    list_display = ["id", "baby", "guardian"]
    list_select_related = ["baby", "guardian"]
    readonly_fields = ["id"]