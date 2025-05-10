import streamlit as st
import webbrowser

def main():
    # Set page configuration
    st.set_page_config(
        page_title="Automated Handwritten Answers Evaluation",
        page_icon="📝",
        layout="wide"
    )
    
    # Custom CSS for styling
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        text-align: center;
        margin-bottom: 2rem;
        color: #1E3A8A;
    }

    .card {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }

    .student-card {
        background-color: #E0F7FA;
        color: #006064;
    }

    .teacher-card {
        background-color: #E8EAF6;
        color: #1A237E;
    }

    .card-title {
        font-size: 1.5rem;
        margin-bottom: 0.5rem;
        text-align: center;
    }

    .card-text {
        font-size: 1rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
        text-align: center;
    }

    .footer {
        margin-top: 3rem;
        text-align: center;
        color: #6B7280;
        font-size: 0.875rem;
    }

    .role-btn {
        display: block;
        width: 100%;
        text-align: center;
        font-weight: bold;
        padding: 0.75rem 1rem;
        border-radius: 0.375rem;
        cursor: pointer;
        text-decoration: none;
        color:white;
        transition: transform 0.15s ease-in-out;
    }

    .role-btn:hover {
        transform: translateY(-3px);
    }

    .student-btn {
        background-color: #00BCD4;
    }

    .student-btn:hover {
        background-color: #0097A7;
    }

    .teacher-btn {
        background-color: #3F51B5;
    }

    .teacher-btn:hover {
        background-color: #303F9F;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # App Header
    st.markdown("<h1 class='main-header'>Automated Handwritten Answers Evaluation System</h1>", 
                unsafe_allow_html=True)
    
    # Brief description
    st.markdown("""
    <p style='font-size: 1.2rem; text-align: center; margin-bottom: 2rem;'>
    Welcome to the automated system that evaluates handwritten answers using AI technology.
    Please select your role below to continue.
    </p>
    """, unsafe_allow_html=True)
    
    # Create two columns for the role cards
    col1, col2 = st.columns(2)
    
    # Student Role Card
    with col1:
        st.markdown("""
        <div class='card student-card'>
            <h2 class='card-title'>Student Portal</h2>
            <p class='card-text'>
                Upload your handwritten answers, receive instant feedback, 
                and track your performance over time.
            </p>
            <a class='role-btn student-btn' href='https://automated-evaluation-of-handwritten-answers-using-mistral-nddm.streamlit.app/' target='_blank'>
                Access Student Portal
            </a>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Open Student Portal", key="student_btn"):
            js = f"""
            <script>
                window.open('https://automated-evaluation-of-handwritten-answers-using-mistral-nddm.streamlit.app/', '_blank');
            </script>
            """
            st.components.v1.html(js, height=0)
    
    # Teacher Role Card
    with col2:
        st.markdown("""
        <div class='card teacher-card'>
            <h2 class='card-title'>Teacher Portal</h2>
            <p class='card-text'>
                Create assignments, review submissions, analyze student performance,
                and provide additional feedback.
            </p>
            <a class='role-btn teacher-btn' href='https://automated-evaluation-of-handwritten-answers-using-mistral-86qm.streamlit.app/' target='_blank'>
                Access Teacher Portal
            </a>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Open Teacher Portal", key="teacher_btn"):
            js = f"""
            <script>
                window.open('https://automated-evaluation-of-handwritten-answers-using-mistral-86qm.streamlit.app/', '_blank');
            </script>
            """
            st.components.v1.html(js, height=0)
    
    # Features section
    st.markdown("<h2 style='text-align: center; margin-top: 3rem;'>Key Features</h2>", 
                unsafe_allow_html=True)
    
    features_col1, features_col2, features_col3 = st.columns(3)
    
    with features_col1:
        st.markdown("""
        <div style='text-align: center; padding: 1rem;'>
            <h3>AI-Powered Evaluation</h3>
            <p>Advanced machine learning algorithms to evaluate handwritten answers accurately.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with features_col2:
        st.markdown("""
        <div style='text-align: center; padding: 1rem;'>
            <h3>Instant Feedback</h3>
            <p>Get immediate assessment and suggestions for improvement.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with features_col3:
        st.markdown("""
        <div style='text-align: center; padding: 1rem;'>
            <h3>Performance Analytics</h3>
            <p>Track progress and identify areas for improvement over time.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # How it works section
    st.markdown("<h2 style='text-align: center; margin-top: 2rem;'>How It Works</h2>", 
                unsafe_allow_html=True)
    
    steps_col1, steps_col2, steps_col3 = st.columns(3)
    
    with steps_col1:
        st.markdown("""
        <div style='text-align: center; padding: 1rem;'>
            <h3>Step 1</h3>
            <p>Upload a clear image of your handwritten answer.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with steps_col2:
        st.markdown("""
        <div style='text-align: center; padding: 1rem;'>
            <h3>Step 2</h3>
            <p>AI analyzes and evaluates the content against standard answers.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with steps_col3:
        st.markdown("""
        <div style='text-align: center; padding: 1rem;'>
            <h3>Step 3</h3>
            <p>Receive detailed feedback, scores and suggestions for improvement.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div class='footer'>
        <p>© 2025 Automated Handwritten Answers Evaluation System</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
