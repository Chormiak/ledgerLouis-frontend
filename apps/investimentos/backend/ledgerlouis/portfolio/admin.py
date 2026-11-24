from django.contrib import admin

from .models import Alert, Holding, InvestorProfile, Proposal, ProposalItem, Thesis


class ItemInline(admin.TabularInline):
    model = ProposalItem
    extra = 0


@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    list_display = ["period", "created_at", "status"]
    inlines = [ItemInline]


admin.site.register([InvestorProfile, Holding, Thesis, Alert])
