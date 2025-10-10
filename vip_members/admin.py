from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils import timezone
from django.contrib import messages
from .models import VIPStaff, VIPMember, VIPActivity, VIPBenefit, VIPNotification, VIPApplication


@admin.register(VIPStaff)
class VIPStaffAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'staff_id', 'department', 'assigned_members_count', 'is_active', 'created_at']
    list_filter = ['department', 'is_active', 'created_at']
    search_fields = ['full_name', 'staff_id', 'user__username', 'email']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Staff Information', {
            'fields': ('user', 'staff_id', 'full_name', 'phone', 'email', 'department')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def assigned_members_count(self, obj):
        count = obj.assigned_members.count()
        if count > 0:
            url = reverse('admin:vip_members_vipmember_changelist') + f'?assigned_staff__id__exact={obj.id}'
            return format_html('<a href="{}">{} members</a>', url, count)
        return '0 members'
    assigned_members_count.short_description = 'Assigned Members'


@admin.register(VIPMember)
class VIPMemberAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'member_id', 'membership_tier', 'status', 'assigned_staff', 
                   'total_investments', 'membership_duration', 'created_at']
    list_filter = ['membership_tier', 'status', 'assigned_staff', 'priority_support', 
                  'dedicated_account_manager', 'created_at']
    search_fields = ['customer__username', 'customer__first_name', 'customer__last_name', 
                    'member_id', 'phone']
    readonly_fields = ['created_at', 'updated_at', 'membership_duration_days']
    raw_id_fields = ['customer', 'assigned_staff']
    
    fieldsets = (
        ('Customer Information', {
            'fields': ('customer', 'member_id', 'phone', 'preferred_contact_method')
        }),
        ('Staff Assignment', {
            'fields': ('assigned_staff',)
        }),
        ('Membership Details', {
            'fields': ('membership_tier', 'status', 'membership_start_date', 'last_contact_date')
        }),
        ('VIP Benefits', {
            'fields': ('priority_support', 'dedicated_account_manager', 
                      'exclusive_investment_opportunities', 'faster_processing'),
            'classes': ('collapse',)
        }),
        ('Financial Information', {
            'fields': ('total_investments', 'monthly_income', 'net_worth'),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'membership_duration_days'),
            'classes': ('collapse',)
        }),
    )
    
    def membership_duration(self, obj):
        days = obj.membership_duration_days
        if days >= 365:
            years = days // 365
            return f"{years} year{'s' if years > 1 else ''}"
        elif days >= 30:
            months = days // 30
            return f"{months} month{'s' if months > 1 else ''}"
        else:
            return f"{days} day{'s' if days > 1 else ''}"
    membership_duration.short_description = 'Membership Duration'
    
    actions = ['assign_bronze_tier', 'assign_silver_tier', 'assign_gold_tier', 'assign_platinum_tier', 'assign_diamond_tier']
    
    def assign_bronze_tier(self, request, queryset):
        queryset.update(membership_tier='bronze')
        self.message_user(request, f"Updated {queryset.count()} members to Bronze VIP tier.")
    assign_bronze_tier.short_description = "Assign Bronze VIP tier to selected members"
    
    def assign_silver_tier(self, request, queryset):
        queryset.update(membership_tier='silver')
        self.message_user(request, f"Updated {queryset.count()} members to Silver VIP tier.")
    assign_silver_tier.short_description = "Assign Silver VIP tier to selected members"
    
    def assign_gold_tier(self, request, queryset):
        queryset.update(membership_tier='gold')
        self.message_user(request, f"Updated {queryset.count()} members to Gold VIP tier.")
    assign_gold_tier.short_description = "Assign Gold VIP tier to selected members"
    
    def assign_platinum_tier(self, request, queryset):
        queryset.update(membership_tier='platinum')
        self.message_user(request, f"Updated {queryset.count()} members to Platinum VIP tier.")
    assign_platinum_tier.short_description = "Assign Platinum VIP tier to selected members"
    
    def assign_diamond_tier(self, request, queryset):
        queryset.update(membership_tier='diamond')
        self.message_user(request, f"Updated {queryset.count()} members to Diamond VIP tier.")
    assign_diamond_tier.short_description = "Assign Diamond VIP tier to selected members"


@admin.register(VIPActivity)
class VIPActivityAdmin(admin.ModelAdmin):
    list_display = ['member_name', 'activity_type', 'title', 'staff_member', 'timestamp', 'is_important']
    list_filter = ['activity_type', 'is_important', 'timestamp', 'staff_member']
    search_fields = ['member__customer__username', 'member__customer__first_name', 
                    'member__customer__last_name', 'title', 'description']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Activity Information', {
            'fields': ('member', 'activity_type', 'title', 'description', 'staff_member', 'is_important')
        }),
        ('Timestamp', {
            'fields': ('timestamp',)
        }),
    )
    
    def member_name(self, obj):
        return obj.member.full_name
    member_name.short_description = 'Member'


