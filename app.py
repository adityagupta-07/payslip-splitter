import streamlit as st
import pdfplumber
from PyPDF2 import PdfReader, PdfWriter
import io
import zipfile
import re

# Page Config
st.set_page_config(page_title="Ultra Tendency Payslip Splitter", page_icon="📄")
st.title("📄 Payslip Splitter")
st.info("Upload the master PDF. I will rename files as: Name_EmployeeNumber.pdf")

uploaded_file = st.file_uploader("Upload Master PDF", type="pdf")

if uploaded_file is not None:
    reader = PdfReader(uploaded_file)
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w") as zf:
        # Use pdfplumber to read text accurately
        with pdfplumber.open(uploaded_file) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                
                # Default values in case extraction fails
                emp_name = "Unknown_Employee"
                emp_id = str(i + 1)
                
                # Split text into lines and clean them
                lines = [line.strip() for line in text.split('\n') if line.strip()]
                
                for idx, line in enumerate(lines):
                    # 1. Extract Employee ID
                    if "Employee ID" in line:
                        # Finds the first number in the line (e.g., '28')
                        id_search = re.findall(r'\d+', line)
                        if id_search:
                            emp_id = id_search[0]
                    
                    # 2. Extract Employee Name
                    # In your PDF, the name usually follows the header 'Employee Name'
                    if "Employee Name" in line:
                        if idx + 1 < len(lines):
                            # The name is on the next line
                            emp_name = lines[idx + 1]
                            # Clean up in case 'Designation' is attached to the string
                            emp_name = emp_name.split("Designation")[0].strip()

                # --- NAMING RULE ---
                # This turns "Aditya Kumar Gupta" into "Aditya_Kumar_Gupta"
                clean_name = emp_name.replace(" ", "_")
                # Result: "Aditya_Kumar_Gupta_28.pdf"
                filename = f"{clean_name}_{emp_id}.pdf"

                # Create the individual PDF page
                writer = PdfWriter()
                writer.add_page(reader.pages[i])
                
                # Write page to memory and add to ZIP
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