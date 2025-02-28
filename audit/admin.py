from django.contrib import admin
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Patient, District, FieldAudit, Coordinator, ActionLog

# First unregister models from default admin
admin.site.unregister(Group)

class PatientInline(admin.TabularInline):
    model = Patient
    extra = 0
    fields = ('patient_name', 'money_collection', 'missing_records', 'admission_date')
    readonly_fields = ('admission_date',)
    can_delete = False
    show_change_link = True
    classes = ('collapse',)

class CoordinatorAdmin(admin.ModelAdmin):
    list_display = ('name', 'employee_id', 'district', 'contact_number', 'email', 'is_active')
    list_filter = ('district', 'is_active', 'date_joined')
    search_fields = ('name', 'employee_id', 'email')
    ordering = ('name',)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

    def generate_unique_username(self, base_username):
        """Generate a unique username by adding a number suffix if needed."""
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}_{counter}"
            counter += 1
        return username

    def clean_email(self, email):
        """Ensure email is unique among users."""
        if User.objects.filter(email=email).exists():
            raise ValidationError('A user with this email already exists.')
        return email

    def save_model(self, request, obj, form, change):
        try:
            if not change:  # Creating new coordinator
                with transaction.atomic():
                    # Clean email
                    self.clean_email(obj.email)
                    
                    # Generate unique username
                    base_username = obj.employee_id.lower().replace(' ', '_')
                    username = self.generate_unique_username(base_username)
                    
                    # Create user account
                    password = User.objects.make_random_password()
                    user = User.objects.create_user(
                        username=username,
                        email=obj.email,
                        password=password,
                        first_name=obj.name.split()[0],
                        last_name=' '.join(obj.name.split()[1:]) if len(obj.name.split()) > 1 else ''
                    )
                    
                    # Set coordinator permissions
                    coordinator_group, created = Group.objects.get_or_create(name='Coordinators')
                    if created:
                        from django.contrib.auth.models import Permission
                        from django.contrib.contenttypes.models import ContentType
                        
                        # Add basic permissions
                        content_types = ContentType.objects.get_for_models(Patient, FieldAudit, ActionLog)
                        permissions = []
                        for model, content_type in content_types.items():
                            permissions.extend(Permission.objects.filter(content_type=content_type, codename__startswith='view_'))
                        coordinator_group.permissions.set(permissions)
                    
                    user.groups.add(coordinator_group)
                    obj.user = user
                    
                    # Show password to admin
                    messages.success(request, 
                        f'Created user account for {obj.name}.\n'
                        f'Username: {username}\n'
                        f'Password: {password}\n'
                        'Please save these credentials and share them with the coordinator.'
                    )
            
            super().save_model(request, obj, form, change)
            
        except ValidationError as e:
            messages.error(request, str(e))
            return
        except Exception as e:
            messages.error(request, f'Error creating coordinator: {str(e)}')
            return

    def delete_model(self, request, obj):
        user = obj.user
        super().delete_model(request, obj)
        if user:
            user.delete()

