"""
Test script to verify all error fixes are working
"""

import os
from PIL import Image, ImageDraw, ImageFont
from mistral_analyzer import mistral_analyzer
from dpa_compliance_checker import DPAComplianceChecker

def create_test_image():
    """Create a test image with privacy content"""
    width, height = 400, 300
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    try:
        font = ImageFont.load_default()
    except:
        font = None
    
    text_lines = [
        "Privacy Policy",
        "Name: John Doe",
        "Email: john@example.com",
        "Phone: 123-456-7890",
        "We collect personal data for marketing.",
        "No consent obtained."
    ]
    
    y_pos = 30
    for line in text_lines:
        draw.text((20, y_pos), line, fill='black', font=font)
        y_pos += 25
    
    test_path = "error_test.png"
    image.save(test_path)
    return test_path

def test_image_analysis_complete():
    """Test complete image analysis pipeline"""
    
    print("🔧 Testing Complete Image Analysis Pipeline")
    print("=" * 50)
    
    test_image = create_test_image()
    print(f"✅ Created test image: {test_image}")
    
    try:
        # Test image analysis
        result = mistral_analyzer.analyze_image_document(test_image, "Error Test Image")
        
        print(f"✅ Image analysis completed")
        
        # Check all required fields
        required_fields = [
            'document_name', 'compliance_status', 'risk_level', 
            'violations', 'recommendations', 'pii_summary'
        ]
        
        missing_fields = []
        for field in required_fields:
            if field not in result:
                missing_fields.append(field)
            else:
                print(f"✅ {field}: Present")
        
        if missing_fields:
            print(f"❌ Missing fields: {missing_fields}")
            return False
        
        # Test pii_summary structure
        pii_summary = result['pii_summary']
        if isinstance(pii_summary, dict):
            required_pii_fields = ['total_pii_count', 'sensitive_count', 'regular_count']
            for field in required_pii_fields:
                if field in pii_summary:
                    print(f"✅ pii_summary.{field}: {pii_summary[field]}")
                else:
                    print(f"❌ pii_summary.{field}: Missing")
                    return False
        else:
            print(f"❌ pii_summary is not a dict: {type(pii_summary)}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Image analysis failed: {e}")
        return False
        
    finally:
        if os.path.exists(test_image):
            os.remove(test_image)

def test_summary_generation():
    """Test summary generation with various data structures"""
    
    print("\n🔧 Testing Summary Generation")
    print("=" * 40)
    
    checker = DPAComplianceChecker()
    
    # Test case 1: Normal compliance report
    normal_report = {
        'document_name': 'Test Document',
        'compliance_status': 'NON-COMPLIANT',
        'risk_level': 'HIGH',
        'violations': [
            {'description': 'Test violation', 'action': 'Fix it'}
        ],
        'recommendations': [
            {'action': 'Test recommendation'}
        ],
        'pii_summary': {
            'total_pii_count': 5,
            'sensitive_count': 2,
            'regular_count': 3
        }
    }
    
    try:
        summary1 = checker.generate_summary(normal_report)
        print(f"✅ Normal report summary: {summary1['document']}")
    except Exception as e:
        print(f"❌ Normal report failed: {e}")
        return False
    
    # Test case 2: AI-enhanced report
    ai_report = {
        'document_name': 'AI Test Document',
        'compliance_status': 'NON-COMPLIANT',
        'risk_level': 'CRITICAL',
        'violations': [
            {'description': 'AI violation', 'source': 'mistral_ai'}
        ],
        'recommendations': [
            {'action': 'AI recommendation', 'source': 'mistral_ai'}
        ],
        'pii_summary': {
            'total_pii_count': 3,
            'sensitive_count': 1,
            'regular_count': 2
        },
        'ai_insights': {
            'document_type': 'Privacy Policy',
            'processing_purpose': 'Marketing'
        },
        'ai_risk_level': 'HIGH'
    }
    
    try:
        summary2 = checker.generate_summary(ai_report)
        print(f"✅ AI report summary: {summary2['document']}")
        print(f"✅ AI document type: {summary2.get('ai_document_type', 'Not found')}")
    except Exception as e:
        print(f"❌ AI report failed: {e}")
        return False
    
    # Test case 3: Minimal/broken report
    minimal_report = {
        'compliance_status': 'ERROR'
    }
    
    try:
        summary3 = checker.generate_summary(minimal_report)
        print(f"✅ Minimal report summary: {summary3['document']}")
    except Exception as e:
        print(f"❌ Minimal report failed: {e}")
        return False
    
    # Test case 4: Missing pii_summary
    no_pii_report = {
        'document_name': 'No PII Document',
        'compliance_status': 'COMPLIANT',
        'risk_level': 'LOW',
        'violations': [],
        'recommendations': []
    }
    
    try:
        summary4 = checker.generate_summary(no_pii_report)
        print(f"✅ No PII report summary: {summary4['document']}")
        print(f"✅ PII found: {summary4['pii_found']}")
    except Exception as e:
        print(f"❌ No PII report failed: {e}")
        return False
    
    return True

def test_text_analysis():
    """Test traditional text analysis"""
    
    print("\n🔧 Testing Text Analysis")
    print("=" * 30)
    
    checker = DPAComplianceChecker()
    
    test_text = """
    Privacy Policy
    
    We collect personal information including:
    - Names: John Doe, Jane Smith
    - Emails: john@example.com
    - Phone: 123-456-7890
    
    We use this for marketing purposes.
    """
    
    try:
        result = checker.analyze_document(test_text, "Test Text Document")
        
        print(f"✅ Text analysis completed")
        print(f"Document: {result.get('document_name', 'Unknown')}")
        print(f"Status: {result.get('compliance_status', 'Unknown')}")
        print(f"Violations: {len(result.get('violations', []))}")
        print(f"PII found: {result.get('pii_summary', {}).get('total_pii_count', 0)}")
        
        # Test summary generation
        summary = checker.generate_summary(result)
        print(f"✅ Summary generated: {summary['document']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Text analysis failed: {e}")
        return False

def main():
    """Run all error fix tests"""
    
    print("🚀 Error Fix Verification Test Suite")
    print("=" * 60)
    
    # Test 1: Image analysis
    image_success = test_image_analysis_complete()
    
    # Test 2: Summary generation
    summary_success = test_summary_generation()
    
    # Test 3: Text analysis
    text_success = test_text_analysis()
    
    print(f"\n🎯 Test Results Summary:")
    print(f"Image Analysis: {'✅ PASS' if image_success else '❌ FAIL'}")
    print(f"Summary Generation: {'✅ PASS' if summary_success else '❌ FAIL'}")
    print(f"Text Analysis: {'✅ PASS' if text_success else '❌ FAIL'}")
    
    if image_success and summary_success and text_success:
        print(f"\n🎉 All tests passed! Error fixes are working correctly.")
        print(f"The web application should now handle all document types without errors.")
    else:
        print(f"\n❌ Some tests failed. There may still be issues.")
    
    print(f"\n📋 Next Steps:")
    print(f"1. The web application is running at http://127.0.0.1:5000")
    print(f"2. Try uploading both text and image documents")
    print(f"3. Verify that analysis completes without 500 errors")
    print(f"4. Check that all results display properly")

if __name__ == "__main__":
    main()
