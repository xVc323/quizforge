import streamlit as st
import pandas as pd
from docx import Document
import PyPDF2
import google.generativeai as genai
import time
import re
import json

# Configuration
st.set_page_config(
    page_title="📝 Elegant Quiz Generator",
    page_icon="📝",
    layout="centered",
    initial_sidebar_state="auto"
)

# Constants
SUPPORTED_FILE_TYPES = [
    "txt", "c", "cpp", "py", "java", "php", "sql", "html",
    "doc", "docx", "pdf", "rtf", "dot", "dotx", "hwp", "hwpx",
    "csv", "tsv", "xls", "xlsx"
]

QUIZ_LENGTHS = [5, 10, 15, 20, 30]
QUESTIONS_PER_CALL = 5
CALLS_PER_MINUTE = 15
CALL_INTERVAL = 60 / CALLS_PER_MINUTE

DIFFICULTY_LEVELS = {
    "Easy": "Make questions straightforward and focus on basic concepts. Use simple language.",
    "Normal": "Balance between basic and advanced concepts. Use moderate complexity in questions.",
    "Hard": "Focus on advanced concepts and include some tricky options. Use complex scenarios.",
    "Insane": "Create extremely challenging questions with subtle differences in options. Include edge cases and complex combinations of concepts."
}

# Load custom CSS
def load_css():
    css = """
    body {
        background-color: #f0f2f6;
    }
    .stButton>button {
        color: white;
        background-color: #4CAF50;
    }
    .difficulty-info {
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    """
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Initialize session state
def initialize_session_state():
    if 'quiz_data' not in st.session_state:
        st.session_state.quiz_data = None
    if 'user_answers' not in st.session_state:
        st.session_state.user_answers = {}
    if 'quiz_submitted' not in st.session_state:
        st.session_state.quiz_submitted = False
    if 'quiz_generated' not in st.session_state:
        st.session_state.quiz_generated = False
    if 'content_processed' not in st.session_state:
        st.session_state.content_processed = None
    if 'question_explanations' not in st.session_state:
        st.session_state.question_explanations = {}
    if 'model' not in st.session_state:
        st.session_state.model = None
    if 'last_difficulty' not in st.session_state:
        st.session_state.last_difficulty = 'Normal'
    if 'last_quiz_length' not in st.session_state:
        st.session_state.last_quiz_length = 5

# Get API Key
def get_api_key():
   api_key = st.text_input(
       "🔑 Enter your Google Gemini API Key",
       type="password",
       help="Required to generate quizzes. Your API key is processed securely and never stored."
   )
   
   with st.expander("📋 How to Get Your API Key"):
       st.markdown("""
       ### Quick Setup Guide:
       1. Visit [Google AI Studio](https://aistudio.google.com/apikey)
       2. Sign in with your Google Account (any Google account works, even new ones)
       3. Click "[Get API Key](https://aistudio.google.com/apikey)" button at the top left
       4. Create a new API key
       5. Paste the key above into the input field
       
       ### About AI Studio
       This app uses the Google AI Studio API (Gemini Flash), which is completely free for personal use. The free tier includes:
       - 15 API calls per minute
       - No credit card required
       - Works with any Google account, including new ones
       - Fast responses optimized for quiz generation
       
       ### Security Note
       Your API key is processed securely in memory and is never stored or logged. Only you have access to your key - it's not saved or accessible by anyone else after you close this page.
       
       For more information about terms of service and usage, visit the [Gemini API Terms of Service](https://ai.google.dev/gemini-api/terms).
       
       **Keep your API key secure and never share it publicly!**
       """)
   
   return api_key

# File Uploader
def file_uploader():
    uploaded_files = st.file_uploader(
        "📂 Upload Files",
        type=SUPPORTED_FILE_TYPES,
        accept_multiple_files=True
    )
    if uploaded_files:
        if len(uploaded_files) > 10:
            st.error("🚫 You can upload up to 10 files at a time.")
            return None
        total_size = sum([file.size for file in uploaded_files])
        if total_size > 100 * 1024 * 1024:
            st.error("🚫 Total upload size exceeds 100 MB.")
            return None
        return uploaded_files
    return None

