"""
Test script to verify the pii_summary fix for image analysis
"""

import os
from PIL import Image, ImageDraw, ImageFont
from mistral_analyzer import mistral_analyzer

def create_simple_test_image():
    """Create a simple test image"""
    width, height = 400, 300
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    # Add simple text
    try:
        font = ImageFont.load_default()
    except:
        font = None
    
    text_lines = [
        "Privacy Policy",
        "Name: John Doe",
        "Email: john@example.com",
        "Phone: 123-456-7890"
    ]
    
    y_pos = 50
    for line in text_lines:
        draw.text((20, y_pos), line, fill='black', font=font)
        y_pos += 30
    
    test_path = "simple_test.png"
    image.save(test_path)
    return test_path

def test_image_analysis_fix():
    """Test that image analysis returns proper pii_summary"""
    
    print("🔧 Testing Image Analysis Fix")
    print("=" * 40)
    
    # Create test image
    test_image = create_simple_test_image()
    print(f"✅ Created test image: {test_image}")
    
    try:
        # Test image analysis
        result = mistral_analyzer.analyze_image_document(test_image, "Test Image")
        
        print(f"✅ Image analysis completed")
        print(f"Document Name: {result.get('document_name', 'Unknown')}")
        print(f"Compliance Status: {result.get('compliance_status', 'Unknown')}")
        
        # Check if pii_summary exists
        if 'pii_summary' in result:
            pii_summary = result['pii_summary']
            print(f"✅ pii_summary found:")
            print(f"  Total PII: {pii_summary.get('total_pii_count', 0)}")
            print(f"  Sensitive: {pii_summary.get('sensitive_count', 0)}")
            print(f"  Regular: {pii_summary.get('regular_count', 0)}")
        else:
            print(f"❌ pii_summary missing!")
            return False
        
        # Check if extracted_text exists
        if 'extracted_text' in result:
            extracted_text = result['extracted_text']
            print(f"✅ extracted_text found: {len(extracted_text)} characters")
            print(f"  Preview: {extracted_text[:100]}...")
        else:
            print(f"⚠️ extracted_text missing")
        
        # Check required fields
        required_fields = ['compliance_status', 'risk_level', 'violations', 'recommendations']
        missing_fields = [field for field in required_fields if field not in result]
        
        if missing_fields:
            print(f"❌ Missing required fields: {missing_fields}")
            return False
        else:
            print(f"✅ All required fields present")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
        
    finally:
        # Clean up
        if os.path.exists(test_image):
            os.remove(test_image)
            print(f"🧹 Cleaned up test image")

def main():
    """Run the fix test"""
    success = test_image_analysis_fix()
    
    if success:
        print(f"\n🎉 Fix successful! Image analysis now works properly.")
        print(f"The web application should handle image uploads without errors.")
    else:
        print(f"\n❌ Fix failed. There may still be issues with image analysis.")
    
    print(f"\nNext steps:")
    print(f"1. The web application is running at http://127.0.0.1:5000")
    print(f"2. Try uploading an image file")
    print(f"3. Check that analysis completes without errors")

if __name__ == "__main__":
    main()
