"""
Enhanced DPA Knowledge Base V2
Uses the newly trained knowledge base from actual DPA text
"""

import json
import os
import re
from datetime import datetime

class EnhancedDPAKnowledgeV2:
    """Enhanced DPA knowledge base using trained data from actual DPA text"""
    
    def __init__(self):
        self.knowledge_base = {}
        self.sections = {}
        self.definitions = {}
        self.penalties = {}
        self.rights = {}
        self.functions = {}
        self.principles = {}
        self.compliance_rules = {}
        self.search_index = {}
        self.load_knowledge_base()
    
    def load_knowledge_base(self):
        """Load the enhanced knowledge base"""
        kb_file = "data/output/enhanced_dpa_knowledge_v2.json"
        
        if os.path.exists(kb_file):
            with open(kb_file, 'r', encoding='utf-8') as f:
                self.knowledge_base = json.load(f)
            
            # Load individual components
            self.sections = self.knowledge_base.get("sections", {})
            self.definitions = self.knowledge_base.get("definitions", {})
            self.penalties = self.knowledge_base.get("penalties", {})
            self.rights = self.knowledge_base.get("data_subject_rights", {})
            self.functions = self.knowledge_base.get("npc_functions", {})
            self.principles = self.knowledge_base.get("processing_principles", {})
            self.compliance_rules = self.knowledge_base.get("compliance_rules", {})
            self.search_index = self.knowledge_base.get("search_index", {})
            
            print(f"✅ Loaded enhanced DPA knowledge base with {len(self.sections)} sections")
        else:
            print("❌ Enhanced knowledge base not found. Run train_dpa_system.py first.")
    
    def get_section(self, section_number):
        """Get a specific section"""
        return self.sections.get(str(section_number), {})
    
    def get_definition(self, term):
        """Get definition of a term"""
        term_lower = term.lower()
        for key, definition in self.definitions.items():
            if term_lower in key or key in term_lower:
                return definition
        return None
    
    def get_penalty_info(self, section_number):
        """Get penalty information for a section"""
        return self.penalties.get(str(section_number), {})
    
    def get_data_subject_rights(self):
        """Get all data subject rights"""
        return self.rights
    
    def get_npc_functions(self):
        """Get all NPC functions"""
        return self.functions
    
    def get_processing_principles(self):
        """Get all processing principles"""
        return self.principles
    
    def get_compliance_rules(self, section_number=None):
        """Get compliance rules for a section or all rules"""
        if section_number:
            return self.compliance_rules.get(str(section_number), {})
        return self.compliance_rules
    
    def search_content(self, keyword, limit=10):
        """Search for content by keyword"""
        keyword_lower = keyword.lower()
        results = []
        
        # Search in index
        if keyword_lower in self.search_index:
            results.extend(self.search_index[keyword_lower][:limit])
        
        # Search in sections if not enough results
        if len(results) < limit:
            for section_num, section_data in self.sections.items():
                if keyword_lower in section_data.get("content", "").lower():
                    results.append({
                        "type": "section_content",
                        "section": section_num,
                        "title": section_data.get("title", ""),
                        "relevance": section_data.get("content", "").lower().count(keyword_lower)
                    })
        
        # Sort by relevance
        results.sort(key=lambda x: x.get("relevance", 1), reverse=True)
        return results[:limit]
    
    def check_violation(self, text, pii_data, context="document"):
        """Check for DPA violations based on content and PII"""
        violations = []
        
        text_lower = text.lower()
        
        # Check for consent violations (Section 12)
        if pii_data and not self._has_consent_indicators(text_lower):
            violations.append({
                "section": "12",
                "title": "Criteria for Lawful Processing of Personal Information",
                "violation": "Processing without consent",
                "severity": "HIGH",
                "description": "Personal information appears to be processed without clear consent from data subjects",
                "dpa_reference": self.get_section("12").get("content", "")[:200] + "..."
            })
        
        # Check for sensitive information violations (Section 13)
        sensitive_pii = [item for item in pii_data if item.get("sensitive", False)]
        if sensitive_pii and not self._has_explicit_consent(text_lower):
            violations.append({
                "section": "13", 
                "title": "Sensitive Personal Information and Privileged Information",
                "violation": "Processing sensitive information without explicit consent",
                "severity": "CRITICAL",
                "description": "Sensitive personal information detected without explicit consent provisions",
                "dpa_reference": self.get_section("13").get("content", "")[:200] + "..."
            })
        
        # Check for transparency violations (Section 16)
        if pii_data and not self._has_transparency_indicators(text_lower):
            violations.append({
                "section": "16",
                "title": "Rights of the Data Subject",
                "violation": "Lack of transparency in data processing",
                "severity": "MEDIUM",
                "description": "Data subjects may not be adequately informed about data processing",
                "dpa_reference": self.get_section("16").get("content", "")[:200] + "..."
            })
        
        # Check for security violations (Section 20)
        if not self._has_security_measures(text_lower):
            violations.append({
                "section": "20",
                "title": "Security of Personal Information",
                "violation": "Inadequate security measures",
                "severity": "HIGH", 
                "description": "Document does not demonstrate adequate security measures for personal information",
                "dpa_reference": self.get_section("20").get("content", "")[:200] + "..."
            })
        
        return violations
    
    def generate_recommendations(self, violations, pii_data):
        """Generate recommendations based on violations"""
        recommendations = []
        
        violation_sections = [v.get("section") for v in violations]
        
        # Consent recommendations
        if "12" in violation_sections or "13" in violation_sections:
            recommendations.append({
                "priority": "CRITICAL",
                "action": "Implement proper consent mechanisms",
                "description": "Establish clear, specific, and informed consent procedures before collecting personal information",
                "section_reference": "Section 12 - Criteria for Lawful Processing"
            })
        
        # Transparency recommendations
        if "16" in violation_sections:
            recommendations.append({
                "priority": "HIGH",
                "action": "Enhance transparency and data subject notifications",
                "description": "Provide clear information about data processing purposes, methods, and data subject rights",
                "section_reference": "Section 16 - Rights of the Data Subject"
            })
        
        # Security recommendations
        if "20" in violation_sections:
            recommendations.append({
                "priority": "HIGH",
                "action": "Implement comprehensive security measures",
                "description": "Deploy organizational, physical, and technical safeguards to protect personal information",
                "section_reference": "Section 20 - Security of Personal Information"
            })
        
        # General recommendations based on PII presence
        if pii_data:
            recommendations.append({
                "priority": "MEDIUM",
                "action": "Conduct data protection impact assessment",
                "description": "Evaluate the risks and implement appropriate measures for personal data processing",
                "section_reference": "Section 11 - General Data Privacy Principles"
            })
        
        return recommendations
    
    def _has_consent_indicators(self, text):
        """Check if text has consent indicators"""
        consent_keywords = [
            "consent", "agree", "permission", "authorize", "approval",
            "opt-in", "accept", "acknowledge", "voluntary"
        ]
        return any(keyword in text for keyword in consent_keywords)
    
    def _has_explicit_consent(self, text):
        """Check if text has explicit consent for sensitive data"""
        explicit_keywords = [
            "explicit consent", "specific consent", "express consent",
            "written consent", "informed consent", "clear consent"
        ]
        return any(keyword in text for keyword in explicit_keywords)
    
    def _has_transparency_indicators(self, text):
        """Check if text has transparency indicators"""
        transparency_keywords = [
            "purpose", "notification", "inform", "disclose", "explain",
            "privacy policy", "data use", "processing purpose"
        ]
        return any(keyword in text for keyword in transparency_keywords)
    
    def _has_security_measures(self, text):
        """Check if text mentions security measures"""
        security_keywords = [
            "security", "encryption", "protection", "safeguard", "secure",
            "confidential", "access control", "authentication", "firewall"
        ]
        return any(keyword in text for keyword in security_keywords)
    
    def get_section_summary(self, section_number):
        """Get a summary of a specific section"""
        section = self.get_section(section_number)
        if not section:
            return None
        
        return {
            "section": section_number,
            "title": section.get("title", ""),
            "summary": section.get("content", "")[:300] + "..." if len(section.get("content", "")) > 300 else section.get("content", ""),
            "compliance_rules": self.get_compliance_rules(section_number).get("rules", []),
            "related_penalties": self.get_penalty_info(section_number)
        }
    
    def get_comprehensive_analysis(self, text, pii_data):
        """Get comprehensive DPA analysis"""
        violations = self.check_violation(text, pii_data)
        recommendations = self.generate_recommendations(violations, pii_data)
        
        # Calculate risk level
        risk_level = "LOW"
        if violations:
            critical_violations = [v for v in violations if v.get("severity") == "CRITICAL"]
            high_violations = [v for v in violations if v.get("severity") == "HIGH"]
            
            if critical_violations:
                risk_level = "CRITICAL"
            elif len(high_violations) >= 2:
                risk_level = "HIGH"
            elif high_violations:
                risk_level = "MEDIUM"
        
        # Determine compliance status
        compliance_status = "COMPLIANT" if not violations else "NON-COMPLIANT"
        
        return {
            "compliance_status": compliance_status,
            "risk_level": risk_level,
            "violations": violations,
            "recommendations": recommendations,
            "analysis_metadata": {
                "knowledge_base_version": "v2",
                "analysis_date": datetime.now().isoformat(),
                "sections_analyzed": len(self.sections),
                "total_pii_found": len(pii_data) if pii_data else 0
            }
        }
    
    def get_knowledge_base_stats(self):
        """Get statistics about the knowledge base"""
        return {
            "total_sections": len(self.sections),
            "definitions": len(self.definitions),
            "penalty_sections": len(self.penalties),
            "data_subject_rights": len(self.rights),
            "npc_functions": len(self.functions),
            "processing_principles": len(self.principles),
            "compliance_rule_sets": len(self.compliance_rules),
            "search_index_terms": len(self.search_index),
            "source": "Republic Act No. 10173 - Data Privacy Act of 2012",
            "last_updated": self.knowledge_base.get("metadata", {}).get("processed_date", "Unknown")
        }

# Global instance
enhanced_dpa_kb_v2 = EnhancedDPAKnowledgeV2()
