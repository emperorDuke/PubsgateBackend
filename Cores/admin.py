from django.contrib import admin

from Cores.models import (
    Discipline,
    TermOfService,
    ArticleType,
    ArticleTypeSection,
)

# Register your models here.
admin.site.register(Discipline)
admin.site.register(TermOfService)
admin.site.register(ArticleTypeSection)
admin.site.register(ArticleType)
