"""
Enhanced DPA Knowledge Base using actual extracted content from the DPA PDF
This replaces the manual knowledge base with real DPA content
"""

import json
import os
import re

class EnhancedDPAKnowledge:
    """Enhanced DPA knowledge base using actual extracted content"""
    
    def __init__(self):
        self.sections = {}
        self.definitions = {}
        self.load_extracted_content()
    
    def load_extracted_content(self):
        """Load the extracted DPA content"""
        sections_file = "data/output/dpa_sections.json"
        
        if os.path.exists(sections_file):
            with open(sections_file, 'r', encoding='utf-8') as f:
                self.sections = json.load(f)
            print(f"Loaded {len(self.sections)} sections from extracted DPA content")
            
            # Extract definitions from Section 3
            self._extract_definitions()
        else:
            print("Warning: No extracted DPA content found. Run extract_dpa_content.py first.")
    
    def _extract_definitions(self):
        """Extract key definitions from Section 3"""
        if "3" not in self.sections:
            return
        
        section_3_content = self.sections["3"]["content"]
        
        # Extract definitions using patterns
        definition_patterns = [
            r'\(([a-z])\)\s*([^()]+?)\s*refers?\s+to\s*([^()]+?)(?=\s*\([a-z]\)|$)',
            r'\(([a-z])\)\s*([^()]+?)\s*means?\s*([^()]+?)(?=\s*\([a-z]\)|$)',
            r'\(([a-z])\)\s*([^()]+?)\s*shall\s+refer\s+to\s*([^()]+?)(?=\s*\([a-z]\)|$)'
        ]
        
        for pattern in definition_patterns:
            matches = re.finditer(pattern, section_3_content, re.IGNORECASE | re.DOTALL)
            for match in matches:
                letter = match.group(1)
                term = match.group(2).strip()
                definition = match.group(3).strip()
                
                # Clean up the definition
                definition = re.sub(r'\s+', ' ', definition)
                definition = definition.rstrip('.,;')
                
                self.definitions[term.lower()] = {
                    "term": term,
                    "definition": definition,
                    "section": "3",
                    "letter": letter
                }
    
    def get_section(self, section_number):
        """Get information about a specific DPA section"""
        return self.sections.get(str(section_number), {})
    
    def get_definition(self, term):
        """Get definition of a specific term"""
        return self.definitions.get(term.lower(), {})
    
    def get_compliance_rules(self, section_number):
        """Get compliance rules for a specific section"""
        section = self.get_section(section_number)
        if not section:
            return []
        
        content = section.get("content", "").lower()
        rules = []
        
        # Section-specific rule extraction based on actual content
        if section_number == "12":  # Lawful Processing
            if "consent" in content:
                rules.append("Data subject consent required")
            if "legal obligation" in content:
                rules.append("Must comply with legal obligations")
            if "legitimate interest" in content:
                rules.append("Must have legitimate interest")
            if "contract" in content:
                rules.append("Processing for contract fulfillment allowed")
            if "vital interest" in content:
                rules.append("Processing to protect vital interests allowed")
        
        elif section_number == "13":  # Sensitive Personal Information
            if "consent" in content:
                rules.append("Explicit consent required for sensitive personal information")
            if "prohibited" in content:
                rules.append("Processing of SPI generally prohibited except in specific cases")
            if "medical" in content:
                rules.append("Medical treatment exception applies")
        
        elif section_number == "11":  # General Principles
            if "transparency" in content:
                rules.append("Transparency principle must be followed")
            if "legitimate purpose" in content:
                rules.append("Must have legitimate purpose")
            if "proportionality" in content:
                rules.append("Processing must be proportional")
            if "specified" in content:
                rules.append("Purposes must be specified")
        
        elif section_number == "20":  # Security
            if "reasonable" in content:
                rules.append("Implement reasonable security measures")
            if "appropriate" in content:
                rules.append("Use appropriate technical safeguards")
            if "organizational" in content:
                rules.append("Implement organizational security measures")
            if "physical" in content:
                rules.append("Implement physical security measures")
        
        return rules
    
    def get_violation_patterns(self, section_number):
        """Get potential violation patterns for a section"""
        violations = []
        
        if section_number == "12":
            violations.append({
                "type": "unauthorized_processing",
                "description": "Processing personal information without lawful basis",
                "severity": "HIGH",
                "indicators": ["no consent", "no legal basis", "unauthorized collection"],
                "section_reference": "Section 12"
            })
        
        elif section_number == "13":
            violations.append({
                "type": "inadequate_spi_protection",
                "description": "Inadequate protection of sensitive personal information",
                "severity": "CRITICAL", 
                "indicators": ["health data", "religious info", "genetic data", "race", "political affiliation"],
                "section_reference": "Section 13"
            })
        
        elif section_number == "11":
            violations.extend([
                {
                    "type": "lack_of_transparency",
                    "description": "Failure to inform data subjects about processing",
                    "severity": "MEDIUM",
                    "indicators": ["no privacy notice", "no purpose statement"],
                    "section_reference": "Section 11"
                },
                {
                    "type": "excessive_processing",
                    "description": "Processing more data than necessary",
                    "severity": "MEDIUM",
                    "indicators": ["excessive data", "irrelevant information"],
                    "section_reference": "Section 11"
                }
            ])
        
        elif section_number == "20":
            violations.append({
                "type": "inadequate_security",
                "description": "Failure to implement appropriate security measures",
                "severity": "HIGH",
                "indicators": ["unencrypted data", "no access controls", "insecure storage"],
                "section_reference": "Section 20"
            })
        
        elif section_number in ["25", "26", "27", "28", "29", "30", "31", "32"]:
            # Penalty sections
            violations.append({
                "type": "criminal_violation",
                "description": f"Criminal violation under {self.get_section(section_number).get('title', 'DPA')}",
                "severity": "CRITICAL",
                "indicators": ["criminal penalty", "imprisonment", "fine"],
                "section_reference": f"Section {section_number}"
            })
        
        return violations
    
    def search_sections(self, keyword):
        """Search for sections containing a specific keyword"""
        results = []
        
        for section_num, section_data in self.sections.items():
            content = section_data.get("content", "").lower()
            title = section_data.get("title", "").lower()
            
            if keyword.lower() in content or keyword.lower() in title:
                results.append({
                    "section": section_num,
                    "title": section_data.get("title", ""),
                    "relevance": content.count(keyword.lower()) + title.count(keyword.lower()) * 2
                })
        
        # Sort by relevance
        results.sort(key=lambda x: x["relevance"], reverse=True)
        return results
    
    def get_key_sections_for_compliance(self):
        """Get the most important sections for compliance checking"""
        key_sections = {
            "3": "Definitions - Understanding key terms",
            "11": "General Data Privacy Principles",
            "12": "Criteria for Lawful Processing",
            "13": "Sensitive Personal Information",
            "16": "Rights of the Data Subject",
            "20": "Security of Personal Information",
            "25": "Unauthorized Processing Penalties",
            "26": "Negligent Access Penalties",
            "27": "Improper Disposal Penalties",
            "28": "Unauthorized Purposes Penalties"
        }
        
        available_sections = {}
        for section_num, description in key_sections.items():
            if section_num in self.sections:
                available_sections[section_num] = {
                    "description": description,
                    "title": self.sections[section_num].get("title", ""),
                    "content_length": len(self.sections[section_num].get("content", ""))
                }
        
        return available_sections
    
    def get_penalties_for_violation(self, violation_type):
        """Get penalty information for specific violation types"""
        penalty_sections = {
            "unauthorized_processing": "25",
            "negligent_access": "26", 
            "improper_disposal": "27",
            "unauthorized_purposes": "28",
            "intentional_breach": "29",
            "concealment": "30",
            "malicious_disclosure": "31",
            "unauthorized_disclosure": "32"
        }
        
        section_num = penalty_sections.get(violation_type)
        if section_num and section_num in self.sections:
            return {
                "section": section_num,
                "title": self.sections[section_num].get("title", ""),
                "content": self.sections[section_num].get("content", "")
            }
        
        return {}
    
    def generate_compliance_summary(self):
        """Generate a summary of DPA compliance requirements"""
        summary = {
            "total_sections": len(self.sections),
            "key_definitions": len(self.definitions),
            "compliance_areas": {
                "lawful_processing": self.get_section("12").get("title", ""),
                "sensitive_data": self.get_section("13").get("title", ""),
                "data_subject_rights": self.get_section("16").get("title", ""),
                "security_requirements": self.get_section("20").get("title", "")
            },
            "penalty_sections": [str(i) for i in range(25, 33) if str(i) in self.sections],
            "key_principles": self.get_compliance_rules("11")
        }
        
        return summary

# Global instance
enhanced_dpa_kb = EnhancedDPAKnowledge()
