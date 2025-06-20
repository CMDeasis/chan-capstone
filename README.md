# DPA Compliance Checker

A comprehensive system for analyzing documents for compliance with the **Republic Act No. 10173 - Data Privacy Act of 2012** (Philippines).

## Features

### 🔍 **Document Analysis**
- **Multi-format support**: PDF, DOCX, JPG, PNG
- **Text extraction**: Uses PyMuPDF for PDFs and Mistral OCR for scanned documents/images
- **Philippine-specific PII detection**: TIN, SSS, PhilHealth numbers, etc.
- **Sensitive information detection**: Health data, religious affiliation, financial information

### 📋 **DPA Compliance Checking**
- **Section 12**: Criteria for Lawful Processing of Personal Information
- **Section 13**: Sensitive Personal Information and Privileged Information
- **Section 11**: General Data Privacy Principles (Transparency, Proportionality)
- **Section 20**: Security of Personal Information
- **Section 25**: Data Privacy Rights

### 📊 **Comprehensive Reporting**
- **Web interface**: Real-time analysis results with visual indicators
- **PDF reports**: Detailed compliance reports with violations and recommendations
- **Risk assessment**: LOW, MEDIUM, HIGH, CRITICAL risk levels
- **Actionable recommendations**: Prioritized steps to achieve compliance

## Installation

### Prerequisites
- Python 3.8+
- Mistral AI API key (for OCR functionality)

### Setup
1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd redaction-system
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```

4. **Set up environment variables**
   ```bash
   echo "MISTRAL_API_KEY=your_api_key_here" > .env
   ```

## Usage

### Web Interface
1. **Start the application**
   ```bash
   python app.py
   ```

2. **Open browser**
   Navigate to `http://127.0.0.1:5000`

3. **Upload document**
   - Select a PDF, DOCX, JPG, or PNG file
   - Click "Analyze Document"
   - View compliance results and download PDF report

### Command Line Testing
```bash
python test_system.py
```
This creates sample documents and tests the compliance checker.

## System Architecture

### Core Components

1. **Document Processor** (`document_processor.py`)
   - Extracts text from various file formats
   - Uses Mistral OCR for scanned documents

2. **PII Detector** (`pii_detector.py`)
   - Detects Philippine-specific PII patterns
   - Uses Presidio and spaCy for entity recognition
   - Categorizes regular vs. sensitive PII

3. **DPA Knowledge Base** (`dpa_knowledge.py`)
   - Contains DPA sections and violation patterns
   - Philippine-specific compliance rules

4. **Compliance Checker** (`dpa_compliance_checker.py`)
   - Analyzes documents for DPA violations
   - Generates risk assessments and recommendations

5. **Report Generator** (`report_generator.py`)
   - Creates detailed PDF compliance reports
   - Professional formatting with color-coded results

6. **Web Interface** (`app.py`, `templates/index.html`)
   - Flask-based web application
   - Real-time document analysis and results display

## Sample Analysis Results

### Compliant Document
- ✅ **Status**: COMPLIANT
- 🟢 **Risk Level**: LOW
- **Features**: Has consent statements, clear purpose, minimal PII

### Non-Compliant Document
- ❌ **Status**: NON-COMPLIANT
- 🔴 **Risk Level**: CRITICAL
- **Issues**: No consent, sensitive PII, excessive data collection

## DPA Sections Covered

| Section | Title | Coverage |
|---------|-------|----------|
| Section 3 | Definition of Terms | ✅ PII/SPI definitions |
| Section 11 | General Data Privacy Principles | ✅ Transparency, Proportionality |
| Section 12 | Criteria for Lawful Processing | ✅ Consent requirements |
| Section 13 | Sensitive Personal Information | ✅ SPI protection |
| Section 20 | Security of Personal Information | ✅ Security measures |
| Section 25 | Data Privacy Rights | ✅ Rights awareness |

## Philippine PII Patterns Detected

- **TIN**: Tax Identification Number (XXX-XXX-XXX-XXX)
- **SSS**: Social Security System (XX-XXXXXXX-X)
- **PhilHealth**: Health Insurance (XX-XXXXXXXXX-X)
- **UMID**: Unified Multi-Purpose ID (XXXX-XXXXXXX-X)
- **Phone Numbers**: Philippine mobile/landline formats
- **Health Information**: Medical conditions, treatments
- **Religious Information**: Religious affiliations
- **Financial Information**: Salary, bank accounts

## API Endpoints

- `GET /` - Main web interface
- `POST /analyze` - Document analysis endpoint
- `GET /download_report/<filename>` - Download PDF reports

## File Structure

```
redaction-system/
├── app.py                      # Flask web application
├── document_processor.py       # Document text extraction
├── pii_detector.py            # PII detection engine
├── dpa_knowledge.py           # DPA knowledge base
├── dpa_compliance_checker.py  # Compliance analysis
├── report_generator.py        # PDF report generation
├── test_system.py            # Testing and sample data
├── requirements.txt          # Python dependencies
├── templates/
│   └── index.html           # Web interface
├── data/
│   ├── input/              # Sample documents
│   └── output/             # Generated reports
└── temp_uploads/           # Temporary file storage
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Disclaimer

This tool is designed to assist with DPA compliance analysis but should not be considered as legal advice. Always consult with legal professionals for official compliance verification.
