import streamlit as st
import pymongo
from pymongo import MongoClient
from streamlit_option_menu import option_menu
import os
from dotenv import load_dotenv
import bcrypt
import fitz  # PyMuPDF
import base64
import re
from dotenv import load_dotenv
from mistralai import Mistral
from mistralai.client import MistralClient
import time
import math


# Load environment variables
load_dotenv()
MONGO_URI = st.secrets["MONGO_URI"]  # Securely fetch MongoDB URI from .env

# Connect to MongoDB
client = MongoClient(MONGO_URI)


# ---------------- Streamlit UI Configuration ----------------
st.set_page_config(page_title="Teacher Dashboard", page_icon="📚", layout="wide")

# Sidebar Navigation
with st.sidebar:
    selected = option_menu(
        menu_title="Teacher Dashboard",
        options=["🔑Login/Signup","🏠 Home", "📝 Create New Test", "📊 Evaluate the Test"],
        icons=["house", "file-earmark-plus", "clipboard-check"],
        menu_icon="cast",
        default_index=1,
    )

# -------------------- Home Section --------------------
# -------------------- Home Section --------------------
# -------------------- Home Section --------------------
# -------------------- Home Section --------------------

 
if selected == "🔑Login/Signup":
    try:
        client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        db = client["teacher"]  # Database for teachers
        collection = db["teacher_metadata"]  # Collection for storing teacher credentials
        client.admin.command('ping')  # Check connection
        st.success("✅ Connected to MongoDB")
    except Exception as e:
        st.error(f"❌ MongoDB Connection Failed: {e}")
        st.stop()

    # ---- SESSION MANAGEMENT ----
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if "teacher_name" not in st.session_state:
        st.session_state["teacher_name"] = ""

    # ---- UI Design ----
    st.title("👩‍🏫 Teacher Login/Signup")
    st.write("Welcome! Please login or sign up below.")

    # ---- Tabs for Login & Signup ----
    tab1, tab2 = st.tabs(["🔑 Login", "🆕 Signup"])

    # ---- SIGNUP ----
    with tab2:
        st.subheader("Create a Teacher Account")
        teacher_name = st.text_input("Full Name", key="signup_name")
        teacher_id = st.text_input("Teacher ID", key="signup_id")
        password = st.text_input("Password", type="password", key="signup_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm")

        if st.button("Sign Up"):
            if not (teacher_name and teacher_id and password and confirm_password):
                st.error("❌ All fields are required.")
            elif password != confirm_password:
                st.error("❌ Passwords do not match.")
            else:
                # Check if teacher already exists
                existing_teacher = collection.find_one({"teacher_id": teacher_id})
                if existing_teacher:
                    st.error("❌ Teacher ID already exists. Please login.")
                else:
                    # Hash password
                    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
                    teacher_data = {
                        "teacher_name": teacher_name,
                        "teacher_id": teacher_id,
                        "password": hashed_password
                    }
                    collection.insert_one(teacher_data)
                    st.success("✅ Signup successful! Please login.")

    # ---- LOGIN ----
    with tab1:
        st.subheader("Teacher Login")
        login_id = st.text_input("Teacher ID", key="login_id")
        login_password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login"):
            teacher = collection.find_one({"teacher_id": login_id})
            if teacher and bcrypt.checkpw(login_password.encode(), teacher["password"].encode()):
                st.session_state["authenticated"] = True
                st.session_state["teacher_name"] = teacher["teacher_name"]
                st.success(f"✅ Welcome, {teacher['teacher_name']}! Login successful.")
                
            else:
                st.error("❌ Invalid Teacher ID or Password.")

    # ---- LOGOUT ----
    if st.session_state["authenticated"]:
        st.subheader(f"👋 Welcome, {st.session_state['teacher_name']}!")
        if st.button("Logout"):
            st.session_state["authenticated"] = False
            st.session_state["teacher_name"] = ""
            st.success("✅ Logged out successfully.")
            

