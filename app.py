import streamlit as st
from brain import analyze_scan, simplify_report
from style import get_base64

st.set_page_config(page_title="Medical Scan Analyzer", layout="wide")
img = get_base64("assets/mdback.jpg")
st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{img}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    
    /* Dark card behind all main content blocks */
    [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] {{
        background: rgba(0, 0, 0, 0.65);
        border-radius: 12px;
        padding: 1.5rem;
    }}
    
    /* Make all text white */
    html, body, h1, h2, h3, p, label, .stMarkdown {{
        color: white !important;
    }}
    </style>
""", unsafe_allow_html=True)

st.title("Medical Scan Analyzer")
st.markdown("Upload an X-ray or MRI scan and get an AI-powered radiological analysis instantly.")
st.divider()

col1, col2 = st.columns([1, 1.5])

with col1:
    st.subheader("Upload Scan")
    uploaded_file = st.file_uploader(
        "Upload your Scan",
        type=["jpg", "jpeg", "png", "webp", "pdf"],
        help="Supported formats: JPEG, PNG, WebP, PDF"
    )

    if uploaded_file is not None:
        if uploaded_file.type != "application/pdf":
            st.image(uploaded_file, caption="Uploaded Scan", use_container_width=True)
        else:
            st.info("PDF uploaded successfully.")

        if st.button("Start Analysing", use_container_width=True):
            with st.spinner("Analysing your scan..."):
                image_bytes = uploaded_file.getvalue()
                media_type = uploaded_file.type
                st.session_state.analysis_result = analyze_scan(image_bytes, media_type)
  

with col2:
    st.subheader("Analysis Report")
    if "analysis_result" in st.session_state:
        st.markdown(st.session_state.analysis_result)
    else:
        st.caption("Your analysis will appear here after uploading a scan.")

st.divider()

if "analysis_result" in st.session_state:
    _, center, _ = st.columns([1, 1, 1])
    with center:
        if st.button("Simplify Report", use_container_width=True):
            with st.spinner("Simplifying the report..."):
                st.session_state.simplified_result = simplify_report(
                    st.session_state.analysis_result
                )

    if "simplified_result" in st.session_state:
        st.subheader("Plain English Summary")
        st.markdown(st.session_state.simplified_result)