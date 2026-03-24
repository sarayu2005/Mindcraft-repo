import streamlit as st
import pandas as pd
import numpy as np
import os
import time
import webbrowser # <-- Added for system-level URL opening


# Scikit-learn & Sentence Transformers dependencies
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sentence_transformers import SentenceTransformer, util

# Gemini API dependency
from google import genai
from google.genai.errors import APIError

# --- CONFIGURATION AND SETUP ---
LLM_MODEL_NAME = "gemini-2.5-flash"
EMBEDDING_MODEL_NAME = 'sentence-transformers/all-MiniLM-L6-v2'
SKILL_MAP = {0: "Beginner", 1: "Intermediate", 2: "Advanced"}
MODEL_SAVE_PATH = 'interviewer_model.pkl'

# Define the absolute local path for the homepage file
# NOTE: This path is hardcoded based on your request. If you move the file, you must update this path.
HOMEPAGE_FILE_PATH = "file:///Users/sarayu/Desktop/MindcraftLogin/public/home_pg.html"


# Set the device to 'cpu' as requested for macOS compatibility
@st.cache_resource
def load_models():
    """Loads the Sentence Transformer model and initializes the Gemini client."""
    try:
        # Sentence Transformer runs on CPU by default if no GPU is found/specified
        embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME, device='cpu')
        
        # The client automatically picks up the API key from the GEMINI_API_KEY environment variable.
        gemini_client = genai.Client()

        return embedding_model, gemini_client
    except Exception as e:
        st.error(f"Error loading models or connecting to Gemini: {e}")
        st.stop()


# --- DATASET AND TRAINING ---
def get_training_data():
    """Defines a small, synthetic dataset for model training."""
    data = {
        'question': [
            "What is the difference between a list and a tuple in Python?",
            "Explain the concept of Python decorators.",
            "How does the Global Interpreter Lock (GIL) affect multi-threading in Python?",
            "Write a simple function to calculate the factorial of a number.",
            "Describe a closure in Python.",
            "Implement a context manager using the @contextmanager decorator."
        ],
        'expected_answer': [
            "Lists are mutable and use square brackets ([]); tuples are immutable and use parentheses (()). Lists are generally used for homogeneous data, while tuples are for heterogeneous, fixed collections.",
            "Decorators are design patterns that allow behavior to be added to a function or class without modifying its structure. They are typically implemented using functions that take a function and return a wrapper function.",
            "The GIL is a mutex that protects access to Python objects, preventing multiple native threads from executing Python bytecodes at once. While it doesn't prevent I/O concurrency, it limits true parallelism for CPU-bound tasks.",
            "A factorial function, using recursion or iteration. The iterative approach is simpler and less prone to stack overflow for large numbers.",
            "A closure is an inner function that remembers and accesses variables from its enclosing function, even after the outer function has finished execution and returned.",
            "A context manager defines the setup and teardown logic for a block of code, ensuring resources are properly managed (e.g., file handling). The `@contextmanager` decorator simplifies this by wrapping a generator function."
        ],
        'skill_level': [0, 1, 2, 0, 1, 2] # 0=Beginner, 1=Intermediate, 2=Advanced
    }
    return pd.DataFrame(data)

@st.cache_resource
def train_expertise_model(df, _model):
    """Trains a Logistic Regression model on the expected answer embeddings."""
    st.write("Training expertise predictor...")

    # 1. Embed the expected answers
    expected_embeddings = _model.encode(df['expected_answer'].tolist(), convert_to_tensor=True)
    
    # 2. Use a dummy score (1.0 for perfect match) for training
    X_train = np.array([1.0] * len(df)).reshape(-1, 1) # Feature is cosine similarity (max 1.0)
    y_train = df['skill_level'].values

    # Train a simple Logistic Regression classifier
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_train)
    
    classifier = LogisticRegression(random_state=42)
    classifier.fit(X_scaled, y_train)
    
    st.success("Expertise model trained!")
    return classifier, scaler, expected_embeddings


# --- EVALUATION FUNCTIONS ---
def get_similarity_score(user_answer, expected_embedding, model):
    """Calculates the cosine similarity between the user's answer and the expected answer."""
    user_embedding = model.encode(user_answer, convert_to_tensor=True)
    # Cosine similarity is a number between -1 (opposite) and 1 (identical)
    score = util.cos_sim(user_embedding, expected_embedding).item()
    return score

def get_predicted_level_from_score(score, classifier, scaler):
    """Predicts the skill level based on the similarity score."""
    # Scale the single score feature
    X_predict = scaler.transform(np.array([[score]]))
    
    # Predict the class (0, 1, or 2)
    predicted_class = classifier.predict(X_predict)[0]
    return SKILL_MAP[predicted_class]

# --- GEMINI API ADAPTIVE QUESTIONING ---
def generate_adaptive_question(client, current_level, chat_history):
    """Uses the Gemini API to generate the next adaptive question."""
    
    # Define a system instruction to set the model's persona and rules
    system_instruction = (
        "You are an expert technical interviewer specializing in Python. "
        "Your task is to conduct an adaptive interview. "
        "Based on the user's current estimated skill level ({current_level}) and past answers, "
        "generate the *next* single, relevant Python interview question. "
        "The question must be focused and specific to either Python language features, "
        "best practices, or core libraries. Do not include any greeting or explanation; "
        "just provide the question text."
    ).format(current_level=current_level)

    # Use the chat service for better context and adaptive flow
    chat = client.chats.create(
        model=LLM_MODEL_NAME, 
        config={'system_instruction': system_instruction}
    )
    
    # Pass the history to the chat instance
    full_prompt = (
        f"The user's current estimated skill level is '{current_level}'. "
        "Ask the next question. Ensure it is adaptive and relevant to their stated level."
    )

    try:
        response = chat.send_message(full_prompt)
        return response.text.strip()
    except APIError as e:
        st.error(f"Gemini API Error: {e}. Please check your API key and quota.")
        st.stop()
    except Exception as e:
        st.error(f"An unexpected error occurred during API call: {e}")
        st.stop()