@admin.register(VIPBenefit)
class VIPBenefitAdmin(admin.ModelAdmin):
    list_display = ['name', 'applicable_tiers_display', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']
    
    def applicable_tiers_display(self, obj):
        tiers = obj.applicable_tiers
        tier_colors = {
            'bronze': '#CD7F32',
            'silver': '#C0C0C0', 
            'gold': '#FFD700',
            'platinum': '#E5E4E2',
            'diamond': '#B9F2FF'
        }
        
        colored_tiers = []
        for tier in tiers:
            color = tier_colors.get(tier, '#666666')
            colored_tiers.append(
                f'<span style="background-color: {color}; color: {"black" if tier in ["silver", "gold", "platinum"] else "white"}; '
                f'padding: 2px 6px; border-radius: 3px; font-size: 11px; font-weight: bold;">{tier.upper()}</span>'
            )
        return mark_safe(' '.join(colored_tiers))
    applicable_tiers_display.short_description = 'Applicable Tiers'


@admin.register(VIPApplication)
class VIPApplicationAdmin(admin.ModelAdmin):
    list_display = ['applicant_name', 'requested_tier', 'status', 'assigned_reviewer', 'submitted_at', 'reviewed_at']
    list_filter = ['status', 'requested_tier', 'assigned_reviewer', 'submitted_at', 'reviewed_at']
    search_fields = ['customer__username', 'customer__first_name', 'customer__last_name', 
                    'reason_for_application', 'investment_experience']
    readonly_fields = ['submitted_at', 'reviewed_at', 'created_at', 'updated_at']
    raw_id_fields = ['customer', 'assigned_reviewer']
    date_hierarchy = 'submitted_at'
    
    fieldsets = (
        ('Applicant Information', {
            'fields': ('customer', 'requested_tier', 'status', 'phone', 'preferred_contact_method')
        }),
        ('Application Details', {
            'fields': ('reason_for_application', 'investment_experience', 'expected_monthly_investment', 'net_worth_range')
        }),
        ('Admin Review', {
            'fields': ('assigned_reviewer', 'admin_notes', 'rejection_reason')
        }),
        ('Timestamps', {
            'fields': ('submitted_at', 'reviewed_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_applications', 'reject_applications', 'assign_to_reviewer', 'mark_under_review']
    
    def approve_applications(self, request, queryset):
        approved_count = 0
        for application in queryset.filter(status__in=['pending', 'under_review']):
            # Create VIP member if approved
            vip_member, created = VIPMember.objects.get_or_create(
                customer=application.customer,
                defaults={
                    'member_id': f'VIP{application.customer.id:06d}',
                    'assigned_staff': application.assigned_reviewer,
                    'membership_tier': application.requested_tier,
                    'status': 'active',
                    'phone': application.phone,
                    'preferred_contact_method': application.preferred_contact_method,
                    'total_investments': application.expected_monthly_investment,
                    'monthly_income': application.expected_monthly_investment,
                    'net_worth': application.expected_monthly_investment * 12,  # Estimate
                    'priority_support': True,
                    'dedicated_account_manager': application.requested_tier in ['silver', 'gold', 'platinum', 'diamond'],
                    'exclusive_investment_opportunities': application.requested_tier in ['gold', 'platinum', 'diamond'],
                    'faster_processing': application.requested_tier in ['silver', 'gold', 'platinum', 'diamond'],
                    'notes': f'Approved from application - {application.reason_for_application[:100]}'
                }
            )
            
            # Update application status
            application.status = 'approved'
            application.reviewed_at = timezone.now()
            application.save()
            
            # Create welcome notification
            VIPNotification.objects.create(
                member=vip_member,
                title='VIP Membership Approved!',
                message=f'Congratulations! Your {application.get_requested_tier_display()} membership has been approved. Welcome to VIP status!',
                notification_type='success'
            )
            
            approved_count += 1
        
        if approved_count > 0:
            self.message_user(request, f"Successfully approved {approved_count} VIP applications.")
        else:
            self.message_user(request, "No eligible applications found for approval.", level=messages.WARNING)
    approve_applications.short_description = "Approve selected VIP applications"
    
    def reject_applications(self, request, queryset):
        rejected_count = queryset.filter(status__in=['pending', 'under_review']).update(
            status='rejected',
            reviewed_at=timezone.now()
        )
        if rejected_count > 0:
            self.message_user(request, f"Rejected {rejected_count} VIP applications.")
        else:
            self.message_user(request, "No eligible applications found for rejection.", level=messages.WARNING)
    reject_applications.short_description = "Reject selected VIP applications"
    
    def assign_to_reviewer(self, request, queryset):
        # This would typically open a form to select reviewer
        self.message_user(request, "Please use the 'Assigned Reviewer' field to assign applications to staff members.")
    assign_to_reviewer.short_description = "Assign applications to reviewer"
    
    def mark_under_review(self, request, queryset):
        updated_count = queryset.filter(status='pending').update(status='under_review')
        if updated_count > 0:
            self.message_user(request, f"Marked {updated_count} applications as under review.")
        else:
            self.message_user(request, "No pending applications found.", level=messages.WARNING)
    mark_under_review.short_description = "Mark as under review"
    
    def save_model(self, request, obj, form, change):
        if change and obj.status == 'approved' and not obj.reviewed_at:
            obj.reviewed_at = timezone.now()
        super().save_model(request, obj, form, change)


@admin.register(VIPNotification)
class VIPNotificationAdmin(admin.ModelAdmin):
    list_display = ['member_name', 'title', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['member__customer__username', 'member__customer__first_name', 
                    'member__customer__last_name', 'title', 'message']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Notification Information', {
            'fields': ('member', 'title', 'message', 'notification_type', 'is_read', 'expires_at')
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        }),
    )
    
    def member_name(self, obj):
        return obj.member.full_name
    member_name.short_description = 'Member'
    
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
        self.message_user(request, f"Marked {queryset.count()} notifications as read.")
    mark_as_read.short_description = "Mark selected notifications as read"
    
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
        self.message_user(request, f"Marked {queryset.count()} notifications as unread.")
    mark_as_unread.short_description = "Mark selected notifications as unread"


# Customize admin site headers
admin.site.site_header = "Meridian Asset Logistics - VIP Management"
admin.site.site_title = "MAL VIP Admin"
admin.site.index_title = "VIP Members Administration"
