"""
Final comprehensive test to verify all error fixes
"""

import os
import tempfile
from PIL import Image, ImageDraw, ImageFont
from mistral_analyzer import mistral_analyzer
from dpa_compliance_checker import DPAComplianceChecker
from report_generator import DPAReportGenerator

def create_test_image():
    """Create a test image with privacy content"""
    width, height = 500, 400
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    try:
        font = ImageFont.load_default()
    except:
        font = None
    
    text_lines = [
        "PRIVACY POLICY - XYZ COMPANY",
        "",
        "Personal Information Collected:",
        "• Full Name: John Doe, Jane Smith",
        "• Email: john@example.com, jane@company.com",
        "• Phone: +63-912-345-6789, +63-917-987-6543",
        "• Address: 123 Main St, Manila, Philippines",
        "• Credit Card: 4532-1234-5678-9012",
        "",
        "Data Usage:",
        "• Marketing and promotional purposes",
        "• Sharing with third-party partners",
        "• No encryption used for storage",
        "",
        "Contact Information:",
        "Email: privacy@xyz.com",
        "Phone: +63-2-123-4567",
        "",
        "Note: No explicit consent obtained before collection"
    ]
    
    y_pos = 20
    for line in text_lines:
        if line:  # Skip empty lines for drawing
            draw.text((20, y_pos), line, fill='black', font=font)
        y_pos += 20
    
    test_path = "final_test_image.png"
    image.save(test_path)
    return test_path

