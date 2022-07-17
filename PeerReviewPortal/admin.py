from django.contrib import admin
import PeerReviewPortal.models as _

admin.site.register(_.JournalSubmission)
admin.site.register(_.JournalSubmissionEditorialTeam)
admin.site.register(_.EditorReport)
admin.site.register(_.ReviewerReport)
admin.site.register(_.ReviewerReportSection)

# Register your models here.
