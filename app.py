import streamlit as st
import pdfplumber
from PyPDF2 import PdfReader, PdfWriter
import io
import zipfile
import re

# Page Config
st.set_page_config(page_title="Ultra Tendency Payslip Splitter", page_icon="📄")
st.title("📄 Payslip Splitter")
st.info("Upload the master PDF. I will rename files based on Employee Name and ID.")

uploaded_file = st.file_uploader("Upload Master PDF", type="pdf")

if uploaded_file is not None:
    reader = PdfReader(uploaded_file)
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w") as zf:
        # Use pdfplumber to read text accurately
        with pdfplumber.open(uploaded_file) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                
                # Custom Logic for Ultra Tendency Nepal Payslips
                emp_name = "Unknown_Employee"
                emp_id = str(i + 1)
                
                lines = text.split('\n')
                for line in lines:
                    if "Employee Name" in line:
                        # Cleans the line to get only the name
                        emp_name = line.replace("Employee Name", "").strip()
                    if "Employee ID" in line:
                        # Cleans the line to get only the ID number
                        emp_id = line.replace("Employee ID", "").strip().split()[0]

                # Create the individual PDF page
                writer = PdfWriter()
                writer.add_page(reader.pages[i])
                
                # Sanitize filename
                clean_name = emp_name.replace(" ", "_")
                filename = f"{clean_name}_{emp_id}.pdf"
                
                # Write to memory and add to ZIP
                page_io = io.BytesIO()
                writer.write(page_io)
                zf.writestr(filename, page_io.getvalue())

    st.success(f"Successfully processed {len(reader.pages)} payslips!")
    st.download_button(
        label="📥 Download All Payslips (ZIP)",
        data=zip_buffer.getvalue(),
        file_name="Split_Payslips.zip",
        mime="application/zip"
    )