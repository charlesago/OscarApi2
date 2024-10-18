from django.contrib import admin

from movie.models import CustomUser


# Register your models here.

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'enabled')
    list_filter = ('enabled',)
    search_fields = ('username', 'email')
    actions = ['toggle_enabled']

    def toggle_enabled(self, request, queryset):
        for user in queryset:
            user.enabled = not user.enabled
            user.save()
        self.message_user(request, "Les utilisateurs sélectionnés ont été mis à jour.")

    toggle_enabled.short_description = "Activer/Désactiver les utilisateurs sélectionnés"

admin.site.register(CustomUser, CustomUserAdmin)