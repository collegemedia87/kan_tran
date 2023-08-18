from django.shortcuts import render,HttpResponse
from django.http import JsonResponse
import os
import pytesseract
from PIL import Image
import os
import fitz  # PyMuPDF
from PIL import Image
# Create your views here.

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def pdf_to_images(pdf_path):
    pdf_document = fitz.open(pdf_path)
    number_of_pages=pdf_document.page_count
    
    pdf_filename = os.path.basename(pdf_path)
    pdf_name = os.path.splitext(pdf_filename)[0]
    output_folder = os.path.join(os.path.dirname(pdf_path), pdf_name)
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    for page_number in range(pdf_document.page_count):
        page = pdf_document[page_number]
        image = page.get_pixmap()
        
        image_path = os.path.join(output_folder, f"page_{page_number + 1}.jpg")
        image.save(image_path)
        
    pdf_document.close()
    return number_of_pages

def extract_kannada_text_from_image(image_path):
    try:
        # Open the image using PIL (Python Imaging Library)
        image = Image.open(image_path)
        
        # Perform OCR on the image with Kannada language
        text = pytesseract.image_to_string(image, lang='kan')
        
        return text
    except Exception as e:
        print("Error:", e)
        return None

def home(request):
    if request.method=='POST':
        if request.method == 'POST' and request.FILES['pdfFile']:
            uploaded_file = request.FILES['pdfFile']

            # Specify the directory where you want to save the uploaded files
            upload_dir = 'kan_app/static/'

            with open(upload_dir + uploaded_file.name, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)

            input_pdf_path=os.path.join(upload_dir,uploaded_file.name)

            pages=pdf_to_images(input_pdf_path)
    
            print("PDF to images conversion complete.")
            
            pdf_filename = os.path.basename(input_pdf_path)
            pdf_name = os.path.splitext(pdf_filename)[0]
            dirtory=os.path.join(os.path.dirname(input_pdf_path),pdf_name)
            
            if not os.path.exists(dirtory):
                os.makedirs(dirtory)
            
            result=''
            for image in range(pages):
                image_path = os.path.join(dirtory, f"page_{image + 1}.jpg")
        #         image_path = r"E:\ML\pdf_to_img\kan\page_7.jpg"
                extracted_text = extract_kannada_text_from_image(image_path)
                result=result+'\n'+extracted_text
                os.remove(image_path)
                
                #To save in .docx
        #         doc = Document()
        #         doc.add_paragraph(extracted_text)
        #         save_path = os.path.join(dirtory, f"page_{image + 1}.docx")
        #         doc.save(save_path)


        # To save in .txt

                # save_path = os.path.join(dirtory, f"page_{image + 1}.txt")

        # Create the .txt file and write the extracted text to it
                # with open(save_path, "w", encoding="utf-8") as txt_file:
                #     txt_file.write(extracted_text)

                if extracted_text:
                    print("Extracted Kannada Text:")
                else:
                    print("Text extraction failed.")
            os.rmdir(dirtory)
            os.remove(input_pdf_path)

            return JsonResponse({'message': result})
        else:
            return JsonResponse({'message': 'Upload failed'}, status=400)
    else:
        return render(request,'home.html')