# --- STREAMLIT APP LOGIC ---

def open_homepage():
    """Opens the local HTML file using the Python webbrowser module."""
    webbrowser.open(HOMEPAGE_FILE_PATH, new=1, autoraise=True)
    st.info("The homepage should have opened in a new browser tab. You can now close this Streamlit tab.")


def main():
    """Main function to run the Streamlit app."""
    st.set_page_config(page_title="AI Python Skill Interviewer", layout="centered")

    st.title("🐍 AI Python Skill Interviewer")
    st.markdown("---")

    # 0. Check for API Key
    if not os.environ.get("GEMINI_API_KEY"):
        st.error(
            "🛑 **API Key Not Found!**\n\n"
            "Please set your Gemini API key as an environment variable named `GEMINI_API_KEY` "
            "before running this app. Instructions are in the section below."
        )
        st.stop()

    # 1. Initialize models and data (cached)
    embedding_model, gemini_client = load_models()
    training_data = get_training_data()
    classifier, scaler, expected_embeddings = train_expertise_model(training_data, embedding_model)

    # 2. Session State Initialization
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 0
        st.session_state.max_steps = 3 # Number of questions to ask
        st.session_state.history = []
        st.session_state.scores = []
        st.session_state.question_bank = training_data['question'].tolist()
        st.session_state.current_level = SKILL_MAP[0] # Start at Beginner

        # Get the first question
        st.session_state.current_question = generate_adaptive_question(
            gemini_client, 
            st.session_state.current_level, 
            st.session_state.history
        )


    # --- INTERVIEW DISPLAY AND PROGRESS ---
    
    st.subheader(f"Question {st.session_state.current_step + 1} of {st.session_state.max_steps}")
    st.info(f"Your Current Estimated Level: **{st.session_state.current_level}**")
    
    # Display the current question
    st.markdown(f"**Question:** *{st.session_state.current_question}*")
    
    user_answer = st.text_area("Your Answer:", height=200, key="answer_input")

    # --- SUBMISSION LOGIC ---
    if st.button("Submit Answer & Get Next Question", type="primary", disabled=(st.session_state.current_step >= st.session_state.max_steps)):
        if not user_answer:
            st.warning("Please provide an answer before submitting.")
            return

        # 1. Find the most relevant expected answer from the training data (for scoring)
        reference_index = 2 
        expected_ans_embedding = expected_embeddings[reference_index]
        
        # 2. Score the answer
        similarity_score = get_similarity_score(user_answer, expected_ans_embedding, embedding_model)
        
        # 3. Predict the next skill level based on the score
        next_predicted_level = get_predicted_level_from_score(similarity_score, classifier, scaler)
        
        # 4. Update session state
        st.session_state.history.append({
            'question': st.session_state.current_question,
            'user_answer': user_answer,
            'score': similarity_score,
            'predicted_level': next_predicted_level
        })
        st.session_state.scores.append(similarity_score)
        
        # 5. Advance step
        st.session_state.current_step += 1
        st.session_state.current_level = next_predicted_level # Update the level for the next question

        if st.session_state.current_step < st.session_state.max_steps:
            # Generate the next adaptive question
            with st.spinner(f"AI Interviewer thinking... generating Question {st.session_state.current_step + 1}"):
                st.session_state.current_question = generate_adaptive_question(
                    gemini_client, 
                    st.session_state.current_level, 
                    st.session_state.history
                )
            
            # Clear the text area for the next question
            st.rerun() # Rerun to display the new question and clear input
        else:
            st.success("Interview complete! Calculating final results...")
            st.rerun() # Rerun to display final results section


    # --- FINAL RESULTS DISPLAY ---
    if st.session_state.current_step >= st.session_state.max_steps:
        st.markdown("---")
        st.header("✅ Interview Complete!")
        
        # Calculate final level based on the last predicted level
        final_level = st.session_state.history[-1]['predicted_level']
        
        st.subheader(f"Final Predicted Expertise: **{final_level}**")
        
        # Determine average score for visualization (normalize to 1-5 scale for flair)
        avg_score = np.mean(st.session_state.scores)
        scaled_score = (avg_score + 1) * 2.5 # Scale from [-1, 1] to [0, 5]
        
        st.metric(label="Average Semantic Score (Closeness to Expert Answer)", 
                  value=f"{avg_score:.2f}", 
                  delta=f"{scaled_score:.1f} / 5.0 (Internal Scale)")

        st.subheader("Interview History")
        
        for i, item in enumerate(st.session_state.history):
            expander = st.expander(f"Question {i+1}: {item['question'][:50]}...", expanded=False)
            with expander:
                st.markdown(f"**Question:** {item['question']}")
                st.markdown(f"**Your Answer:** *{item['user_answer']}*")
                st.markdown(f"**Similarity Score:** `{item['score']:.4f}`")
                st.markdown(f"**Predicted Next Level:** **{item['predicted_level']}**")

        st.markdown("---")
        st.subheader("Next Steps")
        
        # --- NEW HOMEPAGE LINK (using Python's webbrowser) ---
        # This will open the file path directly in the OS, bypassing browser security blocks.
        if st.button("🏠 Go to Homepage", type="secondary"):
            open_homepage()
        # ---------------------------
        
        st.markdown(
            "You can rerun the interview by refreshing the page to test your skills on a new set of adaptive questions! "
            "Remember, the questions adapt based on the most recent prediction."
        )


if __name__ == "__main__":
    main()
