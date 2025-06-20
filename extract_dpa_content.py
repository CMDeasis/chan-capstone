"""
Extract and process the actual Data Privacy Act content from the PDF
This script will use Mistral OCR to extract text from the DPA PDF and create a knowledge base
"""

import os
import re
import json
from document_processor import DocumentProcessor
from dotenv import load_dotenv

load_dotenv()

class DPAContentExtractor:
    """Extract and process DPA content from the official PDF"""

    def __init__(self):
        self.processor = DocumentProcessor()
        self.dpa_text = ""
        self.sections = {}

    def extract_dpa_from_pdf(self, pdf_path):
        """Extract text from the DPA PDF using Mistral OCR"""
        print(f"Extracting text from {pdf_path}...")

        if not os.path.exists(pdf_path):
            print(f"Error: DPA PDF not found at {pdf_path}")
            return False

        try:
            # Extract text using our enhanced document processor
            self.dpa_text = self.processor.extract_text(pdf_path)

            if not self.dpa_text:
                print("Error: No text extracted from PDF")
                return False

            print(f"Successfully extracted {len(self.dpa_text)} characters from DPA PDF")

            # Save raw extracted text
            with open("data/output/dpa_raw_text.txt", "w", encoding="utf-8") as f:
                f.write(self.dpa_text)

            return True

        except Exception as e:
            print(f"Error extracting DPA content: {e}")
            return False

    def parse_sections(self):
        """Parse the DPA text into sections"""
        print("Parsing DPA sections...")

        # Use the raw text for better section detection
        text = self.dpa_text

        # More comprehensive pattern to match sections
        section_pattern = r"SEC\.\s+(\d+)\.\s*([^\n]+)"

        sections_found = {}
        matches = list(re.finditer(section_pattern, text, re.IGNORECASE | re.MULTILINE))

        for i, match in enumerate(matches):
            section_num = match.group(1)
            section_title = match.group(2).strip()
            start_pos = match.end()

            # Find the content until the next section or chapter
            if i + 1 < len(matches):
                # Next section exists
                end_pos = matches[i + 1].start()
            else:
                # Last section - find next chapter or end of document
                chapter_match = re.search(r"##\s*CHAPTER", text[start_pos:], re.IGNORECASE)
                if chapter_match:
                    end_pos = start_pos + chapter_match.start()
                else:
                    # Take remaining text but limit to reasonable length
                    end_pos = min(start_pos + 3000, len(text))

            content = text[start_pos:end_pos].strip()

            # Clean up content - remove extra whitespace and formatting
            content = re.sub(r'\n\s*\n', '\n', content)
            content = re.sub(r'\s+', ' ', content)

            sections_found[section_num] = {
                "title": section_title,
                "content": content,
                "full_text": match.group(0) + " " + content
            }

        self.sections = sections_found
        print(f"Found {len(self.sections)} sections")

        # Print section numbers found for debugging
        section_nums = sorted([int(k) for k in self.sections.keys() if k.isdigit()])
        print(f"Section numbers: {section_nums}")

        # Save parsed sections
        with open("data/output/dpa_sections.json", "w", encoding="utf-8") as f:
            json.dump(self.sections, f, indent=2, ensure_ascii=False)

        return len(self.sections) > 0

    def extract_key_definitions(self):
        """Extract key definitions from Section 3"""
        if "3" not in self.sections:
            print("Section 3 (Definitions) not found")
            return {}

        definitions_text = self.sections["3"]["content"]
        definitions = {}

        # Common definition patterns in legal documents
        definition_patterns = [
            r"([a-zA-Z\s]+)\s*[-–—]\s*([^.]+\.)",  # Term - definition.
            r"\"([^\"]+)\"\s*means\s*([^.]+\.)",    # "Term" means definition.
            r"([a-zA-Z\s]+)\s*means\s*([^.]+\.)",   # Term means definition.
        ]

        for pattern in definition_patterns:
            matches = re.finditer(pattern, definitions_text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                term = match.group(1).strip().lower()
                definition = match.group(2).strip()

                # Filter for key terms
                key_terms = [
                    "personal information", "sensitive personal information",
                    "processing", "consent", "data subject", "personal information controller",
                    "personal information processor", "data privacy", "data protection"
                ]

                if any(key_term in term for key_term in key_terms):
                    definitions[term] = definition

        return definitions

    def create_enhanced_knowledge_base(self):
        """Create an enhanced knowledge base from the extracted DPA content"""
        print("Creating enhanced knowledge base...")

        # Extract key definitions
        definitions = self.extract_key_definitions()

        # Create enhanced knowledge base structure
        enhanced_kb = {
            "source": "Republic Act No. 10173 - Data Privacy Act of 2012",
            "extraction_date": "2025-05-26",
            "total_sections": len(self.sections),
            "definitions": definitions,
            "sections": {}
        }

        # Process key sections for compliance checking
        key_sections = ["3", "11", "12", "13", "20", "25", "26", "27", "28"]

        for section_num in key_sections:
            if section_num in self.sections:
                section_data = self.sections[section_num]

                enhanced_kb["sections"][section_num] = {
                    "title": section_data["title"],
                    "content": section_data["content"],
                    "compliance_rules": self._extract_compliance_rules(section_num, section_data["content"]),
                    "keywords": self._extract_keywords(section_data["content"]),
                    "violations": self._identify_potential_violations(section_num, section_data["content"])
                }

        # Save enhanced knowledge base
        with open("data/output/enhanced_dpa_knowledge.json", "w", encoding="utf-8") as f:
            json.dump(enhanced_kb, f, indent=2, ensure_ascii=False)

        print("Enhanced knowledge base created successfully")
        return enhanced_kb

    def _extract_compliance_rules(self, section_num, content):
        """Extract compliance rules from section content"""
        rules = []

        # Section-specific rule extraction
        if section_num == "12":  # Lawful Processing
            if "consent" in content.lower():
                rules.append("Requires data subject consent")
            if "legal obligation" in content.lower():
                rules.append("Must comply with legal obligations")
            if "legitimate interest" in content.lower():
                rules.append("Must have legitimate interest")

        elif section_num == "13":  # Sensitive Personal Information
            if "consent" in content.lower():
                rules.append("Requires explicit consent for SPI")
            if "security" in content.lower():
                rules.append("Enhanced security measures required")

        elif section_num == "20":  # Security
            if "reasonable" in content.lower():
                rules.append("Implement reasonable security measures")
            if "appropriate" in content.lower():
                rules.append("Use appropriate technical safeguards")

        return rules

    def _extract_keywords(self, content):
        """Extract important keywords from section content"""
        # Common legal and privacy keywords
        keywords = []
        important_terms = [
            "consent", "processing", "personal information", "sensitive",
            "security", "protection", "rights", "lawful", "legitimate",
            "purpose", "necessary", "appropriate", "reasonable"
        ]

        content_lower = content.lower()
        for term in important_terms:
            if term in content_lower:
                keywords.append(term)

        return keywords

    def _identify_potential_violations(self, section_num, content):
        """Identify potential violation patterns based on section content"""
        violations = []

        if section_num == "12":
            violations.append({
                "type": "unauthorized_processing",
                "description": "Processing personal information without lawful basis",
                "indicators": ["no consent", "no legal basis", "unauthorized collection"]
            })

        elif section_num == "13":
            violations.append({
                "type": "inadequate_spi_protection",
                "description": "Inadequate protection of sensitive personal information",
                "indicators": ["health data", "religious info", "genetic data"]
            })

        elif section_num == "20":
            violations.append({
                "type": "inadequate_security",
                "description": "Failure to implement appropriate security measures",
                "indicators": ["unencrypted data", "no access controls", "insecure storage"]
            })

        return violations

    def generate_summary_report(self):
        """Generate a summary report of the extraction process"""
        print("\n" + "="*60)
        print("DPA CONTENT EXTRACTION SUMMARY")
        print("="*60)

        print(f"Total text extracted: {len(self.dpa_text)} characters")
        print(f"Sections found: {len(self.sections)}")

        if self.sections:
            print("\nSections identified:")
            for num, section in sorted(self.sections.items(), key=lambda x: int(x[0]) if x[0].isdigit() else 999):
                print(f"  Section {num}: {section['title'][:60]}...")

        print(f"\nFiles created:")
        print(f"  - data/output/dpa_raw_text.txt")
        print(f"  - data/output/dpa_sections.json")
        print(f"  - data/output/enhanced_dpa_knowledge.json")

def main():
    """Main function to extract DPA content"""

    # Check if Mistral API key is set
    if not os.getenv("MISTRAL_API_KEY"):
        print("Error: MISTRAL_API_KEY not found in environment variables")
        print("Please set your Mistral API key in the .env file")
        return

    # Initialize extractor
    extractor = DPAContentExtractor()

    # Look for the DPA PDF
    possible_paths = [
        "data-privacy-act/dataprivacyact.pdf",
        "data/input/dataprivacyact.pdf",
        "dataprivacyact.pdf"
    ]

    dpa_pdf_path = None
    for path in possible_paths:
        if os.path.exists(path):
            dpa_pdf_path = path
            break

    if not dpa_pdf_path:
        print("Error: DPA PDF not found. Please ensure the file is at one of these locations:")
        for path in possible_paths:
            print(f"  - {path}")
        return

    # Extract content from PDF
    if not extractor.extract_dpa_from_pdf(dpa_pdf_path):
        print("Failed to extract content from DPA PDF")
        return

    # Parse sections
    if not extractor.parse_sections():
        print("Failed to parse DPA sections")
        return

    # Create enhanced knowledge base
    enhanced_kb = extractor.create_enhanced_knowledge_base()

    # Generate summary
    extractor.generate_summary_report()

    print("\n✅ DPA content extraction completed successfully!")
    print("The system now has access to the actual DPA content for compliance checking.")

if __name__ == "__main__":
    main()
