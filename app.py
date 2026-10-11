import streamlit as st
from pypdf import PdfReader
import os
from dotenv import load_dotenv
import google.generativeai as genai
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
import boto3
from botocore.exceptions import ClientError, BotoCoreError
import json
import pandas as pd

st.set_page_config(
    page_title="AI Research Assistant",
    page_icon="📚",
    layout="wide"
)

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# AWS S3 Configuration
s3_client = None

try:
    AWS_ACCESS_KEY_ID = st.secrets["AWS_ACCESS_KEY_ID"]
    AWS_SECRET_ACCESS_KEY = st.secrets["AWS_SECRET_ACCESS_KEY"]
    AWS_REGION = st.secrets["AWS_REGION"]
    AWS_S3_BUCKET = st.secrets["AWS_S3_BUCKET"]

    s3_client = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )

except Exception:
    AWS_S3_BUCKET = None
    st.sidebar.warning("Amazon S3 is not configured.")

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

    st.markdown("---")

    st.subheader("☁️ Cloud Service Status")

    # Gemini API configuration status
    if api_key:
        st.success("🤖 Gemini API: Configured")
    else:
        st.error("🤖 Gemini API: Missing API Key")

    # AWS S3 configuration status
    if s3_client is not None:
        st.success("☁️ Amazon S3: Configured")
    else:
        st.error("☁️ Amazon S3: Not Configured")

    # PDF processing status
    st.info("📄 PDF Processing: Ready")

    st.caption("AI: Gemini API | Storage: Amazon S3")

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

        # Amazon S3 Cloud Storage
    st.subheader("☁️ Amazon S3 Cloud Storage")

    if s3_client is not None:

        st.success("Amazon S3 connection configured")

        if st.button("☁️ Upload PDF to Amazon S3"):

            object_key = f"research-papers/{uploaded_file.name}"

            try:
                with st.status(
                    "☁️ Uploading research paper to Amazon S3...",
                    expanded=True
                ) as status:

                    status.write("Preparing PDF...")
                    status.write("Connecting to Amazon S3...")
                    status.write("Uploading research paper...")

                    s3_client.upload_fileobj(
                        BytesIO(uploaded_file.getvalue()),
                        AWS_S3_BUCKET,
                        object_key,
                        ExtraArgs={
                            "ContentType": "application/pdf"
                        }
                    )

                    status.update(
                        label="✅ Upload completed successfully",
                        state="complete",
                        expanded=False
                    )

                st.success(
                    f"Stored in S3: {object_key}"
                )

            except (ClientError, BotoCoreError) as e:

                st.error(
                    f"Amazon S3 upload failed: {e}"
                )

            except Exception as e:

                st.error(
                    f"Unexpected upload error: {e}"
                )

    else:
        st.warning(
            "Amazon S3 credentials are not configured. "
            "Check your Streamlit Secrets."
        )
        

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
                    {text[:30000]}
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
                    f"Gemini API Error: {type(e).__name__}: {e}"
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

                    {st.session_state.paper_text[:20000]}

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

    if st.button("🔍 Compare Papers", key="compare_papers_button"):

        with st.spinner("☁️ Comparing papers using Cloud AI..."):

            try:
                # Extract text from Paper 1
                reader1 = PdfReader(paper1)
                text1 = ""

                for page in reader1.pages:
                    page_text = page.extract_text()

                    if page_text:
                        text1 += page_text + "\n"

                # Extract text from Paper 2
                reader2 = PdfReader(paper2)
                text2 = ""

                for page in reader2.pages:
                    page_text = page.extract_text()

                    if page_text:
                        text2 += page_text + "\n"

                # Validate extracted text
                if not text1.strip() or not text2.strip():
                    st.error(
                        "Unable to extract text from one or both PDFs. "
                        "Please upload text-readable research papers."
                    )
                    st.stop()

                # Initialize Gemini
                model = genai.GenerativeModel("gemini-2.5-flash")

                comparison_prompt = f"""
                Compare the following two research papers carefully.

                Use only information supported by the papers.
                Do not invent results, contributions, or limitations.
                If information is unavailable, state "Not specified".

                Return ONLY valid JSON, without Markdown code fences,
                using exactly this structure:

                {{
                    "comparison": [
                        {{
                            "category": "Overview",
                            "paper1": "Brief overview of Paper 1",
                            "paper2": "Brief overview of Paper 2"
                        }},
                        {{
                            "category": "Research Objectives",
                            "paper1": "Objectives of Paper 1",
                            "paper2": "Objectives of Paper 2"
                        }},
                        {{
                            "category": "Methodology",
                            "paper1": "Methodology of Paper 1",
                            "paper2": "Methodology of Paper 2"
                        }},
                        {{
                            "category": "Key Contributions",
                            "paper1": "Contributions of Paper 1",
                            "paper2": "Contributions of Paper 2"
                        }},
                        {{
                            "category": "Limitations",
                            "paper1": "Limitations of Paper 1",
                            "paper2": "Limitations of Paper 2"
                        }},
                        {{
                            "category": "Future Work",
                            "paper1": "Future work of Paper 1",
                            "paper2": "Future work of Paper 2"
                        }}
                    ],
                    "overall_comparison": "Explain the major similarities "
                    "and differences between the papers.",
                    "key_insights": [
                        "First important insight",
                        "Second important insight",
                        "Third important insight"
                    ]
                }}

                PAPER 1:
                {text1[:20000]}

                PAPER 2:
                {text2[:20000]}
                """

                response = model.generate_content(comparison_prompt)

                if not response.text:
                    st.error("Gemini returned an empty response.")
                    st.stop()

                # Parse the JSON response
                result_text = response.text.strip()

                # Handle responses wrapped in Markdown code fences
                if result_text.startswith("```"):
                    result_text = result_text.split("\n", 1)[1]
                    result_text = result_text.rsplit("```", 1)[0].strip()

                comparison_data = json.loads(result_text)

                # Save results so they remain visible after reruns
                st.session_state["paper_comparison"] = comparison_data
                st.session_state["comparison_filenames"] = (
                    paper1.name,
                    paper2.name
                )

            except json.JSONDecodeError:
                st.error(
                    "The AI returned an unexpected format. "
                    "Please click Compare Papers and try again."
                )

            except Exception as e:
                st.error(
                    f"Unable to compare the papers: "
                    f"{type(e).__name__}: {e}"
                )


# Display comparison results outside the button block
if st.session_state.get("paper_comparison"):

    comparison_data = st.session_state["paper_comparison"]

    filenames = st.session_state.get(
        "comparison_filenames",
        ("Paper 1", "Paper 2")
    )

    st.success("✅ Papers compared successfully!")

    st.subheader("📊 Research Paper Comparison")

st.caption(
    f"Paper 1: {filenames[0]}  |  Paper 2: {filenames[1]}"
)

# Display each comparison category in a separate card
for item in comparison_data["comparison"]:

    category = item.get("category", "Comparison")

    with st.container(border=True):

        st.markdown(f"### {category}")

        col1, col2 = st.columns(2, gap="medium")

        with col1:
            st.markdown("**📄 Paper 1**")
            st.write(item.get("paper1", "Not specified"))

        with col2:
            st.markdown("**📄 Paper 2**")
            st.write(item.get("paper2", "Not specified"))

    # Overall comparison
    st.subheader("🔍 Overall Comparison")

    st.write(
        comparison_data.get(
            "overall_comparison",
            "No overall comparison provided."
        )
    )

    # Key insights
    st.subheader("💡 Key Insights")

    insights = comparison_data.get("key_insights", [])

    for insight in insights:
        st.markdown(f"- {insight}")
