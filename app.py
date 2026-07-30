import streamlit as st
import json

# Streamlit config MUST be the first command
st.set_page_config(page_title="AgentOps Support", page_icon="🤖", layout="centered")

from graph.workflow import graph

def apply_custom_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Outfit:wght@500;700&display=swap');
        
        /* Force Streamlit containers to be transparent */
        [data-testid="stAppViewContainer"], .main, .stApp {
            background: transparent !important;
        }
        
        /* 1. Synthwave 3D Grid Background */
        .grid-container {
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            perspective: 600px;
            overflow: hidden;
            z-index: -10;
            background: linear-gradient(to bottom, #09090b 0%, #1e1b4b 60%, #2e1065 100%);
        }
        
        /* Glowing Sun */
        .synth-sun {
            position: absolute;
            width: 400px;
            height: 400px;
            background: linear-gradient(to bottom, #fde047 0%, #f97316 40%, #ec4899 100%);
            border-radius: 50%;
            top: 40%;
            left: 50%;
            transform: translate(-50%, -50%);
            box-shadow: 0 0 120px rgba(236, 72, 153, 0.8);
            z-index: -9;
        }

        /* Moving 3D Grid */
        .grid-plane {
            position: absolute;
            width: 300vw;
            height: 150vh;
            bottom: -20vh;
            left: -100vw;
            background-image: 
                linear-gradient(rgba(236, 72, 153, 0.6) 2px, transparent 2px),
                linear-gradient(90deg, rgba(59, 130, 246, 0.6) 2px, transparent 2px);
            background-size: 80px 80px;
            transform: rotateX(75deg);
            transform-origin: top center;
            animation: gridMove 2s linear infinite;
            z-index: -8;
            /* Fade the grid into the horizon */
            -webkit-mask-image: linear-gradient(to bottom, transparent 0%, black 40%);
            mask-image: linear-gradient(to bottom, transparent 0%, black 40%);
        }

        @keyframes gridMove {
            0% { transform: rotateX(75deg) translateY(0); }
            100% { transform: rotateX(75deg) translateY(80px); }
        }

        /* 2. Animated Gradient Text (Title) */
        h1 {
            font-family: 'Outfit', sans-serif !important;
            font-size: 4rem !important;
            background: linear-gradient(to right, #fde047, #f97316, #ec4899, #fde047);
            background-size: 300% auto;
            color: #fff;
            background-clip: text;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: shine 3s linear infinite;
            text-align: center;
            padding-bottom: 0.5rem;
            text-shadow: 0 0 20px rgba(236,72,153,0.3);
        }

        @keyframes shine {
            to { background-position: 300% center; }
        }

        /* 3. Subtitle Fade/Slide Animation */
        .stMarkdown {
            color: #f8fafc;
            font-weight: 400;
            animation: fadeInUp 1s ease-out;
        }
        
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(15px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* Chat Bubbles (Glassmorphism + Neon borders) */
        .stChatMessage {
            background: rgba(15, 23, 42, 0.7) !important;
            backdrop-filter: blur(12px) !important;
            -webkit-backdrop-filter: blur(12px) !important;
            border: 1px solid rgba(236, 72, 153, 0.3) !important;
            border-left: 4px solid #ec4899 !important;
            border-radius: 12px !important;
            padding: 1.5rem !important;
            margin-bottom: 1rem !important;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        
        .stChatMessage:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 40px 0 rgba(236, 72, 153, 0.2);
            border: 1px solid rgba(236, 72, 153, 0.6) !important;
            border-left: 4px solid #fde047 !important;
        }

        /* Avatar styling */
        .stChatMessage [data-testid="stIconMaterial"] {
            color: #fde047 !important;
        }

        /* Expanders */
        div[data-testid="stExpander"] {
            background: rgba(15, 23, 42, 0.8) !important;
            border: 1px solid rgba(59, 130, 246, 0.4) !important;
            border-radius: 8px !important;
            backdrop-filter: blur(10px) !important;
            margin-top: 1rem !important;
            transition: all 0.3s ease;
        }
        
        div[data-testid="stExpander"]:hover {
            border-color: rgba(59, 130, 246, 0.8) !important;
            box-shadow: 0 0 15px rgba(59, 130, 246, 0.3);
        }

        div[data-testid="stExpander"] summary p {
            color: #60a5fa !important;
            font-family: 'Outfit', sans-serif !important;
            font-weight: 500;
            letter-spacing: 0.5px;
        }
        
        /* Code blocks inside expanders */
        div[data-testid="stExpander"] pre {
            background: rgba(0, 0, 0, 0.5) !important;
            border-radius: 6px !important;
            border: 1px solid rgba(59, 130, 246, 0.2);
        }
        
        /* Chat Input Container */
        .stChatInputContainer {
            background: rgba(15, 23, 42, 0.85) !important;
            backdrop-filter: blur(16px) !important;
            border: 1px solid rgba(236, 72, 153, 0.5) !important;
            border-radius: 20px !important;
            box-shadow: 0 0 30px rgba(236, 72, 153, 0.2) !important;
            padding: 0.2rem !important;
            transition: all 0.3s ease !important;
        }
        
        .stChatInputContainer:focus-within {
            border-color: #fde047 !important;
            box-shadow: 0 0 30px rgba(253, 224, 71, 0.4) !important;
            transform: translateY(-2px);
        }
        
        /* Text Area */
        .stChatInputContainer textarea {
            color: #F8FAFC !important;
            caret-color: #fde047 !important;
        }
        
        /* Send Button */
        .stChatInputContainer button {
            color: #ec4899 !important;
            transition: all 0.2s ease;
        }
        
        .stChatInputContainer button:hover {
            color: #fde047 !important;
            transform: scale(1.1);
        }
        
        /* Hide default Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Custom Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        ::-webkit-scrollbar-track {
            background: rgba(0, 0, 0, 0.2);
        }
        ::-webkit-scrollbar-thumb {
            background: rgba(236, 72, 153, 0.5);
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: rgba(236, 72, 153, 0.8);
        }
    </style>
    
    <!-- Injection of the 3D Synthwave DOM elements -->
    <div class="grid-container">
        <div class="synth-sun"></div>
        <div class="grid-plane"></div>
    </div>
    """, unsafe_allow_html=True)

def main():
    apply_custom_css()
    
    st.title("AgentOps Support")
    st.markdown("Ask about IT policies, hardware requests, or ticket management.", unsafe_allow_html=True)
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "trace" in msg and msg["trace"]:
                with st.expander("How I got this answer"):
                    st.json(msg["trace"])
                    
    if prompt := st.chat_input("Enter your request..."):
        if not prompt.strip():
            st.warning("Please enter a request")
            return
            
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            with st.spinner("Processing request..."):
                initial_state = {"raw_input": prompt}
                try:
                    result = graph.invoke(initial_state)
                    final_answer = result.get("final_answer", "Error resolving request.")
                    trace = result.get("trace", [])
                except Exception as e:
                    final_answer = f"Error: {str(e)}"
                    trace = []
                
            st.markdown(final_answer)
            if trace:
                with st.expander("How I got this answer"):
                    st.json(trace)
                    
        st.session_state.messages.append({
            "role": "assistant",
            "content": final_answer,
            "trace": trace
        })

if __name__ == "__main__":
    main()
