import streamlit as st
from pypdf import PdfReader
import os
from dotenv import load_dotenv
import google.generativeai as genai
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO

st.set_page_config(
    page_title="AI Research Assistant",
    page_icon="📚",
    layout="wide"
)

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

with st.sidebar:

    st.title("📚 AI Research Assistant")

    st.markdown("---")

    st.write(
        "Upload research papers and analyze them using cloud-based Generative AI."
    )

    st.markdown("---")

    st.subheader("☁️ Cloud AI Status")

    if api_key:
        st.success("Connected")
        st.write("AI Service: Gemini API")
        st.write("Model: Gemini 2.5 Flash")
        st.write("Processing: Cloud-based")
    else:
        st.error("Not Connected")

    st.markdown("---")

    st.subheader("Features")

    st.write("✅ Summary")
    st.write("✅ Contributions")
    st.write("✅ Limitations")
    st.write("✅ Future Work")
    st.write("✅ Paper Chat")

if "analysis" not in st.session_state:
    st.session_state.analysis = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "paper_text" not in st.session_state:
    st.session_state.paper_text = ""


def extract_section(text, start, end=None):

    try:
        start_index = text.index(start) + len(start)

        if end:
            end_index = text.index(end)
            return text[start_index:end_index].strip()

        return text[start_index:].strip()

    except ValueError:
        return "Section not found."


def create_pdf(summary, contributions, limitations, future_work):

    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()

    content = []

    content.append(
        Paragraph("AI Research Assistant Report", styles["Title"])
    )

    content.append(Spacer(1, 12))

    content.append(
        Paragraph("Summary", styles["Heading1"])
    )

    content.append(
        Paragraph(summary, styles["BodyText"])
    )

    content.append(Spacer(1, 12))

    content.append(
        Paragraph("Key Contributions", styles["Heading1"])
    )

    content.append(
        Paragraph(contributions, styles["BodyText"])
    )

    content.append(Spacer(1, 12))

    content.append(
        Paragraph("Limitations", styles["Heading1"])
    )

    content.append(
        Paragraph(limitations, styles["BodyText"])
    )

    content.append(Spacer(1, 12))

    content.append(
        Paragraph("Future Work", styles["Heading1"])
    )

    content.append(
        Paragraph(future_work, styles["BodyText"])
    )

    doc.build(content)

    buffer.seek(0)

    return buffer


st.title("📚 AI Research Assistant")

st.markdown(
    """
    Analyze research papers using Gemini AI.
    
    Generate:
    - Summary
    - Key Contributions
    - Limitations
    - Future Work
    - Interactive Q&A
    """
)

st.caption(
    "Upload research papers, generate insights, and chat with the paper."
)

st.divider()

st.subheader("☁️ Cloud Architecture")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.info("👤 User\n\nUploads PDF")

with col2:
    st.info("💻 Streamlit\n\nWeb Application")

with col3:
    st.info("🌐 Internet\n\nAPI Request")

with col4:
    st.info("☁️ Cloud AI\n\nGemini API")

with col5:
    st.info("🤖 GenAI Model\n\nGemini 2.5 Flash")

st.caption(
    "The application sends the research paper to a cloud-based "
    "Generative AI service, which processes the request and returns "
    "the generated analysis."
)

st.divider()

uploaded_file = st.file_uploader(
    "Upload a Research Paper",
    type=["pdf"]
)

if uploaded_file:

    st.success("PDF uploaded successfully!")

    st.write("File Name:", uploaded_file.name)
    st.write("File Size:", uploaded_file.size, "bytes")

    reader = PdfReader(uploaded_file)

    text = ""

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            text += page_text

    st.session_state.paper_text = text

    st.write("Total Pages:", len(reader.pages))
    st.write("Total Characters Extracted:", len(text))

    model = genai.GenerativeModel("gemini-2.5-flash")

    if st.button("Generate Analysis"):

        with st.status("☁️ Cloud AI Processing", expanded=True) as status:

            try:
                status.write("📄 Preparing research paper...")
                
                status.write("🌐 Sending request to cloud AI service...")
                
                status.write("🤖 Generative AI model is processing the paper...")
        
                response = model.generate_content(
                    f"""
                    Analyze the following research paper.
        
                    Return your response in the exact format:
        
                    SUMMARY:
                    <summary>
        
                    KEY CONTRIBUTIONS:
                    <bullet points>
        
                    LIMITATIONS:
                    <bullet points>
        
                    FUTURE WORK:
                    <bullet points>
        
                    Research Paper:
                    {text[:20000]}
                    """,
                        request_options={"timeout": 60}
                )
        
                status.write("📥 Receiving AI-generated response...")
        
                st.session_state.analysis = response.text
        
                status.update(
                    label="✅ Cloud AI Analysis Complete",
                    state="complete",
                    expanded=False
                )

            except Exception as e:
        
                status.update(
                    label="❌ Cloud AI Processing Failed",
                    state="error",
                    expanded=True
                )
        
                st.error(
                    "Gemini quota exceeded or API error. Please try again later."
                )


