import streamlit as st
import pymongo
from pymongo import MongoClient
from streamlit_option_menu import option_menu
import os
from dotenv import load_dotenv
import bcrypt
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()
MONGO_URI = st.secrets["MONGO_URI"]  
# Connect to MongoDB
client = MongoClient(MONGO_URI)

# ---------------- Streamlit UI Configuration ----------------
st.set_page_config(page_title="Student Dashboard", page_icon="📚", layout="wide")

# Sidebar Navigation
with st.sidebar:
    selected = option_menu(
        menu_title="Student Dashboard",
        options=["🔑 Login/Signup", "🏠 Home", "📊 View Test Results", "📈 Performance Analytics"],
        icons=["key", "house", "card-checklist", "graph-up"],
        menu_icon="mortarboard",
        default_index=0,
    )

# -------------------- Login/Signup Section --------------------
if selected == "🔑 Login/Signup":
    try:
        client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        db = client["student"]  # Database for students
        collection = db["stud_metadata"]  # Collection for storing student credentials
        client.admin.command('ping')  # Check connection
        st.success("✅ Connected to MongoDB")
    except Exception as e:
        st.error(f"❌ MongoDB Connection Failed: {e}")
        st.stop()

    # ---- SESSION MANAGEMENT ----
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if "student_name" not in st.session_state:
        st.session_state["student_name"] = ""
    if "prn" not in st.session_state:
        st.session_state["prn"] = ""

    # ---- UI Design ----
    st.title("👨‍🎓 Student Login/Signup")
    st.write("Welcome! Please login or sign up below.")

    # ---- Tabs for Login & Signup ----
    tab1, tab2 = st.tabs(["🔑 Login", "🆕 Signup"])

    # ---- SIGNUP ----
    with tab2:
        st.subheader("Create a Student Account")
        student_name = st.text_input("Full Name", key="signup_name")
        prn = st.text_input("PRN Number", key="signup_prn")
        mothers_name = st.text_input("Mother's Name", key="signup_mother_name")
        password = st.text_input("Password", type="password", key="signup_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm")

        if st.button("Sign Up"):
            if not (student_name and prn and mothers_name and password and confirm_password):
                st.error("❌ All fields are required.")
            elif password != confirm_password:
                st.error("❌ Passwords do not match.")
            else:
                # Check if student already exists
                existing_student = collection.find_one({"prn": prn})
                if existing_student:
                    st.error("❌ PRN already exists. Please login.")
                else:
                    # Hash password
                    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
                    student_data = {
                        "student_name": student_name,
                        "prn": prn,
                        "mothers_name": mothers_name,
                        "password": hashed_password,
                        "created_at": datetime.now()
                    }
                    collection.insert_one(student_data)
                    st.success("✅ Signup successful! Please login.")

    # ---- LOGIN ----
    with tab1:
        st.subheader("Student Login")
        login_prn = st.text_input("PRN Number", key="login_prn")
        login_password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login"):
            student = collection.find_one({"prn": login_prn})
            if student and bcrypt.checkpw(login_password.encode(), student["password"].encode()):
                st.session_state["authenticated"] = True
                st.session_state["student_name"] = student["student_name"]
                st.session_state["prn"] = login_prn
                st.success(f"✅ Welcome, {student['student_name']}! Login successful.")
                
            else:
                st.error("❌ Invalid PRN or Password.")

    # ---- LOGOUT ----
    if st.session_state["authenticated"]:
        st.subheader(f"👋 Welcome, {st.session_state['student_name']}!")
        if st.button("Logout"):
            st.session_state["authenticated"] = False
            st.session_state["student_name"] = ""
            st.session_state["prn"] = ""
            st.success("✅ Logged out successfully.")

