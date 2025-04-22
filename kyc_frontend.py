import streamlit as st
import requests
from PIL import Image
import io

API_URL = "http://localhost:8000/api/v1/kyc"

st.set_page_config(page_title="Online KYC Portal", page_icon="🛡️", layout="centered")
st.title("🛡️ Online KYC Verification")

# --- Step 0: Require Document Upload Before Proceeding ---
if 'session_id' not in st.session_state or not st.session_state['session_id']:
    st.write("## Step 1: Upload Your Document (ID/Passport)")
    doc_file = st.file_uploader("Upload your document (ID or passport)", type=["jpg", "jpeg", "png", "pdf"], key="doc_upload_step0")
    if doc_file:
        files = {"document": (doc_file.name, doc_file, doc_file.type)}
        try:
            resp = requests.post(f"{API_URL}/upload-document", files=files)
            if resp.ok:
                session_data = resp.json()
                st.session_state['session_id'] = session_data["session_id"]
                st.success("Document uploaded. Session started.")
                st.rerun()
            else:
                st.error(f"Document upload failed: {resp.text}")
        except Exception as e:
            st.error(f"Document upload error: {e}")
        st.stop()

# --- Step 1: Upload Document ---
st.write("Step 1: Upload your ID/Passport Document")
if 'document_img_bytes' not in st.session_state:
    with st.form(key="doc_form"):
        doc_file = st.file_uploader("Upload ID/Passport (image)", type=["jpg", "jpeg", "png"], key="doc_upload_step1")
        webcam_doc_img = st.camera_input("Or take a live photo of your document", key="webcam_doc")
        submit_doc = st.form_submit_button("Submit Document")

    # Store and display uploaded/captured document image
    if submit_doc and (doc_file or webcam_doc_img):
        if doc_file:
            st.session_state['document_img_bytes'] = doc_file.read()
            st.session_state['document_img_type'] = doc_file.type
            st.session_state['document_img_name'] = doc_file.name
        else:
            st.session_state['document_img_bytes'] = webcam_doc_img.getvalue()
            st.session_state['document_img_type'] = "image/jpeg"
            st.session_state['document_img_name'] = "webcam_document.jpg"

if 'document_img_bytes' in st.session_state:
    st.write("**Uploaded/Captured Document:**")
    st.image(st.session_state['document_img_bytes'], caption="Document Image", use_column_width=True)

# --- Step 2: Upload Selfie and Show Match Result ---
st.write("---")
if 'document_img_bytes' in st.session_state:
    st.write("Step 2: Upload or capture a selfie for face verification")
    selfie_file = st.file_uploader("Upload a selfie", type=["jpg", "jpeg", "png"], key="selfie_upload")
    webcam_selfie_img = st.camera_input("Or take a live selfie", key="webcam_selfie")

    selfie_api_response = None
    if selfie_file or webcam_selfie_img:
        if selfie_file:
            selfie_bytes = selfie_file.read()
            selfie_type = selfie_file.type
            selfie_name = selfie_file.name
        else:
            selfie_bytes = webcam_selfie_img.getvalue()
            selfie_type = "image/jpeg"
            selfie_name = "webcam_selfie.jpg"
        st.session_state['selfie_img_bytes'] = selfie_bytes
        st.session_state['selfie_img_type'] = selfie_type
        st.session_state['selfie_img_name'] = selfie_name
        # Only proceed if session_id exists
        if 'session_id' in st.session_state and st.session_state['session_id']:
            progress = st.progress(0, text="Uploading selfie...")
            files = {"selfie": (selfie_name, selfie_bytes, selfie_type)}
            import time
            try:
                progress.progress(20, text="Uploading selfie to backend...")
                resp = requests.post(f"http://localhost:8000/api/v1/kyc/upload-selfie?session_id={st.session_state['session_id']}", files=files)
                progress.progress(70, text="Waiting for Face++ response...")
                time.sleep(0.5)
                if resp.ok:
                    selfie_api_response = resp.json()
                    st.session_state['selfie_result'] = selfie_api_response
                    progress.progress(100, text="Face++ response received!")
                else:
                    # Handle Face++ concurrency error
                    if 'CONCURRENCY_LIMIT_EXCEEDED' in resp.text:
                        st.error("Too many verification requests at once. Please wait a moment and try again.")
                    else:
                        st.error(f"Selfie verification error: {resp.text}")
                    progress.empty()
            except Exception as e:
                st.error(f"Selfie verification error: {e}")
                progress.empty()
        else:
            st.warning("Please upload your document first to start a session before selfie verification.")

    # Show the uploaded/captured selfie
    if 'selfie_img_bytes' in st.session_state:
        st.write("**Uploaded/Captured Selfie:**")
        st.image(st.session_state['selfie_img_bytes'], caption="Selfie Image", use_column_width=True)

    # Show the match result (Face++ full response)
    if 'selfie_result' in st.session_state:
        result = st.session_state['selfie_result']
        if result.get('verified'):
            st.success(f"✅ Face match: VERIFIED! Confidence: {result.get('confidence', 0):.2f}")
        else:
            st.error(f"❌ Face match: NOT VERIFIED. Confidence: {result.get('confidence', 0):.2f}")
        st.caption(f"(Threshold for match: {result.get('threshold', 80)})")
        st.write("**Face++ Raw Response:**")
        st.json(result)
    elif ('session_id' not in st.session_state or not st.session_state['session_id']):
        st.info("Please upload your document before selfie verification.")

