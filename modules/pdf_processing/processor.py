import PyPDF2
import io
from PIL import Image
import numpy as np
import configparser
import easyocr
import os

# Function to extract images from a PDF file
def extract_images_from_pdf(pdf_path):
    images = []
    pdf_document = PyPDF2.PdfFileReader(pdf_path)
    for current_page_number in range(pdf_document.getNumPages()):
        current_page = pdf_document.getPage(current_page_number)
        if "/XObject" in current_page["/Resources"]:
            x_object = current_page["/Resources"]["/XObject"].getObject()
            for obj in x_object:
                if x_object[obj]["/Subtype"] == "/Image":
                    image = x_object[obj]
                    image_bytes = image._data
                    images.append(Image.open(io.BytesIO(image_bytes)))
    return images

# Function to save images as a single PDF
# def images_to_pdf(images, output_pdf):
#     if images:
#         images[0].save(output_pdf, save_all=True, append_images=images[1:])

from PIL import Image

def images_to_pdf(images, output_pdf_stream):
    # Ensure all are PIL Image objects and are in 'RGB' mode if necessary
    converted_images = [img.convert('RGB') if img.mode != 'RGB' else img for img in images]

    # Attempt to save the images as a PDF
    try:
        if converted_images:
            # The first image is saved and all subsequent images are appended to it
            converted_images[0].save(output_pdf_stream, format='PDF', save_all=True, append_images=converted_images[1:])
    except Exception as e:
        # Log or handle any exceptions raised during PDF saving
        print("Failed to save images to PDF:", e)
        raise ValueError(f"Failed to save images to PDF due to: {e}")

# Function to categorize images based on text detected in specified locations
def categorize_images(images, config):
    reader = easyocr.Reader(['en'])  # Initialize the OCR reader
    texts = [config['OCR']['Text1'], config['OCR']['Text2'], config['OCR']['Text3']]
    locations = [
        tuple(map(int, config['OCR']['Loc1'].split(','))),
        tuple(map(int, config['OCR']['Loc2'].split(','))),
        tuple(map(int, config['OCR']['Loc3'].split(',')))
    ]
    
    categorized_images = {
        "Complaint": [],
        "Summons": [],
        "Appearance": []
    }
    current_category = None
    current_text_index = 0
    
    for image in images:
        if current_text_index >= len(texts):
            break
        
        x1, y1, x2, y2 = locations[current_text_index]
        target_text = texts[current_text_index].upper()
        cropped_image = image.crop((x1, y1, x2, y2))
        results = reader.readtext(np.array(cropped_image))
        
        found = False
        for result in results:
            text = result[1].upper()
            if target_text in text:
                found = True
                break
        
        if found:
            current_text_index += 1
            if current_text_index == 1:
                current_category = "Complaint"
            elif current_text_index == 2:
                current_category = "Summons"
            elif current_text_index == 3:
                current_category = "Appearance"
        
        if current_category:
            categorized_images[current_category].append(image)
    
    return categorized_images

# if __name__ == "__main__":
#     config = configparser.ConfigParser()
#     config.read('config.cfg')
    
#     input_folder = config['Files']['INPUT']
#     output_folder = config['Files']['OUTPUT']
    
#     if not os.path.exists(output_folder):
#         os.makedirs(output_folder)
    
#     for file_name in os.listdir(input_folder):
#         if file_name.endswith(".pdf"):
#             pdf_path = os.path.join(input_folder, file_name)
#             images = extract_images_from_pdf(pdf_path)
#             print(f"Extracted {len(images)} images from {pdf_path}")
            
#             categorized_images = categorize_images(images, config)
#             base_filename = os.path.splitext(os.path.basename(pdf_path))[0]
            
#             for category, imgs in categorized_images.items():
#                 output_pdf_path = os.path.join(output_folder, f"{base_filename}_{category}.pdf")
#                 images_to_pdf(imgs, output_pdf_path)
#                 print(f"Generated PDF for {category} at {output_pdf_path}")


# In[ ]:




