import os
from datetime import datetime
from functools import wraps
from flask import (
    Blueprint, render_template, request,
    redirect, url_for, current_app,
    flash, abort, make_response
)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from fpdf import FPDF

from .models import Report, User, AuditLog
from .utils import process_mri_image
from . import db

main = Blueprint('main', __name__)

# ================= HOME =================
@main.route('/')
def home():
    return render_template('main/home.html')

# ================= ABOUT =================
@main.route('/about')
def about():
    return render_template('main/about.html')

# ================= SIMPLE DOCTOR CHECK =================
def doctor_required(f):
    @wraps(f)
    def decorated_function(report_id, *args, **kwargs):
        if current_user.role != 'doctor':
            abort(403)
        return f(report_id, *args, **kwargs)
    return decorated_function

# ================= UPLOAD MRI =================
@main.route('/upload', methods=['POST'])
@login_required
def upload_mri():

    if current_user.role != "patient":
        return redirect(url_for('main.doctor_dashboard'))

    if 'mri_image' not in request.files:
        flash('No file selected')
        return redirect(url_for('main.patient_dashboard'))

    file = request.files['mri_image']

    if file.filename == '':
        flash('No file selected')
        return redirect(url_for('main.patient_dashboard'))

    filename = secure_filename(file.filename)
    upload_path = os.path.join(
        current_app.config['UPLOAD_FOLDER'], filename
    )

    file.save(upload_path)

    result = process_mri_image(
        upload_path,
        current_app.config['UPLOAD_FOLDER']
    )

    new_report = Report(
        patient_id=current_user.id,
        image_path=filename,
        result_image_path=result['result_image'],
        tumor_detected=result['tumor_detected'],
        tumor_type=result['tumor_type'],
        severity=result['severity'],
        confidence=result['confidence'],
        tumor_area_px=result['area_px'],
        status="Pending"
    )

    db.session.add(new_report)

    log = AuditLog(
        user_id=current_user.id,
        action=f"Uploaded MRI scan: {filename}"
    )
    db.session.add(log)

    db.session.commit()

    return redirect(
        url_for('main.view_result', report_id=new_report.id)
    )

# ================= VIEW RESULT =================
@main.route('/view_result/<int:report_id>')
@login_required
def view_result(report_id):

    report = Report.query.get_or_404(report_id)

    # Patient can only see their own report
    if current_user.role == "patient" and report.patient_id != current_user.id:
        abort(403)

    return render_template(
        'results/detection.html',
        report=report
    )

# ================= PATIENT DASHBOARD =================
@main.route('/patient_dashboard')
@login_required
def patient_dashboard():

    if current_user.role != 'patient':
        return redirect(url_for('main.doctor_dashboard'))

    reports = Report.query.filter_by(
        patient_id=current_user.id
    ).order_by(Report.created_at.desc()).all()

    return render_template(
        'dashboard/patient.html',
        reports=reports
    )

# ================= DOCTOR DASHBOARD =================
@main.route('/doctor_dashboard')
@login_required
def doctor_dashboard():

    if current_user.role != 'doctor':
        return redirect(url_for('main.patient_dashboard'))

    reports = Report.query.order_by(
        Report.created_at.desc()
    ).all()

    return render_template(
        'dashboard/doctor.html',
        reports=reports
    )

# ================= UPDATE DIAGNOSIS =================
@main.route('/update_diagnosis/<int:report_id>', methods=['POST'])
@login_required
@doctor_required
def update_diagnosis(report_id):

    report = Report.query.get_or_404(report_id)

    report.doctor_comments = request.form.get('comments')
    report.status = "Diagnosed"

    log = AuditLog(
        user_id=current_user.id,
        action=f"Updated diagnosis for Report {report_id}"
    )

    db.session.add(log)
    db.session.commit()

    return redirect(url_for('main.doctor_dashboard'))
# ================= PATIENT PROFILE =================
@main.route('/patient_profile')
@login_required
def patient_profile():

    if current_user.role != "patient":
        return redirect(url_for('main.doctor_dashboard'))

    reports = Report.query.filter_by(
        patient_id=current_user.id
    ).order_by(Report.created_at.desc()).all()

    total_reports = len(reports)

    last_diagnosis = None
    for report in reports:
        if report.status == "Diagnosed":
            last_diagnosis = report.created_at.strftime("%d-%m-%Y")
            break

    return render_template(
        'dashboard/patient_profile.html',
        user=current_user,
        total_reports=total_reports,
        last_diagnosis=last_diagnosis
    )


