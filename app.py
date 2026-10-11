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

    # ==========================================
    # SAVE AI ANALYSIS TO AMAZON S3
    # ==========================================

    st.markdown("---")
    st.subheader("☁️ Save Analysis to Cloud")

    st.caption(
        "Save this AI-generated analysis to Amazon S3 "
        "so you can retrieve it later without calling Gemini again."
    )

    if s3_client is None or not AWS_S3_BUCKET:

        st.warning(
            "Amazon S3 is not configured. "
            "Check your Streamlit Secrets."
        )

    else:

        if st.button(
            "☁️ Save Analysis to Amazon S3",
            key="save_analysis_to_s3"
        ):

            try:
                # Prepare analysis data
                analysis_data = {
                    "paper_name": uploaded_file.name,
                    "summary": summary,
                    "key_contributions": contributions,
                    "limitations": limitations,
                    "future_work": future_work,
                    "full_analysis": analysis
                }

                # Convert analysis into JSON
                json_data = json.dumps(
                    analysis_data,
                    ensure_ascii=False,
                    indent=4
                )

                # Create a safe filename
                import hashlib

                paper_hash = hashlib.sha256(
                    uploaded_file.getvalue()
                ).hexdigest()[:12]

                original_name = os.path.splitext(
                    os.path.basename(uploaded_file.name)
                )[0]

                safe_name = "".join(
                    character
                    if character.isalnum() or character in "-_"
                    else "_"
                    for character in original_name
                )

                object_key = (
                    f"analysis-results/{paper_hash}_"
                    f"{safe_name}_analysis.json"
                )

                # Upload JSON to S3
                s3_client.put_object(
                    Bucket=AWS_S3_BUCKET,
                    Key=object_key,
                    Body=json_data.encode("utf-8"),
                    ContentType="application/json"
                )

                st.success(
                    "✅ Analysis saved successfully to Amazon S3!"
                )

                st.code(object_key, language=None)

            except Exception as e:

                st.error(
                    "Unable to save analysis to Amazon S3."
                )

                st.caption(
                    f"Error: {type(e).__name__}: {e}"
                )

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


