#Using streamlit, we dont have to use html or css for frontend
import streamlit as st
import pandas as pd#pandas to do operations on data frame
import time#used for making live url
import os #files are automatically created using os - builtin

#from dotenv import load_dotenv #load_dotenv function from dotenv package
#load_dotenv() #loads environment variables from .env file into the application

try: #using import statements inside try except to catch errors
    from auth import login
    from utils.router import choose_models
    from utils.parallel import run_parallel
    from utils.rate_limiter import check_limit
    from utils.report import generate_report
except Exception as e: #except displays error message if any module is missing from try block
    st.error(e)
    st.stop()

st.set_page_config( #works a s html head
    page_title="LLM Nexus | Enterprise Comparison",
    page_icon="⚡",
    layout="wide", #allows to print in full width
    initial_sidebar_state="expanded" # when page is reloaded everytime, the sodebar is default expanded
)


st.markdown(
    """
<style>
/* =========================
   COLOR VARIABLES
========================= */
:root {
    --bg-gradient: linear-gradient(
        135deg,
        #f0f9ff 0%,
        #eef2ff 35%,
        #faf5ff 70%,
        #ffffff 100%
    );

    --bg-surface: rgba(255, 255, 255, 0.75);
    --bg-card: rgba(255, 255, 255, 0.9);
    --border-soft: #dbeafe;
    --text-main: #0f172a;
    --text-muted: #475569;

    --accent-primary: #6366f1;
    --accent-hover: #4f46e5;
    --accent-glow: rgba(99, 102, 241, 0.25);
}

/* =========================
   BASE LAYOUT
========================= */
html, body, .stApp {
    margin: 0 !important;
    padding: 0 !important;
    background: var(--bg-gradient) !important;
    color: var(--text-main);
}

/* Hide Streamlit default UI */
header,
div[data-testid="stToolbar"],
div[data-testid="stDecoration"],
div[data-testid="stStatusWidget"] {
    display: none !important;
}

/* Main container */
.block-container {
    padding-top: 1.2rem !important;
    padding-bottom: 2rem !important;
}

/* =========================
   TYPOGRAPHY
========================= */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Headings */
h1, h2, h3, h4, h5 {
    color: #0f172a !important;
    margin-top: 0 !important;
}

.main-header {
    font-size: 2.6rem;
    font-weight: 700;
}

.sub-header {
    font-size: 1.1rem;
    color: var(--text-muted);
    margin-bottom: 2rem;
}

/* =========================
   SIDEBAR
========================= */
section[data-testid="stSidebar"] {
    background-color: rgba(255, 255, 255, 0.85);
    backdrop-filter: blur(10px);
    border-right: 1px solid var(--border-soft);
}

/* =========================
   INPUTS
========================= */
.stTextArea textarea {
    background-color: var(--bg-surface);
    border: 1px solid var(--border-soft);
    color: var(--text-main);
    border-radius: 10px;
}

.stTextArea textarea:focus {
    border-color: var(--accent-primary);
    box-shadow: 0 0 0 1px var(--accent-primary);
}

div[data-baseweb="select"] > div {
    background-color: var(--bg-surface);
    border: 1px solid var(--border-soft);
    border-radius: 10px;
    color: var(--text-main);
}

/* =========================
   BUTTONS
========================= */
div.stButton > button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: #ffffff;
    border: none;
    padding: 0.75rem 2rem;
    font-weight: 600;
    border-radius: 12px;
    width: 100%;
    transition: all 0.2s ease;
}

div.stButton > button:hover {
    background: linear-gradient(135deg, #4f46e5, #7c3aed);
    box-shadow: 0 10px 24px var(--accent-glow);
}

/* =========================
   MODEL CARDS
========================= */
.model-card {
    background-color: var(--bg-card);
    border: 1px solid var(--border-soft);
    border-radius: 16px;
    padding: 18px;
    box-shadow: 0 8px 20px rgba(15, 23, 42, 0.08);
}

.model-name {
    font-size: 0.85rem;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    border-bottom: 1px solid var(--border-soft);
    padding-bottom: 6px;
    margin-bottom: 10px;
}

/* =========================
   METRICS
========================= */
div[data-testid="metric-container"] {
    background-color: var(--bg-card);
    border: 1px solid var(--border-soft);
    border-radius: 12px;
    padding: 14px 18px;
}

/* =========================
   CODE / JSON
========================= */
pre, code {
    background-color: #f8fafc !important;
    color: #0f172a !important;
    border-radius: 10px;
}

/* =========================
   TABS
========================= */
div[data-testid="stTabs"] {
    background-color: transparent;
}
</style>
""",
    unsafe_allow_html=True
)



