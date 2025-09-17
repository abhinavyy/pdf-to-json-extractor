import streamlit as st
import os
import json
from src.parser import PDFParser

st.set_page_config(
    page_title="PDF to JSON Extractor",
    page_icon="📄",
    layout="wide"
)

# --- App Title and Description ---
st.title("📄 PDF Content Extractor")
st.write(
    "Upload a PDF file to parse its content. The application will identify paragraphs, "
    "tables, and charts, and organize them into a structured JSON format with section and subsection context."
)

# --- File Uploader ---
uploaded_file = st.file_uploader(
    "Choose a PDF file to begin",
    type="pdf",
    help="Upload your PDF file to start the extraction process."
)

# --- Main Logic ---
if uploaded_file is not None:
    # To keep things tidy, we'll save the uploaded file to a temporary directory.
    # This is also necessary because Camelot works best with file paths.
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    input_pdf_path = os.path.join(upload_dir, uploaded_file.name)
    
    with open(input_pdf_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Display a spinner while the PDF is being processed.
    with st.spinner(f"Parsing '{uploaded_file.name}'... This might take a moment."):
        try:
            # Instantiate our parser and run the extraction process.
            parser = PDFParser()
            extracted_data = parser.parse(input_pdf_path)
            
            st.success("✅ PDF parsed successfully!")

            # Convert the dictionary to a pretty-printed JSON string for the download button.
            json_string = json.dumps(extracted_data, indent=2, ensure_ascii=False)
            
            # --- Download Button ---
            output_filename = f"{os.path.splitext(uploaded_file.name)[0]}_structured.json"
            
            st.download_button(
                label="📥 Download JSON",
                data=json_string,
                file_name=output_filename,
                mime="application/json",
                help="Click to download the extracted content as a JSON file."
            )

            st.subheader("Extracted JSON Content")
            st.json(extracted_data)

        except Exception as e:
            st.error(f"An error occurred during parsing: {e}")
            st.error(
                "Please ensure the PDF is not corrupted and is text-based. "
                "Scanned or image-only PDFs cannot be processed."
            )
        
        finally:
            if os.path.exists(input_pdf_path):
                os.remove(input_pdf_path)

else:
    st.info("Please upload a PDF file to see the results.")