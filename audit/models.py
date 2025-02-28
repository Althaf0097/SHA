from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator

class District(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class FieldAudit(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    ]

    EHCP_TYPES = [
        ('Public', 'Public'),
        ('Private', 'Private'),
    ]

    # Basic Information
    district = models.ForeignKey(District, on_delete=models.PROTECT)
    hospital_id = models.CharField(max_length=50)
    ehcp_name = models.CharField(max_length=200)
    ehcp_type = models.CharField(max_length=10, choices=EHCP_TYPES)
    auditor_name = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    
    # Visit Details
    visit_date = models.DateField()
    visit_time = models.TimeField()
    current_location = models.CharField(max_length=200)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Patient Statistics
    ekgp_patients = models.IntegerField(default=0)
    pmjay_patients = models.IntegerField(default=0)
    beneficiaries = models.IntegerField(default=0)
    
    # Findings Fields
    findings_type = models.CharField(
        max_length=50,
        choices=[
            ('audit_findings', 'AUDIT FINDINGS'),
            ('hnqa_related', 'HNQA RELATED'),
            ('other_fraudulent_activities', 'ANY OTHER FRAUDULENT ACTIVITIES')
        ],
        null=True,
        blank=True,
        default=None
    )
    audit_findings_value = models.CharField(max_length=3, choices=[('Yes', 'Yes'), ('No', 'No')], null=True, blank=True)
    finding_type = models.CharField(max_length=50, null=True, blank=True)
    abuse_type = models.CharField(max_length=50, null=True, blank=True)
    oope_type = models.CharField(max_length=50, null=True, blank=True)
    
    # HNQA Fields
    hnqa_value = models.CharField(max_length=3, choices=[('Yes', 'Yes'), ('No', 'No')], null=True, blank=True)
    hnqa_type = models.CharField(max_length=50, null=True, blank=True)
    infrastructure_type = models.CharField(max_length=50, null=True, blank=True)
    hr_type = models.CharField(max_length=50, null=True, blank=True)
    services_type = models.CharField(max_length=50, null=True, blank=True)
    
    # Fraudulent Activities Fields
    fraudulent_value = models.CharField(max_length=3, choices=[('Yes', 'Yes'), ('No', 'No')], null=True, blank=True)
    fraudulent_type = models.CharField(max_length=100, null=True, blank=True)
    
    # Signature and Photos
    signature = models.TextField(null=True, blank=True)  # Store base64 signature data
    photos = models.JSONField(null=True, blank=True)  # Store list of photo paths
    
    # Assessment Scores
    infrastructure_score = models.IntegerField(default=0)
    service_score = models.IntegerField(default=0)
    documentation_score = models.IntegerField(default=0)
    feedback_score = models.IntegerField(default=0)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    
    # Assessment
    observations = models.TextField(blank=True)
    recommendations = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.beneficiaries = self.ekgp_patients + self.pmjay_patients
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.ehcp_name} - {self.visit_date}"

    class Meta:
        ordering = ['-visit_date', 'ehcp_name']

class Coordinator(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    employee_id = models.CharField(max_length=20, unique=True)
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True)
    contact_number = models.CharField(max_length=15)
    email = models.EmailField()
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.employee_id})"

    def save(self, *args, **kwargs):
        if not self.pk:  # Only for new coordinators
            # Set email and is_active status to match the coordinator
            self.user.email = self.email
            self.user.is_active = self.is_active
            self.user.save()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['name']
        verbose_name = 'Coordinator'
        verbose_name_plural = 'Coordinators'
        permissions = [
            ("view_district_data", "Can view district data"),
            ("edit_district_data", "Can edit district data"),
        ]

class ActionLog(models.Model):
    ACTION_TYPES = (
        ('AUDIT', 'Audit Performed'),
        ('PATIENT_UPDATE', 'Patient Details Updated'),
        ('RECORD_CHECK', 'Records Checked'),
        ('MONEY_VERIFY', 'Money Status Verified'),
        ('OTHER', 'Other Action')
    )

    coordinator = models.ForeignKey(Coordinator, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    description = models.TextField()
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE, null=True, blank=True)
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='completed')
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.coordinator.name} - {self.action_type} - {self.timestamp.date()}"

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Action Log'
        verbose_name_plural = 'Action Logs'

class Patient(models.Model):
    DEVIATION_CHOICES = [
        ('money_collection', 'Money Collection'),
        ('package_upcoding', 'Package Upcoding'),
        ('incomplete_records', 'Incomplete Case Records')
    ]
    
    audit = models.ForeignKey(FieldAudit, on_delete=models.CASCADE, related_name='patients')
    case_id = models.CharField(max_length=100, unique=True, verbose_name='Case ID / IP Number')
    patient_name = models.CharField(max_length=200)
    mobile_number = models.CharField(max_length=15, null=True, blank=True)
    admission_date = models.DateField()
    discharge_date = models.DateField(null=True, blank=True)
    package_name = models.CharField(max_length=200)
    package_code = models.CharField(max_length=50, null=True, blank=True, default='NA')
    missing_records = models.BooleanField(default=False, verbose_name='Mandatory Records')
    money_collection = models.BooleanField(default=False, verbose_name='Money Collection')
    case_summary = models.TextField(blank=True)
    remarks = models.TextField(blank=True, null=True)
    deviations = models.JSONField(default=list, help_text='List of deviations found')
    total_oope = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Total Out of Pocket Expenses')
    digital_signature = models.TextField(null=True, blank=True, verbose_name='Digital Signature')
    patient_photo = models.ImageField(
        upload_to='patient_photos/%Y/%m/%d/',
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])],
        null=True,
        blank=True,
        verbose_name='Patient Photo'
    )
    case_file = models.FileField(
        upload_to='case_files/%Y/%m/%d/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx'])],
        null=True,
        blank=True,
        verbose_name='Case File'
    )
    discharge_summary = models.FileField(
        upload_to='discharge_summaries/%Y/%m/%d/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx'])],
        null=True,
        blank=True
    )
    bills_documents = models.FileField(
        upload_to='bills/%Y/%m/%d/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])],
        null=True,
        blank=True,
        verbose_name='Bills and Documents'
    )

    class Meta:
        ordering = ['-admission_date']
        verbose_name = "Patient"
        verbose_name_plural = "Patients"

    def __str__(self):
        return f"{self.patient_name} - {self.case_id}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