# ================= EDIT PROFILE =================
@main.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():

    if current_user.role != "patient":
        return redirect(url_for('main.doctor_dashboard'))

    if request.method == 'POST':

        # ✅ NEW: Save age and gender
        current_user.age = request.form.get('age')
        current_user.gender = request.form.get('gender')

        # Existing fields
        current_user.phone = request.form.get('phone')
        current_user.place = request.form.get('place')

        # Handle profile image upload
        if 'profile_image' in request.files:
            file = request.files['profile_image']

            if file and file.filename != "":
                filename = secure_filename(file.filename)
                file_path = os.path.join(
                    current_app.config['PROFILE_UPLOAD_FOLDER'],
                    filename
                )
                file.save(file_path)
                current_user.profile_image = filename

        db.session.commit()
        flash("Profile updated successfully!", "success")

        return redirect(url_for('main.patient_profile'))

    return render_template('dashboard/edit_profile.html')

# ================= DOWNLOAD REPORT PDF =================
@main.route('/download_report/<int:report_id>')
@login_required
def download_report(report_id):

    report = Report.query.get_or_404(report_id)

    if current_user.role == "patient" and report.patient_id != current_user.id:
        abort(403)

    from datetime import datetime

    issue_time = datetime.now().strftime("%d-%m-%Y %H:%M")

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # ===== HOSPITAL HEADER =====
    pdf.set_font("helvetica", "B", 18)
    pdf.cell(0, 10, "NEUROSCAN AI DIAGNOSTIC CENTER", ln=True, align='C')

    pdf.set_font("helvetica", "", 12)
    pdf.cell(0, 8, "Advanced Brain Tumor Detection System", ln=True, align='C')
    pdf.ln(5)

    pdf.line(10, 30, 200, 30)  # horizontal line
    pdf.ln(10)

    # ===== REPORT TITLE =====
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(0, 10, "MRI BRAIN TUMOR ANALYSIS REPORT", ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("helvetica", size=12)

    # ===== PATIENT DETAILS =====
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 8, "Patient Information", ln=True)
    pdf.set_font("helvetica", size=12)

    pdf.cell(95, 8, f"Patient Name: {report.patient.name}", border=0)
    pdf.cell(95, 8, f"Report ID: {report.id}", ln=True)

    pdf.cell(95, 8, f"Upload Date: {report.created_at.strftime('%d-%m-%Y %H:%M')}", border=0)
    pdf.cell(95, 8, f"Issue Date: {issue_time}", ln=True)

    pdf.ln(8)

    # ===== DIAGNOSIS SECTION =====
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 8, "Tumor Analysis Results", ln=True)
    pdf.set_font("helvetica", size=12)

    pdf.cell(95, 8, f"Tumor Detected: {'Yes' if report.tumor_detected else 'No'}", border=0)
    pdf.cell(95, 8, f"Tumor Type: {report.tumor_type}", ln=True)

    pdf.cell(95, 8, f"Severity Level: {report.severity}", border=0)
    pdf.cell(95, 8, f"Confidence Score: {report.confidence}", ln=True)

    pdf.cell(95, 8, f"Tumor Area (px): {report.tumor_area_px}", ln=True)

    pdf.ln(8)

    # ===== DOCTOR SECTION =====
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 8, "Doctor's Clinical Notes", ln=True)
    pdf.set_font("helvetica", size=12)

    pdf.multi_cell(
        0, 8,
        report.doctor_comments or "No additional clinical notes provided."
    )

    pdf.ln(15)

    # ===== SIGNATURE =====
    pdf.cell(0, 8, "-------------------------------------------", ln=True, align='R')
    pdf.cell(0, 8, f"Dr. {current_user.name}", ln=True, align='R')
    pdf.cell(0, 8, "Consultant Radiologist", ln=True, align='R')
    pdf.cell(0, 8, f"Issued on: {issue_time}", ln=True, align='R')

    pdf.ln(10)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())

    pdf.set_font("helvetica", "I", 9)
    pdf.multi_cell(
        0, 6,
        "This is a system-generated medical analysis report. "
        "Clinical correlation and further medical evaluation is advised."
    )

    pdf_output = bytes(pdf.output(dest='S'))

    response = make_response(pdf_output)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f"attachment; filename=Brain_Tumor_Report_{report_id}.pdf"

    return response