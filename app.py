import streamlit as st
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from io import BytesIO
from datetime import datetime

# -------------------- PDF GENERATION FUNCTION (defined first) --------------------
def generate_pdf(doc_type, company_name, company_address, company_contact,
                 employee_name, employee_id, context):
    """
    Generate a PDF document based on the provided data.
    context is a dict containing all form variables.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=72)
    elements = []
    styles = getSampleStyleSheet()

    # Custom styles
    styles.add(ParagraphStyle(name='Center', alignment=1, fontSize=12, spaceAfter=6))
    styles.add(ParagraphStyle(name='Right', alignment=2, fontSize=10, textColor=colors.gray))
    styles.add(ParagraphStyle(name='Body', fontSize=11, spaceAfter=12, leading=14))
    styles.add(ParagraphStyle(name='Signature', fontSize=11, spaceBefore=30, spaceAfter=6))

    # Header with company details
    elements.append(Paragraph(f"<b>{company_name}</b>", styles['Title']))
    elements.append(Paragraph(company_address, styles['Normal']))
    elements.append(Paragraph(company_contact, styles['Normal']))
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(Paragraph(f"Date: {datetime.now().strftime('%d %B %Y')}", styles['Right']))
    elements.append(Spacer(1, 0.3 * inch))

    # Document title
    elements.append(Paragraph(f"<b>{doc_type.upper()}</b>", styles['Center']))
    elements.append(Spacer(1, 0.2 * inch))

    # Content based on document type
    if doc_type == "Offer Letter":
        content = f"""
        Dear <b>{employee_name}</b>,<br/><br/>
        We are delighted to offer you the position of <b>{context['job_title']}</b> in the <b>{context['department']}</b> department at {company_name}. 
        We were impressed with your skills and believe you will be a valuable addition to our team.<br/><br/>
        <b>Compensation:</b> Your annual CTC will be <b>{context['salary']}</b>.<br/>
        <b>Joining Date:</b> {context['joining_date'].strftime('%d %B %Y')}<br/>
        <b>Probation Period:</b> {context['probation']}<br/>
        <b>Notice Period:</b> {context['notice_period']}<br/><br/>
        Please find attached the detailed terms and conditions. Kindly sign a copy of this letter as acceptance of the offer and return it to us by [Date].<br/><br/>
        We look forward to welcoming you to the team!<br/><br/>
        Yours sincerely,<br/>
        <b>HR Manager</b><br/>
        {company_name}
        """
        elements.append(Paragraph(content, styles['Body']))

    elif doc_type == "Salary Slip":
        # Calculations
        basic = context['basic']
        hra = context['hra']
        allowances = context['allowances']
        pf = context['pf']
        tds = context['tds']
        gross = basic + hra + allowances
        total_deduction = pf + tds
        net = gross - total_deduction

        # Employee details table
        emp_data = [
            ["Employee Name", employee_name],
            ["Employee ID", employee_id],
            ["Pay Month", context['pay_month']],
        ]
        emp_table = Table(emp_data, colWidths=[2 * inch, 3 * inch])
        emp_table.setStyle(TableStyle([
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 11),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
        ]))
        elements.append(emp_table)
        elements.append(Spacer(1, 0.2 * inch))

        # Salary breakdown table
        salary_data = [
            ["Earnings", "Amount (₹)", "Deductions", "Amount (₹)"],
            ["Basic Pay", f"{basic:,.2f}", "Provident Fund", f"{pf:,.2f}"],
            ["HRA", f"{hra:,.2f}", "TDS", f"{tds:,.2f}"],
            ["Allowances", f"{allowances:,.2f}", "", ""],
            ["<b>Gross Pay</b>", f"<b>{gross:,.2f}</b>", "<b>Total Deduction</b>", f"<b>{total_deduction:,.2f}</b>"],
        ]
        salary_table = Table(salary_data, colWidths=[1.8 * inch, 1.2 * inch, 1.8 * inch, 1.2 * inch])
        salary_table.setStyle(TableStyle([
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('ALIGN', (1,0), (1,-1), 'RIGHT'),
            ('ALIGN', (3,0), (3,-1), 'RIGHT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('GRID', (0,0), (-1,-2), 0.5, colors.grey),
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('SPAN', (0,4), (1,4)),   # Merge Gross Pay row for Earnings
            ('SPAN', (2,4), (3,4)),   # Merge Total Deduction row
            ('ALIGN', (0,4), (1,4), 'CENTER'),
            ('ALIGN', (2,4), (3,4), 'CENTER'),
        ]))
        elements.append(salary_table)
        elements.append(Spacer(1, 0.1 * inch))

        # Net Pay highlighted
        net_para = f"<para align=right><b>NET PAY: ₹ {net:,.2f}</b></para>"
        elements.append(Paragraph(net_para, styles['Normal']))
        elements.append(Spacer(1, 0.3 * inch))

        # Footer
        elements.append(Paragraph("This is a system-generated salary slip and does not require a signature.", styles['Italic']))

    elif doc_type == "Experience Letter":
        content = f"""
        To Whom It May Concern,<br/><br/>
        This is to certify that <b>{employee_name}</b> (Employee ID: {employee_id}) was employed with <b>{company_name}</b> 
        from <b>{context['from_date'].strftime('%d %B %Y')}</b> to <b>{context['to_date'].strftime('%d %B %Y')}</b>.<br/><br/>
        During this tenure, {employee_name} served as <b>{context['job_title']}</b> in the <b>{context['department']}</b> department. 
        His/Her key responsibilities included:<br/>
        {context['responsibilities']}<br/><br/>
        {employee_name} was a dedicated and valued member of our team. We found him/her to be sincere, hardworking, and capable. 
        We wish him/her all the best in future endeavors.<br/><br/>
        For any further queries, please feel free to contact us.<br/><br/>
        Sincerely,<br/>
        <b>HR Manager</b><br/>
        {company_name}
        """
        elements.append(Paragraph(content, styles['Body']))

    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

# -------------------- STREAMLIT APP --------------------
st.set_page_config(page_title="AI HR Document Generator", layout="centered")
st.title("📄 AI HR Document Generator")
st.markdown("Fill in the details below to generate a professional HR document.")

# Initialize session state to store form data (optional, but helps persist across reruns)
if "form_submitted" not in st.session_state:
    st.session_state.form_submitted = False

# Sidebar for instructions
with st.sidebar:
    st.header("About")
    st.info(
        "This tool generates professional HR documents: Offer Letters, Salary Slips, "
        "and Experience Letters. All generated PDFs include your company letterhead."
    )
    st.markdown("---")
    st.caption("Ensure all required fields are filled before generating.")

# Main form to batch input
with st.form("hr_form"):
    document_type = st.selectbox(
        "Select Document Type",
        ["Offer Letter", "Salary Slip", "Experience Letter"],
        index=0
    )

    st.markdown("### Company Information")
    col1, col2 = st.columns(2)
    with col1:
        company_name = st.text_input("Company Name *")
        company_address = st.text_input("Company Address *")
    with col2:
        company_contact = st.text_input("Company Contact (Phone/Email) *")
        employee_name = st.text_input("Employee Name *")

    employee_id = st.text_input("Employee ID *")

    st.markdown("### Document Specific Details")
    # Extra fields based on document type
    if document_type == "Offer Letter":
        col1, col2 = st.columns(2)
        with col1:
            job_title = st.text_input("Job Title *")
            department = st.text_input("Department *")
            salary = st.text_input("CTC (e.g., ₹5,00,000 per annum) *")
        with col2:
            joining_date = st.date_input("Joining Date *", value=datetime.today())
            probation = st.text_input("Probation Period (e.g., 6 months) *")
            notice_period = st.text_input("Notice Period (e.g., 30 days) *")

    elif document_type == "Salary Slip":
        col1, col2 = st.columns(2)
        with col1:
            pay_month = st.text_input("Pay Month (e.g., Jan 2026) *")
            basic = st.number_input("Basic Pay (₹) *", min_value=0, step=1000)
            hra = st.number_input("HRA (₹) *", min_value=0, step=1000)
        with col2:
            allowances = st.number_input("Allowances (₹) *", min_value=0, step=1000)
            pf = st.number_input("PF Deduction (₹) *", min_value=0, step=100)
            tds = st.number_input("TDS Deduction (₹) *", min_value=0, step=100)

    elif document_type == "Experience Letter":
        col1, col2 = st.columns(2)
        with col1:
            job_title = st.text_input("Job Title *")
            department = st.text_input("Department *")
            from_date = st.date_input("From Date *")
        with col2:
            to_date = st.date_input("To Date *")
        responsibilities = st.text_area("Key Responsibilities *", height=100)

    st.markdown("---")
    submitted = st.form_submit_button("Generate Document")

# Validation and PDF generation
if submitted:
    # Check required fields
    missing = []
    if not company_name:
        missing.append("Company Name")
    if not company_address:
        missing.append("Company Address")
    if not company_contact:
        missing.append("Company Contact")
    if not employee_name:
        missing.append("Employee Name")
    if not employee_id:
        missing.append("Employee ID")

    if document_type == "Offer Letter":
        if not job_title:
            missing.append("Job Title")
        if not department:
            missing.append("Department")
        if not salary:
            missing.append("CTC")
        if not joining_date:
            missing.append("Joining Date")
        if not probation:
            missing.append("Probation Period")
        if not notice_period:
            missing.append("Notice Period")
    elif document_type == "Salary Slip":
        if not pay_month:
            missing.append("Pay Month")
        # basic, hra, etc are numbers with default 0, so they are always filled.
    elif document_type == "Experience Letter":
        if not job_title:
            missing.append("Job Title")
        if not department:
            missing.append("Department")
        if not from_date:
            missing.append("From Date")
        if not to_date:
            missing.append("To Date")
        if not responsibilities:
            missing.append("Responsibilities")

    if missing:
        st.error(f"Please fill in the following required fields: {', '.join(missing)}")
    else:
        with st.spinner("Generating PDF..."):
            # Prepare data for PDF generation
            pdf_buffer = generate_pdf(
                document_type,
                company_name,
                company_address,
                company_contact,
                employee_name,
                employee_id,
                locals()  # pass all local variables for simplicity
            )
            st.success("Document generated successfully!")
            st.download_button(
                label="📥 Download PDF",
                data=pdf_buffer,
                file_name=f"{document_type}_{employee_name.replace(' ', '_')}.pdf",
                mime="application/pdf"
            )