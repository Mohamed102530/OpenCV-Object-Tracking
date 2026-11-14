import streamlit as st
import cv2
import numpy as np
import tempfile
import os
import time
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ---------------- PAGE CONFIGURATION ----------------
st.set_page_config(
    page_title="Motion Analytics Studio Pro",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- CUSTOM CSS (MODERN GLASSMORPHISM DARK DESIGN) ----------------
st.markdown("""
<style>
    /* Main Background & Base Styling */
    .stApp {
        background: linear-gradient(135deg, #0d1117 0%, #161b22 50%, #0d1117 100%);
        color: #e6edf3;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #161b22 !important;
        border-right: 1px solid #30363d;
    }
    
    /* Metric Cards Styling */
    div[data-testid="stMetric"] {
        background: rgba(22, 27, 34, 0.7);
        backdrop-filter: blur(10px);
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        border-color: #58a6ff;
    }
    
    /* Header Gradient Accent */
    .main-title {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #58a6ff 0%, #a5d6ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    .sub-title {
        color: #8b949e;
        font-size: 1.05rem;
        margin-bottom: 25px;
    }
    
    /* Custom Card Containers */
    .content-card {
        background: rgba(22, 27, 34, 0.6);
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
    }
    
    /* Buttons Styling */
    .stButton>button {
        background: linear-gradient(90deg, #238636 0%, #2ea043 100%);
        color: #ffffff;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 600;
        letter-spacing: 0.5px;
        transition: all 0.2s ease;
        box-shadow: 0 4px 12px rgba(46, 160, 67, 0.2);
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #2ea043 0%, #3fb950 100%);
        box-shadow: 0 6px 16px rgba(46, 160, 67, 0.4);
        transform: translateY(-1px);
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #0d1117;
        padding: 8px;
        border-radius: 10px;
        border: 1px solid #30363d;
    }
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        white-space: pre;
        border-radius: 6px;
        color: #8b949e;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background-color: #21262d !important;
        color: #58a6ff !important;
    }
</style>
""", unsafe_allow_html=True)


# ---------------- HELPER FUNCTION FOR VIDEO WRITING ----------------
def get_video_writer(output_path, fps, width, height):
    """
    Attempts to write video using H.264 codecs compatible with web browsers.
    """
    codecs_to_try = [
        ('avc1', 'mp4'),
        ('H264', 'mp4'),
        ('mp4v', 'mp4'),
        ('XVID', 'avi')
    ]
    
    for codec, ext in codecs_to_try:
        fourcc = cv2.VideoWriter_fourcc(*codec)
        writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        if writer.isOpened():
            return writer
    return None


# ---------------- HEADER ----------------
st.markdown('<div class="main-title">⚡ Motion Analytics Studio Pro</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Computer vision-powered video activity tracking and real-time motion diagnostics</div>', unsafe_allow_html=True)

# ---------------- SIDEBAR CONTROLS ----------------
with st.sidebar:
    st.title("⚙️ Engine Parameters")
    
    st.subheader("Background Subtractor")
    history = st.slider("History Frame Depth", 100, 1000, 500, help="Number of previous frames affecting the background model.")
    var_threshold = st.slider("Variance Threshold", 5, 100, 32, help="Threshold on the squared Mahalanobis distance to decide whether it is foreground or background.")
    detect_shadows = st.checkbox("Detect Shadows", value=True, help="Shadows will be marked in gray if enabled.")
    
    st.divider()
    
    st.subheader("Spatial Filtering")
    min_area = st.slider("Minimum Object Area (px)", 100, 10000, 600, step=100)
    learning_rate = st.slider("Learning Rate", 0.0, 0.1, 0.001, format="%.4f")
    blur_size = st.selectbox("Gaussian Blur Kernel", [3, 5, 7, 9, 11], index=1)
    
    st.divider()
    
    st.subheader("Visualization Overlay")
    box_color = st.color_picker("Bounding Box Color", "#00FF66")
    # Convert hex color to BGR for OpenCV
    box_color_bgr = tuple(int(box_color.lstrip('#')[i:i+2], 16) for i in (4, 2, 0))

# ---------------- TAB LAYOUT ----------------
tab1, tab2 = st.tabs(["📁 Video File Processing", "🎥 Live Camera Feed"])

# ================= TAB 1: FILE PROCESSING =================
with tab1:
    uploaded_file = st.file_uploader("Upload target video file", type=["mp4", "avi", "mov", "mkv"])
    
    if uploaded_file is not None:
        col_btn1, col_btn2 = st.columns([1, 4])
        with col_btn1:
            run_processing = st.button("🚀 Process Video", use_container_width=True)
            
        if run_processing:
            input_path = None
            output_path = None
            
            try:
                # Save input temporarily
                suffix = os.path.splitext(uploaded_file.name)[1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_in:
                    temp_in.write(uploaded_file.read())
                    input_path = temp_in.name

                cap = cv2.VideoCapture(input_path)
                if not cap.isOpened():
                    st.error("Failed to read video format.")
                    st.stop()

                fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
                total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_out:
                    output_path = temp_out.name

                writer = get_video_writer(output_path, fps, width, height)
                
                # Background Subtractor Initialization
                bg_subtractor = cv2.createBackgroundSubtractorMOG2(
                    history=history,
                    varThreshold=var_threshold,
                    detectShadows=detect_shadows
                )
                
                kernel = np.ones((3, 3), np.uint8)
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                frame_data = []
                total_detections = 0
                max_objects = 0
                frame_idx = 0
                start_time = time.time()
                
                while cap.isOpened():
                    ret, frame = cap.read()
                    if not ret:
                        break
                        
                    frame_idx += 1
                    
                    # Preprocessing
                    blurred = cv2.GaussianBlur(frame, (blur_size, blur_size), 0)
                    fg_mask = bg_subtractor.apply(blurred, learningRate=learning_rate)
                    
                    if detect_shadows:
                        _, fg_mask = cv2.threshold(fg_mask, 200, 255, cv2.THRESH_BINARY)
                        
                    # Noise Reduction
                    fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
                    fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)
                    
                    # Contours Detection
                    contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    
                    current_objects = 0
                    for cnt in contours:
                        if cv2.contourArea(cnt) > min_area:
                            x, y, w, h = cv2.boundingRect(cnt)
                            cv2.rectangle(frame, (x, y), (x + w, y + h), box_color_bgr, 2)
                            cv2.putText(
                                frame, "Motion", (x, max(y - 8, 15)),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, box_color_bgr, 1, cv2.LINE_AA
                            )
                            current_objects += 1

                    total_detections += current_objects
                    max_objects = max(max_objects, current_objects)
                    
                    frame_data.append({
                        "Frame": frame_idx,
                        "Timestamp (s)": round(frame_idx / fps, 2),
                        "Detected Objects": current_objects
                    })
                    
                    writer.write(frame)
                    
                    if total_frames > 0:
                        pct = min(frame_idx / total_frames, 1.0)
                        progress_bar.progress(pct)
                        status_text.caption(f"Processing Frame **{frame_idx}** of **{total_frames}** ({int(pct*100)}%)")

                cap.release()
                writer.release()
                
                processing_time = round(time.time() - start_time, 2)
                progress_bar.progress(1.0)
                status_text.success(f"Processing complete in {processing_time} seconds!")
                
                # Cache results in Session State
                with open(output_path, "rb") as vf:
                    st.session_state["processed_video"] = vf.read()
                    
                st.session_state["original_video"] = uploaded_file.getvalue()
                st.session_state["frame_data"] = frame_data
                st.session_state["total_detections"] = total_detections
                st.session_state["max_objects"] = max_objects
                st.session_state["total_frames"] = frame_idx
                st.session_state["processing_fps"] = round(frame_idx / processing_time, 1)

            finally:
                if input_path and os.path.exists(input_path):
                    os.remove(input_path)
                if output_path and os.path.exists(output_path):
                    os.remove(output_path)

    # Display Results Dashboard
    if "processed_video" in st.session_state:
        st.divider()
        st.subheader("📊 Key Metrics & Diagnostics")
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Analyzed Frames", f"{st.session_state['total_frames']:,}")
        m2.metric("Cumulative Detections", f"{st.session_state['total_detections']:,}")
        m3.metric("Peak Concurrent Objects", st.session_state['max_objects'])
        m4.metric("Engine Processing Speed", f"{st.session_state['processing_fps']} FPS")
        
        st.divider()
        
        col_vid_orig, col_vid_proc = st.columns(2)
        with col_vid_orig:
            st.markdown("### 📽️ Original Source")
            st.video(st.session_state["original_video"])
            
        with col_vid_proc:
            st.markdown("### 🎯 Motion Overlay Result")
            st.video(st.session_state["processed_video"])
            st.download_button(
                label="⬇️ Download Output Video",
                data=st.session_state["processed_video"],
                file_name="motion_detected_output.mp4",
                mime="video/mp4",
                use_container_width=True
            )
            
        st.divider()
        
        # Analytics Visualizations
        st.subheader("📈 Motion Time-Series Analysis")
        df_analytics = pd.DataFrame(st.session_state["frame_data"])
        
        chart_col, stat_col = st.columns([3, 1])
        
        with chart_col:
            fig = px.area(
                df_analytics,
                x="Timestamp (s)",
                y="Detected Objects",
                title="Motion Intensity Timeline",
                color_discrete_sequence=["#58a6ff"]
            )
            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(22, 27, 34, 0.8)",
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor="#30363d")
            )
            st.plotly_chart(fig, use_container_width=True)
            
        with stat_col:
            st.markdown("#### Activity Summary")
            active_frames = len(df_analytics[df_analytics["Detected Objects"] > 0])
            activity_pct = round((active_frames / len(df_analytics)) * 100, 1)
            
            st.write(f"• **Active Motion Frames:** {active_frames}")
            st.write(f"• **Activity Ratio:** {activity_pct}%")
            st.write(f"• **Average Motion Count:** {round(df_analytics['Detected Objects'].mean(), 2)}")
            
            # Export CSV
            csv_data = df_analytics.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📄 Export Analytics (CSV)",
                data=csv_data,
                file_name="motion_analysis.csv",
                mime="text/csv",
                use_container_width=True
            )

