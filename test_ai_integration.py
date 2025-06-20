"""
Test script for Mistral AI integration with DPA compliance checker
"""

import os
from dotenv import load_dotenv
from mistral_analyzer import mistral_analyzer
from dpa_compliance_checker import DPAComplianceChecker

load_dotenv()

def test_ai_integration():
    """Test the AI-enhanced DPA compliance analysis"""
    
    print("🤖 Testing Mistral AI Integration")
    print("=" * 50)
    
    # Check API key
    if not os.getenv("MISTRAL_API_KEY"):
        print("❌ Error: MISTRAL_API_KEY not found in environment variables")
        print("Please add your Mistral API key to the .env file:")
        print("MISTRAL_API_KEY=your_api_key_here")
        return
    
    # Initialize compliance checker
    checker = DPAComplianceChecker()
    
    # Test document with various compliance issues
    test_document = """
    Privacy Policy - XYZ Company
    
    We collect personal information including:
    - Full names: John Doe, Jane Smith
    - Email addresses: john@example.com, jane@company.com
    - Phone numbers: +63-912-345-6789, +63-917-987-6543
    - Credit card numbers: 4532-1234-5678-9012
    - Social Security Numbers: 123-45-6789
    
    We use this information for marketing purposes and may share it with third parties.
    We store data on our servers without encryption.
    Users cannot access or delete their personal information.
    We do not obtain consent before collecting sensitive information.
    
    Contact us at: privacy@xyz.com
    """
    
    print("📄 Test Document:")
    print(test_document[:200] + "...")
    
    print("\n🔍 Running AI-Enhanced Analysis...")
    
    try:
        # Test with AI enhancement enabled
        checker.set_ai_enhancement(True)
        ai_result = checker.analyze_document(test_document, "Test Privacy Policy")
        
        print("\n✅ AI-Enhanced Analysis Results:")
        print(f"Analysis Type: {ai_result.get('analysis_metadata', {}).get('analysis_type', 'Unknown')}")
        print(f"Compliance Status: {ai_result['compliance_status']}")
        print(f"Risk Level: {ai_result['risk_level']}")
        
        if 'ai_risk_level' in ai_result:
            print(f"AI Risk Assessment: {ai_result['ai_risk_level']}")
        
        print(f"Total Violations: {len(ai_result['violations'])}")
        ai_violations = [v for v in ai_result['violations'] if v.get('source') == 'mistral_ai']
        print(f"AI-Detected Violations: {len(ai_violations)}")
        
        print(f"Total Recommendations: {len(ai_result['recommendations'])}")
        ai_recommendations = [r for r in ai_result['recommendations'] if r.get('source') == 'mistral_ai']
        print(f"AI Recommendations: {len(ai_recommendations)}")
        
        # Show AI insights if available
        if 'ai_insights' in ai_result:
            ai_insights = ai_result['ai_insights']
            print(f"\n🤖 AI Insights:")
            print(f"Document Type: {ai_insights.get('document_type', 'Unknown')}")
            print(f"Processing Purpose: {ai_insights.get('processing_purpose', 'Not specified')}")
            print(f"Data Flow: {ai_insights.get('data_flow', 'Unknown')}")
            
            if ai_insights.get('compliance_gaps'):
                print(f"Compliance Gaps: {', '.join(ai_insights['compliance_gaps'])}")
        
        # Show top violations
        print(f"\n⚠️ Top Violations:")
        for i, violation in enumerate(ai_result['violations'][:3], 1):
            source = " (AI)" if violation.get('source') == 'mistral_ai' else " (KB)"
            print(f"{i}. {violation['section']}: {violation.get('violation', violation.get('title', 'Unknown'))}{source}")
            print(f"   Severity: {violation['severity']}")
            print(f"   Description: {violation['description'][:100]}...")
        
        # Show top recommendations
        print(f"\n✅ Top Recommendations:")
        for i, rec in enumerate(ai_result['recommendations'][:3], 1):
            source = " (AI)" if rec.get('source') == 'mistral_ai' else " (KB)"
            print(f"{i}. {rec['action']}{source}")
            print(f"   Priority: {rec['priority']}")
            print(f"   Description: {rec['description'][:100]}...")
        
        # Test traditional analysis for comparison
        print(f"\n📊 Comparing with Traditional Analysis...")
        checker.set_ai_enhancement(False)
        traditional_result = checker.analyze_document(test_document, "Test Privacy Policy")
        
        print(f"\n📈 Comparison Results:")
        print(f"Traditional Violations: {len(traditional_result['violations'])}")
        print(f"AI-Enhanced Violations: {len(ai_result['violations'])}")
        print(f"Traditional Recommendations: {len(traditional_result['recommendations'])}")
        print(f"AI-Enhanced Recommendations: {len(ai_result['recommendations'])}")
        
        improvement = len(ai_result['violations']) - len(traditional_result['violations'])
        if improvement > 0:
            print(f"✅ AI detected {improvement} additional violations")
        elif improvement < 0:
            print(f"⚠️ AI detected {abs(improvement)} fewer violations")
        else:
            print(f"📊 Same number of violations detected")
        
        return True
        
    except Exception as e:
        print(f"❌ AI Integration Test Failed: {e}")
        print(f"Error Type: {type(e).__name__}")
        
        # Test fallback to traditional analysis
        print(f"\n🔄 Testing Fallback to Traditional Analysis...")
        try:
            checker.set_ai_enhancement(False)
            fallback_result = checker.analyze_document(test_document, "Test Privacy Policy")
            print(f"✅ Fallback successful: {len(fallback_result['violations'])} violations found")
            return False
        except Exception as fallback_error:
            print(f"❌ Fallback also failed: {fallback_error}")
            return False

