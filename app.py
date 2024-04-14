import streamlit as st
import configparser
from io import BytesIO
from modules.pdf_processing.processor import extract_images_from_pdf, images_to_pdf, categorize_images
from werkzeug.utils import secure_filename
import zipfile
import base64
import os

st.set_page_config(page_title="PDF Processing App", page_icon=":page_with_curl:", layout="wide")

hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)


# Configuring the app
config = configparser.ConfigParser()
config.read('modules/pdf_processing/config.cfg')
allowed_extensions = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def displayPDF(pdf_stream, width_percent=100, height=800):
    pdf_stream.seek(0)
    base64_pdf = base64.b64encode(pdf_stream.read()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="{width_percent}%" height="{height}" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

# def displayPDF(pdf_stream, width_percent=100, height=800):
#     try:
#         pdf_stream.seek(0)
#         base64_pdf = base64.b64encode(pdf_stream.read()).decode('utf-8')
#         components.iframe("https://example.com", height=500)
#         pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="{width_percent}%" height="{height}" type="application/pdf"></iframe>'
#         st.markdown(pdf_display, unsafe_allow_html=True)
#     except Exception as e:
#         st.error("Failed to display the PDF. You can download it instead.")
#         pdf_stream.seek(0)
#         st.download_button(
#             label="Download PDF",
#             data=pdf_stream,
#             file_name="output.pdf",
#             mime="application/pdf"
#         )
#         print(f"Error displaying PDF: {e}")

# import streamlit.components.v1 as components
# import base64

# def displayPDF(pdf_stream):
#     pdf_stream.seek(0)
#     base64_pdf = base64.b64encode(pdf_stream.read()).decode('utf-8')
#     pdf_url = f"data:application/pdf;base64,{base64_pdf}"
    
#     html_content = f"""
#     <html>
#       <head>
#         <script src="https://mozilla.github.io/pdf.js/build/pdf.worker.js"></script>
#         <script src="https://mozilla.github.io/pdf.js/build/pdf.js"></script>
#       </head>
#       <body>
#         <canvas id="pdf-canvas"></canvas>
#         <script>
#           const url = "{pdf_url}";
#           const pdfjsLib = window['pdfjsLib'];  # Corrected typo
          
#           // Rest of the PDF rendering code...
#         </script>
#       </body>
#     </html>
#     """
    
#     components.html(html_content, height=900, unsafe_allow_html=True)



def create_zip_archive(files, output_filename):
    in_memory_zip = BytesIO()
    with zipfile.ZipFile(in_memory_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_stream, name in files:
            file_stream.seek(0)
            zipf.writestr(name, file_stream.read())
    in_memory_zip.seek(0)
    return in_memory_zip

def process_file(file):
    if file is not None and allowed_file(file.name):
        filename = secure_filename(file.name)
        file_stream = BytesIO(file.getbuffer())
        images = extract_images_from_pdf(file_stream)

        categorized_images = categorize_images(images, config)
        base_filename = os.path.splitext(filename)[0]
        output_files = []

        for category, imgs in categorized_images.items():
            output_pdf_stream = BytesIO()
            images_to_pdf(imgs, output_pdf_stream)
            output_files.append((output_pdf_stream, f"{base_filename}_{category}.pdf"))

        return output_files
    return []

# Streamlit UI Components
st.title('OCR PDF SPlitter')
col1, col2 = st.columns([1.5, 2.5])

# col1.header("Upload your PDF files below.")
# uploaded_files = col1.file_uploader("Choose a PDF file", accept_multiple_files=True, type=['pdf'])
# if uploaded_files:
#     for uploaded_file in uploaded_files:
#         process_file(uploaded_file)


# col1.header("Team Members")
# col1.write("1) Aamir Hullur")
# col1.write("2) Atharva Gurav")
# col1.write("3) Maitreya Kanitkar")
# col1.write("4) Parth Godse")


with col1:
    st.header("Upload your PDF files below.")
    uploaded_files = st.file_uploader("Choose a PDF file", accept_multiple_files=True, type=['pdf'])
    st.write('Upload another file or check the outputs below.')
    
    all_files = []
    if uploaded_files:
        with st.spinner("Processing PDFs... Please wait"):
            for uploaded_file in uploaded_files:
                all_files.extend(process_file(uploaded_file))

    col1.header("Team Members")
    col1.write("1) Aamir Hullur")
    col1.write("2) Atharva Gurav")
    col1.write("3) Maitreya Kanitkar")
    col1.write("4) Parth Godse")
    
    if all_files:
        zip_stream = create_zip_archive(all_files, 'all_output_pdfs.zip')
        btn = st.download_button(
            label="Download All PDFs as ZIP",
            data=zip_stream,
            file_name='all_output_pdfs.zip',
            mime="application/zip"
        )

with col2:
    st.header("Output PDFs")
    if all_files:
        with st.spinner("Loading PDFs... Please wait"):
            tabs = st.tabs([name for _, name in all_files])
            for tab, (file_stream, name) in zip(tabs, all_files):
                with tab:
                    displayPDF(file_stream)
