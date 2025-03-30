from typing import Optional
import PyPDF2


def get_pdf_page_count(file_path: str) -> Optional[int]:
    """Get the number of pages in a PDF file.
    
    Args:
        file_path (str): Path to the PDF file
        
    Returns:
        int: Number of pages in the PDF or None if an error occurs
    """
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            return len(pdf_reader.pages)
    except Exception as e:
        print(f"Error reading PDF file: {e}")
        return None 