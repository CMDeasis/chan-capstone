"""
Test script for Pixtral AI vision integration with DPA compliance checker
"""

import os
from dotenv import load_dotenv
from mistral_analyzer import mistral_analyzer
from PIL import Image, ImageDraw, ImageFont
import io

load_dotenv()

def create_test_image():
    """Create a test image with privacy policy content"""
    
    # Create a simple privacy policy image
    width, height = 800, 600
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    # Try to use a default font, fallback to basic if not available
    try:
        font_title = ImageFont.truetype("arial.ttf", 24)
        font_text = ImageFont.truetype("arial.ttf", 16)
    except:
        font_title = ImageFont.load_default()
        font_text = ImageFont.load_default()
    
    # Add privacy policy content
    y_position = 50
    
    # Title
    draw.text((50, y_position), "PRIVACY POLICY", fill='black', font=font_title)
    y_position += 60
    
    # Content
    privacy_content = [
        "XYZ Company Privacy Policy",
        "",
        "We collect the following personal information:",
        "• Full Name: John Doe, Jane Smith",
        "• Email: john@example.com, jane@company.com", 
        "• Phone: +63-912-345-6789",
        "• Credit Card: 4532-1234-5678-9012",
        "• SSN: 123-45-6789",
        "",
        "Data Usage:",
        "• Marketing purposes",
        "• Sharing with third parties",
        "• No encryption used",
        "",
        "Contact: privacy@xyz.com",
        "",
        "Note: No consent obtained before collection"
    ]
    
    for line in privacy_content:
        draw.text((50, y_position), line, fill='black', font=font_text)
        y_position += 25
    
    # Save test image
    test_image_path = "test_privacy_policy.png"
    image.save(test_image_path)
    print(f"✅ Created test image: {test_image_path}")
    
    return test_image_path

def test_image_analysis():
    """Test the AI vision analysis for image documents"""
    
    print("👁️ Testing Pixtral AI Vision Integration")
    print("=" * 50)
    
    # Check API key
    if not os.getenv("MISTRAL_API_KEY"):
        print("❌ Error: MISTRAL_API_KEY not found in environment variables")
        print("Please add your Mistral API key to the .env file:")
        print("MISTRAL_API_KEY=your_api_key_here")
        return False
    
    # Create test image
    test_image_path = create_test_image()
    
    try:
        print(f"\n📄 Test Image: {test_image_path}")
        print("🔍 Running AI Vision Analysis...")
        
        # Test image analysis
        result = mistral_analyzer.analyze_image_document(test_image_path, "Test Privacy Policy Image")
        
        print("\n✅ AI Vision Analysis Results:")
        print(f"Analysis Type: {result.get('analysis_metadata', {}).get('analysis_type', 'Unknown')}")
        print(f"AI Model: {result.get('analysis_metadata', {}).get('ai_model', 'Unknown')}")
        print(f"Has Image: {result.get('analysis_metadata', {}).get('has_image', False)}")
        print(f"Compliance Status: {result['compliance_status']}")
        print(f"Risk Level: {result['risk_level']}")
        
        if 'ai_risk_level' in result:
            print(f"AI Risk Assessment: {result['ai_risk_level']}")
        
        print(f"Total Violations: {len(result['violations'])}")
        ai_violations = [v for v in result['violations'] if v.get('source') == 'mistral_ai']
        print(f"AI-Detected Violations: {len(ai_violations)}")
        
        print(f"Total Recommendations: {len(result['recommendations'])}")
        ai_recommendations = [r for r in result['recommendations'] if r.get('source') == 'mistral_ai']
        print(f"AI Recommendations: {len(ai_recommendations)}")
        
        # Show AI insights if available
        if 'ai_insights' in result:
            ai_insights = result['ai_insights']
            print(f"\n👁️ AI Vision Insights:")
            print(f"Document Type: {ai_insights.get('document_type', 'Unknown')}")
            print(f"Processing Purpose: {ai_insights.get('processing_purpose', 'Not specified')}")
            
            if ai_insights.get('visual_observations'):
                print(f"Visual Observations: {', '.join(ai_insights['visual_observations'])}")
            
            if ai_insights.get('form_analysis'):
                print(f"Form Analysis: {ai_insights['form_analysis']}")
            
            if ai_insights.get('consent_mechanisms'):
                print(f"Consent Mechanisms: {ai_insights['consent_mechanisms']}")
            
            if ai_insights.get('compliance_gaps'):
                print(f"Compliance Gaps: {', '.join(ai_insights['compliance_gaps'])}")
        
        # Show top violations with visual evidence
        print(f"\n⚠️ Top Violations (with Visual Evidence):")
        for i, violation in enumerate(result['violations'][:3], 1):
            source = " (AI Vision)" if violation.get('source') == 'mistral_ai' else " (KB)"
            print(f"{i}. {violation['section']}: {violation.get('violation', violation.get('title', 'Unknown'))}{source}")
            print(f"   Severity: {violation['severity']}")
            print(f"   Description: {violation['description'][:100]}...")
            
            if violation.get('visual_evidence'):
                print(f"   Visual Evidence: {violation['visual_evidence']}")
        
        # Show top recommendations with visual improvements
        print(f"\n✅ Top Recommendations (with Visual Improvements):")
        for i, rec in enumerate(result['recommendations'][:3], 1):
            source = " (AI Vision)" if rec.get('source') == 'mistral_ai' else " (KB)"
            print(f"{i}. {rec['action']}{source}")
            print(f"   Priority: {rec['priority']}")
            print(f"   Description: {rec['description'][:100]}...")
            
            if rec.get('visual_improvement'):
                print(f"   Visual Improvement: {rec['visual_improvement']}")
        
        # Clean up test image
        if os.path.exists(test_image_path):
            os.remove(test_image_path)
            print(f"\n🧹 Cleaned up test image: {test_image_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ AI Vision Test Failed: {e}")
        print(f"Error Type: {type(e).__name__}")
        
        # Clean up on error
        if os.path.exists(test_image_path):
            os.remove(test_image_path)
        
        return False

