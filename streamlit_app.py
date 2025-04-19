import streamlit as st
import requests
import json
from datetime import datetime
import os

# Configure the page
st.set_page_config(
    page_title="KYC Automation System",
    page_icon="🔍",
    layout="wide"
)

# Title and description
st.title("KYC Automation System")
st.markdown("""
This application automates the KYC (Know Your Customer) process using AI-powered document verification and facial recognition.
""")

# Initialize session state
if 'kyc_status' not in st.session_state:
    st.session_state.kyc_status = None
if 'customer_id' not in st.session_state:
    st.session_state.customer_id = None

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["New KYC", "Check Status", "Review KYC"])

# API endpoint
API_URL = "http://127.0.0.1:8000/api/v1"

# New KYC Page
if page == "New KYC":
    st.header("New KYC Application")
    
    # Customer Information Form
    with st.form("kyc_form"):
        st.subheader("Customer Information")
        first_name = st.text_input("First Name")
        last_name = st.text_input("Last Name")
        email = st.text_input("Email")
        phone = st.text_input("Phone Number")
        date_of_birth = st.date_input("Date of Birth")
        address = st.text_area("Address")
        
        st.subheader("Document Upload")
        id_document = st.file_uploader("ID Document (Passport/Driver's License)", type=["jpg", "jpeg", "png"])
        selfie = st.file_uploader("Selfie Photo", type=["jpg", "jpeg", "png"])
        address_document = st.file_uploader("Address Proof", type=["jpg", "jpeg", "png"])
        
        submitted = st.form_submit_button("Submit KYC")
        
        if submitted:
            if not all([first_name, last_name, email, phone, date_of_birth, address, id_document, selfie, address_document]):
                st.error("Please fill in all fields and upload all required documents.")
            else:
                try:
                    # Prepare the data
                    customer_data = {
                        "first_name": first_name,
                        "last_name": last_name,
                        "email": email,
                        "phone": phone,
                        "date_of_birth": date_of_birth.isoformat(),
                        "address": address
                    }
                    
                    # Create files dictionary
                    files = {
                        "id_document": ("id_document.jpg", id_document.getvalue()),
                        "selfie": ("selfie.jpg", selfie.getvalue()),
                        "address_document": ("address_document.jpg", address_document.getvalue())
                    }
                    
                    # Make API request
                    response = requests.post(
                        f"{API_URL}/kyc/start",
                        data={"customer_data": json.dumps(customer_data)},
                        files=files
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.session_state.customer_id = result["customer_id"]
                        st.session_state.kyc_status = result["status"]
                        st.success(f"KYC process started successfully! Your reference ID is: {result['customer_id']}")
                    else:
                        st.error(f"Error starting KYC process: {response.text}")
                
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

# Check Status Page
elif page == "Check Status":
    st.header("Check KYC Status")
    
    customer_id = st.text_input("Enter your KYC Reference ID", value=st.session_state.customer_id or "")
    
    if st.button("Check Status"):
        if customer_id:
            try:
                response = requests.get(f"{API_URL}/kyc/status/{customer_id}")
                if response.status_code == 200:
                    result = response.json()
                    st.session_state.kyc_status = result["status"]
                    
                    # Display status
                    status_colors = {
                        "pending": "orange",
                        "approved": "green",
                        "rejected": "red",
                        "in_review": "blue"
                    }
                    
                    st.markdown(f"""
                    ### KYC Status: :{status_colors[result['status']]}[{result['status'].upper()}]
                    
                    **Customer ID:** {result['customer_id']}
                    **Name:** {result['customer_name']}
                    **Email:** {result['customer_email']}
                    """)
                    
                    # Display verification results
                    st.subheader("Verification Results")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Document Verification", result['document_verification'])
                    with col2:
                        st.metric("Facial Match", result['facial_match'])
                    with col3:
                        st.metric("Compliance Check", result['compliance_check'])
                    
                else:
                    st.error(f"Error checking status: {response.text}")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
        else:
            st.warning("Please enter a KYC Reference ID")

# Review KYC Page
elif page == "Review KYC":
    st.header("Review KYC Application")
    
    if st.session_state.kyc_status == "pending":
        customer_id = st.text_input("Enter KYC Reference ID to Review", value=st.session_state.customer_id or "")
        
        if customer_id:
            try:
                response = requests.get(f"{API_URL}/kyc/status/{customer_id}")
                if response.status_code == 200:
                    result = response.json()
                    
                    # Display customer information
                    st.subheader("Customer Information")
                    st.write(f"**Name:** {result['customer_name']}")
                    st.write(f"**Email:** {result['customer_email']}")
                    st.write(f"**Phone:** {result['customer_phone']}")
                    
                    # Display verification results
                    st.subheader("Verification Results")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Document Verification", result['document_verification'])
                    with col2:
                        st.metric("Facial Match", result['facial_match'])
                    with col3:
                        st.metric("Compliance Check", result['compliance_check'])
                    
                    # Review form
                    with st.form("review_form"):
                        decision = st.radio("Decision", ["approve", "reject"])
                        comments = st.text_area("Comments (optional)")
                        
                        if st.form_submit_button("Submit Review"):
                            try:
                                review_response = requests.post(
                                    f"{API_URL}/kyc/review/{customer_id}",
                                    json={
                                        "decision": decision,
                                        "comments": comments
                                    }
                                )
                                
                                if review_response.status_code == 200:
                                    st.success(f"KYC application {decision}ed successfully!")
                                    st.session_state.kyc_status = decision
                                else:
                                    st.error(f"Error submitting review: {review_response.text}")
                            except Exception as e:
                                st.error(f"An error occurred: {str(e)}")
                else:
                    st.error(f"Error fetching KYC details: {response.text}")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
    else:
        st.info("No pending KYC applications to review.")

# Footer
st.markdown("---")
st.markdown("KYC Automation System v1.0 | Powered by AI") 