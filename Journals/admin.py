from django.contrib import admin
import Journals.models as _

# Register your models here.

admin.site.register(_.Journal)
admin.site.register(_.JournalBanner)
admin.site.register(_.JournalDetail)
admin.site.register(_.JournalVolumeIssue)
admin.site.register(_.JournalSubjectArea)
admin.site.register(_.JournalViewLog)
admin.site.register(_.JournalVolume)
admin.site.register(_.JournalPermission)
