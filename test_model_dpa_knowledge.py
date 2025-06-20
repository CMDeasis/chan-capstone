"""
Test script to verify if AI models have knowledge of the Data Privacy Act
"""

import os
from mistralai import Mistral
from dotenv import load_dotenv
import json

load_dotenv()

class DPAModelTester:
    """Test various models for DPA knowledge"""
    
    def __init__(self):
        self.mistral_client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))
        
    def test_mistral_dpa_knowledge(self):
        """Test Mistral's knowledge of Philippine DPA"""
        print("🔍 Testing Mistral's DPA Knowledge...")
        
        test_questions = [
            "What is Republic Act No. 10173?",
            "What are the key principles of the Philippine Data Privacy Act?",
            "What constitutes sensitive personal information under Philippine DPA?",
            "What are the penalties for DPA violations in the Philippines?",
            "What is the role of the National Privacy Commission in the Philippines?",
            "What are the data subject rights under Philippine DPA Section 16?",
            "What constitutes lawful processing under Philippine DPA Section 12?",
            "What are the security requirements under Philippine DPA Section 20?"
        ]
        
        results = {}
        
        for question in test_questions:
            try:
                response = self.mistral_client.chat.complete(
                    model="mistral-large-latest",
                    messages=[
                        {
                            "role": "user", 
                            "content": f"{question} Please be specific about Philippine law."
                        }
                    ],
                    max_tokens=500
                )
                
                answer = response.choices[0].message.content
                results[question] = {
                    "answer": answer,
                    "mentions_philippines": "philippines" in answer.lower() or "philippine" in answer.lower(),
                    "mentions_ra_10173": "10173" in answer or "republic act" in answer.lower(),
                    "mentions_npc": "national privacy commission" in answer.lower() or "npc" in answer.lower(),
                    "answer_length": len(answer)
                }
                
                print(f"\n❓ {question}")
                print(f"✅ Answer: {answer[:200]}...")
                print(f"📊 Philippines mentioned: {results[question]['mentions_philippines']}")
                print(f"📊 RA 10173 mentioned: {results[question]['mentions_ra_10173']}")
                
            except Exception as e:
                print(f"❌ Error testing question '{question}': {e}")
                results[question] = {"error": str(e)}
        
        return results
    
    def test_model_specific_sections(self):
        """Test knowledge of specific DPA sections"""
        print("\n🔍 Testing Specific DPA Section Knowledge...")
        
        section_tests = [
            {
                "section": "Section 12",
                "question": "What does Section 12 of Philippine RA 10173 say about lawful processing of personal data?"
            },
            {
                "section": "Section 13", 
                "question": "What does Section 13 of Philippine RA 10173 say about sensitive personal information?"
            },
            {
                "section": "Section 16",
                "question": "What are the data subject rights listed in Section 16 of Philippine RA 10173?"
            },
            {
                "section": "Section 20",
                "question": "What security measures are required under Section 20 of Philippine RA 10173?"
            }
        ]
        
        results = {}
        
        for test in section_tests:
            try:
                response = self.mistral_client.chat.complete(
                    model="mistral-large-latest",
                    messages=[
                        {
                            "role": "user",
                            "content": test["question"]
                        }
                    ],
                    max_tokens=300
                )
                
                answer = response.choices[0].message.content
                results[test["section"]] = {
                    "question": test["question"],
                    "answer": answer,
                    "has_specific_content": len(answer) > 100 and "section" in answer.lower()
                }
                
                print(f"\n📋 {test['section']}")
                print(f"✅ Answer: {answer[:150]}...")
                
            except Exception as e:
                print(f"❌ Error testing {test['section']}: {e}")
                results[test["section"]] = {"error": str(e)}
        
        return results
    
    def compare_with_actual_dpa(self):
        """Compare model answers with actual DPA content"""
        print("\n🔍 Comparing with Actual DPA Content...")
        
        # Load our extracted DPA content
        try:
            with open("data/output/dpa_sections.json", "r", encoding="utf-8") as f:
                actual_dpa = json.load(f)
        except FileNotFoundError:
            print("❌ No extracted DPA content found. Run extract_dpa_content.py first.")
            return {}
        
        comparison_results = {}
        
        # Test key sections
        key_sections = ["12", "13", "16", "20"]
        
        for section_num in key_sections:
            if section_num in actual_dpa:
                actual_content = actual_dpa[section_num]["content"]
                actual_title = actual_dpa[section_num]["title"]
                
                # Ask model about this section
                question = f"What does Section {section_num} of Philippine Republic Act 10173 cover? Please provide details."
                
                try:
                    response = self.mistral_client.chat.complete(
                        model="mistral-large-latest",
                        messages=[{"role": "user", "content": question}],
                        max_tokens=400
                    )
                    
                    model_answer = response.choices[0].message.content
                    
                    # Simple comparison metrics
                    actual_keywords = set(actual_content.lower().split())
                    model_keywords = set(model_answer.lower().split())
                    
                    overlap = len(actual_keywords.intersection(model_keywords))
                    similarity_score = overlap / len(actual_keywords.union(model_keywords)) if actual_keywords.union(model_keywords) else 0
                    
                    comparison_results[f"Section {section_num}"] = {
                        "actual_title": actual_title,
                        "actual_content_length": len(actual_content),
                        "model_answer": model_answer,
                        "model_answer_length": len(model_answer),
                        "keyword_overlap": overlap,
                        "similarity_score": similarity_score,
                        "mentions_key_terms": any(term in model_answer.lower() for term in ["consent", "processing", "data subject", "personal data"])
                    }
                    
                    print(f"\n📋 Section {section_num}: {actual_title}")
                    print(f"📊 Similarity Score: {similarity_score:.2f}")
                    print(f"📊 Keyword Overlap: {overlap}")
                    print(f"✅ Model Answer: {model_answer[:100]}...")
                    
                except Exception as e:
                    print(f"❌ Error testing Section {section_num}: {e}")
        
        return comparison_results
    
    def generate_knowledge_assessment(self):
        """Generate overall assessment of model's DPA knowledge"""
        print("\n📊 Generating DPA Knowledge Assessment...")
        
        # Run all tests
        general_knowledge = self.test_mistral_dpa_knowledge()
        section_knowledge = self.test_model_specific_sections()
        comparison_results = self.compare_with_actual_dpa()
        
        # Calculate assessment scores
        assessment = {
            "general_dpa_awareness": {
                "total_questions": len(general_knowledge),
                "mentions_philippines": sum(1 for r in general_knowledge.values() if isinstance(r, dict) and r.get("mentions_philippines", False)),
                "mentions_ra_10173": sum(1 for r in general_knowledge.values() if isinstance(r, dict) and r.get("mentions_ra_10173", False)),
                "score": 0
            },
            "section_specific_knowledge": {
                "total_sections": len(section_knowledge),
                "detailed_answers": sum(1 for r in section_knowledge.values() if isinstance(r, dict) and r.get("has_specific_content", False)),
                "score": 0
            },
            "accuracy_vs_actual": {
                "sections_compared": len(comparison_results),
                "average_similarity": sum(r.get("similarity_score", 0) for r in comparison_results.values()) / len(comparison_results) if comparison_results else 0,
                "score": 0
            }
        }
        
        # Calculate scores
        if assessment["general_dpa_awareness"]["total_questions"] > 0:
            assessment["general_dpa_awareness"]["score"] = (
                assessment["general_dpa_awareness"]["mentions_philippines"] + 
                assessment["general_dpa_awareness"]["mentions_ra_10173"]
            ) / (assessment["general_dpa_awareness"]["total_questions"] * 2)
        
        if assessment["section_specific_knowledge"]["total_sections"] > 0:
            assessment["section_specific_knowledge"]["score"] = (
                assessment["section_specific_knowledge"]["detailed_answers"] / 
                assessment["section_specific_knowledge"]["total_sections"]
            )
        
        assessment["accuracy_vs_actual"]["score"] = assessment["accuracy_vs_actual"]["average_similarity"]
        
        # Overall assessment
        overall_score = (
            assessment["general_dpa_awareness"]["score"] + 
            assessment["section_specific_knowledge"]["score"] + 
            assessment["accuracy_vs_actual"]["score"]
        ) / 3
        
        assessment["overall_score"] = overall_score
        assessment["recommendation"] = self._get_recommendation(overall_score)
        
        # Save results
        with open("data/output/model_dpa_knowledge_assessment.json", "w", encoding="utf-8") as f:
            json.dump({
                "assessment": assessment,
                "general_knowledge": general_knowledge,
                "section_knowledge": section_knowledge,
                "comparison_results": comparison_results
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n🎯 Overall DPA Knowledge Score: {overall_score:.2f}/1.0")
        print(f"📋 Recommendation: {assessment['recommendation']}")
        
        return assessment
    
    def _get_recommendation(self, score):
        """Get recommendation based on knowledge score"""
        if score >= 0.8:
            return "HIGH: Model has strong DPA knowledge. Can be used for DPA-related tasks with confidence."
        elif score >= 0.6:
            return "MEDIUM: Model has moderate DPA knowledge. Should be supplemented with actual DPA content."
        elif score >= 0.4:
            return "LOW: Model has limited DPA knowledge. Must use actual DPA content for accuracy."
        else:
            return "VERY LOW: Model lacks DPA knowledge. Rely entirely on extracted DPA content."

def main():
    """Run DPA model knowledge tests"""
    print("🔍 DPA Model Knowledge Testing")
    print("=" * 50)
    
    if not os.getenv("MISTRAL_API_KEY"):
        print("❌ Error: MISTRAL_API_KEY not found in environment variables")
        print("Please set your Mistral API key in .env file")
        return
    
    # Create output directory
    os.makedirs("data/output", exist_ok=True)
    
    tester = DPAModelTester()
    assessment = tester.generate_knowledge_assessment()
    
    print("\n✅ DPA Knowledge Testing Complete!")
    print("📄 Results saved to: data/output/model_dpa_knowledge_assessment.json")

if __name__ == "__main__":
    main()
