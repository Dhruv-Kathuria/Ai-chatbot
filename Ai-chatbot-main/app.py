import streamlit as st
import json
import boto3
from datetime import datetime

REGION = "us-east-1"
MODEL_ID = "anthropic.claude-3-haiku-20240307-v1:0"
IDENTITY_POOL_ID = "us-east-1:7771aae7-be2c-4496-a582-615af64292cf"
USER_POOL_ID = "us-east-1_koPKi1lPU"
APP_CLIENT_ID = "3h7m15971bnfah362dldub1u2p"
USERNAME="s3993592@student.rmit.edu.au"
PASSWORD="Dhruv2580@"

def get_credentials(username, password):
    """Get AWS credentials"""
    idp_client = boto3.client("cognito-idp", region_name=REGION)
    response = idp_client.initiate_auth(
        AuthFlow="USER_PASSWORD_AUTH",
        AuthParameters={"USERNAME": username, "PASSWORD": password},
        ClientId=APP_CLIENT_ID,
    )
    id_token = response["AuthenticationResult"]["IdToken"]

    identity_client = boto3.client("cognito-identity", region_name=REGION)
    identity_response = identity_client.get_id(
        IdentityPoolId=IDENTITY_POOL_ID,
        Logins={f"cognito-idp.{REGION}.amazonaws.com/{USER_POOL_ID}": id_token},
    )

    creds_response = identity_client.get_credentials_for_identity(
        IdentityId=identity_response["IdentityId"],
        Logins={f"cognito-idp.{REGION}.amazonaws.com/{USER_POOL_ID}": id_token},
    )

    return creds_response["Credentials"]

def invoke_bedrock(prompt_text, max_tokens=640, temperature=0.3, top_p=0.9):
    """Invoke Bedrock Claude"""
    credentials = get_credentials(USERNAME, PASSWORD)

    bedrock_runtime = boto3.client(
        "bedrock-runtime",
        region_name=REGION,
        aws_access_key_id=credentials["AccessKeyId"],
        aws_secret_access_key=credentials["SecretKey"],
        aws_session_token=credentials["SessionToken"],
    )

    payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": top_p,
        "messages": [{"role": "user", "content": prompt_text}]
    }

    response = bedrock_runtime.invoke_model(
        body=json.dumps(payload),
        modelId=MODEL_ID,
        contentType="application/json",
        accept="application/json"
    )

    result = json.loads(response["body"].read())
    return result["content"][0]["text"]

