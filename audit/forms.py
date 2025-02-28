from django import forms
from .models import EHCPAudit, Patient, FieldAudit

class FieldAuditForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['current_location'].required = True

    class Meta:
        model = FieldAudit
        fields = '__all__'
        widgets = {
            'visit_date': forms.DateInput(attrs={'type': 'date'}),
            'visit_time': forms.TimeInput(attrs={'type': 'time'}),
            'current_location': forms.TextInput(attrs={'required': 'required'}),
            'latitude': forms.NumberInput(attrs={'step': 'any'}),
            'longitude': forms.NumberInput(attrs={'step': 'any'}),
            'findings_type': forms.Select(choices=[
                ('', 'Select Findings Type'),
                ('audit_findings', 'AUDIT FINDINGS'),
                ('hnqa_related', 'HNQA RELATED'),
                ('other_fraudulent_activities', 'ANY OTHER FRAUDULENT ACTIVITIES')
            ]),
            'audit_findings_value': forms.Select(choices=[
                ('', 'Select Value'),
                ('Yes', 'Yes'),
                ('No', 'No')
            ]),
            'finding_type': forms.TextInput(attrs={'placeholder': 'Enter finding type'}),
            'abuse_type': forms.TextInput(attrs={'placeholder': 'Enter abuse type'}),
            'oope_type': forms.TextInput(attrs={'placeholder': 'Enter OOPE type'}),
            'hnqa_value': forms.Select(choices=[
                ('', 'Select Value'),
                ('Yes', 'Yes'),
                ('No', 'No')
            ]),
            'hnqa_type': forms.TextInput(attrs={'placeholder': 'Enter HNQA type'}),
            'infrastructure_type': forms.TextInput(attrs={'placeholder': 'Enter infrastructure type'}),
            'hr_type': forms.TextInput(attrs={'placeholder': 'Enter HR type'}),
            'services_type': forms.TextInput(attrs={'placeholder': 'Enter services type'}),
            'fraudulent_value': forms.Select(choices=[
                ('', 'Select Value'),
                ('Yes', 'Yes'),
                ('No', 'No')
            ]),
            'fraudulent_type': forms.TextInput(attrs={'placeholder': 'Enter fraudulent type'}),
            'observations': forms.Textarea(attrs={'rows': 4}),
            'recommendations': forms.Textarea(attrs={'rows': 4})
        }

    def clean(self):
        cleaned_data = super().clean()
        latitude = cleaned_data.get('latitude')
        longitude = cleaned_data.get('longitude')

        if latitude is not None:
            try:
                float(latitude)
            except (TypeError, ValueError):
                self.add_error('latitude', 'Please enter a valid decimal number')

        if longitude is not None:
            try:
                float(longitude)
            except (TypeError, ValueError):
                self.add_error('longitude', 'Please enter a valid decimal number')

        return cleaned_data

    def clean_current_location(self):
        current_location = self.cleaned_data.get('current_location')
        if not current_location:
            raise forms.ValidationError('Current location is required.')
        return current_location

class EHCPAuditForm(forms.ModelForm):
    class Meta:
        model = EHCPAudit
        fields = '__all__'
        widgets = {
            'visit_date': forms.DateInput(attrs={'type': 'date'}),
            'district_name': forms.Select(choices=[]),
            'ehcp_type': forms.Select(choices=[
                ('', 'Select EHCP Type'),
                ('hospital', 'Hospital'),
                ('clinic', 'Clinic'),
                ('diagnostic', 'Diagnostic Center'),
            ]),
            'visit_type': forms.Select(choices=[
                ('', 'Select Visit Type'),
                ('scheduled', 'Scheduled'),
                ('surprise', 'Surprise Visit'),
            ]),
        }

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        exclude = ['audit']
        widgets = {
            'admission_date': forms.DateInput(attrs={'type': 'date'}),
            'discharge_date': forms.DateInput(attrs={'type': 'date'}),
            'case_summary': forms.Textarea(attrs={'rows': 4}),
        }
