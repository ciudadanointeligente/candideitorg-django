from django.contrib import admin
from candideitorg.models import Election as CanElection, Candidate, Category, Question, Answer, InformationSource

class CandidateInline(admin.TabularInline):
    model = Candidate
    extra = 0

class CanElectionAdmin(admin.ModelAdmin):
    inlines = [
        CandidateInline
    ]
    actions = ['update_election_from_candideit']
    def update_election_from_candideit(self, request, queryset):
        for election in queryset:
            election.update_answers()
    update_election_from_candideit.short_description = "Actualizar elecciones desde candideitorg"
    
admin.site.register(CanElection, CanElectionAdmin)



class CategoryAdmin(admin.ModelAdmin):
    pass    

admin.site.register(Category, CategoryAdmin)


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0

class InformationSourceAdmin(admin.TabularInline):
    model = InformationSource
    extra = 0

class QuestionAdmin(admin.ModelAdmin):
    inlines = [
        AnswerInline,
        InformationSourceAdmin
    ]

admin.site.register(Question, QuestionAdmin)
