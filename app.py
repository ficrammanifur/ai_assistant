from flask import Flask, request, jsonify, render_template
import threading
import time
import json
from datetime import datetime
import os
import sys
from spellchecker import SpellChecker

# AI Model imports
try:
    from llama_cpp import Llama
    LLAMA_AVAILABLE = True
except ImportError:
    print("Warning: llama-cpp-python not installed. Install with: pip install llama-cpp-python")
    LLAMA_AVAILABLE = False

# OLED Display import
try:
    from oled_display import OLEDDisplay
    OLED_AVAILABLE = True
except ImportError:
    print("Warning: OLED display not available. Install dependencies or run without OLED.")
    OLED_AVAILABLE = False

app = Flask(__name__)

# Initialize spell checker with custom Indonesian word list
spell = SpellChecker()
try:
    with open('database/id_words.txt', 'r', encoding='utf-8') as f:
        custom_words = f.read().splitlines()
    spell.word_frequency.load_words(custom_words)
except FileNotFoundError:
    print("Warning: id_words.txt not found, using default spell checker.")

def fix_typo(text):
    """Correct typos in user input using pyspellchecker"""
    words = text.split()
    corrected = [spell.correction(w) if spell.correction(w) else w for w in words]
    return " ".join(corrected)

class AIAssistant:
    def __init__(self):
        self.model = None
        self.oled = None
        self.chat_history = []
        self.prompts_db = []
        
        # Load prompts from database
        self.load_prompts_db()
        
        # Initialize OLED if available
        if OLED_AVAILABLE:
            try:
                self.oled = OLEDDisplay()
                self.oled.show_expression("idle")
            except Exception as e:
                print(f"OLED initialization failed: {e}")
                self.oled = None
        
        # Initialize AI model
        self.load_ai_model()
    
    def load_prompts_db(self):
        """Load prompts from prompts.json"""
        try:
            with open('database/prompts.json', 'r', encoding='utf-8') as f:
                self.prompts_db = json.load(f)
        except Exception as e:
            print(f"Error loading prompts.json: {e}")
            self.prompts_db = []
    
    def load_ai_model(self):
        """Load TinyLlama model using llama.cpp"""
        if not LLAMA_AVAILABLE:
            print("llama-cpp-python not available. Using fallback responses.")
            return
        
        try:
            print("Loading TinyLlama model... This may take a moment.")
            
            # Path to the TinyLlama model (replace with LLaMA 3 path when available)
            model_path = "./models/tinyllama-1.1b-chat-v1.0.Q6_K.gguf"
            
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Model file not found at {model_path}")
            
            # Load the model with llama.cpp
            self.model = Llama(
                model_path=model_path,
                n_ctx=512,  # Context length
                n_threads=4,  # Use 4 CPU threads
                n_gpu_layers=0,  # CPU-only for Raspberry Pi
                chat_format="chatml"  # Use TinyLlama's default chat template
            )
            
            print("TinyLlama model loaded successfully!")
            
        except Exception as e:
            print(f"Error loading AI model: {e}")
            self.model = None
    
    def get_prompt_from_db(self, user_input):
        """Check if user input matches a prompt in prompts.json"""
        cleaned_input = fix_typo(user_input.lower())
        for entry in self.prompts_db:
            if cleaned_input in entry['prompt'].lower():
                return entry['response']
        return None
    
    def generate_response(self, user_input):
        """Generate AI response with spell correction and database fallback"""
        try:
            # Show thinking expression
            if self.oled:
                self.oled.show_expression("thinking")
            
            # Correct typos in user input
            cleaned_input = fix_typo(user_input)
            
            # Check prompts.json for a direct match
            db_response = self.get_prompt_from_db(cleaned_input)
            if db_response:
                ai_response = db_response
            elif self.model:
                # Build chat history in ChatML format
                messages = [
                    {
                        "role": "system",
                        "content": "You are a helpful and concise AI assistant running on a Raspberry Pi. Provide accurate, relevant answers in 1-3 sentences. If the input contains typos, respond to the corrected intent."
                    }
                ]
                # Add recent chat history (last 2 interactions)
                for entry in self.chat_history[-2:]:
                    messages.append({"role": "user", "content": entry['user']})
                    messages.append({"role": "assistant", "content": entry['assistant']})
                
                # Add corrected user input
                messages.append({"role": "user", "content": cleaned_input})
                
                # Generate response using ChatML format
                response = self.model.create_chat_completion(
                    messages=messages,
                    max_tokens=100,
                    temperature=0.6,
                    top_k=50,
                    top_p=0.9,
                    stop=["<|user|>", "<|assistant|>", "</s>"]
                )
                
                # Extract the assistant's response
                ai_response = response['choices'][0]['message']['content'].strip()
                
                # Clean up the response
                sentences = ai_response.split('. ')
                if len(sentences) > 3:
                    ai_response = '. '.join(sentences[:3]) + '.'
                if not ai_response.endswith('.'):
                    ai_response += '.'
                
                # Check if response is too similar to input or too short
                if cleaned_input.lower() in ai_response.lower() or len(ai_response) < 15:
                    ai_response = "Could you clarify or provide more details for a better response?"
            else:
                # Fallback responses
                fallback_responses = [
                    "I'm here to help! However, the AI model isn't loaded yet.",
                    "That's an interesting question! The AI model is currently unavailable.",
                    "I'd love to help with that, but I'm running in fallback mode right now.",
                    "Great question! Please make sure the AI model is properly installed."
                ]
                ai_response = fallback_responses[len(cleaned_input) % len(fallback_responses)]
            
            # Save to history.json
            self.save_to_history(user_input, ai_response)
            
            # Show speaking expression
            if self.oled:
                self.oled.show_expression("speaking")
                # Return to idle after a delay
                threading.Timer(3.0, lambda: self.oled.show_expression("idle")).start()
            
            return ai_response
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return "I apologize, but I encountered an error while processing your request."
    
    def add_to_history(self, user_input, ai_response):
        """Add conversation to in-memory history"""
        self.chat_history.append({
            "timestamp": datetime.now().isoformat(),
            "user": user_input,
            "assistant": ai_response
        })
        # Keep only last 50 conversations
        if len(self.chat_history) > 50:
            self.chat_history = self.chat_history[-50:]
    
    def save_to_history(self, user_input, ai_response):
        """Save conversation to history.json"""
        try:
            history_entry = {
                "id": len(self.chat_history) + 1,
                "prompt": user_input,
                "response": ai_response
            }
            with open('database/history.json', 'r+', encoding='utf-8') as f:
                history = json.load(f)
                history.append(history_entry)
                f.seek(0)
                json.dump(history, f, ensure_ascii=False, indent=2)
            self.add_to_history(user_input, ai_response)
        except Exception as e:
            print(f"Error saving to history.json: {e}")

