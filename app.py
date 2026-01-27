import streamlit as st
import pdfplumber
from PyPDF2 import PdfReader, PdfWriter
import io
import zipfile
import re

# Page Config
st.set_page_config(page_title="Ultra Tendency Payslip Splitter", page_icon="📄")
st.title("📄 Payslip Splitter")
st.info("Goal: Rename files as 'Name_ID.pdf'")

uploaded_file = st.file_uploader("Upload Master PDF", type="pdf")

if uploaded_file is not None:
    reader = PdfReader(uploaded_file)
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w") as zf:
        with pdfplumber.open(uploaded_file) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                
                emp_name = "Unknown"
                emp_id = "00"
                
                # Split and clean lines
                lines = [line.strip() for line in text.split('\n') if line.strip()]
                
                for idx, line in enumerate(lines):
                    # 1. FIXED ID LOGIC
                    if "Employee ID" in line:
                        # Extract all numbers from this line
                        ids = re.findall(r'\d+', line)
                        if ids:
                            emp_id = ids[0]
                    
                    # 2. FIXED NAME LOGIC
                    # In your PDF, 'Employee Name' and 'Designation' are in the same box
                    if "Employee Name" in line:
                        # We check the next 1 or 2 lines to find the actual name
                        for offset in [1, 2]:
                            if idx + offset < len(lines):
                                potential_name = lines[idx + offset]
                                # If the line isn't another label, it's the name!
                                if "Designation" not in potential_name and "Contact" not in potential_name:
                                    emp_name = potential_name
                                    break
                
                # --- FINAL CLEANING ---
                # Remove any leftover "Designation" text if it got stuck to the name
                emp_name = emp_name.split("Designation")[0].strip()
                
                # The Rule: Aditya_Kumar_Gupta_28
                clean_name = emp_name.replace(" ", "_")
                filename = f"{clean_name}_{emp_id}.pdf"

                # Save page
                writer = PdfWriter()
                writer.add_page(reader.pages[i])
                page_io = io.BytesIO()
                writer.write(page_io)
                zf.writestr(filename, page_io.getvalue())

    st.success("Successfully processed!")
    st.download_button(
        label="📥 Download ZIP",
        data=zip_buffer.getvalue(),
        file_name="Processed_Payslips.zip",
        mime="application/zip"
    )