# --- Step 3: Upload/Capture One Hand Photo (only after document and selfie verified) ---
if (
    'document_img_bytes' in st.session_state and
    'selfie_result' in st.session_state and
    st.session_state['selfie_result'].get('verified')
):
    st.write("---")
    if 'hand_phase' not in st.session_state:
        st.session_state['hand_phase'] = 'left'
    hand_label = 'Left Hand' if st.session_state['hand_phase'] == 'left' else 'Right Hand'
    st.write(f"Step 3: Upload or capture a photo of your {hand_label} (spread out, palm visible)")
    hand_file = st.file_uploader(f"Upload a photo of your {hand_label}", type=["jpg", "jpeg", "png"], key=f"{hand_label}_upload")
    webcam_hand_img = st.camera_input(f"Or take a live photo of your {hand_label}", key=f"webcam_{hand_label}")

    hand_api_response = None
    if hand_file or webcam_hand_img:
        if hand_file:
            st.session_state[f'{hand_label}_img_bytes'] = hand_file.read()
            st.session_state[f'{hand_label}_img_type'] = hand_file.type
            st.session_state[f'{hand_label}_img_name'] = hand_file.name
        else:
            st.session_state[f'{hand_label}_img_bytes'] = webcam_hand_img.getvalue()
            st.session_state[f'{hand_label}_img_type'] = "image/jpeg"
            st.session_state[f'{hand_label}_img_name'] = f"webcam_{hand_label}.jpg"
        # Call backend for finger segmentation
        with st.spinner(f"Detecting fingers for {hand_label}..."):
            files = {"image": (st.session_state[f'{hand_label}_img_name'], st.session_state[f'{hand_label}_img_bytes'], st.session_state[f'{hand_label}_img_type'])}
            try:
                resp = requests.post("http://localhost:8000/api/v1/fingerprint/extract-fingers", files=files)
                if resp.ok:
                    hand_api_response = resp.json()
                    st.session_state[f'{hand_label}_api_response'] = hand_api_response
                else:
                    st.error(f"Extraction error: {resp.text}")
            except Exception as e:
                st.error(f"Extraction error: {e}")

    if f'{hand_label}_img_bytes' in st.session_state:
        st.write(f"**Uploaded/Captured {hand_label}:**")
        st.image(st.session_state[f'{hand_label}_img_bytes'], caption=f"{hand_label} Photo", use_column_width=True)
        if hand_api_response:
            st.write(f"**Detected Fingers ({hand_label}):** {hand_api_response['num_fingers']}")
            for i, f_b64 in enumerate(hand_api_response['fingers']):
                st.image(f"data:image/jpeg;base64,{f_b64}", caption=f"Finger {i+1}", use_column_width=True)
            # Show contour image if available
            if 'contour_img' in hand_api_response:
                st.image(
                    f"data:image/jpeg;base64,{hand_api_response['contour_img']}",
                    caption="Detected Contours on Hand",
                    use_column_width=True
                )
        # Show button to proceed to next hand if left hand is done
        if st.session_state['hand_phase'] == 'left':
            if st.button("Next: Capture Right Hand"):
                st.session_state['hand_phase'] = 'right'
                st.rerun()
        else:
            st.write("Both hands captured. Proceed to next step.")

# --- Step 4: Button to Verify All Documents and Show Results on a New Page ---
if (
    'hand_phase' in st.session_state and st.session_state['hand_phase'] == 'right' and
    f'Right Hand_img_bytes' in st.session_state and
    'selfie_img_bytes' in st.session_state and
    'session_id' in st.session_state and st.session_state['session_id']
):
    st.write("---")
    st.write(":white_check_mark: All documents and biometrics are ready.")
    if st.button("Click to Verify All Documents and Show Results"):
        st.session_state['show_results_page'] = True
        st.rerun()

# --- Results Page ---
if st.session_state.get('show_results_page', False):
    st.write("# Verification Results")
    st.write("## Document and Selfie Face Match")
    if 'selfie_result' in st.session_state:
        result = st.session_state['selfie_result']
        if result.get('verified'):
            st.success(f"✅ Face match: VERIFIED! Confidence: {result.get('confidence', 0):.2f}")
        else:
            st.error(f"❌ Face match: NOT VERIFIED. Confidence: {result.get('confidence', 0):.2f}")
        st.caption(f"(Threshold for match: {result.get('threshold', 80)})")
        st.write("**Face++ Raw Response:**")
        st.json(result)

    st.write("---")
    st.write("## Detected Fingers (Left Hand)")
    if 'Left Hand_img_bytes' in st.session_state and 'Left Hand_img_name' in st.session_state:
        st.image(st.session_state['Left Hand_img_bytes'], caption="Left Hand Photo", use_column_width=True)
        if 'Left Hand_api_response' in st.session_state:
            left_api = st.session_state['Left Hand_api_response']
            for i, f_b64 in enumerate(left_api['fingers']):
                st.image(f"data:image/jpeg;base64,{f_b64}", caption=f"Left Finger {i+1}", use_column_width=True)
    st.write("## Detected Fingers (Right Hand)")
    if 'Right Hand_img_bytes' in st.session_state and 'Right Hand_img_name' in st.session_state:
        st.image(st.session_state['Right Hand_img_bytes'], caption="Right Hand Photo", use_column_width=True)
        if 'Right Hand_api_response' in st.session_state:
            right_api = st.session_state['Right Hand_api_response']
            for i, f_b64 in enumerate(right_api['fingers']):
                st.image(f"data:image/jpeg;base64,{f_b64}", caption=f"Right Finger {i+1}", use_column_width=True)
    st.write("---")
    st.button("Back to Main Page", on_click=lambda: st.session_state.update({'show_results_page': False}))
    st.stop()

st.write("---")
st.caption(" 2025 Online KYC Demo. For demo purposes only.")