def test_mistral_direct():
    """Test Mistral AI directly"""
    print(f"\n🔧 Testing Mistral AI Direct Connection...")
    
    try:
        # Test simple analysis
        sample_text = "This document contains email addresses and phone numbers for marketing purposes."
        sample_pii = [
            {"text": "john@example.com", "entity_type": "EMAIL", "sensitive": False}
        ]
        
        result = mistral_analyzer.analyze_document_with_ai(sample_text, sample_pii, "Direct Test")
        
        print(f"✅ Direct Mistral AI test successful")
        print(f"Analysis Type: {result.get('analysis_metadata', {}).get('analysis_type', 'Unknown')}")
        print(f"Violations Found: {len(result.get('violations', []))}")
        print(f"Recommendations: {len(result.get('recommendations', []))}")
        
        return True
        
    except Exception as e:
        print(f"❌ Direct Mistral AI test failed: {e}")
        return False

def main():
    """Run all AI integration tests"""
    print("🚀 Mistral AI Integration Test Suite")
    print("=" * 60)
    
    # Test 1: Direct Mistral connection
    direct_success = test_mistral_direct()
    
    # Test 2: Full integration test
    integration_success = test_ai_integration()
    
    print(f"\n🎯 Test Results Summary:")
    print(f"Direct Mistral AI: {'✅ PASS' if direct_success else '❌ FAIL'}")
    print(f"Full Integration: {'✅ PASS' if integration_success else '❌ FAIL'}")
    
    if direct_success and integration_success:
        print(f"\n🎉 All tests passed! AI integration is working correctly.")
        print(f"Your DPA Compliance Checker now has AI-enhanced analysis capabilities!")
    elif direct_success:
        print(f"\n⚠️ Mistral AI works but integration has issues.")
        print(f"The system will fall back to traditional analysis.")
    else:
        print(f"\n❌ AI integration not working. Check your MISTRAL_API_KEY.")
        print(f"The system will use traditional analysis only.")
    
    print(f"\n📋 Next Steps:")
    print(f"1. Start the web application: python app.py")
    print(f"2. Upload a document to test AI-enhanced analysis")
    print(f"3. Look for the 'AI-Enhanced Analysis' banner in results")
    print(f"4. Compare AI insights with traditional analysis")

if __name__ == "__main__":
    main()
