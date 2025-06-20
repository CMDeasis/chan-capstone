from flask import Flask, request, render_template, jsonify, send_file
import os
from dotenv import load_dotenv
from document_processor import DocumentProcessor
from dpa_compliance_checker import DPAComplianceChecker
from report_generator import DPAReportGenerator
from datetime import datetime

load_dotenv()

app = Flask(__name__)

# Initialize components
document_processor = DocumentProcessor()
compliance_checker = DPAComplianceChecker()
report_generator = DPAReportGenerator()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'document' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file uploaded'}), 400

    file = request.files['document']
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'No file selected'}), 400

    try:
        # Save uploaded file temporarily
        temp_path = os.path.join('temp_uploads', file.filename)
        os.makedirs('temp_uploads', exist_ok=True)
        file.save(temp_path)

        # Determine file type
        file_type = document_processor.get_file_type(temp_path)

        # Process document based on type
        if file_type == "image":
            # Use AI vision analysis for images
            try:
                from mistral_analyzer import mistral_analyzer
                compliance_report = mistral_analyzer.analyze_image_document(temp_path, file.filename)
                cleaned_text = compliance_report.get('extracted_text', 'Text extraction from image')
                print("✅ Image document analyzed with AI vision")

                # Ensure all required fields are present
                if 'pii_summary' not in compliance_report:
                    compliance_report['pii_summary'] = {
                        "total_pii_count": 0,
                        "sensitive_count": 0,
                        "regular_count": 0,
                        "regular_pii": [],
                        "sensitive_pii": []
                    }

            except Exception as e:
                print(f"⚠️ AI vision analysis failed, falling back to OCR: {e}")
                # Fallback to traditional OCR + analysis
                text = document_processor.extract_text(temp_path)
                cleaned_text = document_processor.clean_text(text)
                compliance_report = compliance_checker.analyze_document(cleaned_text, file.filename)
        else:
            # Traditional text extraction for PDFs and DOCX
            text = document_processor.extract_text(temp_path)
            cleaned_text = document_processor.clean_text(text)
            compliance_report = compliance_checker.analyze_document(cleaned_text, file.filename)

        # Generate summary for web display
        try:
            summary = compliance_checker.generate_summary(compliance_report)
        except Exception as e:
            print(f"❌ Summary generation failed: {e}")
            # Create a basic summary as fallback
            summary = {
                "document": compliance_report.get("document_name", file.filename),
                "status": compliance_report.get("compliance_status", "ERROR"),
                "risk_level": compliance_report.get("risk_level", "UNKNOWN"),
                "total_violations": len(compliance_report.get("violations", [])),
                "pii_found": 0,
                "sensitive_pii_found": 0,
                "key_issues": ["Summary generation failed"],
                "top_recommendations": ["Manual review required"],
                "analysis_type": "Error"
            }

        # Generate PDF report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"dpa_report_{timestamp}.pdf"
        report_path = os.path.join('data', 'output', report_filename)

        # Ensure output directory exists
        os.makedirs(os.path.dirname(report_path), exist_ok=True)

        report_generator.generate_report(compliance_report, report_path)

        # Clean up temporary file
        os.remove(temp_path)

        # Check if AI enhancement was used
        is_ai_enhanced = "ai_insights" in compliance_report

        # Safely get data with fallbacks
        violations = compliance_report.get('violations', [])
        recommendations = compliance_report.get('recommendations', [])
        pii_summary = compliance_report.get('pii_summary', {
            'total_pii_count': 0,
            'sensitive_count': 0,
            'regular_count': 0,
            'regular_pii': [],
            'sensitive_pii': []
        })

        response_data = {
            'status': 'success',
            'summary': summary,
            'compliance_status': compliance_report.get('compliance_status', 'UNKNOWN'),
            'risk_level': compliance_report.get('risk_level', 'UNKNOWN'),
            'violations': violations,
            'recommendations': recommendations[:5],  # Top 5 recommendations
            'pii_summary': pii_summary,
            'report_filename': report_filename,
            'text_preview': cleaned_text[:500] + '...' if len(cleaned_text) > 500 else cleaned_text,
            'analysis_type': 'AI-Enhanced' if is_ai_enhanced else 'Traditional'
        }

        # Add AI-specific data if available
        if is_ai_enhanced:
            ai_insights = compliance_report.get('ai_insights', {})
            response_data.update({
                'ai_insights': ai_insights,
                'ai_risk_level': compliance_report.get('ai_risk_level', 'Unknown'),
                'ai_detected_violations': len([v for v in violations if v.get('source') == 'mistral_ai']),
                'ai_recommendations': len([r for r in recommendations if r.get('source') == 'mistral_ai']),
                'ai_document_type': ai_insights.get('document_type', 'Unknown'),
                'ai_processing_purpose': ai_insights.get('processing_purpose', 'Not specified')
            })

        return jsonify(response_data)

    except Exception as e:
        # Clean up on error
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.remove(temp_path)

        return jsonify({
            'status': 'error',
            'message': f'Error processing document: {str(e)}'
        }), 500

@app.route('/download_report/<filename>')
def download_report(filename):
    """Download the generated PDF report"""
    try:
        report_path = os.path.join('data', 'output', filename)
        if os.path.exists(report_path):
            return send_file(report_path, as_attachment=True, download_name=filename)
        else:
            return jsonify({'status': 'error', 'message': 'Report not found'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
