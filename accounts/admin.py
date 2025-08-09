from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import StaffProfile


class StaffProfileInline(admin.StackedInline):
    """Inline admin for StaffProfile"""
    model = StaffProfile
    can_delete = False
    verbose_name_plural = 'Staff Profile'
    fk_name = 'user'


class CustomUserAdmin(UserAdmin):
    """Custom User admin with StaffProfile inline"""
    inlines = (StaffProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'get_role')
    list_filter = ('is_staff', 'is_superuser', 'staff_profile__role', 'staff_profile__is_active_staff')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    
    def get_role(self, obj):
        try:
            return obj.staff_profile.get_role_display()
        except StaffProfile.DoesNotExist:
            return 'No Role'
    get_role.short_description = 'Role'
    
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    """Admin for StaffProfile"""
    list_display = ('user', 'role', 'department', 'phone_number', 'is_active_staff', 'created_at')
    list_filter = ('role', 'department', 'is_active_staff', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email', 'department')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'role', 'department')
        }),
        ('Contact Information', {
            'fields': ('phone_number',)
        }),
        ('Status', {
            'fields': ('is_active_staff',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
