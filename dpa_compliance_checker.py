"""
DPA Compliance Checker
Analyzes documents for violations of the Data Privacy Act of 2012
"""

from enhanced_dpa_knowledge_v2 import enhanced_dpa_kb_v2
from pii_detector import EnhancedPIIDetector
from mistral_analyzer import mistral_analyzer
import re
from datetime import datetime

class DPAComplianceChecker:
    """Main compliance checker for DPA violations using actual DPA content"""

    def __init__(self):
        self.dpa_knowledge = enhanced_dpa_kb_v2
        self.pii_detector = EnhancedPIIDetector()
        self.mistral_analyzer = mistral_analyzer
        self.use_ai_enhancement = True  # Flag to enable/disable AI enhancement

    def analyze_document(self, text, document_name="Unknown Document"):
        """Perform comprehensive DPA compliance analysis with AI enhancement"""

        # Detect PII
        pii_results = self.pii_detector.detect_pii(text)
        pii_categorized = self.pii_detector.categorize_pii(pii_results)

        # Detect consent and purpose indicators
        consent_indicators = self.pii_detector.detect_consent_indicators(text)
        purpose_indicators = self.pii_detector.detect_purpose_statements(text)

        # Choose analysis method based on AI enhancement setting
        if self.use_ai_enhancement:
            try:
                # Use AI-enhanced analysis
                compliance_report = self.mistral_analyzer.analyze_document_with_ai(
                    text, pii_results, document_name
                )

                # Add traditional indicators for compatibility
                compliance_report["consent_indicators"] = consent_indicators
                compliance_report["purpose_indicators"] = purpose_indicators
                compliance_report["pii_summary"] = pii_categorized

                print("✅ AI-enhanced analysis completed")

            except Exception as e:
                print(f"⚠️ AI enhancement failed, falling back to traditional analysis: {e}")
                # Fallback to traditional analysis
                compliance_report = self._traditional_analysis(
                    text, document_name, pii_categorized, consent_indicators, purpose_indicators
                )
        else:
            # Use traditional analysis
            compliance_report = self._traditional_analysis(
                text, document_name, pii_categorized, consent_indicators, purpose_indicators
            )

        return compliance_report

    def _traditional_analysis(self, text, document_name, pii_categorized, consent_indicators, purpose_indicators):
        """Traditional analysis method (fallback)"""

        # Check for violations
        violations = self._check_violations(
            text, pii_categorized, consent_indicators, purpose_indicators
        )

        # Generate compliance report
        compliance_report = {
            "document_name": document_name,
            "analysis_date": datetime.now().isoformat(),
            "pii_summary": pii_categorized,
            "consent_indicators": consent_indicators,
            "purpose_indicators": purpose_indicators,
            "violations": violations,
            "compliance_status": "COMPLIANT" if not violations else "NON-COMPLIANT",
            "risk_level": self._assess_risk_level(violations, pii_categorized),
            "recommendations": self._generate_recommendations(violations, pii_categorized),
            "analysis_type": "traditional"
        }

        return compliance_report

    def _check_violations(self, text, pii_categorized, consent_indicators, purpose_indicators):
        """Check for specific DPA violations using actual DPA content"""
        violations = []

        # Get actual section information from extracted DPA content
        section_12 = self.dpa_knowledge.get_section("12")
        section_13 = self.dpa_knowledge.get_section("13")
        section_11 = self.dpa_knowledge.get_section("11")
        section_20 = self.dpa_knowledge.get_section("20")

        # Section 12: Unauthorized Processing
        if pii_categorized["total_pii_count"] > 0 and not consent_indicators:
            violations.append({
                "section": "Section 12",
                "violation_type": "unauthorized_processing",
                "title": section_12.get("title", "Criteria for Lawful Processing of Personal Information"),
                "description": "Personal information detected without evidence of consent or other lawful basis as required by Section 12",
                "severity": "HIGH",
                "details": f"Found {pii_categorized['total_pii_count']} PII instances without consent indicators. Section 12 requires: {self._get_section_summary(section_12)}",
                "affected_data": [pii["text"] for pii in pii_categorized["regular_pii"][:5]],
                "dpa_reference": section_12.get("content", "")[:200] + "..."
            })

        # Section 13: Sensitive Personal Information
        if pii_categorized["sensitive_count"] > 0:
            violations.append({
                "section": "Section 13",
                "violation_type": "inadequate_spi_protection",
                "title": section_13.get("title", "Sensitive Personal Information and Privileged Information"),
                "description": "Sensitive personal information detected without adequate protection measures as required by Section 13",
                "severity": "CRITICAL",
                "details": f"Found {pii_categorized['sensitive_count']} sensitive PII instances. Section 13 states: {self._get_section_summary(section_13)}",
                "affected_data": [pii["text"] for pii in pii_categorized["sensitive_pii"][:5]],
                "dpa_reference": section_13.get("content", "")[:200] + "..."
            })

        # Section 11: Lack of Transparency (Purpose)
        if pii_categorized["total_pii_count"] > 0 and not purpose_indicators:
            violations.append({
                "section": "Section 11",
                "violation_type": "lack_of_transparency",
                "title": section_11.get("title", "General Data Privacy Principles"),
                "description": "Personal information processing without clear purpose statement violates transparency principle",
                "severity": "MEDIUM",
                "details": f"No purpose statement found for data processing. Section 11 requires: {self._get_section_summary(section_11)}",
                "affected_data": [],
                "dpa_reference": section_11.get("content", "")[:200] + "..."
            })

        # Section 11: Proportionality Check
        if pii_categorized["total_pii_count"] > 10:  # Threshold for excessive data
            violations.append({
                "section": "Section 11",
                "violation_type": "excessive_processing",
                "title": section_11.get("title", "General Data Privacy Principles"),
                "description": "Potentially excessive personal information processing violates proportionality principle",
                "severity": "MEDIUM",
                "details": f"Large amount of PII detected ({pii_categorized['total_pii_count']} instances) may violate proportionality requirements",
                "affected_data": [],
                "dpa_reference": section_11.get("content", "")[:200] + "..."
            })

        # Section 20: Security Measures
        security_violations = self._check_security_violations(text, section_20)
        violations.extend(security_violations)

        return violations

    def _get_section_summary(self, section_data):
        """Get a brief summary of a section's key requirements"""
        if not section_data:
            return "Section content not available"

        content = section_data.get("content", "")
        # Extract first sentence or first 100 characters
        sentences = content.split('. ')
        if sentences:
            return sentences[0][:100] + "..."
        return content[:100] + "..."

    def _check_security_violations(self, text, section_20_data):
        """Check for security-related violations using actual Section 20 content"""
        violations = []

        # Check for unencrypted data indicators
        unencrypted_patterns = [
            r"\bunencrypted\b", r"\bplain text\b", r"\bno encryption\b",
            r"\bunsecured\b", r"\bno password\b", r"\bno security\b"
        ]

        for pattern in unencrypted_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                violations.append({
                    "section": "Section 20",
                    "violation_type": "inadequate_security",
                    "title": section_20_data.get("title", "Security of Personal Information"),
                    "description": "Inadequate security measures for personal information as required by Section 20",
                    "severity": "HIGH",
                    "details": f"Security concern detected: {pattern}. Section 20 requires: {self._get_section_summary(section_20_data)}",
                    "affected_data": [],
                    "dpa_reference": section_20_data.get("content", "")[:200] + "..."
                })
                break  # Only report once

        return violations

    def _assess_risk_level(self, violations, pii_categorized):
        """Assess overall risk level based on violations and PII"""
        if not violations:
            return "LOW"

        critical_count = sum(1 for v in violations if v["severity"] == "CRITICAL")
        high_count = sum(1 for v in violations if v["severity"] == "HIGH")

        if critical_count > 0 or pii_categorized["sensitive_count"] > 5:
            return "CRITICAL"
        elif high_count > 0 or pii_categorized["total_pii_count"] > 10:
            return "HIGH"
        else:
            return "MEDIUM"

    def _generate_recommendations(self, violations, pii_categorized):
        """Generate recommendations based on violations"""
        recommendations = []

        violation_types = [v["violation_type"] for v in violations]

        if "unauthorized_processing" in violation_types:
            recommendations.append({
                "priority": "HIGH",
                "action": "Obtain proper consent",
                "description": "Implement consent mechanisms before processing personal information",
                "section_reference": "Section 12"
            })

        if "inadequate_spi_protection" in violation_types:
            recommendations.append({
                "priority": "CRITICAL",
                "action": "Enhance SPI protection",
                "description": "Implement additional security measures for sensitive personal information",
                "section_reference": "Section 13, Section 20"
            })

        if "lack_of_transparency" in violation_types:
            recommendations.append({
                "priority": "MEDIUM",
                "action": "Add purpose statements",
                "description": "Clearly state the purpose for processing personal information",
                "section_reference": "Section 11"
            })

        if "excessive_processing" in violation_types:
            recommendations.append({
                "priority": "MEDIUM",
                "action": "Review data minimization",
                "description": "Ensure only necessary personal information is processed",
                "section_reference": "Section 11"
            })

        if "inadequate_security" in violation_types:
            recommendations.append({
                "priority": "HIGH",
                "action": "Implement security measures",
                "description": "Deploy appropriate technical and organizational security measures",
                "section_reference": "Section 20"
            })

        # General recommendations
        if pii_categorized["total_pii_count"] > 0:
            recommendations.append({
                "priority": "LOW",
                "action": "Conduct privacy impact assessment",
                "description": "Perform a comprehensive privacy impact assessment for this document",
                "section_reference": "General DPA Compliance"
            })

        return recommendations

    def generate_summary(self, compliance_report):
        """Generate a human-readable summary of the compliance report"""

        # Check if this is an AI-enhanced analysis
        is_ai_enhanced = "ai_insights" in compliance_report

        # Safely get PII information
        pii_summary = compliance_report.get("pii_summary", {})
        pii_found = pii_summary.get("total_pii_count", 0) if isinstance(pii_summary, dict) else 0
        sensitive_pii_found = pii_summary.get("sensitive_count", 0) if isinstance(pii_summary, dict) else 0

        # Safely get violations and recommendations
        violations = compliance_report.get("violations", [])
        recommendations = compliance_report.get("recommendations", [])

        summary = {
            "document": compliance_report.get("document_name", "Unknown Document"),
            "status": compliance_report.get("compliance_status", "UNKNOWN"),
            "risk_level": compliance_report.get("risk_level", "UNKNOWN"),
            "total_violations": len(violations),
            "pii_found": pii_found,
            "sensitive_pii_found": sensitive_pii_found,
            "key_issues": [v.get("description", "Unknown issue") for v in violations[:3]],
            "top_recommendations": [r.get("action", "Unknown recommendation") for r in recommendations[:3]],
            "analysis_type": "AI-Enhanced" if is_ai_enhanced else "Traditional"
        }

        # Add AI-specific insights if available
        if is_ai_enhanced:
            ai_insights = compliance_report.get("ai_insights", {})
            summary.update({
                "ai_document_type": ai_insights.get("document_type", "Unknown"),
                "ai_processing_purpose": ai_insights.get("processing_purpose", "Not specified"),
                "ai_risk_level": compliance_report.get("ai_risk_level", "Unknown"),
                "ai_detected_violations": len([v for v in violations if v.get("source") == "mistral_ai"]),
                "ai_recommendations": len([r for r in recommendations if r.get("source") == "mistral_ai"]),
                "compliance_gaps": ai_insights.get("compliance_gaps", [])
            })

        return summary

    def set_ai_enhancement(self, enabled=True):
        """Enable or disable AI enhancement"""
        self.use_ai_enhancement = enabled
        print(f"✅ AI enhancement {'enabled' if enabled else 'disabled'}")

    def get_ai_enhanced_summary(self, compliance_report):
        """Get AI-enhanced summary if available"""
        if hasattr(self.mistral_analyzer, 'get_ai_enhanced_summary'):
            return self.mistral_analyzer.get_ai_enhanced_summary(compliance_report)
        return self.generate_summary(compliance_report)