# Generate comparison
if paper1 and paper2:

    # Upload comparison papers to Amazon S3
    st.markdown("---")
    st.subheader("☁️ Cloud Storage")
    
    st.caption(
        "Optionally store both research papers in your private "
        "Amazon S3 bucket."
    )
    
    if paper1 and paper2:
    
        if st.button(
            "☁️ Upload Both Papers to AWS S3",
            key="upload_comparison_papers_s3"
        ):
    
            if s3_client is None or not AWS_S3_BUCKET:
                st.error(
                    "Amazon S3 is not configured. "
                    "Please check your Streamlit Secrets."
                )
    
            else:
                import uuid
    
                papers_to_upload = [
                    paper1,
                    paper2
                ]
    
                successful_uploads = 0
    
                for uploaded_paper in papers_to_upload:
    
                    # Generate a unique object key to avoid overwriting
                    unique_id = uuid.uuid4().hex[:12]
    
                    safe_filename = os.path.basename(
                        uploaded_paper.name
                    )
    
                    object_key = (
                        f"research-papers/{unique_id}_{safe_filename}"
                    )
    
                    try:
                        s3_client.upload_fileobj(
                            BytesIO(uploaded_paper.getvalue()),
                            AWS_S3_BUCKET,
                            object_key,
                            ExtraArgs={
                                "ContentType": "application/pdf"
                            }
                        )
    
                        st.success(
                            f"✅ {uploaded_paper.name} uploaded successfully."
                        )
    
                        successful_uploads += 1
    
                    except Exception as e:
                        st.error(
                            f"❌ Failed to upload "
                            f"{uploaded_paper.name}: {e}"
                        )
    
                if successful_uploads == 2:
                    st.success(
                        "🎉 Both research papers are stored in Amazon S3!"
                    )
                elif successful_uploads == 1:
                    st.warning(
                        "One paper was uploaded successfully. "
                        "Check the error above for the other paper."
                    )

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

                else:
                    # Initialize Gemini
                    model = genai.GenerativeModel("gemini-2.5-flash")

                    comparison_prompt = f"""
                    Compare the following two research papers carefully.

                    RULES:
                    - Use only information supported by the papers.
                    - Do not invent results, contributions, or limitations.
                    - If information is unavailable, write "Not specified".
                    - Focus on meaningful differences, not repeated text.
                    - Keep every description concise and informative.
                    - Return valid JSON only, without Markdown code fences.

                    LENGTH GUIDELINES:
                    - Overview: maximum 45 words per paper.
                    - Research Objectives: maximum 35 words per paper.
                    - Methodology: maximum 40 words per paper.
                    - Key Contributions: maximum 40 words per paper.
                    - Limitations: maximum 30 words per paper.
                    - Future Work: maximum 30 words per paper.
                    - Overall Comparison: maximum 100 words.
                    - Key Insights: exactly 3 insights, maximum 20 words each.

                    Return JSON using exactly this structure:

                    {{
                        "comparison": [
                            {{
                                "category": "Overview",
                                "paper1": "Concise overview of Paper 1",
                                "paper2": "Concise overview of Paper 2"
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
                        "overall_comparison": "Concise comparison of similarities and differences.",
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

                    else:
                        # Clean the response
                        result_text = response.text.strip()

                        # Remove Markdown code fences if present
                        if result_text.startswith("```"):
                            result_text = result_text.split("\n", 1)[1]
                            result_text = result_text.rsplit("```", 1)[0].strip()

                        # Parse JSON
                        comparison_data = json.loads(result_text)

                        # Save results in session state
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


# Display comparison results
if st.session_state.get("paper_comparison"):

    comparison_data = st.session_state["paper_comparison"]

    filenames = st.session_state.get(
        "comparison_filenames",
        ("Paper 1", "Paper 2")
    )

    # Short labels for a cleaner interface
    paper1_label = "Paper 1"
    paper2_label = "Paper 2"

    st.divider()

    st.success("✅ Papers compared successfully!")

    st.subheader("📊 Research Paper Comparison")

    st.caption(
        f"Paper 1: {filenames[0]}  |  Paper 2: {filenames[1]}"
    )

    # Compact comparison sections
    for index, item in enumerate(comparison_data.get("comparison", [])):

        category = item.get("category", "Comparison")

        with st.expander(category, expanded=(index == 0)):

            col1, col2 = st.columns(2, gap="large")

            with col1:
                st.markdown(f"**📄 {paper1_label}**")
                st.caption(filenames[0])

                st.write(
                    item.get("paper1", "Not specified")
                )

            with col2:
                st.markdown(f"**📄 {paper2_label}**")
                st.caption(filenames[1])

                st.write(
                    item.get("paper2", "Not specified")
                )

    # Overall comparison
    st.subheader("🔍 Overall Comparison")

    with st.container(border=True):
        st.write(
            comparison_data.get(
                "overall_comparison",
                "No overall comparison provided."
            )
        )

    # Key insights
    st.subheader("💡 Key Insights")

    insights = comparison_data.get("key_insights", [])

    if insights:
        for index, insight in enumerate(insights, start=1):
            st.markdown(f"**{index}.** {insight}")
    else:
        st.info("No key insights were generated.")


# ==========================================
# CLOUD RESEARCH LIBRARY
# ==========================================

st.markdown("---")

st.header("📚 Cloud Research Library")

st.write(
    "View and download research papers stored "
    "in your private Amazon S3 bucket."
)

if s3_client is None or not AWS_S3_BUCKET:

    st.warning(
        "Amazon S3 is not configured. "
        "Please check your Streamlit Secrets."
    )

else:

    try:
        response = s3_client.list_objects_v2(
            Bucket=AWS_S3_BUCKET,
            Prefix="research-papers/"
        )

        papers = response.get("Contents", [])

        if not papers:

            st.info(
                "No research papers found in cloud storage. "
                "Upload a paper to get started."
            )

        else:

            # Display total number of papers
            st.success(
                f"📄 {len(papers)} research paper(s) found in S3."
            )

            # Search functionality
            search_query = st.text_input(
                "🔍 Search research papers by filename",
                key="cloud_library_search"
            )

            filtered_papers = [
                paper for paper in papers
                if search_query.lower()
                in paper["Key"].split("/")[-1].lower()
            ]

            if not filtered_papers:

                st.info("No matching research papers found.")

            else:

                # Display papers
                for paper in filtered_papers:

                    object_key = paper["Key"]
                    filename = object_key.split("/")[-1]

                    # Ignore folder placeholders
                    if not filename:
                        continue

                    with st.container(border=True):

                        col1, col2 = st.columns([3, 1])

                        with col1:

                            st.markdown(f"**📄 {filename}**")

                            st.caption(
                                f"Size: {paper['Size'] / 1024:.2f} KB"
                            )

                            st.caption(
                                f"Last modified: "
                                f"{paper['LastModified'].strftime('%d %b %Y, %I:%M %p')}"
                            )

                        with col2:

                            if st.button(
                                "⬇️ Download",
                                key=f"download_{object_key}"
                            ):

                                download_url = (
                                    s3_client.generate_presigned_url(
                                        "get_object",
                                        Params={
                                            "Bucket": AWS_S3_BUCKET,
                                            "Key": object_key
                                        },
                                        ExpiresIn=300
                                    )
                                )

                                st.link_button(
                                    "Open Download Link",
                                    download_url
                                )

    except Exception as e:

        st.error(
            "Unable to load research papers from Amazon S3."
        )

        st.caption(
            "Check your AWS permissions and bucket configuration."
        )

# ==========================================
# SAVED AI ANALYSES
# ==========================================

st.markdown("---")

st.header("☁️ Saved AI Analyses")

st.write(
    "Retrieve previously generated AI analyses from Amazon S3 "
    "without making another Gemini API call."
)

if s3_client is None or not AWS_S3_BUCKET:

    st.warning(
        "Amazon S3 is not configured. "
        "Check your Streamlit Secrets."
    )

else:

    try:
        response = s3_client.list_objects_v2(
            Bucket=AWS_S3_BUCKET,
            Prefix="analysis-results/"
        )

        analysis_files = [
            obj for obj in response.get("Contents", [])
            if obj["Key"].endswith(".json")
        ]

        if not analysis_files:

            st.info(
                "No saved analyses found. "
                "Generate an analysis and save it to the cloud first."
            )

        else:

            # Create a mapping between filenames and S3 object keys
            analysis_options = {
                obj["Key"].split("/")[-1]: obj["Key"]
                for obj in analysis_files
            }

            selected_filename = st.selectbox(
                "Select a saved analysis",
                options=list(analysis_options.keys()),
                key="saved_analysis_selector"
            )

            if st.button(
                "📂 Load Saved Analysis",
                key="load_saved_analysis"
            ):

                selected_key = analysis_options[selected_filename]

                with st.spinner("Retrieving analysis from Amazon S3..."):

                    saved_object = s3_client.get_object(
                        Bucket=AWS_S3_BUCKET,
                        Key=selected_key
                    )

                    saved_analysis = json.loads(
                        saved_object["Body"].read().decode("utf-8")
                    )

                    st.session_state["loaded_cloud_analysis"] = (
                        saved_analysis
                    )

                    st.session_state["loaded_cloud_analysis_name"] = (
                        selected_filename
                    )

                st.success("Saved analysis loaded successfully!")

            # Display the previously loaded analysis
            if st.session_state.get("loaded_cloud_analysis"):

                saved_analysis = st.session_state[
                    "loaded_cloud_analysis"
                ]

                st.subheader(
                    st.session_state.get(
                        "loaded_cloud_analysis_name",
                        "Saved Analysis"
                    )
                )

                st.caption(
                    "Retrieved from Amazon S3. "
                    "No new Gemini analysis was generated."
                )

                st.markdown("### 📄 Research Paper")

                st.write(
                    saved_analysis.get(
                        "paper_name",
                        "Filename not available"
                    )
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
                    st.write(
                        saved_analysis.get(
                            "summary",
                            "No summary available."
                        )
                    )

                with tab2:
                    st.write(
                        saved_analysis.get(
                            "key_contributions",
                            "No contributions available."
                        )
                    )

                with tab3:
                    st.write(
                        saved_analysis.get(
                            "limitations",
                            "No limitations available."
                        )
                    )

                with tab4:
                    st.write(
                        saved_analysis.get(
                            "future_work",
                            "No future work available."
                        )
                    )

    except Exception as e:

        st.error(
            "Unable to retrieve saved analyses from Amazon S3."
        )

        st.caption(
            f"Error: {type(e).__name__}: {e}"
        )