# Extract Text from Files
def extract_text(file):
    try:
        if file.type == "text/plain":
            return file.read().decode("utf-8")
        elif file.type in ["application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
            doc = Document(file)
            return "\n".join([para.text for para in doc.paragraphs])
        elif file.type == "application/pdf":
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
            return text
        elif file.type in ["application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]:
            df = pd.read_excel(file)
            return df.to_csv(index=False)
        elif file.type == "text/csv":
            df = pd.read_csv(file)
            return df.to_csv(index=False)
        elif file.type == "text/tab-separated-values":
            df = pd.read_csv(file, sep='\t')
            return df.to_csv(index=False)
        else:
            st.warning(f"⚠️ Unsupported file type: {file.type}")
            return ""
    except Exception as e:
        st.error(f"❌ Error processing {file.name}: {e}")
        return ""

def process_files(uploaded_files):
    content = ""
    for file in uploaded_files:
        content += f"\n\n--- Content from {file.name} ---\n\n"
        content += extract_text(file)
    return content

def generate_quiz_chunk(content, model, difficulty, chunk_index=0):
    # Calculate the actual question numbers for this chunk
    questions_in_chunk = QUESTIONS_PER_CALL
    
    prompt = f"""
    Create a multiple-choice quiz based on the following content. Generate exactly {questions_in_chunk} questions.
    Difficulty level: {difficulty}
    {DIFFICULTY_LEVELS[difficulty]}
    
    Return ONLY a JSON object with this structure:
    {{
        "title": "Quiz on [Topic]",
        "instructions": "Read each question carefully and select the best answer.",
        "questions": [
            {{
                "number": 1,
                "question": "Question text here",
                "options": {{
                    "A": "First option",
                    "B": "Second option",
                    "C": "Third option",
                    "D": "Fourth option"
                }},
                "correct": "A",
                "explanation": "Detailed explanation of why this is the correct answer and why others are incorrect"
            }}
        ]
    }}
    Content to base the quiz on:
    """ + content

    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Clean up the response
        if response_text.startswith("```json"):
            response_text = response_text[7:-3]
        elif response_text.startswith("```"):
            response_text = response_text[3:-3]
        
        quiz_data = json.loads(response_text)
        
        # Adjust question numbers based on chunk index
        for i, question in enumerate(quiz_data["questions"]):
            question["number"] = i + 1 + (chunk_index * QUESTIONS_PER_CALL)
        
        return quiz_data
    except Exception as e:
        st.error(f"Failed to generate quiz chunk: {str(e)}")
        return None

def combine_quiz_chunks(chunks):
    if not chunks:
        return None
    
    combined_quiz = chunks[0].copy()  # Create a deep copy of the first chunk
    combined_quiz["questions"] = []
    
    question_number = 1  # Initialize question number
    for chunk in chunks:
        for question in chunk["questions"]:
            question["number"] = question_number  # Reset the question number
            combined_quiz["questions"].append(question)
            question_number += 1
    
    return combined_quiz

def generate_quiz(content, model, difficulty="Normal", num_questions=5):
    chunks = []
    num_chunks = (num_questions + QUESTIONS_PER_CALL - 1) // QUESTIONS_PER_CALL
    
    with st.spinner(f"🔄 Generating {num_questions} questions..."):
        for i in range(num_chunks):
            chunk = generate_quiz_chunk(content, model, difficulty, i)
            
            if chunk:
                chunks.append(chunk)
                if i < num_chunks - 1:  # Don't sleep after the last chunk
                    time.sleep(CALL_INTERVAL)  # Rate limiting
            else:
                st.error(f"Failed to generate chunk {i+1}")
                return None
    
    combined_quiz = combine_quiz_chunks(chunks)
    if combined_quiz:
        # Ensure we only keep the requested number of questions
        combined_quiz["questions"] = combined_quiz["questions"][:num_questions]
        st.session_state.quiz_data = combined_quiz
        st.session_state.quiz_generated = True
    return combined_quiz

def display_results():
    quiz = st.session_state.quiz_data
    score = 0
    total_questions = len(quiz["questions"])
    
    st.subheader("📊 Quiz Results")
    
    for question in quiz["questions"]:
        q_num = question["number"]
        user_answer = st.session_state.user_answers.get(q_num)
        correct_answer = question["correct"]
        
        with st.expander(f"Question {q_num} Results"):
            st.write(f"**{question['question']}**")
            st.write("\nOptions:")
            
            for key, value in question["options"].items():
                # Only show user answer indication if they actually provided an answer
                if user_answer and key == correct_answer and key == user_answer:
                    st.markdown(f"✅ **{key}. {value}** (Your correct answer)")
                    score += 1
                elif user_answer and key == user_answer:
                    st.markdown(f"❌ **{key}. {value}** (Your answer)")
                elif key == correct_answer:
                    st.markdown(f"✅ **{key}. {value}** (Correct answer)")
                else:
                    st.write(f"{key}. {value}")
            
            # Display explanation
            st.write("\n**Explanation:**")
            st.write(question.get("explanation", "No explanation available for this question."))
    
    # Only calculate score for answered questions
    answered_questions = sum(1 for ans in st.session_state.user_answers.values() if ans is not None)
    if answered_questions > 0:
        final_score = (score / total_questions) * 100
        st.success(f"🎯 Your Score: {final_score:.1f}%")
    else:
        st.warning("No questions were answered.")

def display_quiz():
    if not st.session_state.quiz_data:
        return
    
    quiz = st.session_state.quiz_data
    st.header(f"📝 {quiz['title']}")
    st.markdown(quiz['instructions'])
    
    # Create form for quiz
    with st.form(key='quiz_form'):
        for question in quiz["questions"]:
            q_num = question["number"]
            q_text = question["question"]
            options = question["options"]
            
            st.subheader(f"Question {q_num}")
            st.write(q_text)
            
            # Radio buttons for options with default=None to prevent auto-selection
            option_key = f"q_{q_num}"
            selected = st.radio(
                f"Select answer for Question {q_num}:",
                options=[f"{k}. {v}" for k, v in options.items()],
                key=option_key,
                label_visibility="collapsed",
                index=None  # This prevents auto-selection of the first option
            )
            
            if selected:
                st.session_state.user_answers[q_num] = selected.split(".")[0]

        # Submit button inside form
        submit_button = st.form_submit_button("Submit Quiz")
        if submit_button:
            if len(st.session_state.user_answers) < len(quiz["questions"]):
                st.warning("Please answer all questions before submitting.")
            else:
                st.session_state.quiz_submitted = True

    # Display results if quiz is submitted
    if st.session_state.quiz_submitted:
        display_results()

def main():
    load_css()
    initialize_session_state()
    
    st.title("📝 Elegant Quiz Generator App")
    
    api_key = get_api_key()
    
    if not api_key:
        st.warning("⚠️ **Important:** Please set up your Google Gemini API Key above to use the quiz generator.")
        return
        
    st.write("""
        Upload your documents, and we'll generate a multiple-choice quiz for you. 
        After completing the quiz, you'll receive a score and detailed feedback.
    """)
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        st.session_state.model = model
        
        # Always show file uploader
        col1, col2 = st.columns([2, 1])
        with col1:
            uploaded_files = file_uploader()
        
        if uploaded_files:
            with st.spinner("Processing files..."):
                content = process_files(uploaded_files)
                st.session_state.content_processed = content
            
            if content:
                st.success("✅ Files processed successfully!")
        
        # Show quiz configuration if we have processed content
        if st.session_state.content_processed and not st.session_state.quiz_generated:
            col1, col2 = st.columns(2)
            
            with col1:
                difficulty = st.selectbox(
                    "Select Quiz Difficulty",
                    options=list(DIFFICULTY_LEVELS.keys()),
                    index=1,  # Default to "Normal"
                )
                st.session_state.last_difficulty = difficulty
            
            with col2:
                num_questions = st.selectbox(
                    "Number of Questions",
                    options=QUIZ_LENGTHS,
                    index=0,  # Default to 5 questions
                )
                st.session_state.last_quiz_length = num_questions
            
            with st.expander("ℹ️ Difficulty Levels Explained"):
                for level, desc in DIFFICULTY_LEVELS.items():
                    st.write(f"**{level}**: {desc}")
            
            if st.button("Generate Quiz"):
                with st.spinner("🔄 Generating quiz..."):
                    generate_quiz(st.session_state.content_processed, model, difficulty, num_questions)
        
        # Display quiz if it's generated
        if st.session_state.quiz_generated:
            display_quiz()
            
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()