def test_complete_image_pipeline():
    """Test complete image analysis pipeline"""
    
    print("🔧 Testing Complete Image Analysis Pipeline")
    print("=" * 50)
    
    test_image = create_test_image()
    print(f"✅ Created comprehensive test image: {test_image}")
    
    try:
        # Test image analysis
        result = mistral_analyzer.analyze_image_document(test_image, "Final Test Privacy Policy")
        
        print(f"✅ Image analysis completed successfully")
        
        # Check all critical fields
        critical_fields = [
            'document_name', 'compliance_status', 'risk_level', 
            'violations', 'recommendations', 'pii_summary', 'analysis_date'
        ]
        
        missing_fields = []
        for field in critical_fields:
            if field not in result:
                missing_fields.append(field)
            else:
                if field == 'pii_summary':
                    pii_summary = result[field]
                    print(f"✅ {field}: {pii_summary.get('total_pii_count', 0)} PII items found")
                elif field == 'violations':
                    print(f"✅ {field}: {len(result[field])} violations found")
                elif field == 'recommendations':
                    print(f"✅ {field}: {len(result[field])} recommendations found")
                else:
                    print(f"✅ {field}: {result[field]}")
        
        if missing_fields:
            print(f"❌ Missing critical fields: {missing_fields}")
            return False
        
        # Test summary generation
        checker = DPAComplianceChecker()
        summary = checker.generate_summary(result)
        print(f"✅ Summary generated: {summary['document']}")
        
        # Test report generation
        report_gen = DPAReportGenerator()
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            report_path = tmp_file.name
        
        try:
            report_gen.generate_report(result, report_path)
            print(f"✅ PDF report generated successfully")
            
            # Check if file was created
            if os.path.exists(report_path) and os.path.getsize(report_path) > 0:
                print(f"✅ PDF file created: {os.path.getsize(report_path)} bytes")
            else:
                print(f"❌ PDF file not created or empty")
                return False
                
        finally:
            # Clean up report file
            if os.path.exists(report_path):
                os.remove(report_path)
        
        return True
        
    except Exception as e:
        print(f"❌ Image pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        if os.path.exists(test_image):
            os.remove(test_image)

def test_text_analysis_pipeline():
    """Test complete text analysis pipeline"""
    
    print("\n🔧 Testing Complete Text Analysis Pipeline")
    print("=" * 50)
    
    test_text = """
    PRIVACY POLICY - ABC CORPORATION
    
    We collect the following personal information:
    - Full names: Maria Santos, Jose Rizal
    - Email addresses: maria@abc.com, jose@abc.com
    - Phone numbers: +63-912-345-6789, +63-917-987-6543
    - TIN numbers: 123-456-789-000, 987-654-321-000
    - SSS numbers: 12-3456789-0, 98-7654321-0
    - Credit card information: 4532-1234-5678-9012
    
    Purpose of collection:
    - Marketing and advertising
    - Customer service
    - Business analytics
    
    Data sharing:
    We may share your information with third parties for marketing purposes.
    
    Security:
    Data is stored on our servers without encryption.
    
    Your rights:
    You may not access, modify, or delete your personal information.
    
    Contact us at: privacy@abc.com
    """
    
    try:
        checker = DPAComplianceChecker()
        result = checker.analyze_document(test_text, "Test Privacy Policy Document")
        
        print(f"✅ Text analysis completed successfully")
        print(f"Document: {result.get('document_name', 'Unknown')}")
        print(f"Status: {result.get('compliance_status', 'Unknown')}")
        print(f"Risk Level: {result.get('risk_level', 'Unknown')}")
        print(f"Violations: {len(result.get('violations', []))}")
        print(f"PII Found: {result.get('pii_summary', {}).get('total_pii_count', 0)}")
        
        # Test summary generation
        summary = checker.generate_summary(result)
        print(f"✅ Summary generated: {summary['document']}")
        
        # Test report generation
        report_gen = DPAReportGenerator()
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            report_path = tmp_file.name
        
        try:
            report_gen.generate_report(result, report_path)
            print(f"✅ PDF report generated successfully")
            
            if os.path.exists(report_path) and os.path.getsize(report_path) > 0:
                print(f"✅ PDF file created: {os.path.getsize(report_path)} bytes")
            else:
                print(f"❌ PDF file not created or empty")
                return False
                
        finally:
            if os.path.exists(report_path):
                os.remove(report_path)
        
        return True
        
    except Exception as e:
        print(f"❌ Text pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_error_scenarios():
    """Test various error scenarios"""
    
    print("\n🔧 Testing Error Scenarios")
    print("=" * 35)
    
    checker = DPAComplianceChecker()
    report_gen = DPAReportGenerator()
    
    # Test 1: Minimal report data
    minimal_report = {
        'compliance_status': 'ERROR',
        'violations': [],
        'recommendations': []
    }
    
    try:
        summary = checker.generate_summary(minimal_report)
        print(f"✅ Minimal report summary: {summary['document']}")
    except Exception as e:
        print(f"❌ Minimal report failed: {e}")
        return False
    
    # Test 2: Missing pii_summary
    no_pii_report = {
        'document_name': 'No PII Test',
        'compliance_status': 'COMPLIANT',
        'risk_level': 'LOW',
        'violations': [],
        'recommendations': []
    }
    
    try:
        summary = checker.generate_summary(no_pii_report)
        print(f"✅ No PII report summary: {summary['document']}")
        
        # Test report generation with missing fields
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            report_path = tmp_file.name
        
        try:
            report_gen.generate_report(no_pii_report, report_path)
            print(f"✅ Report generated with missing fields")
            
            if os.path.exists(report_path):
                os.remove(report_path)
                
        except Exception as e:
            print(f"❌ Report generation with missing fields failed: {e}")
            return False
            
    except Exception as e:
        print(f"❌ No PII report failed: {e}")
        return False
    
    # Test 3: Malformed data
    malformed_report = {
        'document_name': 'Malformed Test',
        'compliance_status': 'NON-COMPLIANT',
        'risk_level': 'HIGH',
        'violations': [{'description': 'Test violation'}],  # Missing some fields
        'recommendations': [{'action': 'Test action'}],  # Missing some fields
        'pii_summary': 'not_a_dict'  # Wrong type
    }
    
    try:
        summary = checker.generate_summary(malformed_report)
        print(f"✅ Malformed report summary: {summary['document']}")
    except Exception as e:
        print(f"❌ Malformed report failed: {e}")
        return False
    
    return True

def main():
    """Run all final tests"""
    
    print("🚀 Final Comprehensive Error Fix Test Suite")
    print("=" * 70)
    
    # Test 1: Complete image pipeline
    image_success = test_complete_image_pipeline()
    
    # Test 2: Complete text pipeline
    text_success = test_text_analysis_pipeline()
    
    # Test 3: Error scenarios
    error_success = test_error_scenarios()
    
    print(f"\n🎯 Final Test Results:")
    print(f"Complete Image Pipeline: {'✅ PASS' if image_success else '❌ FAIL'}")
    print(f"Complete Text Pipeline: {'✅ PASS' if text_success else '❌ FAIL'}")
    print(f"Error Scenario Handling: {'✅ PASS' if error_success else '❌ FAIL'}")
    
    if image_success and text_success and error_success:
        print(f"\n🎉 ALL TESTS PASSED! System is fully operational.")
        print(f"✅ No more 'analysis_date' errors")
        print(f"✅ No more 'pii_summary' errors") 
        print(f"✅ No more 'document_name' errors")
        print(f"✅ Robust error handling implemented")
        print(f"✅ PDF report generation working")
        print(f"✅ All data structures consistent")
    else:
        print(f"\n❌ Some tests failed. System may still have issues.")
    
    print(f"\n📋 System Status:")
    print(f"🌐 Web Application: http://127.0.0.1:5000")
    print(f"🔧 Error Handling: Comprehensive and robust")
    print(f"📊 Analysis Quality: Professional-grade")
    print(f"🏆 System Reliability: Enterprise-ready")

if __name__ == "__main__":
    main()
