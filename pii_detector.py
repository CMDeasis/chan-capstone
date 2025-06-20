"""
Enhanced PII Detector for Philippine Data Privacy Act Compliance
Detects both general and Philippine-specific personally identifiable information.
"""

import re
import spacy
from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
from dpa_knowledge import PHILIPPINE_PII_PATTERNS, SENSITIVE_KEYWORDS

class EnhancedPIIDetector:
    """Enhanced PII detector with Philippine-specific patterns"""
    
    def __init__(self):
        self.analyzer = AnalyzerEngine()
        self.nlp = spacy.load("en_core_web_sm")
        self._setup_philippine_recognizers()
    
    def _setup_philippine_recognizers(self):
        """Set up Philippine-specific PII recognizers"""
        
        # TIN (Tax Identification Number)
        tin_pattern = Pattern(name="PH_TIN", regex=PHILIPPINE_PII_PATTERNS["tin"], score=0.9)
        tin_recognizer = PatternRecognizer(
            supported_entity="PH_TIN", 
            patterns=[tin_pattern],
            context=["TIN", "tax", "identification", "number"]
        )
        
        # SSS Number
        sss_pattern = Pattern(name="PH_SSS", regex=PHILIPPINE_PII_PATTERNS["sss"], score=0.9)
        sss_recognizer = PatternRecognizer(
            supported_entity="PH_SSS",
            patterns=[sss_pattern],
            context=["SSS", "social security", "system"]
        )
        
        # PhilHealth Number
        philhealth_pattern = Pattern(name="PH_PHILHEALTH", regex=PHILIPPINE_PII_PATTERNS["philhealth"], score=0.9)
        philhealth_recognizer = PatternRecognizer(
            supported_entity="PH_PHILHEALTH",
            patterns=[philhealth_pattern],
            context=["PhilHealth", "health", "insurance"]
        )
        
        # UMID
        umid_pattern = Pattern(name="PH_UMID", regex=PHILIPPINE_PII_PATTERNS["umid"], score=0.9)
        umid_recognizer = PatternRecognizer(
            supported_entity="PH_UMID",
            patterns=[umid_pattern],
            context=["UMID", "unified", "multi-purpose", "ID"]
        )
        
        # Philippine Phone Numbers
        phone_pattern = Pattern(name="PH_PHONE", regex=PHILIPPINE_PII_PATTERNS["phone"], score=0.8)
        phone_recognizer = PatternRecognizer(
            supported_entity="PH_PHONE",
            patterns=[phone_pattern],
            context=["phone", "mobile", "cellphone", "telepono"]
        )
        
        # Health Information
        health_keywords = "|".join(SENSITIVE_KEYWORDS["health"])
        health_pattern = Pattern(name="HEALTH_INFO", regex=f"\\b({health_keywords})\\b", score=0.7)
        health_recognizer = PatternRecognizer(
            supported_entity="HEALTH_INFO",
            patterns=[health_pattern],
            context=["medical", "health", "disease", "condition"]
        )
        
        # Religious Information
        religious_keywords = "|".join(SENSITIVE_KEYWORDS["religious"])
        religious_pattern = Pattern(name="RELIGIOUS_INFO", regex=f"\\b({religious_keywords})\\b", score=0.7)
        religious_recognizer = PatternRecognizer(
            supported_entity="RELIGIOUS_INFO",
            patterns=[religious_pattern],
            context=["religion", "faith", "belief", "church"]
        )
        
        # Financial Information
        financial_keywords = "|".join(SENSITIVE_KEYWORDS["financial"])
        financial_pattern = Pattern(name="FINANCIAL_INFO", regex=f"\\b({financial_keywords})\\b", score=0.6)
        financial_recognizer = PatternRecognizer(
            supported_entity="FINANCIAL_INFO",
            patterns=[financial_pattern],
            context=["money", "salary", "income", "bank"]
        )
        
        # Add all recognizers to the analyzer
        recognizers = [
            tin_recognizer, sss_recognizer, philhealth_recognizer, 
            umid_recognizer, phone_recognizer, health_recognizer,
            religious_recognizer, financial_recognizer
        ]
        
        for recognizer in recognizers:
            self.analyzer.registry.add_recognizer(recognizer)
    
    def detect_pii(self, text):
        """Detect PII in the given text"""
        # Standard entities
        standard_entities = [
            "PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER", "CREDIT_CARD", 
            "IBAN_CODE", "IP_ADDRESS", "DATE_TIME", "LOCATION"
        ]
        
        # Philippine-specific entities
        ph_entities = [
            "PH_TIN", "PH_SSS", "PH_PHILHEALTH", "PH_UMID", "PH_PHONE"
        ]
        
        # Sensitive information entities
        sensitive_entities = [
            "HEALTH_INFO", "RELIGIOUS_INFO", "FINANCIAL_INFO"
        ]
        
        all_entities = standard_entities + ph_entities + sensitive_entities
        
        # Analyze text
        results = self.analyzer.analyze(
            text=text, 
            entities=all_entities, 
            language="en"
        )
        
        # Format results
        detected_pii = []
        for result in results:
            detected_pii.append({
                "entity_type": result.entity_type,
                "text": text[result.start:result.end],
                "start": result.start,
                "end": result.end,
                "confidence": result.score,
                "is_sensitive": result.entity_type in sensitive_entities + ph_entities
            })
        
        return detected_pii
    
    def categorize_pii(self, pii_results):
        """Categorize detected PII into regular and sensitive"""
        regular_pii = []
        sensitive_pii = []
        
        for pii in pii_results:
            if pii["is_sensitive"] or pii["entity_type"] in [
                "HEALTH_INFO", "RELIGIOUS_INFO", "FINANCIAL_INFO",
                "PH_TIN", "PH_SSS", "PH_PHILHEALTH"
            ]:
                sensitive_pii.append(pii)
            else:
                regular_pii.append(pii)
        
        return {
            "regular_pii": regular_pii,
            "sensitive_pii": sensitive_pii,
            "total_pii_count": len(pii_results),
            "sensitive_count": len(sensitive_pii),
            "regular_count": len(regular_pii)
        }
    
    def extract_names_with_spacy(self, text):
        """Extract person names using spaCy NER"""
        doc = self.nlp(text)
        names = []
        
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                names.append({
                    "text": ent.text,
                    "start": ent.start_char,
                    "end": ent.end_char,
                    "confidence": 0.8  # spaCy doesn't provide confidence scores
                })
        
        return names
    
    def detect_consent_indicators(self, text):
        """Detect consent-related language in the text"""
        consent_patterns = [
            r"\bconsent\b", r"\bagree\b", r"\bauthorize\b", r"\bpermit\b",
            r"\ballow\b", r"\bapprove\b", r"\baccept\b", r"\bpayag\b",
            r"\bsang-ayon\b", r"\bpahintulot\b"
        ]
        
        consent_indicators = []
        for pattern in consent_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                consent_indicators.append({
                    "text": match.group(),
                    "start": match.start(),
                    "end": match.end(),
                    "pattern": pattern
                })
        
        return consent_indicators
    
    def detect_purpose_statements(self, text):
        """Detect purpose statements in the text"""
        purpose_patterns = [
            r"\bpurpose\b", r"\bintended for\b", r"\bused for\b",
            r"\bprocessed for\b", r"\blayunin\b", r"\bgagamitin\b"
        ]
        
        purpose_indicators = []
        for pattern in purpose_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                purpose_indicators.append({
                    "text": match.group(),
                    "start": match.start(),
                    "end": match.end(),
                    "pattern": pattern
                })
        
        return purpose_indicators
