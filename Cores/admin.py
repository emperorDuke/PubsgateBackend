from django.contrib import admin

from Cores.models import (
    SubjectDiscipline,
    TermOfService,
    ArticleType,
    ArticleTypeSection,
)

# Register your models here.
admin.site.register(SubjectDiscipline)
admin.site.register(TermOfService)
admin.site.register(ArticleTypeSection)
admin.site.register(ArticleType)