elif selected == "🏠 Home":
    st.title("📚 Welcome to the Teacher Dashboard")
    st.write("Manage and evaluate tests efficiently ")

    # Ensure teacher is logged in
    if "teacher_name" not in st.session_state or not st.session_state["teacher_name"]:
        st.error("❌ Please log in to view your tests.")
        st.stop()

    teacher_name = st.session_state["teacher_name"].replace(" ", "_")  # Replace spaces with underscores
    teacher_db = client[teacher_name]  # Use sanitized name for MongoDB database

    quiz_ids = teacher_db.list_collection_names()
    subject_tests = {}  # Dictionary to store tests grouped by subject

    for quiz_id in quiz_ids:
        collection = teacher_db[quiz_id]
        test_data = collection.find_one({}, {"_id": 0})  # Fetch first document (ignore _id)

        if test_data:
            subject = test_data.get("subject")  # Extract subject
            if subject:
                if subject not in subject_tests:
                    subject_tests[subject] = []
                subject_tests[subject].append(quiz_id)  # Store quiz_id (collection name)

    # ---- Updated CSS (Two Columns, Centered Layout) ----
    st.markdown(
        """
        <style>
        .subject-container {
            display: grid;
            grid-template-columns: repeat(2, minmax(250px, 1fr)); /* Two columns */
            gap: 25px;  /* Increased gap between flexboxes */
            justify-content: center;
            max-width: 800px; /* Prevents full-screen width */
            margin: auto;
            margin-top: 20px;
        }
        .subject-card {
            background: #D6EAF8;  /* Light Blue */
            border-radius: 12px;
            padding: 20px;
            box-shadow: 3px 3px 10px rgba(0,0,0,0.1);
            color: #1A5276; /* Dark Blue Text */
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            text-align: center;
            max-width: 350px; /* Prevents oversized cards */
            margin: auto;
        }
        .subject-card:hover {
            transform: scale(1.05);
            box-shadow: 5px 5px 15px rgba(0,0,0,0.2);
        }
        .subject-title {
            font-size: 20px;
            font-weight: bold;
            text-transform: capitalize;
            margin-bottom: 10px;
        }
        .test-list {
            font-size: 16px;
            list-style-type: none;
            padding: 0;
        }
        .test-list li {
            background: rgba(255, 255, 255, 0.7);
            padding: 8px;
            border-radius: 6px;
            margin: 5px 0;
            transition: background 0.2s ease;
        }
        .test-list li:hover {
            background: rgba(255, 255, 255, 0.9);
            cursor: pointer;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # ---- Display Subject-wise Tests ----
    st.markdown('<div class="subject-container">', unsafe_allow_html=True)

    if subject_tests:
        for subject, test_list in subject_tests.items():
            test_list_html = "".join([f'<li>{quiz_id}</li>' for quiz_id in test_list])

            subject_card_html = f"""
            <div class="subject-card">
                <div class="subject-title">{subject}</div>
                <ul class="test-list">{test_list_html}</ul>
            </div>
            """

            st.markdown(subject_card_html, unsafe_allow_html=True)
    else:
        st.info("No tests found. Create a new test in the 'Create New Test' section.")

    st.markdown('</div>', unsafe_allow_html=True)

# -------------------- Create New Test Section --------------------
elif selected == "📝 Create New Test":
    st.title("📝 Create New Test")

    # Ensure teacher is logged in
    if "teacher_name" not in st.session_state or not st.session_state["teacher_name"]:
        st.error("❌ Please log in to create tests.")
        st.stop()

    teacher_name = st.session_state["teacher_name"].replace(" ", "_")  # Replace spaces with underscores
    teacher_db = client[teacher_name]  # Use sanitized name for MongoDB database

 

    with st.form("create_test_form"):
        quiz_id = st.text_input("Test ID (Quiz ID)").strip().replace(" ", "_")
        subject_name = st.text_input("Subject Name")

        questions = []
        keywords = []

        for i in range(1, 7):
            q = st.text_area(f"Question {i}")
            k = st.text_input(f"Keywords for Question {i} (comma-separated)")
            questions.append(q)
            keywords.append(k)

        submit_button = st.form_submit_button("Save Test")

        if submit_button:
            if quiz_id and subject_name and any(questions):
                collection = teacher_db[quiz_id]  # Create a collection named after the test ID

                # Insert test data
                test_data = {
                    "subject": subject_name,
                    "quiz_id": quiz_id,
                    "questions": [{"question": q, "keywords": k} for q, k in zip(questions, keywords)],
                    "created_by": st.session_state["teacher_name"]  # Store the teacher name
                }

                collection.insert_one(test_data)

                st.success(f"Test '{quiz_id}' created successfully in database '{st.session_state['teacher_name']}'!")
            else:
                st.error("Please fill in all fields.")


# -------------------- Evaluate the Test Section --------------------
elif selected == "📊 Evaluate the Test":
    st.title("📊 Evaluate the Test")
    
    # Ensure teacher is logged in
    if "teacher_name" not in st.session_state or not st.session_state["teacher_name"]:
        st.error("❌ Please log in to view your tests.")
        st.stop()

    # Teacher's database (replace spaces with underscores)
    teacher_name = st.session_state["teacher_name"].replace(" ", "_")
    teacher_db = client[teacher_name]

    # Initialize Mistral API with separate keys for different functions
    MISTRAL_API_KEY_IMAGE = st.secrets["MISTRAL_API_KEY_IMAGE"]
    MISTRAL_API_KEY_EVALUATION = st.secrets["MISTRAL_API_KEY_EVALUATION"]
    
    # Create separate Mistral clients for each functionality
    mistral_image_client = Mistral(api_key=MISTRAL_API_KEY_IMAGE)
    mistral_eval_client = Mistral(api_key=MISTRAL_API_KEY_EVALUATION)
    
    # Import required libraries
    from datetime import datetime
    
    # Connect to student scores database
    students_db = client["student"]
    scores_collection = students_db["student_scores"]

    # Function to fetch questions and keywords from MongoDB
    def fetch_questions(test_id):
        try:
            collection = teacher_db[test_id]
            document = collection.find_one({}, {"_id": 0, "questions": 1})
            return document["questions"] if document and "questions" in document else []
        except Exception as e:
            st.error(f"❌ Error accessing test '{test_id}': {e}")
            return []

    # Function to convert PDF to base64 images using PyMuPDF
    def pdf_to_base64_pymupdf(pdf_path):
        doc = fitz.open(pdf_path)
        return [base64.b64encode(doc[page_num].get_pixmap().tobytes("png")).decode("utf-8") for page_num in range(len(doc))]

    # Extract text from images using Mistral API for OCR
    def extract_text_from_images(base64_images):
        full_text = ""
        
        for idx, image in enumerate(base64_images):
            # Use Mistral directly with IMAGE key
            
            extract_messages = [{"role": "user", "content": [
                {"type": "text", "text": "Extract all the handwritten text from this image, preserving formatting and layout."},
                {"type": "image_url", "image_url": f"data:image/png;base64,{image}"}
            ]}]
            
            try:
                # Using Mistral's best model for image processing
                chat_response = mistral_image_client.chat.complete(model="pixtral-12b-2409", messages=extract_messages)
                extracted_text = chat_response.choices[0].message.content.strip()
                full_text += f"\nPage {idx+1}:\n{extracted_text}\n"
               
            except Exception as e:
                st.error(f"Error processing image {idx+1}: {str(e)}")
                full_text += f"\nPage {idx+1}: Error processing image\n"
                
            # Small delay to prevent overloading APIs
            time.sleep(0.5)
            
        return full_text

    # Improved function to match answers with the correct questions
    def match_answers_to_questions(full_text, questions_data):
        st.subheader("Matching answers to questions...")
        grouped_answers = {}
        
        # First ensure questions are sorted by question number
        questions_data = sorted(questions_data, key=lambda x: int(x.get("question_number", "0")) if x.get("question_number", "0").isdigit() else 0)
        
        for question in questions_data:
            q_num = question.get("question_number", "0")
            q_text = question.get("question", "No question found")
            
            # Try to find the question text in the full text
            pattern = re.escape(q_text[:20])
            match = re.search(pattern, full_text, re.IGNORECASE)
            
            if match:
                # Extract from match to next question or end
                start_pos = match.start()
                end_pos = len(full_text)
                
                # Find the next question start if it exists
                for next_q in questions_data:
                    if next_q.get("question_number", "0") > q_num:
                        next_pattern = re.escape(next_q.get("question", "")[:20])
                        next_match = re.search(next_pattern, full_text[start_pos:], re.IGNORECASE)
                        if next_match:
                            end_pos = start_pos + next_match.start()
                            break
                
                grouped_answers[q_num] = full_text[start_pos:end_pos].strip()
            else:
                grouped_answers[q_num] = "No Answer Found"
                
        return grouped_answers

    # Function to evaluate answers using Mistral
    def evaluate_answers(grouped_answers, questions_data, student_name, prn, test_id):
        results = []
        total_marks = 0
        max_marks = len(questions_data) * 5  # Each question is out of 5 marks
        
        # Sort questions by question number for consistent display
        questions_data = sorted(questions_data, key=lambda x: int(x.get("question_number", "0")) if x.get("question_number", "0").isdigit() else 0)
        
        for i, question in enumerate(questions_data):
            q_num = question.get("question_number", "0")
            q_text = question.get("question", "No question found")
            keywords = question.get("expected_keywords", [])
            student_answer = grouped_answers.get(q_num, "No Answer Found")
            
            score = 0 if student_answer == "No Answer Found" or student_answer.strip() == "" else None
            
            if score is None:
                prompt = f"""
                            As an expert educational assessor, evaluate the following student answer based on content accuracy, keyword usage, and clarity.  
                            Be EXTREMELY lenient and generous while giving marks to encourage student learning.  
                            Use a minimum score of 3 and maximum of 5, even for minimal or partially correct answers.
                            If the student has made any attempt at all, the minimum score should be 3.
                            If the answer has some relevance to the topic, give at least 4 marks.
                            Only give less than 3 marks if the answer is completely blank or entirely unrelated.
                            Give same marking for same answer content everytime.

                            QUESTION {q_num}: {q_text}

                            EXPECTED KEYWORDS: {', '.join(keywords)}

                            STUDENT ANSWER: {student_answer}

                            Evaluation Criteria:  
                            - Content Accuracy: Assess factual correctness and relevance with extreme leniency.  
                            - Keyword Usage: Consider even minimal keyword matches positively.  
                            - Clarity & Completeness: Reward any attempt at structure and coherence.  

                            STRICT RESPONSE FORMAT (NO MARKING SYSTEM DISCLOSURE):  
                            Score: [numeric score from 3-5 unless completely blank]  
                            Feedback: [Short, 4-5 lines of encouraging feedback highlighting strengths first, then gentle suggestions]  
                            """
                
                # Use Mistral API with EVALUATION key
                eval_prompt = [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
                
                try:
                    # Using Mistral's best model for evaluation
                    eval_response = mistral_eval_client.chat.complete(model="mistral-large-latest", messages=eval_prompt)
                    evaluation_result = eval_response.choices[0].message.content
                except Exception as e:
                    st.error(f"Error evaluating question {q_num}: {str(e)}")
                    evaluation_result = "Error in evaluation process. Score: 0"
                    score = 0
                
               
                # Extract score using regex
                if score is None:  # Only if we haven't set it due to error
                    score_match = re.search(r'Score:\s*(\d+\.?\d*)', evaluation_result)
                    if score_match:
                        raw_score = float(score_match.group(1))
                        # Ensure minimum of 3 unless blank
                        score = max(3, math.ceil(raw_score))
                    else:
                        score = 3  # Default to minimum score if parsing fails
                
            total_marks += score
            
            results.append({
                "question_number": q_num, 
                "question": q_text, 
                "evaluation": evaluation_result, 
                "score": score
            })
            
            # Display with improved formatting
            st.subheader(f"Question {i+1} (ID: {q_num})")
            st.markdown(f"{q_text}")
            st.markdown(f"Score: {score}/5")
            st.markdown(evaluation_result)
        
        # Save to MongoDB
        scores_collection.insert_one({
            "test_id": test_id,
            "student_name": student_name,
            "prn": prn,
            "results": results,
            "total_marks": total_marks,
            "max_marks": max_marks,
            "timestamp": datetime.now()
        })
        
        st.success(f"Evaluation results saved successfully! Total Marks: {total_marks}/{max_marks}")

    # Streamlit UI
    st.subheader("Handwritten Answer Evaluator")
    st.write("Enter details and upload a handwritten PDF containing answers for evaluation.")

    test_id = st.text_input("Enter Test ID:")
    student_name = st.text_input("Enter Student Name:")
    prn = st.text_input("Enter PRN Number:")
    uploaded_answers = st.file_uploader("Upload Answer Sheet (PDF)", type=["pdf"])

    

    if st.button("Process and Evaluate"):
        if not (test_id and student_name and prn and uploaded_answers):
            st.error("Please fill all fields and upload an answer sheet.")
        else:
            try:
                with st.spinner("Processing..."):
                    pdf_path = "uploaded_answers.pdf"
                    with open(pdf_path, "wb") as f:
                        f.write(uploaded_answers.read())
                    
                    questions_data = fetch_questions(test_id)
                    
                    if not questions_data:
                        st.error("No questions found in the database. Please check MongoDB entries.")
                    else:
                        st.info("Converting PDF to images...")
                        base64_images = pdf_to_base64_pymupdf(pdf_path)
                        
                        st.info("Extracting text from images...")
                        full_text = extract_text_from_images(base64_images)
                        
                        st.info("Matching answers to questions...")
                        grouped_answers = match_answers_to_questions(full_text, questions_data)
                        
                        st.info("Evaluating answers...")
                        evaluate_answers(grouped_answers, questions_data, student_name, prn, test_id)
            except Exception as e:
                st.error(f"An error occurred: {e}")
                st.error(traceback.format_exc())
