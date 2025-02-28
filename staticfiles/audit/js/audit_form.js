document.addEventListener('DOMContentLoaded', function() {
    const addPatientBtn = document.querySelector('.btn-add-patient');
    const patientForm = document.querySelector('.patient-form');
    const patientList = document.querySelector('.patient-list');
    let patientCount = 1;

    if (addPatientBtn) {
        addPatientBtn.addEventListener('click', function() {
            // Clear the form fields
            const inputs = patientForm.querySelectorAll('input:not([type="radio"]):not([type="checkbox"]), textarea');
            inputs.forEach(input => input.value = '');
            
            // Uncheck checkboxes
            const checkboxes = patientForm.querySelectorAll('input[type="checkbox"]');
            checkboxes.forEach(checkbox => checkbox.checked = false);
            
            // Update the patient number
            patientCount++;
            const patientTitle = patientForm.querySelector('.patient-title');
            if (patientTitle) {
                patientTitle.textContent = `Patient ${patientCount}`;
            }
        });
    }

    // Form submission handling
    const auditForm = document.querySelector('#audit-form');
    if (auditForm) {
        auditForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Validate required fields
            const requiredFields = auditForm.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value) {
                    isValid = false;
                    field.classList.add('is-invalid');
                } else {
                    field.classList.remove('is-invalid');
                }
            });
            
            if (!isValid) {
                alert('Please fill in all required fields');
                return;
            }
            
            // Submit the form
            auditForm.submit();
        });
    }

    // Date input handling
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(input => {
        input.addEventListener('change', function() {
            const admissionDate = document.querySelector('input[name="admission_date"]');
            const dischargeDate = document.querySelector('input[name="discharge_date"]');
            
            if (admissionDate && dischargeDate && admissionDate.value && dischargeDate.value) {
                if (new Date(dischargeDate.value) < new Date(admissionDate.value)) {
                    alert('Discharge date cannot be earlier than admission date');
                    dischargeDate.value = '';
                }
            }
        });
    });

    // File input handling
    const photoInput = document.querySelector('input[name="patient_photo"]');
    if (photoInput) {
        photoInput.addEventListener('change', function() {
            const file = this.files[0];
            const maxSize = 5 * 1024 * 1024; // 5MB
            
            if (file && file.size > maxSize) {
                alert('File size must not exceed 5MB');
                this.value = '';
                return;
            }
            
            const validTypes = ['image/jpeg', 'image/png', 'image/jpg'];
            if (file && !validTypes.includes(file.type)) {
                alert('Please upload a valid image file (JPG, JPEG, or PNG)');
                this.value = '';
            }
        });
    }
});
