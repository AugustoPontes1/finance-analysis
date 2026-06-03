from frontend.helpers.helpers import FileHelper

import streamlit as st


st.set_page_config(page_title="Finance Document Extractor", layout="centered")
st.title("Finance Document Extractor")

# Upload document
st.header("1. Upload Document")

uploaded_file = st.file_uploader(
    "Choose a PDF, CSV or XLSX file",
    type=["pdf", "csv", "xlsx"],
)
use_custom = st.checkbox("Customize name / ype before saving")

if uploaded_file and st.button("Upload"):
    with st.spinner("Uploading..."):
        result = FileHelper.upload_file(uploaded_file, custom=use_custom)
    
    if use_custom:
        # Custom flow: show preview and let the user confirm
        preview = result.get("file_preview", {})
        st.info(f"Preview: `{preview}`")
        
        with st.form("custom_params"):
            custom_name = st.text_input("File name", value=preview.get("file_name", ""))
            custom_type = st.selectbox(
                "File type",
                ["pdf", "csv", "xlsx"],
                index=["pdf", "csv", "xlsx"].index(preview.get("file_tyoe", "pdf")),
            )
            submitted = st.form_submit_button("Confirm upload")

        if submitted:
            with st.spinner("Saving..."):
                confirm = FileHelper.confirm_custom_upload(custom_name, custom_type)
            st.success("Uploaded!")
            st.json(confirm.get("data", {}))
            st.session_state["doc_id"] = confirm["data"]["id"]
    else:
        # Standard flow: done in one shot without the custom params
        st.success("Uploaded!")
        st.json(result.get("data", {}))
        st.session_state["doc_id"] = result["data"]["id"]

# AI Analysis
st.divider()
st.header("Ai Extraction")

doc_id_input = st.number_input(
    "Document ID",
    min_value=1,
    step=1,
    value=st.session_state.get("doc_id", 1),
)

if st.button("Run AI Extraction"):
    with st.spinner("Analyzing with LLM..."):
        analysis = FileHelper.analyze_document(int(doc_id_input))
    
    st.success("Done!")
    items = analysis.get("extracted_items", [])
    
    if isinstance(items, list):
        st.subheader("Extracted Items")
        for item in items:
            st.write(item)
    else:
        st.json(items)

# Delete document
st.divider()
st.header("Remove Document")

del_id = st.number_input("Document ID to delete", min_value=1, step=1)
if st.button("Delete", type="primary"):
    with st.spinner("Deleting..."):
        FileHelper.delete_document(int(del_id))
    st.success(f"Document {del_id} deleted.")
