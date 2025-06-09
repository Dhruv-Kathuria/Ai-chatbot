import requests
import os

def download_rmit_policies():
    """Download comprehensive RMIT policies using verified IDs"""
    
    os.makedirs("data/policies", exist_ok=True)
    
    policies = {
        # Assessment & Academic Performance
        7: "Assessment and Assessment Flexibility Policy",
        190: "Assessment, Academic Progress and Appeals Regulations", 
        168: "Academic Integrity Policy",
        179: "Academic Integrity Procedure",
        
        # Student Conduct & Behaviour
        35: "Student Conduct Policy",
        106: "Student Conduct Procedure", 
        171: "Student Conduct Board Procedure",
        172: "Student Conduct - Appeals Procedure",
        180: "Student Conduct Regulations",
        
        # Complaints & Appeals
        33: "Student and Student-Related Complaints Policy",
        34: "Student and Student-Related Complaints Procedure",
        112: "RMIT Ombuds Procedure",
        
        # Enrollment & Admission
        11: "Enrolment Policy",
        113: "Enrolment Procedure",
        6: "Admission and Credit Policy", 
        37: "Credit Procedure",
        
        # Financial & Fees
        117: "Remission and Removal of Debt Procedure",
        118: "Refund of Fees Procedure",
        31: "Scholarships and Prizes Policy",
        
        # Student Support & Services
        293: "Support for Students Policy",
        
        # Research & HDR
        16: "HDR Admissions and Enrolment Procedure",
        22: "HDR and RTP Scholarships Policy",
        
        # Program & Course Management
        203: "Program and Course Guide Instruction",
        119: "Program and Course Work Integrated Learning Procedure"
    }
    
    base_url = "https://policies.rmit.edu.au/download.php?id={}&version=1"
    
    for policy_id, policy_name in policies.items():
        try:
            url = base_url.format(policy_id)
            print(f"Downloading ID {policy_id}: {policy_name}...")
            
            response = requests.get(url)
            if response.status_code == 200:
                filename = f"data/policies/{policy_name.replace(' ', '_').replace('-', '_')}.pdf"
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f"Downloaded: {policy_name}")
            else:
                print(f"Failed ID {policy_id}: {policy_name}")
        except Exception as e:
            print(f"Error ID {policy_id}: {e}")

    print(f"\nDownloaded {len(policies)} policies to data/policies/")

download_rmit_policies()