if st.session_state.analysis:

    analysis = st.session_state.analysis

    summary = extract_section(
        analysis,
        "SUMMARY:",
        "KEY CONTRIBUTIONS:"
    )

    contributions = extract_section(
        analysis,
        "KEY CONTRIBUTIONS:",
        "LIMITATIONS:"
    )

    limitations = extract_section(
        analysis,
        "LIMITATIONS:",
        "FUTURE WORK:"
    )

    future_work = extract_section(
        analysis,
        "FUTURE WORK:"
    )

    pdf_file = create_pdf(
        summary,
        contributions,
        limitations,
        future_work
    )

    st.download_button(
        label="📄 Download Analysis Report",
        data=pdf_file,
        file_name="Research_Analysis_Report.pdf",
        mime="application/pdf"
    )

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "Summary",
            "Contributions",
            "Limitations",
            "Future Work"
        ]
    )

    with tab1:
        st.write(summary)

    with tab2:
        st.write(contributions)

    with tab3:
        st.write(limitations)

    with tab4:
        st.write(future_work)

    st.divider()

    st.subheader("Ask Questions About This Paper")

    question = st.text_input(
        "Enter your question"
    )

    if st.button("Ask Question"):

        with st.spinner("Thinking..."):

            try:

                model = genai.GenerativeModel("gemini-2.5-flash")

                response = model.generate_content(
                    f"""
                    You are helping a student understand a research paper.

                    Research Paper:

                    {st.session_state.paper_text[:10000]}

                    Question:

                    {question}

                    Answer clearly and accurately.
                    """
                )

                st.session_state.chat_history.append(
                    {
                        "question": question,
                        "answer": response.text
                    }
                )

            except Exception as e:

                st.error(
                    "Gemini quota exceeded or API error. Please try again later."
                )

    st.divider()

st.subheader("🔬 Compare Research Papers")

st.write(
    "Upload two research papers and use Generative AI to compare "
    "their objectives, methodologies, contributions, limitations, "
    "and future work."
)

col1, col2 = st.columns(2)

with col1:
    paper1 = st.file_uploader(
        "Upload Paper 1",
        type=["pdf"],
        key="comparison_paper1"
    )

with col2:
    paper2 = st.file_uploader(
        "Upload Paper 2",
        type=["pdf"],
        key="comparison_paper2"
    )

if paper1 and paper2:

    if st.button("🔍 Compare Papers"):

        with st.spinner("☁️ Comparing papers using Cloud AI..."):

            try:

                reader1 = PdfReader(paper1)
                reader2 = PdfReader(paper2)

                text1 = ""
                text2 = ""

                for page in reader1.pages:
                    page_text = page.extract_text()

                    if page_text:
                        text1 += page_text

                for page in reader2.pages:
                    page_text = page.extract_text()

                    if page_text:
                        text2 += page_text

                model = genai.GenerativeModel("gemini-2.5-flash")

                response = model.generate_content(
                    f"""
                    Compare the following two research papers.

                    Provide the comparison in the following format:

                    OVERVIEW:
                    Give a brief overview of both papers.

                    OBJECTIVES:
                    Compare the objectives of both papers.

                    METHODOLOGY:
                    Compare the methodologies used.

                    KEY CONTRIBUTIONS:
                    Compare the major contributions.

                    LIMITATIONS:
                    Compare the limitations.

                    FUTURE WORK:
                    Compare the suggested future directions.

                    FINAL COMPARISON:
                    Explain which paper provides a stronger contribution
                    and why.

                    PAPER 1:
                    {text1[:15000]}

                    PAPER 2:
                    {text2[:15000]}
                    """
                )

                st.success("✅ Papers compared successfully!")

                st.subheader("📊 AI-Generated Comparison")

                st.write(response.text)

            except Exception as e:

                st.error(
                    "Unable to compare the papers. "
                    "Please check the files or Gemini API."
                )

    if st.session_state.chat_history:

        st.subheader("Conversation")

        for chat in reversed(st.session_state.chat_history):

            st.markdown(
                f"**Question:** {chat['question']}"
            )

            st.markdown(
                f"**Answer:** {chat['answer']}"
            )

            st.divider()