class PatientAdmin(admin.ModelAdmin):
    list_display = ('patient_name', 'case_id', 'get_district', 'get_ehcp_name', 'package_name', 'package_code', 
                   'admission_date', 'discharge_date', 'missing_records', 'money_collection', 'total_oope')
    list_filter = ('audit__district', 'money_collection', 'missing_records', 'admission_date', 'discharge_date')
    search_fields = ('patient_name', 'case_id', 'mobile_number', 'package_name', 'package_code', 'audit__ehcp_name')
    date_hierarchy = 'admission_date'
    ordering = ('-admission_date',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('audit', 'case_id', 'patient_name', 'mobile_number', 'patient_photo')
        }),
        ('Dates', {
            'fields': ('admission_date', 'discharge_date')
        }),
        ('Package Details', {
            'fields': ('package_name', 'package_code')
        }),
        ('Documents', {
            'fields': ('case_file', 'discharge_summary', 'bills_documents'),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ('digital_signature',)
    
    actions = ['verify_records', 'check_money_status', 'mark_audit_complete']
    
    def get_district(self, obj):
        return obj.audit.district if obj.audit else None
    get_district.short_description = 'District'
    get_district.admin_order_field = 'audit__district'

    def get_ehcp_name(self, obj):
        return obj.audit.ehcp_name if obj.audit else None
    get_ehcp_name.short_description = 'EHCP Name'
    get_ehcp_name.admin_order_field = 'audit__ehcp_name'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        coordinator = Coordinator.objects.filter(user=request.user).first()
        if coordinator:
            return qs.filter(audit__district=coordinator.district)
        return qs.none()

    def verify_records(self, request, queryset):
        coordinator = Coordinator.objects.filter(user=request.user, is_active=True).first()
        if not coordinator:
            messages.error(request, "No active coordinator found.")
            return

        for patient in queryset:
            if patient.audit.district == coordinator.district:
                ActionLog.objects.create(
                    coordinator=coordinator,
                    action_type='RECORD_CHECK',
                    description=f'Records verified for patient {patient.patient_name}',
                    patient=patient,
                    district=patient.audit.district,
                    status='completed'
                )
                patient.missing_records = False
                patient.save()

        self.message_user(request, f"Successfully verified records for {queryset.count()} patients.")
    verify_records.short_description = "Verify patient records"

    def check_money_status(self, request, queryset):
        coordinator = Coordinator.objects.filter(user=request.user, is_active=True).first()
        if not coordinator:
            messages.error(request, "No active coordinator found.")
            return

        for patient in queryset:
            if patient.audit.district == coordinator.district:
                ActionLog.objects.create(
                    coordinator=coordinator,
                    action_type='MONEY_VERIFY',
                    description=f'Money status verified for patient {patient.patient_name}',
                    patient=patient,
                    district=patient.audit.district,
                    status='completed'
                )
                patient.money_collection = True
                patient.save()

        self.message_user(request, f"Successfully verified money status for {queryset.count()} patients.")
    check_money_status.short_description = "Verify money status"

    def mark_audit_complete(self, request, queryset):
        coordinator = Coordinator.objects.filter(user=request.user, is_active=True).first()
        if not coordinator:
            messages.error(request, "No active coordinator found.")
            return

        for patient in queryset:
            if patient.audit.district == coordinator.district:
                ActionLog.objects.create(
                    coordinator=coordinator,
                    action_type='AUDIT',
                    description=f'Audit completed for patient {patient.patient_name}',
                    patient=patient,
                    district=patient.audit.district,
                    status='completed'
                )

        self.message_user(request, f"Successfully marked audit complete for {queryset.count()} patients.")
    mark_audit_complete.short_description = "Mark audit as complete"

class FieldAuditAdmin(admin.ModelAdmin):
    list_display = ('ehcp_name', 'district', 'visit_date', 'total_patients', 'completed_patients', 'assigned_coordinator')
    list_filter = ('district', 'visit_date', 'status')
    date_hierarchy = 'visit_date'
    ordering = ('-visit_date',)
    inlines = [PatientInline]

    fieldsets = (
        ('Hospital Information', {
            'fields': (('district', 'hospital_id'), ('ehcp_name', 'ehcp_type')),
            'classes': ('wide',),
            'description': 'Basic details about the healthcare facility'
        }),
        ('Audit Personnel', {
            'fields': (('auditor_name', 'designation'),),
            'classes': ('wide',),
            'description': 'Information about the audit personnel'
        }),
        ('Visit Information', {
            'fields': (('visit_date', 'visit_time'), 'current_location', ('latitude', 'longitude')),
            'classes': ('wide',),
            'description': 'Details about the audit visit'
        }),
        ('Patient Statistics', {
            'fields': (('ekgp_patients', 'pmjay_patients', 'beneficiaries'),),
            'classes': ('wide',),
            'description': 'Statistical information about patients'
        }),
        ('Audit Findings', {
            'fields': (
                ('findings_type', 'audit_findings_value'),
                ('finding_type', 'abuse_type', 'oope_type')
            ),
            'classes': ('wide',),
            'description': 'Detailed findings from the audit'
        }),
        ('Healthcare Quality Assessment', {
            'fields': (
                ('hnqa_value', 'hnqa_type'),
                ('infrastructure_type', 'hr_type', 'services_type')
            ),
            'classes': ('wide',),
            'description': 'HNQA evaluation details'
        }),
        ('Status', {
            'fields': ('status',),
            'classes': ('wide',),
            'description': 'Current status of the audit'
        })
    )
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:
            form.base_fields['current_location'].initial = obj.current_location
            form.base_fields['current_location'].required = True
        return form

    def save_model(self, request, obj, form, change):
        if not obj.current_location:
            obj.current_location = obj.ehcp_name
        if not change:  # New audit
            messages.info(request, 'Creating new audit record...')
        else:  # Editing existing audit
            messages.info(request, 'Updating audit record...')
        try:
            super().save_model(request, obj, form, change)
            messages.success(request, 'Audit record saved successfully.')
        except Exception as e:
            messages.error(request, f'Error saving audit record: {str(e)}')

    def save_related(self, request, form, formsets, change):
        try:
            super().save_related(request, form, formsets, change)
            obj = form.instance
            if not obj.current_location:
                obj.current_location = obj.ehcp_name
                obj.save()
        except Exception as e:
            messages.error(request, f'Error saving related data: {str(e)}')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        coordinator = Coordinator.objects.filter(user=request.user).first()
        if coordinator:
            return qs.filter(district=coordinator.district)
        return qs.none()

    def total_patients(self, obj):
        return obj.patients.count()
    total_patients.short_description = 'Total Patients'

    def completed_patients(self, obj):
        return obj.patients.filter(missing_records=False, money_collection=True).count()
    completed_patients.short_description = 'Completed'

    def assigned_coordinator(self, obj):
        coordinator = Coordinator.objects.filter(district=obj.district, is_active=True).first()
        return coordinator.name if coordinator else 'Not Assigned'
    assigned_coordinator.short_description = 'Assigned Coordinator'

class ActionLogAdmin(admin.ModelAdmin):
    list_display = ('coordinator', 'action_type', 'district', 'timestamp', 'status')
    list_filter = ('action_type', 'district', 'coordinator', 'status')
    search_fields = ('description', 'notes')
    date_hierarchy = 'timestamp'
    ordering = ('-timestamp',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        coordinator = Coordinator.objects.filter(user=request.user).first()
        if coordinator:
            return qs.filter(coordinator=coordinator)
        return qs.none()

class DistrictAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)

# Register models with custom admin classes
admin.site.register(District, DistrictAdmin)
admin.site.register(Coordinator, CoordinatorAdmin)
admin.site.register(Patient, PatientAdmin)
admin.site.register(FieldAudit, FieldAuditAdmin)
admin.site.register(ActionLog, ActionLogAdmin)

# Register Group back with default admin
admin.site.register(Group)

from django.contrib.admin import AdminSite

class HospitalAdminSite(AdminSite):
    site_header = 'Hospital Management'
    site_title = 'Hospital Management'
    index_title = 'Hospital Management Dashboard'
    
    def get_urls(self):
        urls = super().get_urls()
        return urls

    def get_app_list(self, request):
        app_list = super().get_app_list(request)
        return app_list

    def index(self, request, extra_context=None):
        # Get statistics
        total_patients = Patient.objects.count()
        total_audits = FieldAudit.objects.count()
        total_issues = Patient.objects.filter(missing_records=True).count()

        # Get recent actions
        from django.contrib.admin.models import LogEntry
        recent_actions = []
        for entry in LogEntry.objects.select_related('content_type', 'user')[:5]:
            icon = 'plus-circle' if entry.is_addition else 'edit' if entry.is_change else 'minus-circle'
            recent_actions.append({
                'title': f"{entry.object_repr} was {'added' if entry.is_addition else 'modified' if entry.is_change else 'deleted'}",
                'time': entry.action_time.strftime('%Y-%m-%d %H:%M'),
                'icon': icon
            })

        context = {
            'total_patients': total_patients,
            'total_audits': total_audits,
            'total_issues': total_issues,
            'recent_actions': recent_actions,
            **(extra_context or {})
        }
        return super().index(request, context)

# Create an instance of the custom admin site
admin_site = HospitalAdminSite(name='hospital_admin')

# Register your models with the custom admin site
admin_site.register(District, DistrictAdmin)
admin_site.register(Patient, PatientAdmin)
admin_site.register(FieldAudit, FieldAuditAdmin)
admin_site.register(Coordinator, CoordinatorAdmin)
admin_site.register(ActionLog, ActionLogAdmin)

# Unregister models from the default admin site
from django.contrib import admin
admin.site.unregister([Patient, FieldAudit, Coordinator, ActionLog, District])
