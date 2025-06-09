import os
import json
import PyPDF2
from pathlib import Path

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF file"""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
        return ""

def process_policies():
    """Process all PDFs and create knowledge base"""
    
    # Create knowledge_base directory
    os.makedirs("knowledge_base", exist_ok=True)
    
    policies_dir = Path("data/policies")
    policies = []
    
    print("Processing RMIT policy PDFs...")
    
    # Process each PDF file
    for pdf_file in policies_dir.glob("*.pdf"):
        print(f"Processing: {pdf_file.name}")
        
        # Extract text
        content = extract_text_from_pdf(pdf_file)
        
        if content:
           
            title = pdf_file.stem.replace("_", " ").title()
            
            policy_entry = {
                "title": title,
                "filename": pdf_file.name,
                "content": content,
                "word_count": len(content.split()),
                "processed_date": "2024-12-07"  
            }
            
            policies.append(policy_entry)
            print(f"✅ Processed: {title} ({len(content.split())} words)")
        else:
            print(f"❌ Failed to extract text from: {pdf_file.name}")
    
    # Create knowledge base structure
    knowledge_base = {
        "source_directory": "data/policies",
        "total_policies": len(policies),
        "processed_date": "2024-12-07",
        "policies": policies
    }
    
    # Save to JSON file
    output_file = "knowledge_base/policy_knowledge_base.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(knowledge_base, f, indent=2, ensure_ascii=False)
    
    print(f"\n🎉 Successfully processed {len(policies)} policies!")
    print(f"📁 Knowledge base saved to: {output_file}")
    print(f"📊 Total words processed: {sum(p['word_count'] for p in policies):,}")
    
    return knowledge_base

if __name__ == "__main__":
    print("Note: Make sure you have PyPDF2 installed:")
    print("pip install PyPDF2")
    print()
    
    knowledge_base = process_policies()