@st.cache_data
def load_policy_knowledge_base():
    """Load processed policy knowledge base"""
    try:
        with open('knowledge_base/policy_knowledge_base.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("❌ Policy knowledge base not found!")
        st.info("Please run the policy processing script first:")
        st.code("python process_policies.py")
        return {"policies": []}

def find_relevant_policies(user_question, policies, max_policies=3):
    """Find most relevant policies based on keyword matching"""
    
    if not policies.get("policies"):
        return []
    
    # Extract meaningful words from question
    question_words = [word.lower().strip() for word in user_question.split() 
                     if len(word) > 3 and word.lower() not in ['what', 'when', 'where', 'how']]
    
    relevant_policies = []
    
    for policy in policies["policies"]:
        relevance_score = 0
        policy_title = policy.get("title", "").lower()
        policy_content = policy.get("content", "").lower()
        
        # Score based on matches
        for word in question_words:
            # Title matches are more important
            if word in policy_title:
                relevance_score += 10
            # Content matches
            policy_content_words = policy_content.split()
            word_count = sum(1 for w in policy_content_words if word in w)
            relevance_score += min(word_count, 5)  # Cap at 5 to avoid over-weighting
        
        if relevance_score > 0:
            relevant_policies.append((policy, relevance_score))
    
    # Sort by relevance and return top policies
    relevant_policies.sort(key=lambda x: x[1], reverse=True)
    return [policy for policy, score in relevant_policies[:max_policies]]

def build_policy_prompt(user_question, policies):
    """Build comprehensive prompt with policy context"""
    
    relevant_policies = find_relevant_policies(user_question, policies)
    
    if not relevant_policies:
        return f"""You are RMIT's Academic Policy Assistant. A student has asked: "{user_question}"

I don't have specific policy information to answer this question. Please provide general guidance and recommend they contact Student Connect at RMIT for official information.

Keep your response helpful and direct them to appropriate resources."""

    # Context with relevant policies
    context = f"""You are RMIT's Academic Policy Assistant. You help students understand RMIT's academic policies and procedures.

Student Question: {user_question}

Relevant RMIT Policy Information:
"""
    
    for i, policy in enumerate(relevant_policies, 1):
        context += f"\n{'='*50}\nPolicy {i}: {policy['title']}\n{'='*50}\n"
        # Include first 1000 characters to stay within token limits
        content_excerpt = policy['content'][:1000]
        context += f"{content_excerpt}...\n"
    
    context += f"""

Instructions:
1. Answer the student's question using the official RMIT policies provided above
2. Explain procedures in clear, step-by-step language that's easy to understand
3. Reference specific policy names when providing information
4. If the policies don't fully answer the question, acknowledge this and suggest contacting Student Connect
5. Be helpful, accurate, and student-focused
6. Always add a disclaimer about verifying information for specific situations

Provide a comprehensive answer based on these official RMIT policies."""
    
    return context

st.set_page_config(
    page_title="RMIT Policy Assistant", 
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 RMIT Academic Policy Assistant")
st.subheader("Navigate RMIT policies with confidence")

# Load policy data
policies = load_policy_knowledge_base()

# Display status
col1, col2, col3 = st.columns(3)
with col1:
    if policies and policies.get("policies"):
        st.metric("📋 Policies Loaded", len(policies["policies"]))
with col2:
    if policies and policies.get("policies"):
        total_words = sum(p.get('word_count', 0) for p in policies["policies"])
        st.metric("📝 Total Words", f"{total_words:,}")
with col3:
    if policies and policies.get("policies"):
        st.success("✅ Ready to Help")
    else:
        st.error("❌ Setup Required")

# Sidebar with common questions
st.sidebar.title("💡 Common Questions")
common_questions = [
    "How do I apply for special consideration?",
    "What is the academic appeals process?",
    "How do I withdraw from a course?",
    "What are the rules about plagiarism?",
    "How do I make a complaint about services?",
    "What financial assistance is available?",
    "How do I get academic support?",
    "What are the assessment policies?",
    "How do I appeal a grade?",
    "What happens if I fail a course?"
]

for question in common_questions:
    if st.sidebar.button(question, key=f"sidebar_{question}"):
        st.session_state.suggested_question = question

# Chat interface
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle suggested questions
prompt = None
if 'suggested_question' in st.session_state:
    prompt = st.session_state.suggested_question
    del st.session_state.suggested_question

# Chat input
if not prompt:
    prompt = st.chat_input("Ask about RMIT policies and procedures...")

if prompt:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        if not policies.get("policies"):
            st.error("Policy knowledge base not loaded. Please run the policy processing script first.")
        else:
            with st.spinner("🔍 Searching policy database..."):
                try:
                    # Build policy context
                    policy_prompt = build_policy_prompt(prompt, policies)
                    
                    # Get AI response
                    response = invoke_bedrock(policy_prompt)
                    
                    # Add disclaimer
                    response += "\n\n---\n*💡 This guidance is based on official RMIT policies. For advice specific to your situation, please contact Student Connect or your course coordinator for verification.*"
                    
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    
                except Exception as e:
                    st.error(f"Error generating response: {e}")
                    st.info("Please check your AWS credentials and try again.")

# Information panel
with st.expander("ℹ️ About this Assistant"):
    st.markdown("""
    **What this assistant covers:**
    - 📋 Assessment policies and special consideration
    - ⚖️ Academic appeals and complaints procedures  
    - 📚 Enrollment and course management
    - 🎯 Student conduct and academic integrity
    - 💰 Financial assistance and fee policies
    - 🤝 Student support services
    - 🔬 Research and HDR procedures
    
    **How it works:**
    This AI assistant searches through official RMIT policy documents to provide accurate, 
    up-to-date information about university procedures and regulations.
    
    **Important Note:**
    Always verify policy information for your specific situation by contacting:
    - 📞 Student Connect: 1800 944 722
    - 💬 Online chat via RMIT website
    - 📧 Your course coordinator
    """)


if st.sidebar.checkbox("🔧 Debug Info"):
    st.sidebar.write(f"Policies loaded: {len(policies.get('policies', []))}")
    if policies.get("policies"):
        st.sidebar.write("Sample policy titles:")
        for policy in policies["policies"][:3]:
            st.sidebar.write(f"- {policy.get('title', 'Unknown')}")