"""
DPA Knowledge Base - Republic Act No. 10173 (Data Privacy Act of 2012)
Contains key sections and provisions for compliance checking.
"""

class DPAKnowledge:
    """Knowledge base for the Data Privacy Act of 2012"""
    
    def __init__(self):
        self.sections = {
            "3": {
                "title": "Definition of Terms",
                "key_definitions": {
                    "personal_information": "Any information whether recorded in a material form or not, from which the identity of an individual is apparent or can be reasonably and directly ascertained by the entity holding the information, or when put together with other information would directly and certainly identify an individual.",
                    "sensitive_personal_information": "Personal information: (a) About an individual's race, ethnic origin, marital status, age, color, and religious, philosophical or political affiliations; (b) About an individual's health, education, genetic or sexual life of a person, or to any proceeding for any offense committed or alleged to have been committed by such person, the disposal of such proceedings, or the sentence of any court in such proceedings; (c) Issued by government agencies peculiar to an individual which includes, but not limited to, social security numbers, previous or current health records, licenses or its denials, suspension or revocation, and tax returns; and (d) Specifically established by an executive order or an act of Congress to be kept classified.",
                    "processing": "Any operation or any set of operations performed upon personal information including, but not limited to, the collection, recording, organization, storage, updating or modification, retrieval, consultation, use, consolidation, blocking, erasure or destruction of data.",
                    "consent": "Any freely given, specific, informed indication of will, whereby the data subject agrees to the collection and processing of personal information about and/or relating to him or her."
                }
            },
            "11": {
                "title": "General Data Privacy Principles",
                "principles": [
                    "Transparency - The data subject must be aware of the nature, purpose, and extent of the processing of his or her personal information",
                    "Legitimate purpose - The processing of personal information shall be compatible with a declared and specified purpose",
                    "Proportionality - The processing shall be adequate, relevant, suitable, necessary, and not excessive in relation to a declared and specified purpose"
                ]
            },
            "12": {
                "title": "Criteria for Lawful Processing of Personal Information",
                "lawful_criteria": [
                    "The data subject has given his or her consent",
                    "The processing is necessary for compliance with a legal obligation",
                    "The processing is necessary to protect the vital interests of the data subject or of another natural person",
                    "The processing is necessary for the performance of a task carried out in the public interest",
                    "The processing is necessary for the purposes of the legitimate interests pursued by the personal information controller"
                ]
            },
            "13": {
                "title": "Sensitive Personal Information and Privileged Information",
                "requirements": [
                    "The data subject has given his or her consent, specific to the purpose prior to the processing",
                    "The processing is provided for by existing laws and regulations",
                    "The processing is necessary to protect the life and health of the data subject or another person"
                ]
            },
            "20": {
                "title": "Security of Personal Information",
                "requirements": [
                    "The personal information controller must implement reasonable and appropriate organizational, physical, and technical measures",
                    "The security measures shall include safeguards to protect personal information against any accidental or unlawful destruction, alteration and disclosure",
                    "The measures shall be appropriate to the harm that might result from any unlawful destruction, alteration and disclosure"
                ]
            },
            "25": {
                "title": "Data Privacy Rights",
                "rights": [
                    "Right to be informed",
                    "Right to object",
                    "Right to access",
                    "Right to rectification",
                    "Right to erasure or blocking",
                    "Right to damages"
                ]
            }
        }
        
        self.violation_patterns = {
            "unauthorized_processing": {
                "section": "Section 12",
                "description": "Processing personal information without lawful basis",
                "indicators": ["no consent", "no legal basis", "unauthorized collection"]
            },
            "inadequate_spi_protection": {
                "section": "Section 13 & 20",
                "description": "Inadequate protection of sensitive personal information",
                "indicators": ["health data", "medical records", "genetic information", "religious affiliation"]
            },
            "lack_of_transparency": {
                "section": "Section 11",
                "description": "Failure to inform data subjects about processing",
                "indicators": ["no privacy notice", "no purpose statement", "undisclosed processing"]
            },
            "excessive_processing": {
                "section": "Section 11",
                "description": "Processing more data than necessary for the stated purpose",
                "indicators": ["excessive data collection", "irrelevant information", "disproportionate processing"]
            },
            "inadequate_security": {
                "section": "Section 20",
                "description": "Failure to implement appropriate security measures",
                "indicators": ["unencrypted data", "insecure storage", "no access controls"]
            }
        }
    
    def get_section(self, section_number):
        """Get information about a specific DPA section"""
        return self.sections.get(section_number, {})
    
    def get_violation_info(self, violation_type):
        """Get information about a specific violation type"""
        return self.violation_patterns.get(violation_type, {})
    
    def get_all_sections(self):
        """Get all DPA sections"""
        return self.sections
    
    def get_all_violations(self):
        """Get all violation patterns"""
        return self.violation_patterns

# Philippine-specific PII patterns
PHILIPPINE_PII_PATTERNS = {
    "tin": r"\b\d{3}-\d{3}-\d{3}-\d{3}\b",  # Tax Identification Number
    "sss": r"\b\d{2}-\d{7}-\d{1}\b",        # Social Security System Number
    "philhealth": r"\b\d{2}-\d{9}-\d{1}\b", # PhilHealth Number
    "umid": r"\b\d{4}-\d{7}-\d{1}\b",       # Unified Multi-Purpose ID
    "passport": r"\b[A-Z]{2}\d{7}\b",       # Philippine Passport
    "drivers_license": r"\b[A-Z]\d{2}-\d{2}-\d{6}\b", # Driver's License
    "phone": r"\b(\+63|0)\d{10}\b",         # Philippine Phone Numbers
    "landline": r"\b\(\d{2,3}\)\s?\d{3}-\d{4}\b" # Philippine Landline
}

# Sensitive information keywords (Filipino and English)
SENSITIVE_KEYWORDS = {
    "health": [
        "diabetes", "diabetic", "hypertension", "cancer", "HIV", "AIDS", 
        "mental health", "depression", "anxiety", "medical record", 
        "prescription", "diagnosis", "treatment", "surgery", "hospital",
        "may sakit", "ospital", "gamot", "operasyon", "doktor"
    ],
    "religious": [
        "Catholic", "Protestant", "Muslim", "Buddhist", "Hindu", "Iglesia",
        "Born Again", "Seventh Day Adventist", "religion", "faith",
        "relihiyon", "pananampalataya", "simbahan", "mosque", "temple"
    ],
    "political": [
        "political party", "candidate", "election", "vote", "campaign",
        "partido", "halalan", "boto", "kandidato", "pulitika"
    ],
    "financial": [
        "salary", "income", "bank account", "credit card", "loan", "debt",
        "sweldo", "kita", "utang", "bangko", "pera", "salapi"
    ]
}