# Initialize AI Assistant
assistant = AIAssistant()

@app.route('/')
def index():
    """Serve the web interface"""
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat requests"""
    try:
        data = request.get_json()
        user_input = data.get('message', '').strip()
        
        if not user_input:
            return jsonify({'error': 'No message provided'}), 400
        
        # Show listening expression
        if assistant.oled:
            assistant.oled.show_expression("listening")
        
        print(f"[USER]: {user_input}")
        
        # Generate AI response
        ai_response = assistant.generate_response(user_input)
        
        print(f"[AI]: {ai_response}")
        
        return jsonify({
            'response': ai_response,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/history')
def history():
    """Get chat history from history.json"""
    try:
        with open('database/history.json', 'r', encoding='utf-8') as f:
            history = json.load(f)
        return jsonify(history)
    except Exception as e:
        print(f"Error reading history.json: {e}")
        return jsonify([])

@app.route('/status')
def status():
    """Get system status"""
    return jsonify({
        'ai_model_loaded': assistant.model is not None,
        'oled_available': assistant.oled is not None,
        'chat_history_count': len(assistant.chat_history)
    })

def terminal_interface():
    """Terminal chat interface"""
    print("\n" + "="*50)
    print("🤖 TinyLlama Assistant Terminal Interface")
    print("Type 'quit' or 'exit' to stop")
    print("="*50 + "\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            if not user_input:
                continue
            
            # Generate response
            ai_response = assistant.generate_response(user_input)
            
            print(f"AI: {ai_response}\n")
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == '__main__':
    # Start terminal interface in a separate thread
    terminal_thread = threading.Thread(target=terminal_interface, daemon=True)
    terminal_thread.start()
    
    print("Starting TinyLlama Assistant...")
    print("Web interface will be available at: http://0.0.0.0:5000")
    print("Terminal interface is running in parallel")
    
    # Start Flask app
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)