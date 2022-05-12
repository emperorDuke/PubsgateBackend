from django.contrib import admin
import Contents.models as _

# Register your models here.


admin.site.register(_.ManuscriptAuthor)
admin.site.register(_.ManuscriptSection)
admin.site.register(_.ManuscriptFile)
admin.site.register(_.ManuscriptKeywordTag)
admin.site.register(_.ManuscriptReference)
admin.site.register(_.Manuscript)
