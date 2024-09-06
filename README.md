
# IBAN Extraction from PDFs using OCR

This repository provides a Python-based solution for extracting International Bank Account Numbers (IBANs) from PDF documents using Optical Character Recognition (OCR).This tool helps automate the detection and extraction of IBANs from text-heavy or scanned PDFs.

## Features
- **OCR Integration**: Leverages powerful OCR library Pytesseract to process scanned PDFs.
- **IBAN Detection**: Utilizes regular expressions to identify and extract IBANs from the text obtained via OCR.
- **Multi-PDF Support**: Process multiple PDF files in batch mode for large-scale extraction tasks.
- **Error Handling**: Robust handling of OCR inaccuracies and extraction failures, ensuring reliable output.
- **Output Formats**: Extracted IBANs can be saved to CSV, Excel or JSON.

## Dependencies
- Python 3.9.13
- Tesseract OCR
- PDF handling library: pdftotext
- Regular expression for IBAN pattern matching
- Utility for IBAN pattern verification

## Usage
1. Install the necessary dependencies via `pip install -r requirements.txt`.
2. Provide the PDF file(s) to be processed by placing them in the "RIB" folder.
3. Run the script to extract IBANs

---

Let me know if you'd like any further details!