# -------------------- Home Section --------------------
elif selected == "🏠 Home":
    st.title("📚 Welcome to the Student Dashboard")
    
    # Check if student is logged in
    if not st.session_state.get("authenticated", False):
        st.warning("⚠️ Please login to access your dashboard.")
        st.stop()
    
    # Get student info from session
    student_name = st.session_state["student_name"]
    prn = st.session_state["prn"]
    
    # Connect to MongoDB
    students_db = client["student"]
    metadata_collection = students_db["stud_metadata"]
    scores_collection = students_db["student_scores"]
    
    # Fetch student data
    student_data = metadata_collection.find_one({"prn": prn})
    student_scores = list(scores_collection.find({"prn": prn}))
    
    # Dashboard Layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🧑‍🎓 Student Profile")
        st.markdown(f"""
        **Name:** {student_name}  
        **PRN:** {prn}  
        **Mother's Name:** {student_data.get('mothers_name', 'Not provided')}  
        """)
    
    with col2:
        # Calculate stats
        total_tests = len(student_scores)
        
        if total_tests > 0:
            latest_scores = sorted(student_scores, key=lambda x: x.get('timestamp', datetime.min), reverse=True)
            latest_test = latest_scores[0]
            latest_score = latest_test.get('total_marks', 0)
            latest_max = latest_test.get('max_marks', 1)
            latest_percentage = (latest_score / latest_max) * 100 if latest_max else 0
            
            avg_percentage = sum([(s.get('total_marks', 0) / s.get('max_marks', 1)) * 100 if s.get('max_marks', 0) > 0 else 0 
                                for s in student_scores]) / total_tests
            
            st.subheader("📊 Quick Stats")
            st.markdown(f"""
            **Tests Taken:** {total_tests}  
            **Latest Score:** {latest_score}/{latest_max} ({latest_percentage:.1f}%)  
            **Average Performance:** {avg_percentage:.1f}%
            """)
        else:
            st.info("No test results found. Check the 'View Test Results' section to look up your scores.")
    
    # Recent Tests Section
    st.subheader("📝 Recent Tests")
    
    if student_scores:
        # Create a DataFrame for recent tests
        recent_tests_data = []
        for score in sorted(student_scores, key=lambda x: x.get('timestamp', datetime.min), reverse=True)[:5]:
            recent_tests_data.append({
                "Test ID": score.get('test_id', 'Unknown'),
                "Date": score.get('timestamp', datetime.now()).strftime("%Y-%m-%d"),
                "Score": f"{score.get('total_marks', 0)}/{score.get('max_marks', 0)}",
                "Percentage": f"{(score.get('total_marks', 0) / score.get('max_marks', 1)) * 100:.1f}%" if score.get('max_marks', 0) > 0 else "N/A"
            })
        
        if recent_tests_data:
            recent_df = pd.DataFrame(recent_tests_data)
            st.dataframe(recent_df, use_container_width=True)
        else:
            st.info("No recent tests found.")
    else:
        st.info("You haven't taken any tests yet.")
    
    # Quick links
    st.subheader("🔗 Quick Links")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 View All Test Results", use_container_width=True):
            st.session_state["page_selection"] = "📊 View Test Results"
            st.rerun()
    with col2:
        if st.button("📈 View Performance Analytics", use_container_width=True):
            st.session_state["page_selection"] = "📈 Performance Analytics"
            st.rerun()

