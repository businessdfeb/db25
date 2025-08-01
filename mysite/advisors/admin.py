from django.contrib import admin
from .models import Advisor, AdvisorRole, AdvisorToRole

admin.site.register(Advisor)
admin.site.register(AdvisorRole)
admin.site.register(AdvisorToRole)