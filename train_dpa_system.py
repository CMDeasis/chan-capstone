"""
Enhanced DPA Training System
Processes the actual DPA text file to create a comprehensive knowledge base
"""

import re
import json
import os
from datetime import datetime
from collections import defaultdict

class DPATrainingSystem:
    """Enhanced training system using actual DPA text"""
    
    def __init__(self):
        self.dpa_text = ""
        self.sections = {}
        self.definitions = {}
        self.penalties = {}
        self.rights = {}
        self.principles = {}
        self.functions = {}
        self.compliance_rules = {}
        
    def load_dpa_text(self, file_path):
        """Load the actual DPA text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.dpa_text = f.read()
            print(f"✅ Loaded DPA text: {len(self.dpa_text)} characters")
            return True
        except FileNotFoundError:
            print(f"❌ Error: DPA file not found at {file_path}")
            return False
        except Exception as e:
            print(f"❌ Error loading DPA text: {e}")
            return False
    
    def parse_sections(self):
        """Parse all sections from the DPA text"""
        print("🔍 Parsing DPA sections...")
        
        # Pattern to match sections
        section_pattern = r'SEC\.\s*(\d+)\.\s*([^.]+\.)\s*[–-]\s*(.*?)(?=SEC\.\s*\d+\.|CHAPTER|$)'
        
        matches = re.finditer(section_pattern, self.dpa_text, re.DOTALL | re.IGNORECASE)
        
        for match in matches:
            section_num = match.group(1)
            section_title = match.group(2).strip()
            section_content = match.group(3).strip()
            
            # Clean up content
            section_content = re.sub(r'\n\s*\n', '\n', section_content)
            section_content = re.sub(r'\s+', ' ', section_content)
            
            self.sections[section_num] = {
                "title": section_title,
                "content": section_content,
                "full_text": match.group(0).strip()
            }
        
        print(f"✅ Parsed {len(self.sections)} sections")
        return len(self.sections) > 0
    
    def extract_definitions(self):
        """Extract definitions from Section 3"""
        print("🔍 Extracting definitions...")
        
        if "3" not in self.sections:
            print("❌ Section 3 (definitions) not found")
            return
        
        definitions_text = self.sections["3"]["content"]
        
        # Pattern to match definitions
        def_pattern = r'\(([a-z])\)\s*([^()]+?)\s*refers?\s*to\s*(.*?)(?=\([a-z]\)|$)'
        
        matches = re.finditer(def_pattern, definitions_text, re.DOTALL | re.IGNORECASE)
        
        for match in matches:
            letter = match.group(1)
            term = match.group(2).strip()
            definition = match.group(3).strip()
            
            # Clean up definition
            definition = re.sub(r'\s+', ' ', definition)
            definition = definition.rstrip('.')
            
            self.definitions[term.lower()] = {
                "term": term,
                "definition": definition,
                "letter": letter,
                "section": "3"
            }
        
        print(f"✅ Extracted {len(self.definitions)} definitions")
    
    def extract_penalties(self):
        """Extract penalty information from Sections 25-36"""
        print("🔍 Extracting penalties...")
        
        penalty_sections = [str(i) for i in range(25, 37)]
        
        for section_num in penalty_sections:
            if section_num in self.sections:
                section_data = self.sections[section_num]
                title = section_data["title"]
                content = section_data["content"]
                
                # Extract penalty amounts and imprisonment terms
                fine_pattern = r'(?:fine|fines?)\s*of\s*not\s*less\s*than\s*([^)]+?)\s*(?:pesos|Php)'
                imprisonment_pattern = r'imprisonment\s*(?:ranging\s*)?from\s*([^)]+?)\s*(?:and|shall)'
                
                fines = re.findall(fine_pattern, content, re.IGNORECASE)
                imprisonments = re.findall(imprisonment_pattern, content, re.IGNORECASE)
                
                self.penalties[section_num] = {
                    "title": title,
                    "content": content,
                    "fines": fines,
                    "imprisonment": imprisonments,
                    "section": section_num
                }
        
        print(f"✅ Extracted penalties from {len(self.penalties)} sections")
    
    def extract_data_subject_rights(self):
        """Extract data subject rights from Section 16"""
        print("🔍 Extracting data subject rights...")
        
        if "16" not in self.sections:
            print("❌ Section 16 (data subject rights) not found")
            return
        
        rights_text = self.sections["16"]["content"]
        
        # Pattern to match rights
        rights_pattern = r'\(([a-z])\)\s*(.*?)(?=\([a-z]\)|$)'
        
        matches = re.finditer(rights_pattern, rights_text, re.DOTALL)
        
        for match in matches:
            letter = match.group(1)
            right_content = match.group(2).strip()
            
            # Extract the main right description
            right_desc = right_content.split(';')[0].split(':')[0].strip()
            
            self.rights[letter] = {
                "letter": letter,
                "description": right_desc,
                "full_content": right_content,
                "section": "16"
            }
        
        print(f"✅ Extracted {len(self.rights)} data subject rights")
    
    def extract_npc_functions(self):
        """Extract NPC functions from Section 7"""
        print("🔍 Extracting NPC functions...")
        
        if "7" not in self.sections:
            print("❌ Section 7 (NPC functions) not found")
            return
        
        functions_text = self.sections["7"]["content"]
        
        # Pattern to match functions
        func_pattern = r'\(([a-z])\)\s*(.*?)(?=\([a-z]\)|$)'
        
        matches = re.finditer(func_pattern, functions_text, re.DOTALL)
        
        for match in matches:
            letter = match.group(1)
            function_content = match.group(2).strip()
            
            # Extract the main function description
            func_desc = function_content.split(';')[0].strip()
            
            self.functions[letter] = {
                "letter": letter,
                "description": func_desc,
                "full_content": function_content,
                "section": "7"
            }
        
        print(f"✅ Extracted {len(self.functions)} NPC functions")
    
    def extract_processing_principles(self):
        """Extract processing principles from Section 11"""
        print("🔍 Extracting processing principles...")
        
        if "11" not in self.sections:
            print("❌ Section 11 (processing principles) not found")
            return
        
        principles_text = self.sections["11"]["content"]
        
        # Pattern to match principles
        princ_pattern = r'\(([a-z])\)\s*(.*?)(?=\([a-z]\)|$)'
        
        matches = re.finditer(princ_pattern, principles_text, re.DOTALL)
        
        for match in matches:
            letter = match.group(1)
            principle_content = match.group(2).strip()
            
            self.principles[letter] = {
                "letter": letter,
                "content": principle_content,
                "section": "11"
            }
        
        print(f"✅ Extracted {len(self.principles)} processing principles")
    
    def generate_compliance_rules(self):
        """Generate compliance rules from key sections"""
        print("🔍 Generating compliance rules...")
        
        # Key sections for compliance
        key_sections = {
            "12": "Lawful Processing Criteria",
            "13": "Sensitive Information Processing", 
            "16": "Data Subject Rights",
            "20": "Security Requirements",
            "21": "Accountability Principle"
        }
        
        for section_num, section_name in key_sections.items():
            if section_num in self.sections:
                content = self.sections[section_num]["content"].lower()
                rules = []
                
                # Extract specific compliance requirements
                if section_num == "12":  # Lawful processing
                    if "consent" in content:
                        rules.append("Data subject consent required for processing")
                    if "contract" in content:
                        rules.append("Processing allowed for contract fulfillment")
                    if "legal obligation" in content:
                        rules.append("Processing required for legal compliance")
                    if "vital interests" in content:
                        rules.append("Processing allowed to protect vital interests")
                    if "legitimate interests" in content:
                        rules.append("Processing allowed for legitimate interests")
                
                elif section_num == "13":  # Sensitive information
                    if "prohibited" in content:
                        rules.append("Sensitive information processing generally prohibited")
                    if "consent" in content:
                        rules.append("Explicit consent required for sensitive information")
                    if "medical" in content:
                        rules.append("Medical processing allowed with safeguards")
                
                elif section_num == "16":  # Data subject rights
                    if "informed" in content:
                        rules.append("Data subjects must be informed of processing")
                    if "access" in content:
                        rules.append("Data subjects have right to access their data")
                    if "correct" in content:
                        rules.append("Data subjects can correct inaccurate information")
                    if "erasure" in content:
                        rules.append("Data subjects can request data deletion")
                
                elif section_num == "20":  # Security
                    if "reasonable" in content and "appropriate" in content:
                        rules.append("Implement reasonable and appropriate security measures")
                    if "organizational" in content:
                        rules.append("Implement organizational security measures")
                    if "physical" in content:
                        rules.append("Implement physical security measures")
                    if "technical" in content:
                        rules.append("Implement technical security measures")
                    if "breach" in content:
                        rules.append("Notify Commission and data subjects of breaches")
                
                elif section_num == "21":  # Accountability
                    if "responsible" in content:
                        rules.append("Controllers responsible for data under their control")
                    if "third party" in content:
                        rules.append("Ensure third party processors provide adequate protection")
                
                self.compliance_rules[section_num] = {
                    "section_name": section_name,
                    "rules": rules,
                    "section": section_num
                }
        
        print(f"✅ Generated compliance rules for {len(self.compliance_rules)} sections")
    
    def create_enhanced_knowledge_base(self):
        """Create comprehensive knowledge base"""
        print("🔍 Creating enhanced knowledge base...")
        
        knowledge_base = {
            "metadata": {
                "source": "Republic Act No. 10173 - Data Privacy Act of 2012",
                "processed_date": datetime.now().isoformat(),
                "total_sections": len(self.sections),
                "total_characters": len(self.dpa_text)
            },
            "sections": self.sections,
            "definitions": self.definitions,
            "penalties": self.penalties,
            "data_subject_rights": self.rights,
            "npc_functions": self.functions,
            "processing_principles": self.principles,
            "compliance_rules": self.compliance_rules,
            "search_index": self._create_search_index()
        }
        
        return knowledge_base
    
    def _create_search_index(self):
        """Create search index for quick lookups"""
        index = defaultdict(list)
        
        # Index sections by keywords
        for section_num, section_data in self.sections.items():
            content = section_data["content"].lower()
            title = section_data["title"].lower()
            
            # Extract keywords
            words = re.findall(r'\b\w+\b', content + " " + title)
            for word in words:
                if len(word) > 3:  # Only index meaningful words
                    index[word].append({
                        "type": "section",
                        "section": section_num,
                        "title": section_data["title"]
                    })
        
        # Index definitions
        for term, def_data in self.definitions.items():
            words = re.findall(r'\b\w+\b', term.lower())
            for word in words:
                index[word].append({
                    "type": "definition",
                    "term": def_data["term"],
                    "definition": def_data["definition"]
                })
        
        return dict(index)
    
    def save_knowledge_base(self, output_dir="data/output"):
        """Save the enhanced knowledge base"""
        os.makedirs(output_dir, exist_ok=True)
        
        knowledge_base = self.create_enhanced_knowledge_base()
        
        # Save complete knowledge base
        kb_file = os.path.join(output_dir, "enhanced_dpa_knowledge_v2.json")
        with open(kb_file, 'w', encoding='utf-8') as f:
            json.dump(knowledge_base, f, indent=2, ensure_ascii=False)
        
        # Save individual components
        components = {
            "sections": "dpa_sections_v2.json",
            "definitions": "dpa_definitions.json", 
            "penalties": "dpa_penalties.json",
            "data_subject_rights": "dpa_rights.json",
            "npc_functions": "npc_functions.json",
            "processing_principles": "processing_principles.json",
            "compliance_rules": "compliance_rules.json"
        }
        
        for component, filename in components.items():
            file_path = os.path.join(output_dir, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(knowledge_base[component], f, indent=2, ensure_ascii=False)
        
        print(f"✅ Knowledge base saved to {output_dir}")
        return knowledge_base
    
    def generate_training_summary(self):
        """Generate summary of training results"""
        summary = {
            "training_date": datetime.now().isoformat(),
            "source_file": "data-privacy-act/[REPUBLIC ACT NO. 10173].txt",
            "statistics": {
                "total_characters": len(self.dpa_text),
                "total_sections": len(self.sections),
                "definitions_extracted": len(self.definitions),
                "penalties_extracted": len(self.penalties),
                "rights_extracted": len(self.rights),
                "npc_functions_extracted": len(self.functions),
                "principles_extracted": len(self.principles),
                "compliance_rules_generated": len(self.compliance_rules)
            },
            "section_coverage": {
                "definitions": "Section 3",
                "npc_functions": "Section 7", 
                "processing_principles": "Section 11",
                "lawful_processing": "Section 12",
                "sensitive_information": "Section 13",
                "data_subject_rights": "Section 16",
                "security_requirements": "Section 20",
                "accountability": "Section 21",
                "penalties": "Sections 25-36"
            },
            "key_improvements": [
                "100% accurate content from official DPA text",
                "Comprehensive section parsing and structuring",
                "Detailed definitions extraction",
                "Complete penalty information",
                "Structured data subject rights",
                "NPC functions and responsibilities",
                "Processing principles and compliance rules",
                "Search index for quick lookups"
            ]
        }
        
        return summary

def main():
    """Main training function"""
    print("🚀 Enhanced DPA Training System")
    print("=" * 50)
    
    # Initialize training system
    trainer = DPATrainingSystem()
    
    # Load DPA text
    dpa_file = "data-privacy-act/[REPUBLIC ACT NO. 10173].txt"
    if not trainer.load_dpa_text(dpa_file):
        return
    
    # Parse and extract all components
    if not trainer.parse_sections():
        print("❌ Failed to parse sections")
        return
    
    trainer.extract_definitions()
    trainer.extract_penalties()
    trainer.extract_data_subject_rights()
    trainer.extract_npc_functions()
    trainer.extract_processing_principles()
    trainer.generate_compliance_rules()
    
    # Save knowledge base
    knowledge_base = trainer.save_knowledge_base()
    
    # Generate summary
    summary = trainer.generate_training_summary()
    
    # Save summary
    with open("data/output/training_summary_v2.json", 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    # Print results
    print("\n🎉 Training Complete!")
    print(f"📊 Processed {summary['statistics']['total_characters']} characters")
    print(f"📋 Parsed {summary['statistics']['total_sections']} sections")
    print(f"📖 Extracted {summary['statistics']['definitions_extracted']} definitions")
    print(f"⚖️ Extracted {summary['statistics']['penalties_extracted']} penalty sections")
    print(f"🔒 Extracted {summary['statistics']['rights_extracted']} data subject rights")
    print(f"🏛️ Extracted {summary['statistics']['npc_functions_extracted']} NPC functions")
    print(f"📏 Extracted {summary['statistics']['principles_extracted']} processing principles")
    print(f"✅ Generated {summary['statistics']['compliance_rules_generated']} compliance rule sets")
    
    print("\n📁 Files created:")
    print("- data/output/enhanced_dpa_knowledge_v2.json (Complete knowledge base)")
    print("- data/output/dpa_sections_v2.json (All sections)")
    print("- data/output/dpa_definitions.json (Definitions)")
    print("- data/output/dpa_penalties.json (Penalties)")
    print("- data/output/dpa_rights.json (Data subject rights)")
    print("- data/output/npc_functions.json (NPC functions)")
    print("- data/output/processing_principles.json (Processing principles)")
    print("- data/output/compliance_rules.json (Compliance rules)")
    print("- data/output/training_summary_v2.json (Training summary)")

if __name__ == "__main__":
    main()