# ================= TAB 2: WEBCAM LIVE STREAM =================
with tab2:
    st.subheader("🎥 Real-Time Camera Stream")
    run_cam = st.checkbox("Turn On Webcam")
    FRAME_WINDOW = st.image([])
    
    if run_cam:
        cam = cv2.VideoCapture(0)
        bg_sub_live = cv2.createBackgroundSubtractorMOG2(
            history=history,
            varThreshold=var_threshold,
            detectShadows=detect_shadows
        )
        kernel = np.ones((3, 3), np.uint8)

        while run_cam:
            ret, frame = cam.read()
            if not ret:
                st.warning("Unable to retrieve webcam stream.")
                break
                
            blurred = cv2.GaussianBlur(frame, (blur_size, blur_size), 0)
            fg_mask = bg_sub_live.apply(blurred, learningRate=learning_rate)
            
            if detect_shadows:
                _, fg_mask = cv2.threshold(fg_mask, 200, 255, cv2.THRESH_BINARY)
                
            fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
            contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for cnt in contours:
                if cv2.contourArea(cnt) > min_area:
                    x, y, w, h = cv2.boundingRect(cnt)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), box_color_bgr, 2)
                    
            # Convert BGR to RGB for Streamlit rendering
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            FRAME_WINDOW.image(frame_rgb)
        
        cam.release()