from flask import Flask, request, jsonify, render_template
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import google.generativeai as genai
from langchain.prompts import PromptTemplate
import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Load models and configurations
def load_together_ai():
    return {
        "name": "together_ai",
        "display_name": "Together AI (Mixtral-8x7B)",
        "api_key": os.getenv('TOGETHER_API_KEY')
    }

def load_gemini():
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("Warning: GEMINI_API_KEY not found in environment variables")
        return None
        
    try:
        genai.configure(api_key=api_key)
        generation_config = {
            "temperature": 0.7,
            "top_p": 0.85,
            "top_k": 30,
            "max_output_tokens": 1024,
        }
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=generation_config,
        )
        return {
            "name": "gemini",
            "display_name": "Gemini 1.5",
            "model": model
        }
    except Exception as e:
        print(f"Error loading Gemini model: {str(e)}")
        return None

# Initialize models
models = {
    "together_ai": load_together_ai()
}

# Only add Gemini if successfully loaded
gemini_model = load_gemini()
if (gemini_model):
    models["gemini"] = gemini_model

# Load vector store
vector_store = FAISS.load_local(
    "faiss_combined_index", 
    HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2"),
    allow_dangerous_deserialization=True
)

# Global variable to store conversation history
conversation_history = []

def generate_together_ai(question, contexts, model_config):
    API_KEY = model_config["api_key"]
    API_URL = "https://api.together.xyz/v1/completions"
    
    context_text = "\n".join([doc.page_content for doc in contexts])
    prompt = f"""Based on the following context, answer the question. Keep the answer concise and focused.
    
    Context: {context_text}
    
    Question: {question}
    
    Answer:"""
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
        "prompt": prompt,
        "max_tokens": 512,
        "temperature": 0.7,
        "top_p": 0.7,
        "top_k": 50,
        "repetition_penalty": 1.1,
        "stop": ["</s>", "[/INST]", "[INST]"]
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=data)
        # print(f"Status Code: {response.status_code}")
        # print(f"Response Headers: {response.headers}")
        # print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            return response.json()['choices'][0]['text'].strip()
        else:
            error_msg = f"API Error: {response.status_code} - {response.text}"
            print(error_msg)
            return error_msg
            
    except Exception as e:
        error_msg = f"Exception occurred: {str(e)}"
        print(error_msg)
        return error_msg

def generate_gemini(question, contexts, model_config):
    docs_content = "\n".join([f"{i+1}. {doc.page_content[:500]}" 
                             for i, doc in enumerate(contexts)])
    
    conversation = [
        {"role": "user", "parts": [question]},
        {"role": "user", "parts": [docs_content]}
    ]
    
    response = model_config["model"].generate_content(conversation)
    return response.text

generators = {
    "together_ai": generate_together_ai,
    "gemini": generate_gemini
}

@app.route('/')
def home():
    return render_template('index.html', models=models)

@app.route('/ask', methods=['POST'])
def ask():
    try:
        data = request.json
        question = data.get('question', '')
        model_name = data.get('model', 'together_ai')
        
        docs = vector_store.similarity_search(question, k=3)
        
        generator = generators.get(model_name)
        model_config = models.get(model_name)
        
        if not generator or not model_config:
            raise ValueError(f"Invalid model selection: {model_name}")
            
        answer = generator(question, docs, model_config)
        
        # Update conversation history
        conversation_history.append({
            'question': question,
            'answer': answer,
            'model_used': model_config["display_name"],
        })
        
        return jsonify({
            'status': 'success',
            'generated_answer': answer,
            'model_used': model_config["display_name"],
            'conversation_history': conversation_history  # Include conversation history in the response
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5501)