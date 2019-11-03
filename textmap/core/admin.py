from django.contrib import admin

from core import models


@admin.register(models.Text)
class AdminText(admin.ModelAdmin):
    def save_model(self, request, obj: models.Text, form, change):
        obj.owner = request.user
        super().save_model(request, obj, form, change)


@admin.register(models.Part)
class AdminPart(admin.ModelAdmin):
    pass


@admin.register(models.Paragraph)
class AdminParagraph(admin.ModelAdmin):
    pass


@admin.register(models.Sentence)
class AdminSentence(admin.ModelAdmin):
    pass
