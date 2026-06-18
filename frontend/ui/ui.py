import logging

from frontend.helpers.helpers import FileHelper
import streamlit as st

logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


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
    logger.info(f"Upload triggered: file='{uploaded_file.name}', custom={use_custom}")

    if use_custom:
        file_ext = uploaded_file.name.split(".")[-1].lower()
        st.session_state["custom_preview"] = {
            "file_name": uploaded_file.name,
            "file_type": file_ext,
            "file_size": uploaded_file.size,
        }
        st.session_state["custom_file_bytes"] = uploaded_file.getvalue()
        logger.debug(f"Custom flow: preview and file bytes stored in session_state")
    else:
        with st.spinner("Uploading..."):
            result = FileHelper.upload_file(uploaded_file, custom=False)
        doc_id = result["data"]["id"]
        logger.info(f"Standard upload complete: doc_id={doc_id}")
        st.success("Uploaded!")
        st.json(result.get("data", {}))
        st.session_state["doc_id"] = doc_id
        st.session_state.pop("custom_preview", None)
        st.session_state.pop("custom_file_bytes", None)

if use_custom and "custom_preview" in st.session_state:
    import io
    preview = st.session_state["custom_preview"]
    st.info(f"Preview: `{preview}`")

    with st.form("custom_params"):
        custom_name = st.text_input("File Name", value=preview.get("file_name", ""))
        custom_type = st.selectbox(
            "File Type",
            ["pdf", "csv", "xlsx"],
            index=["pdf", "csv", "xlsx"].index(preview.get("file_type", "pdf"))
        )
        submitted = st.form_submit_button("Confirm Upload")

    if submitted:
        logger.info(f"Confirming custom upload: name='{custom_name}', type='{custom_type}'")
        file_obj = io.BytesIO(st.session_state["custom_file_bytes"])
        with st.spinner("Saving..."):
            confirm = FileHelper.confirm_custom_upload(file_obj, custom_name, custom_type)
        doc_id = confirm["data"]["id"]
        logger.info(f"Custom upload confirmed: doc_id={doc_id}")
        st.success("Uploaded!")
        st.json(confirm.get("data", {}))
        st.session_state["doc_id"] = doc_id
        st.session_state.pop("custom_preview", None)
        st.session_state.pop("custom_file_bytes", None)

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
    logger.info(f"AI extraction triggered for doc_id={doc_id_input}")
    try:
        with st.spinner("Analyzing with LLM... (this may take a minute)"):
            analysis = FileHelper.analyze_document(int(doc_id_input))
        logger.info(f"AI extraction complete for doc_id={doc_id_input}")

        warning = analysis.get("warning")
        if warning:
            st.warning(warning)

        summary = analysis.get("summary", "")
        st.subheader("Analysis")
        if not summary:
            st.info("No content was extracted from this document.")
        else:
            st.markdown(summary)
    except Exception as e:
        logger.error(f"AI extraction failed for doc_id={doc_id_input}: {e}", exc_info=True)
        st.error(f"Failed to retrieve data: {e}")


# Delete document
st.divider()
st.header("Remove Document")

del_id = st.number_input("Document ID to delete", min_value=1, step=1)
if st.button("Delete", type="primary"):
    logger.info(f"Delete triggered for doc_id={del_id}")
    try:
        with st.spinner("Deleting..."):
            FileHelper.delete_document(int(del_id))
        logger.info(f"Document {del_id} deleted successfully")
        st.success(f"Document {del_id} deleted.")
    except Exception as e:
        logger.error(f"Failed to delete document {del_id}: {e}", exc_info=True)
        st.error(f"Failed to delete document {del_id}: {e}")
