import streamlit as st
from main import VernierFSRLogger
from pathlib import Path
from datetime import datetime

st.set_page_config(
    page_title="Vernier FSR Logger",
    page_icon="📟",
    layout="wide",  # Makes the layout wider
)

def run_logger(duration, delay, baud, timeout, save_csv, exp_name):
    logger = VernierFSRLogger(baud=baud, timeout=timeout)
    logger.run_for(duration_seconds=duration, start_delay=delay)

    raw_file = clean_file = None
    if save_csv:
        if exp_name:
            base_dir = Path("hta") / exp_name
            base_dir.mkdir(parents=True, exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            raw_file = base_dir / f"{exp_name}_raw_{ts}.csv"
            clean_file = base_dir / f"{exp_name}_clean_{ts}.csv"

        raw_file = logger.save_to_csv(filename=str(raw_file) if raw_file else None)
        clean_file = logger.save_clean_csv(filename=str(clean_file) if clean_file else None)

    return raw_file, clean_file

def main():
    st.markdown("<h1 style='font-size: 2.5rem;'>📟 Vernier FSR Logger Interface</h1>", unsafe_allow_html=True)
    st.markdown("Use this interface to run your Vernier FSR Logger and save logs.")
    st.markdown("---")

    col1, col2 = st.columns([3, 1])

    with col1:
            exp_name = st.text_input("Experiment Name", placeholder="Enter name (optional)")

    with col2:
            st.markdown("<div style='margin-top: 2.5em;'>", unsafe_allow_html=True)  # align toggle vertically
            save_csv = st.toggle("💾 Save CSV logs", value=True)
            st.markdown("</div>", unsafe_allow_html=True)

    duration = st.slider("Logging Duration (seconds)", min_value=5, max_value=120, value=30, step=5)
    delay = st.slider("Start Delay (seconds)", min_value=0, max_value=30, value=0, step=1)


    st.markdown("---")
    if st.button("🚀 Start Logging", use_container_width=True):
        st.info("Running the logger...")
        with st.spinner("Logging in progress..."):
            raw_file, clean_file = run_logger(duration, delay, 9600, 1.0, save_csv, exp_name)

        st.success("Logging complete.")
        if save_csv:
            if raw_file:
                st.write(f"Raw CSV saved at: `{raw_file}`")
            if clean_file:
                st.write(f"🧹 Clean CSV saved at: `{clean_file}`")

if __name__ == "__main__":
    main()
