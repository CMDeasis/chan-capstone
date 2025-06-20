from mistralai import Mistral
import fitz  # PyMuPDF
from docx import Document
import os
import base64
from dotenv import load_dotenv

load_dotenv()

class DocumentProcessor:
    def __init__(self):
        self.mistral_client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

    def is_image_file(self, file_path):
        """Check if file is an image"""
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']
        return any(file_path.lower().endswith(ext) for ext in image_extensions)

    def get_file_type(self, file_path):
        """Determine file type for processing"""
        if file_path.endswith(".pdf"):
            return "pdf"
        elif file_path.endswith(".docx"):
            return "docx"
        elif self.is_image_file(file_path):
            return "image"
        else:
            return "unknown"

    def encode_pdf_to_base64(self, pdf_path):
        """Encode PDF to base64 for Mistral OCR"""
        try:
            with open(pdf_path, "rb") as pdf_file:
                return base64.b64encode(pdf_file.read()).decode('utf-8')
        except FileNotFoundError:
            print(f"Error: The file {pdf_path} was not found.")
            return None
        except Exception as e:
            print(f"Error encoding PDF: {e}")
            return None

    def encode_image_to_base64(self, image_path):
        """Encode image to base64 for Mistral OCR"""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except FileNotFoundError:
            print(f"Error: The file {image_path} was not found.")
            return None
        except Exception as e:
            print(f"Error encoding image: {e}")
            return None

    def extract_text_with_mistral_ocr(self, file_path, file_type="pdf"):
        """Extract text using Mistral OCR API"""
        try:
            if file_type == "pdf":
                base64_content = self.encode_pdf_to_base64(file_path)
                if not base64_content:
                    return ""

                ocr_response = self.mistral_client.ocr.process(
                    model="mistral-ocr-latest",
                    document={
                        "type": "document_url",
                        "document_url": f"data:application/pdf;base64,{base64_content}"
                    },
                    include_image_base64=False
                )
            else:  # image
                base64_content = self.encode_image_to_base64(file_path)
                if not base64_content:
                    return ""

                # Determine image type
                ext = file_path.lower().split('.')[-1]
                mime_type = f"image/{ext}" if ext in ['png', 'jpg', 'jpeg'] else "image/jpeg"

                ocr_response = self.mistral_client.ocr.process(
                    model="mistral-ocr-latest",
                    document={
                        "type": "image_url",
                        "image_url": f"data:{mime_type};base64,{base64_content}"
                    },
                    include_image_base64=False
                )

            # Extract text from response
            if hasattr(ocr_response, 'pages'):
                # Extract markdown content from all pages
                text_content = ""
                for page in ocr_response.pages:
                    if hasattr(page, 'markdown'):
                        text_content += page.markdown + "\n\n"
                return text_content
            elif hasattr(ocr_response, 'text'):
                return ocr_response.text
            elif hasattr(ocr_response, 'content'):
                return ocr_response.content
            else:
                print(f"Unexpected OCR response format: {ocr_response}")
                return ""

        except Exception as e:
            print(f"Error with Mistral OCR: {e}")
            return ""

    def extract_text(self, file_path):
        """Extract text from PDF, DOCX, or image files"""
        if file_path.endswith(".pdf"):
            try:
                # Try PyMuPDF for non-scanned PDF first
                doc = fitz.open(file_path)
                text = ""
                for page in doc:
                    text += page.get_text()
                doc.close()

                # If we got substantial text, it's likely not scanned
                if text.strip() and len(text.strip()) > 100:
                    print("Using PyMuPDF for text extraction")
                    return text
            except Exception as e:
                print(f"PyMuPDF failed: {e}")

            # Use Mistral OCR for scanned PDFs or if PyMuPDF failed
            print("Using Mistral OCR for PDF")
            return self.extract_text_with_mistral_ocr(file_path, "pdf")

        elif file_path.endswith(".docx"):
            try:
                doc = Document(file_path)
                return "\n".join([para.text for para in doc.paragraphs])
            except Exception as e:
                print(f"Error reading DOCX: {e}")
                return ""

        elif file_path.endswith((".jpg", ".jpeg", ".png")):
            print("Using Mistral OCR for image")
            return self.extract_text_with_mistral_ocr(file_path, "image")

        else:
            raise ValueError("Unsupported file type")

    def clean_text(self, text):
        """Clean extracted text"""
        import re
        # Remove page numbers, extra whitespace, and clean up formatting
        text = re.sub(r"Page \d+", "", text)
        text = re.sub(r"\[.*?\]", "", text)
        text = re.sub(r"\n\s*\n", "\n", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()