def test_text_extraction():
    """Test text extraction from image using Pixtral"""
    print(f"\n🔧 Testing Pixtral Text Extraction...")
    
    try:
        # Create test image
        test_image_path = create_test_image()
        
        # Test text extraction
        extracted_text = mistral_analyzer._extract_text_from_image(test_image_path)
        
        print(f"✅ Text extraction successful")
        print(f"Extracted text length: {len(extracted_text)} characters")
        print(f"Text preview: {extracted_text[:200]}...")
        
        # Clean up
        if os.path.exists(test_image_path):
            os.remove(test_image_path)
        
        return True
        
    except Exception as e:
        print(f"❌ Text extraction test failed: {e}")
        return False

def test_image_encoding():
    """Test image encoding to base64"""
    print(f"\n🔧 Testing Image Encoding...")
    
    try:
        # Create test image
        test_image_path = create_test_image()
        
        # Test encoding
        base64_data = mistral_analyzer._encode_image_to_base64(test_image_path)
        
        print(f"✅ Image encoding successful")
        print(f"Base64 data length: {len(base64_data)} characters")
        print(f"Base64 preview: {base64_data[:50]}...")
        
        # Clean up
        if os.path.exists(test_image_path):
            os.remove(test_image_path)
        
        return True
        
    except Exception as e:
        print(f"❌ Image encoding test failed: {e}")
        return False

def main():
    """Run all AI vision integration tests"""
    print("👁️ Pixtral AI Vision Integration Test Suite")
    print("=" * 60)
    
    # Test 1: Image encoding
    encoding_success = test_image_encoding()
    
    # Test 2: Text extraction
    extraction_success = test_text_extraction()
    
    # Test 3: Full image analysis
    analysis_success = test_image_analysis()
    
    print(f"\n🎯 Test Results Summary:")
    print(f"Image Encoding: {'✅ PASS' if encoding_success else '❌ FAIL'}")
    print(f"Text Extraction: {'✅ PASS' if extraction_success else '❌ FAIL'}")
    print(f"Full Image Analysis: {'✅ PASS' if analysis_success else '❌ FAIL'}")
    
    if encoding_success and extraction_success and analysis_success:
        print(f"\n🎉 All tests passed! AI Vision integration is working correctly.")
        print(f"Your DPA Compliance Checker now has AI vision analysis capabilities!")
    elif encoding_success and extraction_success:
        print(f"\n⚠️ Basic vision functions work but full analysis has issues.")
        print(f"The system will fall back to traditional OCR + analysis.")
    else:
        print(f"\n❌ AI Vision integration not working. Check your MISTRAL_API_KEY.")
        print(f"The system will use traditional OCR analysis for images.")
    
    print(f"\n📋 Next Steps:")
    print(f"1. Start the web application: python app.py")
    print(f"2. Upload an image document (JPG, PNG, etc.)")
    print(f"3. Look for the 'AI Vision Analysis' banner in results")
    print(f"4. Check AI insights for visual observations and form analysis")

if __name__ == "__main__":
    main()