with st.sidebar:
    st.title("⚙️ Controls")
    
    if "user" in st.session_state: #used to keep track of time spent on server
        st.info(f"👤 Logged in as: **{st.session_state.user}**")
    
    st.markdown("---")
    
    st.subheader("Configuration")
    model_temp = st.slider("Temperature (Creativity)", 0.0, 1.0, 0.7)
    max_tokens = st.number_input("Max Tokens", value=1024, step=256)
    
    st.markdown("---")
    st.caption("v2.1.0 | Enterprise Edition")


def main():
    
    login() 
    if "user" not in st.session_state:
        st.stop()

   
    st.markdown('<div class="main-header">LLM Nexus</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Intelligent routing & cost-analysis engine for Generative AI.</div>', unsafe_allow_html=True)

    
    col1, col2 = st.columns([1, 3])

    with col1:
        task = st.selectbox(
            "Target Objective",
            ["General", "Coding", "Fast Response", "Cost Saving"],
            help="This determines which models are selected via the router."
        )
        
       
        st.metric(label="Active Models", value="3 Online", delta="All Systems Go")

    with col2:
        prompt = st.text_area(
            "Input Prompt",
            height=140,
            placeholder="E.g., Write a secure Python function to connect to AWS S3...",
            label_visibility="visible"
        )

   
    col_submit, col_spacer = st.columns([1, 4])
    with col_submit:
        run_btn = st.button("⚡ Execute Query")

    if run_btn:
        if not check_limit(st.session_state.user):
            st.error("🚫 Rate limit reached. Please upgrade your plan or wait.")
            st.stop()
            
        if not prompt.strip():
            st.warning("⚠️ Please provide a prompt to analyze.")
            st.stop()

     
        with st.status("🔄 Orchestrating Model Requests...", expanded=True) as status:
            st.write("🔍 Analyzing intent...")
            models = choose_models(task)
            st.write(f"✅ Selected optimized models: **{', '.join(models)}**")
            
            st.write("🚀 Dispatching parallel requests...")
            start_time = time.time()
            
            responses = run_parallel(prompt, models)
            
            elapsed = round(time.time() - start_time, 2)
            status.update(label=f"✅ Complete! Processed in {elapsed}s", state="complete", expanded=False)

     
        st.markdown("### 📊 Analysis Results")
        
       
        tab1, tab2, tab3, tab4 = st.tabs([
            "👁️ Visual Comparison",
            "📝 Raw Data",
            "📉 Cost Report",
            "📊 Performance Dashboard"
        ])



        with tab1:
           
            cols = st.columns(len(responses))
            
         
            for idx, (model_name, response_text) in enumerate(responses.items()):
                with cols[idx]:
                    st.markdown(f"""
                    <div class="model-card">
                        <div class="model-name">{model_name}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.markdown("---")
                    st.markdown(response_text) 

        with tab2:
            st.json(responses)

        with tab3:
           
            report_status = generate_report(prompt, responses)
            st.success("Report generated and saved to database.")
            
           
            metrics_col1, metrics_col2 = st.columns(2)
            metrics_col1.metric("Estimated Cost", "$0.0042", "-12%")
            metrics_col2.metric("Latency Average", f"{elapsed}s", "Fast")
        with tab4:
            st.markdown("### 📊 Model Performance Dashboard")

            metrics_file = "data/metrics/metrics.csv"

            if not os.path.exists(metrics_file):
                st.warning("No metrics data available yet. Run some prompts first.")
            else:
                df = pd.read_csv(metrics_file)

                df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")

                st.subheader("⏱️ Average Latency per Model")
                latency_df = df.groupby("model")["latency"].mean().reset_index()
                st.bar_chart(latency_df.set_index("model"))

                st.subheader("📏 Average Response Length")
                length_df = df.groupby("model")["response_length"].mean().reset_index()
                st.bar_chart(length_df.set_index("model"))

                st.subheader("📈 Requests Over Time")
                time_df = df.set_index("timestamp").resample("1min").count()["model"]
                st.line_chart(time_df)


if __name__ == "__main__":
    main()
