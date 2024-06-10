from django.contrib import admin
from .models import *
from import_export.admin import ImportExportMixin

class FAQModelAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ['id', 'question', 'answer', 'created_at']
    list_filter = ['created_at']
    search_fields = ['question', 'answer']

admin.site.register(FAQ, FAQModelAdmin)

class KGModelAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ['id', 'purpose', 'title', 'json', 'owner']

admin.site.register(KnowledgeGraph, KGModelAdmin)

class HistoryModelAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ['id', 'username', 'question', 'answer', 'created_at']

admin.site.register(History, HistoryModelAdmin)

class RuleModelAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ['id', 'rule', 'created_at']

admin.site.register(Rule, RuleModelAdmin)