# -------------------- View Test Results Section --------------------
elif selected == "📊 View Test Results":
    st.title("📊 View Your Test Results")
    
    # Check if student is logged in
    if not st.session_state.get("authenticated", False):
        st.warning("⚠️ Please login to view your test results.")
        st.stop()
    
    # Get student info from session
    student_name = st.session_state.get("student_name", "")
    prn = st.session_state.get("prn", "")
    
    # UI for filtering tests
    st.subheader("Search for Test Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        subject_filter = st.text_input("Subject (optional)", key="subject_filter")
    
    with col2:
        test_id_filter = st.text_input("Test ID (optional)", key="test_id_filter")
    
    if st.button("Search"):
        # Direct connection to student database and student_scores collection
        student_db = client["student"]
        scores_collection = student_db["student_scores"]
        
        # Build query based on PRN and optional test_id
        query = {"prn": prn}
        if test_id_filter:
            query["test_id"] = test_id_filter
        
        # Execute the query
        results = list(scores_collection.find(query))
        
        if results:
            st.success(f"Found {len(results)} test results for PRN: {prn}")
            
            # Display results
            for result in results:
                test_id = result.get('test_id', 'Unknown')
                timestamp = result.get('timestamp', '')
                date_str = timestamp.strftime('%Y-%m-%d') if isinstance(timestamp, datetime) else 'No date'
                
                with st.expander(f"Test: {test_id} - {date_str}"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(f"**Test ID:** {test_id}")
                        st.markdown(f"**Student:** {result.get('student_name', 'Unknown')}")
                    with col2:
                        st.markdown(f"**PRN:** {result.get('prn', 'Unknown')}")
                        st.markdown(f"**Date:** {date_str}")
                    with col3:
                        # Calculate total score from results array if available
                        if "results" in result:
                            total_score = sum(q.get('score', 0) for q in result.get('results', []))
                            max_score = len(result.get('results', [])) * 5  # Assuming max score per question is 5
                            percentage = (total_score / max_score * 100) if max_score > 0 else 0
                            st.markdown(f"**Total Score:** {total_score}/{max_score}")
                            st.markdown(f"**Percentage:** {percentage:.1f}%")
                        else:
                            # Use total_marks if available
                            total_marks = result.get('total_marks', 0)
                            max_marks = result.get('max_marks', 0)
                            percentage = (total_marks / max_marks * 100) if max_marks > 0 else 0
                            st.markdown(f"**Total Score:** {total_marks}/{max_marks}")
                            st.markdown(f"**Percentage:** {percentage:.1f}%")
                    
                    # Display question-wise results if available
                    if "results" in result and result["results"]:
                        st.subheader("Question-wise Feedback")
                        for question_result in result["results"]:
                            question_num = question_result.get('question_number', 'Unknown')
                            question_text = question_result.get('question', 'No question text')
                            
                            st.markdown(f"""
                            <div style="background-color:#f0f2f6;padding:10px;border-radius:5px;margin-bottom:10px">
                                <strong>Question {question_num}:</strong> {question_text}
                            </div>
                            """, unsafe_allow_html=True)
                            
                            score = question_result.get('score', 0)
                            evaluation = question_result.get('evaluation', 'No feedback')
                            
                            st.markdown(f"""
                            <div style="color:{"green" if score >= 4 else "orange" if score >= 2 else "red"};font-weight:bold;margin-bottom:10px">
                                Score: {score}/5
                            </div>
                            """, unsafe_allow_html=True)
                            
                            st.markdown(f"""
                            <div style="background-color:#fafafa;padding:10px;border-radius:5px;margin-bottom:20px">
                                <strong>Feedback:</strong> {evaluation}
                            </div>
                            """, unsafe_allow_html=True)
        else:
            st.warning(f"No test results found for PRN: {prn} {f'with Test ID: {test_id_filter}' if test_id_filter else ''}")

# -------------------- Performance Analytics Section --------------------
elif selected == "📈 Performance Analytics":
    st.title("📈 Performance Analytics")
    
    # Check if student is logged in
    if not st.session_state.get("authenticated", False):
        st.warning("⚠️ Please login to view your analytics.")
        st.stop()
    
    # Get student info from session
    prn = st.session_state["prn"]
    
    # Connect to MongoDB
    students_db = client["student"]
    scores_collection = students_db["student_scores"]
    
    # Fetch all test results for this student
    all_results = list(scores_collection.find({"prn": prn}))
    
    if not all_results:
        st.info("No test data available for analysis. Take some tests to see analytics.")
        st.stop()
    
    # Extract subject information for all tests
    test_subjects = {}
    
    # First, get all test IDs
    test_ids = [result.get("test_id") for result in all_results]
    
    # Then, search all databases for subject information
    for db_name in client.list_database_names():
        # Skip system databases
        if db_name.startswith('admin') or db_name.startswith('local') or db_name.startswith('config'):
            continue
        
        current_db = client[db_name]
        
        # Check each test_id
        for test_id in test_ids:
            if test_id in current_db.list_collection_names():
                test_collection = current_db[test_id]
                test_info = test_collection.find_one({})
                
                if test_info and "subject" in test_info:
                    test_subjects[test_id] = test_info["subject"]
    
    # If we have subject information, allow filtering by subject
    if test_subjects:
        unique_subjects = list(set(test_subjects.values()))
        selected_subject = st.selectbox("Select Subject for Analysis", ["All Subjects"] + unique_subjects)
    else:
        selected_subject = "All Subjects"
    
    # Filter results by subject if needed
    if selected_subject != "All Subjects":
        filtered_test_ids = [test_id for test_id, subject in test_subjects.items() if subject == selected_subject]
        filtered_results = [result for result in all_results if result.get("test_id") in filtered_test_ids]
    else:
        filtered_results = all_results
    
    if not filtered_results:
        st.warning(f"No test data available for subject: {selected_subject}")
        st.stop()
    
    # Prepare data for visualization
    analysis_data = []
    
    for result in filtered_results:
        test_id = result.get("test_id", "Unknown")
        timestamp = result.get("timestamp", datetime.now())
        total_marks = result.get("total_marks", 0)
        max_marks = result.get("max_marks", 1)
        percentage = (total_marks / max_marks) * 100 if max_marks > 0 else 0
        subject = test_subjects.get(test_id, "Unknown Subject")
        
        analysis_data.append({
            "Test ID": test_id,
            "Date": timestamp,
            "Total Marks": total_marks,
            "Max Marks": max_marks,
            "Percentage": percentage,
            "Subject": subject
        })
    
    # Convert to DataFrame for easier plotting
    df = pd.DataFrame(analysis_data)
    df = df.sort_values("Date")
    
    # ---- VISUALIZATIONS ----
    
    # 1. Performance Timeline
    st.subheader("📊 Performance Timeline")
    
    fig = px.line(df, x="Date", y="Percentage", 
                 title="Performance Over Time",
                 labels={"Percentage": "Score (%)", "Date": "Test Date"},
                 markers=True)
    
    fig.update_layout(
        xaxis_title="Test Date",
        yaxis_title="Score (%)",
        yaxis=dict(range=[0, 105]),
        hovermode="x unified"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Create subject_df for analysis - FIX: moved this here so it's created before being used
    # Used for both subject-wise performance and personalized insights
    subject_performance = {}
    for _, row in df.iterrows():
        subject = row["Subject"]
        if subject not in subject_performance:
            subject_performance[subject] = {"scores": [], "count": 0}
        subject_performance[subject]["scores"].append(row["Percentage"])
        subject_performance[subject]["count"] += 1
    
    # Create subject_df here with proper structure
    subject_data = []
    for subject, data in subject_performance.items():
        subject_data.append({
            "Subject": subject,
            "Average_Score": sum(data["scores"]) / len(data["scores"]) if data["scores"] else 0,
            "Tests_Taken": data["count"]
        })
    
    subject_df = pd.DataFrame(subject_data)
    
    # 2. Subject-wise Performance (if we have multiple subjects)
    if len(test_subjects) > 1 and selected_subject == "All Subjects":
        st.subheader("📚 Subject-wise Performance")
        
        fig1, fig2 = st.columns(2)
        
        with fig1:
            # Bar chart for average scores
            fig = px.bar(subject_df, x="Subject", y="Average_Score",
                        labels={"Average_Score": "Average Score (%)", "Subject": "Subject"},
                        title="Average Score by Subject")
            
            fig.update_layout(yaxis=dict(range=[0, 105]))
            st.plotly_chart(fig, use_container_width=True)
        
        with fig2:
            # Radar chart for subject strength analysis
            if not subject_df.empty:  # Make sure we have data
                fig = go.Figure()
                
                fig.add_trace(go.Scatterpolar(
                    r=subject_df["Average_Score"].tolist(),
                    theta=subject_df["Subject"].tolist(),
                    fill='toself',
                    name='Your Score'
                ))
                
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 100]
                        )
                    ),
                    title="Subject Strength Analysis"
                )
                
                st.plotly_chart(fig, use_container_width=True)
    
    # 3. Question-wise Analysis for recent tests
    st.subheader("🔍 Question-wise Performance")
    
    # Select a specific test for question analysis
    test_options = [(idx, f"{result.get('test_id')} - {result.get('timestamp').strftime('%Y-%m-%d')}") 
                   for idx, result in enumerate(filtered_results) 
                   if isinstance(result.get('timestamp'), datetime)]
    
    if test_options:
        selected_test_idx, _ = list(zip(*test_options))
        selected_test_label = [label for _, label in test_options]
        selected_test = st.selectbox("Select Test for Question Analysis", selected_test_label)
        
        # Get selected test index
        selected_idx = selected_test_idx[selected_test_label.index(selected_test)]
        test_result = filtered_results[selected_idx]
        
        if "results" in test_result and test_result["results"]:
            # Extract question data
            question_data = []
            
            for question in test_result["results"]:
                question_data.append({
                    "Question": f"Q{question.get('question_number', '?')}",
                    "Score": question.get('score', 0),
                    "Max Score": 5  # Assuming max score is 5 per question
                })
            
            question_df = pd.DataFrame(question_data)
            
            # Create bar chart for question scores
            fig = px.bar(question_df, x="Question", y="Score",
                        labels={"Score": "Score", "Question": "Question Number"},
                        title=f"Scores by Question - {selected_test}",
                        range_y=[0, 5.5])
            
            fig.add_hline(y=5, line_dash="dash", line_color="green", annotation_text="Max Score")
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No question-wise data available for this test.")
    else:
        st.info("No tests available for question-wise analysis.")
    
    # 4. Performance Trends and Improvement Analysis
    if len(filtered_results) >= 2:
        st.subheader("📈 Performance Trends")
        
        # Calculate moving average for trend line
        df['MA_3'] = df['Percentage'].rolling(window=min(3, len(df))).mean()
        
        # Performance over last few tests
        fig = px.line(df, x="Date", y=["Percentage", "MA_3"],
                     title="Performance Trend Analysis",
                     labels={"value": "Score (%)", "Date": "Test Date", "variable": "Metric"},
                     color_discrete_map={"Percentage": "royalblue", "MA_3": "firebrick"})
        
        fig.update_layout(
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            yaxis=dict(range=[0, 105])
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Calculate improvement metrics
        first_test = df.iloc[0]["Percentage"]
        last_test = df.iloc[-1]["Percentage"]
        improvement = last_test - first_test
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("First Test Score", f"{first_test:.1f}%")
        
        with col2:
            st.metric("Latest Test Score", f"{last_test:.1f}%")
        
        with col3:
            st.metric("Overall Improvement", f"{improvement:.1f}%", delta=f"{improvement:.1f}%")
    
    # 5. Performance Distribution
    st.subheader("📊 Score Distribution")
    
    # Create histogram of scores
    fig = px.histogram(df, x="Percentage", 
                     nbins=10, 
                     title="Distribution of Test Scores",
                     labels={"Percentage": "Score (%)", "count": "Number of Tests"})
    
    fig.update_layout(
        xaxis=dict(range=[0, 105]),
        bargap=0.2
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 6. Custom Insights Based on Data
    st.subheader("🔍 Personalized Insights")
    
    # Calculate some analytics for insights
    avg_score = df["Percentage"].mean()
    recent_avg = df.iloc[-min(3, len(df)):]["Percentage"].mean()
    improvement_rate = recent_avg - df.iloc[:min(3, len(df))]["Percentage"].mean()
    
    # Only use subject_df if it exists and has data
    strongest_subject = None
    if not subject_df.empty and len(subject_df) > 1:
        strongest_subject = subject_df.iloc[subject_df["Average_Score"].argmax()]["Subject"]
    
    # Display insights
    insights_col1, insights_col2 = st.columns(2)
    
    with insights_col1:
        st.info(f"📈 Your average score across all tests is {avg_score:.1f}%")
        
        if improvement_rate > 0:
            st.success(f"⬆️ Your recent performance shows an improvement of {improvement_rate:.1f}% compared to your earlier tests!")
        elif improvement_rate < 0:
            st.warning(f"⬇️ Your recent performance shows a decline of {abs(improvement_rate):.1f}% compared to your earlier tests.")
        else:
            st.info("➡️ Your performance has been consistent across your tests.")
    
    with insights_col2:
        if strongest_subject and len(subject_df) > 1:
            strongest_score = subject_df.iloc[subject_df["Average_Score"].argmax()]["Average_Score"]
            st.success(f"💪 Your strongest subject is {strongest_subject} with an average score of {strongest_score:.1f}%")
            
            # Weakest subject
            weakest_subject = subject_df.iloc[subject_df["Average_Score"].argmin()]["Subject"]
            weakest_score = subject_df.iloc[subject_df["Average_Score"].argmin()]["Average_Score"]
            
            if weakest_score < 60:
                st.warning(f"📚 You might want to focus more on {weakest_subject} where your average score is {weakest_score:.1f}%")
        
        # Check for perfect scores
        perfect_tests = df[df["Percentage"] >= 95]
        if not perfect_tests.empty:
            st.success(f"🌟 Excellent work! You scored above 95% in {len(perfect_tests)} test(s)!")
