import pdftotext
import fitz
import re
import glob
import pytesseract
import numpy as np
from schwifty import IBAN
import sys
import pandas as pd
from json import loads, dumps
import os

directory = 'RIB'

# To convert pimap to byte image
def pix_to_image(pix):
    bytes = np.frombuffer(pix.samples, dtype=np.uint8)
    img = bytes.reshape(pix.height, pix.width, pix.n)
    return img

# extract iban from text with regular expressions
def regExp_extract(text):
    text = re.sub(r"\|", " ", text)
    text = re.sub(r"\s+", " ", text)
    text = text.upper()
    iban_regex = r"(?:^|\s|\n|\r)([A-Z]{2}\s?[0-9]{2})(?=(?:\s?[A-Z0-9]){9,30})((?:\s?(?:[A-Z]{0,4}\d){,5}){2,7})(\s?[A-Z0-9]{1,3})?"
    iban_number_elems = re.finditer(iban_regex, text)
    country_dic = {
        "AL": [28, "Albania"],
        "AD": [24, "Andorra"],
        "AT": [20, "Austria"],
        "BE": [16, "Belgium"],
        "BA": [20, "Bosnia"],
        "BG": [22, "Bulgaria"],
        "HR": [21, "Croatia"],
        "CY": [28, "Cyprus"],
        "CZ": [24, "Czech Republic"],
        "DK": [18, "Denmark"],
        "EE": [20, "Estonia"],
        "FO": [18, "Faroe Islands"],
        "FI": [18, "Finland"],
        "FR": [27, "France"],
        "DE": [22, "Germany"],
        "GI": [23, "Gibraltar"],
        "GR": [27, "Greece"],
        "GL": [18, "Greenland"],
        "HU": [28, "Hungary"],
        "IS": [26, "Iceland"],
        "IE": [22, "Ireland"],
        "IL": [23, "Israel"],
        "IT": [27, "Italy"],
        "LV": [21, "Latvia"],
        "LI": [21, "Liechtenstein"],
        "LT": [20, "Lithuania"],
        "LU": [20, "Luxembourg"],
        "MK": [19, "Macedonia"],
        "MT": [31, "Malta"],
        "MU": [30, "Mauritius"],
        "MC": [27, "Monaco"],
        "ME": [22, "Montenegro"],
        "NL": [18, "Netherlands"],
        "NO": [15, "Northern Ireland"],
        "PO": [28, "Poland"],
        "PT": [25, "Portugal"],
        "RO": [24, "Romania"],
        "SM": [27, "San Marino"],
        "SA": [24, "Saudi Arabia"],
        "RS": [22, "Serbia"],
        "SK": [24, "Slovakia"],
        "SI": [19, "Slovenia"],
        "ES": [24, "Spain"],
        "SE": [24, "Sweden"],
        "CH": [21, "Switzerland"],
        "TR": [26, "Turkey"],
        "TN": [24, "Tunisia"],
        "GB": [22, "United Kingdom"]
    }
        
    ibans = []
    for iban_number_elem in iban_number_elems:
        clean_list = [x for x in list(iban_number_elem.groups()) if x is not None]
        iban_number = ''.join(clean_list).strip().replace(" ", "")
        if 14 <= len(iban_number) <= 34:
            country_code = iban_number[:2]
            if (country_code in country_dic) and (len(iban_number) > country_dic[country_code][0]) :             
                ibans.append(iban_number[:country_dic[country_code][0]])
            else:
                ibans.append(iban_number) 
                
    return list(set(ibans))
    
# Extract text from xml of a well-formated pdf    
def pdftotext_extract(file_name):
    
    with open(file_name, 'rb') as f:
        print("************************")
        print(file_name)
        pdf = pdftotext.PDF(f, raw=True)
        text = '\n\n'.join(pdf)
        return regExp_extract(text)
           
# Extract text from a pdf with scanned image with an OCR algorithm (Pytesseract)
def pytesseract_extract(file_name):
    pytesseract.pytesseract.tesseract_cmd = r'C:\Users\csfrlaay\AppData\Local\Programs\Tesseract-OCR-5\tesseract.exe'
    doc = fitz.open(file_name)
    zoom = 2
    mat = fitz.Matrix(zoom, zoom)
    count = 0
    # Count variable is to get the number of pages in the pdf
    for p in doc:
        count += 1
    ibans = []
    for i in range(count):
        page = doc.load_page(i)
        pix = page.get_pixmap(matrix=mat)
        image = pix_to_image(pix)
        text = pytesseract.image_to_string(image, lang='fra') #, config=options
        ibans.extend(regExp_extract(text))
    
    doc.close()
    
    return ibans
    
# Return a VALID iban from the list 
def ibans_validation(ibans):
    valid_iban = None
    for iban in ibans:
        try:
            IBAN(iban)
        except Exception as ex:
            #print(ex)
            #print(type(ex).__name__)
            pass
        else:
            valid_iban = iban
            break
    return valid_iban
               

if __name__ == '__main__':
    
    # Get all pdfs from the directory
    files = glob.glob(directory+'//*.pdf')
    valid_ibans = []
    
    for i, file_name in enumerate(files):
        
        # FIRST STEP: if pdf is formatted as an xml, extract text from it
        ibans = pdftotext_extract(file_name)
        valid_iban = ibans_validation(ibans)
        
        # SECOND STEP: if no valid iban available, try OCR method    
        if not valid_iban:
            ibans = pytesseract_extract(file_name)
            valid_iban = ibans_validation(ibans)
        
        print(valid_iban)
        valid_ibans.append({"FILE_NAME": os.path.basename(file_name), "IBAN": valid_iban})
                
    df_ibans = pd.DataFrame(valid_ibans)
    df_ibans.columns = ['FILE_NAME', 'IBAN']
    
    # Save result to file according to argument of the script given through command line (CSV, Excel or JSON)
    if len(sys.argv) > 1:
        output_format = sys.argv[1]
    else:
        output_format = None
    if (not output_format) or (output_format.lower() == 'csv'):
        df_ibans.to_csv('ibans_extracted.csv', index=False)
    elif output_format.lower() in ['xlsx', 'xls', 'excel']:
        df_ibans.to_excel('ibans_extracted.xlsx', index=False)
    elif output_format.lower() == 'json':
        result = df_ibans.to_json(orient="index")
        parsed = loads(result)
        json_string = dumps(parsed, indent=4)
        with open('ibans_extracted.json', 'w') as outfile:
            outfile.write(json_string)
        