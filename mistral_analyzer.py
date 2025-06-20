"""
Mistral AI Integration for Enhanced Document Analysis
Combines Mistral AI intelligence with actual DPA knowledge base
"""

import os
import base64
from mistralai import Mistral
from dotenv import load_dotenv
import json
from datetime import datetime
from enhanced_dpa_knowledge_v2 import enhanced_dpa_kb_v2
from PIL import Image
import io

load_dotenv()

class MistralDPAAnalyzer:
    """Enhanced DPA analyzer using Mistral AI with actual DPA knowledge"""

    def __init__(self):
        self.client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))
        self.text_model = "mistral-small-latest"
        self.vision_model = "pixtral-12b-2409"
        self.dpa_knowledge = enhanced_dpa_kb_v2

        if not os.getenv("MISTRAL_API_KEY"):
            raise ValueError("MISTRAL_API_KEY not found in environment variables")

    def analyze_document_with_ai(self, text, pii_data, document_name="Unknown Document", image_path=None):
        """Perform AI-enhanced DPA compliance analysis"""

        # Get baseline analysis from knowledge base
        baseline_analysis = self.dpa_knowledge.get_comprehensive_analysis(text, pii_data)

        # Enhance with Mistral AI analysis (text or image)
        if image_path:
            ai_analysis = self._get_mistral_image_analysis(image_path, text, pii_data)
            model_used = self.vision_model
            analysis_type = "hybrid_ai_vision_enhanced"
        else:
            ai_analysis = self._get_mistral_text_analysis(text, pii_data)
            model_used = self.text_model
            analysis_type = "hybrid_ai_enhanced"

        # Combine and validate results
        enhanced_analysis = self._combine_analyses(baseline_analysis, ai_analysis, text, pii_data)

        # Ensure required fields are in the main result
        enhanced_analysis["document_name"] = document_name
        enhanced_analysis["analysis_date"] = datetime.now().isoformat()

        # Add metadata
        enhanced_analysis["analysis_metadata"] = {
            "document_name": document_name,
            "analysis_date": datetime.now().isoformat(),
            "ai_model": model_used,
            "knowledge_base_version": "v2",
            "analysis_type": analysis_type,
            "has_image": image_path is not None
        }

        return enhanced_analysis

    def analyze_image_document(self, image_path, document_name="Unknown Image Document"):
        """Analyze image document using Pixtral vision model"""

        try:
            # First, extract text from image using Pixtral
            extracted_text = self._extract_text_from_image(image_path)

            # Detect PII in extracted text (using existing PII detector)
            from pii_detector import EnhancedPIIDetector
            pii_detector = EnhancedPIIDetector()
            pii_results = pii_detector.detect_pii(extracted_text)
            pii_categorized = pii_detector.categorize_pii(pii_results)

            # Perform AI-enhanced analysis with image context
            result = self.analyze_document_with_ai(
                extracted_text,
                pii_results,
                document_name,
                image_path=image_path
            )

            # Ensure pii_summary is included
            if 'pii_summary' not in result:
                result['pii_summary'] = pii_categorized

            # Add extracted text for reference
            result['extracted_text'] = extracted_text

            return result

        except Exception as e:
            print(f"❌ Image analysis failed: {e}")
            # Return basic analysis with error info and required fields
            return {
                "document_name": document_name,
                "analysis_date": datetime.now().isoformat(),
                "compliance_status": "ERROR",
                "risk_level": "UNKNOWN",
                "violations": [],
                "recommendations": [{
                    "priority": "HIGH",
                    "action": "Manual review required",
                    "description": f"Image analysis failed: {str(e)}",
                    "section_reference": "System Error"
                }],
                "pii_summary": {
                    "total_pii_count": 0,
                    "sensitive_count": 0,
                    "regular_count": 0,
                    "regular_pii": [],
                    "sensitive_pii": []
                },
                "analysis_metadata": {
                    "analysis_type": "image_analysis_failed",
                    "error": str(e)
                },
                "extracted_text": "Text extraction failed"
            }

    def _extract_text_from_image(self, image_path):
        """Extract text from image using Pixtral vision model"""

        try:
            # Encode image to base64
            image_base64 = self._encode_image_to_base64(image_path)

            response = self.client.chat.complete(
                model=self.vision_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert OCR system. Extract all text content from the provided image. Maintain the original structure and formatting as much as possible. Return only the extracted text without any additional commentary."
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Please extract all text from this image. Preserve the structure and formatting."
                            },
                            {
                                "type": "image_url",
                                "image_url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        ]
                    }
                ],
                max_tokens=2000,
                temperature=0.1
            )

            extracted_text = response.choices[0].message.content
            print(f"✅ Text extracted from image: {len(extracted_text)} characters")
            return extracted_text

        except Exception as e:
            print(f"❌ Text extraction from image failed: {e}")
            raise e

    def _encode_image_to_base64(self, image_path):
        """Encode image file to base64 string"""
        try:
            with open(image_path, "rb") as image_file:
                image_data = image_file.read()

            # Convert to base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            return image_base64

        except Exception as e:
            print(f"❌ Image encoding failed: {e}")
            raise e

    def _get_mistral_text_analysis(self, text, pii_data):
        """Get text analysis from Mistral AI using actual DPA context"""

        # Prepare context with actual DPA sections
        dpa_context = self._prepare_dpa_context()

        # Create analysis prompt
        prompt = self._create_analysis_prompt(text, pii_data, dpa_context)

        try:
            response = self.client.chat.complete(
                model=self.text_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert DPA compliance analyst. Analyze documents for violations of Philippine Republic Act No. 10173 (Data Privacy Act of 2012). Use the provided DPA context for accurate legal analysis."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=2000,
                temperature=0.1  # Low temperature for consistent legal analysis
            )

            ai_response = response.choices[0].message.content
            return self._parse_ai_response(ai_response)

        except Exception as e:
            print(f"❌ Mistral AI text analysis failed: {e}")
            return {"error": str(e), "ai_violations": [], "ai_recommendations": []}

    def _get_mistral_image_analysis(self, image_path, text, pii_data):
        """Get image analysis from Pixtral vision model with DPA context"""

        # Prepare context with actual DPA sections
        dpa_context = self._prepare_dpa_context()

        # Create image analysis prompt
        prompt = self._create_image_analysis_prompt(text, pii_data, dpa_context)

        try:
            # Encode image to base64
            image_base64 = self._encode_image_to_base64(image_path)

            response = self.client.chat.complete(
                model=self.vision_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert DPA compliance analyst with vision capabilities. Analyze image documents for violations of Philippine Republic Act No. 10173 (Data Privacy Act of 2012). Consider both the visual elements and extracted text. Use the provided DPA context for accurate legal analysis."
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        ]
                    }
                ],
                max_tokens=2000,
                temperature=0.1
            )

            ai_response = response.choices[0].message.content
            return self._parse_ai_response(ai_response)

        except Exception as e:
            print(f"❌ Mistral AI image analysis failed: {e}")
            return {"error": str(e), "ai_violations": [], "ai_recommendations": []}

    def _prepare_dpa_context(self):
        """Prepare relevant DPA context for AI analysis"""

        # Get key sections for context
        key_sections = ["11", "12", "13", "16", "20", "21"]
        context = {
            "dpa_title": "Republic Act No. 10173 - Data Privacy Act of 2012",
            "key_sections": {},
            "definitions": {},
            "penalties": {}
        }

        # Add section content
        for section_num in key_sections:
            section = self.dpa_knowledge.get_section(section_num)
            if section:
                context["key_sections"][section_num] = {
                    "title": section.get("title", ""),
                    "content": section.get("content", "")[:500] + "..."  # Truncate for token limit
                }

        # Add key definitions
        key_terms = ["personal information", "consent", "sensitive personal information", "processing"]
        for term in key_terms:
            definition = self.dpa_knowledge.get_definition(term)
            if definition:
                context["definitions"][term] = definition["definition"]

        # Add penalty information
        penalty_sections = ["25", "26", "27", "28"]
        for section_num in penalty_sections:
            penalty = self.dpa_knowledge.get_penalty_info(section_num)
            if penalty:
                context["penalties"][section_num] = {
                    "title": penalty.get("title", ""),
                    "fines": penalty.get("fines", []),
                    "imprisonment": penalty.get("imprisonment", [])
                }

        return context

    def _create_analysis_prompt(self, text, pii_data, dpa_context):
        """Create comprehensive analysis prompt for Mistral AI"""

        pii_summary = f"Found {len(pii_data)} PII instances: " + ", ".join([
            f"{item.get('entity_type', 'UNKNOWN')}: {item.get('text', '')[:20]}..."
            for item in pii_data[:5]
        ]) if pii_data else "No PII detected"

        prompt = f"""
PHILIPPINE DPA COMPLIANCE ANALYSIS

DOCUMENT TEXT TO ANALYZE:
{text[:2000]}...

PII DETECTED:
{pii_summary}

DPA LEGAL CONTEXT:
{json.dumps(dpa_context, indent=2)}

ANALYSIS REQUIREMENTS:
1. Identify specific DPA violations based on the provided legal context
2. Assess compliance with each relevant section (11, 12, 13, 16, 20, 21)
3. Evaluate the adequacy of consent mechanisms
4. Check for proper handling of sensitive personal information
5. Assess transparency and data subject rights compliance
6. Identify security and accountability issues

RESPONSE FORMAT (JSON):
{{
    "ai_violations": [
        {{
            "section": "Section X",
            "violation_type": "specific_violation_name",
            "severity": "LOW|MEDIUM|HIGH|CRITICAL",
            "description": "Clear description of the violation",
            "legal_basis": "Specific DPA requirement violated",
            "confidence": 0.0-1.0
        }}
    ],
    "ai_recommendations": [
        {{
            "priority": "LOW|MEDIUM|HIGH|CRITICAL",
            "action": "Specific action to take",
            "description": "Detailed recommendation",
            "section_reference": "Relevant DPA section",
            "implementation": "How to implement this recommendation"
        }}
    ],
    "ai_risk_assessment": {{
        "overall_risk": "LOW|MEDIUM|HIGH|CRITICAL",
        "risk_factors": ["factor1", "factor2"],
        "mitigation_priority": "immediate|short_term|medium_term|long_term"
    }},
    "ai_insights": {{
        "document_type": "inferred document type",
        "processing_purpose": "inferred purpose",
        "data_flow": "how data flows in the document",
        "compliance_gaps": ["gap1", "gap2"]
    }}
}}

Provide detailed, legally accurate analysis based on the actual DPA content provided.
"""

        return prompt

    def _create_image_analysis_prompt(self, text, pii_data, dpa_context):
        """Create comprehensive image analysis prompt for Pixtral vision model"""

        pii_summary = f"Found {len(pii_data)} PII instances: " + ", ".join([
            f"{item.get('entity_type', 'UNKNOWN')}: {item.get('text', '')[:20]}..."
            for item in pii_data[:5]
        ]) if pii_data else "No PII detected"

        prompt = f"""
PHILIPPINE DPA COMPLIANCE ANALYSIS - IMAGE DOCUMENT

EXTRACTED TEXT FROM IMAGE:
{text[:2000]}...

PII DETECTED IN TEXT:
{pii_summary}

DPA LEGAL CONTEXT:
{json.dumps(dpa_context, indent=2)}

ANALYSIS REQUIREMENTS:
Analyze this image document for DPA compliance considering:

1. VISUAL ELEMENTS:
   - Document type and layout
   - Forms, fields, and data collection methods
   - Visual indicators of consent mechanisms
   - Security warnings or privacy notices
   - Data handling procedures shown

2. TEXT CONTENT ANALYSIS:
   - Specific DPA violations based on the provided legal context
   - Compliance with each relevant section (11, 12, 13, 16, 20, 21)
   - Adequacy of consent mechanisms
   - Proper handling of sensitive personal information
   - Transparency and data subject rights compliance
   - Security and accountability measures

3. IMAGE-SPECIFIC CONSIDERATIONS:
   - Is this a form collecting personal information?
   - Are there visible consent checkboxes or signatures?
   - Does the document show proper data handling procedures?
   - Are there any visual security indicators?
   - Is sensitive information visibly exposed or protected?

RESPONSE FORMAT (JSON):
{{
    "ai_violations": [
        {{
            "section": "Section X",
            "violation_type": "specific_violation_name",
            "severity": "LOW|MEDIUM|HIGH|CRITICAL",
            "description": "Clear description of the violation",
            "legal_basis": "Specific DPA requirement violated",
            "confidence": 0.0-1.0,
            "visual_evidence": "What was observed in the image"
        }}
    ],
    "ai_recommendations": [
        {{
            "priority": "LOW|MEDIUM|HIGH|CRITICAL",
            "action": "Specific action to take",
            "description": "Detailed recommendation",
            "section_reference": "Relevant DPA section",
            "implementation": "How to implement this recommendation",
            "visual_improvement": "Specific visual/form improvements needed"
        }}
    ],
    "ai_risk_assessment": {{
        "overall_risk": "LOW|MEDIUM|HIGH|CRITICAL",
        "risk_factors": ["factor1", "factor2"],
        "mitigation_priority": "immediate|short_term|medium_term|long_term"
    }},
    "ai_insights": {{
        "document_type": "inferred document type from image",
        "processing_purpose": "inferred purpose from visual context",
        "data_flow": "how data flows based on visual elements",
        "compliance_gaps": ["gap1", "gap2"],
        "visual_observations": ["observation1", "observation2"],
        "form_analysis": "analysis of any forms or data collection elements",
        "consent_mechanisms": "visible consent elements or lack thereof"
    }}
}}

Provide detailed, legally accurate analysis based on both the visual elements and the actual DPA content provided.
"""

        return prompt

    def _parse_ai_response(self, ai_response):
        """Parse and validate AI response"""
        try:
            # Try to extract JSON from response
            json_start = ai_response.find('{')
            json_end = ai_response.rfind('}') + 1

            if json_start != -1 and json_end != -1:
                json_str = ai_response[json_start:json_end]
                parsed = json.loads(json_str)

                # Validate structure
                required_keys = ["ai_violations", "ai_recommendations", "ai_risk_assessment", "ai_insights"]
                for key in required_keys:
                    if key not in parsed:
                        parsed[key] = []

                return parsed
            else:
                # Fallback parsing
                return self._fallback_parse(ai_response)

        except json.JSONDecodeError:
            return self._fallback_parse(ai_response)

    def _fallback_parse(self, ai_response):
        """Fallback parsing when JSON parsing fails"""
        return {
            "ai_violations": [],
            "ai_recommendations": [],
            "ai_risk_assessment": {
                "overall_risk": "MEDIUM",
                "risk_factors": ["AI parsing error"],
                "mitigation_priority": "immediate"
            },
            "ai_insights": {
                "document_type": "unknown",
                "processing_purpose": "unknown",
                "data_flow": "unknown",
                "compliance_gaps": ["AI analysis incomplete"]
            },
            "raw_response": ai_response
        }

    def _combine_analyses(self, baseline_analysis, ai_analysis, text, pii_data):
        """Combine baseline knowledge base analysis with AI insights"""

        # Start with baseline analysis
        combined = baseline_analysis.copy()

        # Enhance violations with AI insights
        ai_violations = ai_analysis.get("ai_violations", [])
        baseline_violations = combined.get("violations", [])

        # Add AI-detected violations that aren't duplicates
        for ai_violation in ai_violations:
            if not self._is_duplicate_violation(ai_violation, baseline_violations):
                # Convert AI violation to standard format
                standard_violation = {
                    "section": ai_violation.get("section", "AI-Detected"),
                    "title": ai_violation.get("section", "AI-Detected Violation"),
                    "violation": ai_violation.get("violation_type", "ai_detected"),
                    "severity": ai_violation.get("severity", "MEDIUM"),
                    "description": ai_violation.get("description", ""),
                    "details": ai_violation.get("legal_basis", ""),
                    "confidence": ai_violation.get("confidence", 0.8),
                    "source": "mistral_ai"
                }
                combined["violations"].append(standard_violation)

        # Enhance recommendations with AI insights
        ai_recommendations = ai_analysis.get("ai_recommendations", [])
        baseline_recommendations = combined.get("recommendations", [])

        for ai_rec in ai_recommendations:
            if not self._is_duplicate_recommendation(ai_rec, baseline_recommendations):
                standard_rec = {
                    "priority": ai_rec.get("priority", "MEDIUM"),
                    "action": ai_rec.get("action", ""),
                    "description": ai_rec.get("description", ""),
                    "section_reference": ai_rec.get("section_reference", "AI Analysis"),
                    "implementation": ai_rec.get("implementation", ""),
                    "source": "mistral_ai"
                }
                combined["recommendations"].append(standard_rec)

        # Update risk level based on AI assessment
        ai_risk = ai_analysis.get("ai_risk_assessment", {})
        if ai_risk.get("overall_risk"):
            combined["ai_risk_level"] = ai_risk["overall_risk"]
            # Use higher risk level between baseline and AI
            risk_levels = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
            baseline_risk_idx = risk_levels.index(combined.get("risk_level", "LOW"))
            ai_risk_idx = risk_levels.index(ai_risk["overall_risk"])
            combined["risk_level"] = risk_levels[max(baseline_risk_idx, ai_risk_idx)]

        # Add AI insights
        combined["ai_insights"] = ai_analysis.get("ai_insights", {})
        combined["ai_risk_assessment"] = ai_risk

        # Update compliance status
        if combined["violations"]:
            combined["compliance_status"] = "NON-COMPLIANT"

        return combined

    def _is_duplicate_violation(self, ai_violation, baseline_violations):
        """Check if AI violation is duplicate of baseline violation"""
        ai_section = ai_violation.get("section", "").lower()
        ai_type = ai_violation.get("violation_type", "").lower()

        for baseline in baseline_violations:
            baseline_section = baseline.get("section", "").lower()
            baseline_type = baseline.get("violation", "").lower()

            if ai_section in baseline_section or baseline_section in ai_section:
                if ai_type in baseline_type or baseline_type in ai_type:
                    return True

        return False

    def _is_duplicate_recommendation(self, ai_rec, baseline_recommendations):
        """Check if AI recommendation is duplicate of baseline recommendation"""
        ai_action = ai_rec.get("action", "").lower()

        for baseline in baseline_recommendations:
            baseline_action = baseline.get("action", "").lower()

            if ai_action in baseline_action or baseline_action in ai_action:
                return True

        return False

    def get_ai_enhanced_summary(self, analysis_result):
        """Generate AI-enhanced summary"""
        ai_insights = analysis_result.get("ai_insights", {})

        summary = {
            "document_type": ai_insights.get("document_type", "Unknown"),
            "processing_purpose": ai_insights.get("processing_purpose", "Not specified"),
            "compliance_status": analysis_result.get("compliance_status", "UNKNOWN"),
            "risk_level": analysis_result.get("risk_level", "UNKNOWN"),
            "ai_risk_level": analysis_result.get("ai_risk_level", "UNKNOWN"),
            "total_violations": len(analysis_result.get("violations", [])),
            "ai_detected_violations": len([v for v in analysis_result.get("violations", []) if v.get("source") == "mistral_ai"]),
            "total_recommendations": len(analysis_result.get("recommendations", [])),
            "ai_recommendations": len([r for r in analysis_result.get("recommendations", []) if r.get("source") == "mistral_ai"]),
            "key_compliance_gaps": ai_insights.get("compliance_gaps", []),
            "mitigation_priority": analysis_result.get("ai_risk_assessment", {}).get("mitigation_priority", "medium_term")
        }

        return summary

# Global instance
mistral_analyzer = MistralDPAAnalyzer()
