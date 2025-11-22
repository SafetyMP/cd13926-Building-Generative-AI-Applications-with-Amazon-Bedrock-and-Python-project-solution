#!/usr/bin/env python3
"""
Check PDF content to verify if it contains extractable text
"""
import boto3
import PyPDF2
import io
import sys

def download_and_check_pdf(bucket_name, key):
    """Download a PDF from S3 and check if it contains text"""
    s3 = boto3.client('s3')
    
    try:
        print(f"Downloading {key} from {bucket_name}...")
        response = s3.get_object(Bucket=bucket_name, Key=key)
        pdf_content = response['Body'].read()
        
        # Try to extract text from the PDF
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
        
        print(f"\n=== PDF Information ===")
        print(f"Number of pages: {len(pdf_reader.pages)}")
        
        # Extract text from the first page
        if len(pdf_reader.pages) > 0:
            first_page = pdf_reader.pages[0]
            text = first_page.extract_text()
            
            print("\n=== First 500 characters of text ===")
            print(text[:500])
            
            # Check if the text is meaningful
            if len(text.strip()) < 50:  # Arbitrary threshold for minimal text
                print("\nWARNING: Very little text extracted. This might be a scanned PDF.")
            else:
                print("\nText extraction successful. PDF appears to contain extractable text.")
                
        return True
        
    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python check_pdf_content.py <bucket_name> <key>")
        sys.exit(1)
        
    bucket_name = sys.argv[1]
    key = sys.argv[2]
    
    # Install PyPDF2 if not already installed
    try:
        import PyPDF2
    except ImportError:
        print("Installing PyPDF2...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "PyPDF2"])
        import PyPDF2
    
    download_and_check_pdf(bucket_name, key)
