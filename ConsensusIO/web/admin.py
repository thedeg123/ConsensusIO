from django.contrib import admin

from django.contrib import admin
from .models import Company, Article
# Register your models here.

class  ArticleInline(admin.TabularInline):
    model = Article
    extra=1

class CompanyAdmin(admin.ModelAdmin):
    fieldsets = [
        ('General', {
            'fields': ['name', 'ticker', 'logo_img', 'common_name', 'last_blank_day']
        })
    ]
    inlines = [ArticleInline]
    search_fields = ['name']

admin.site.register(Company, CompanyAdmin)