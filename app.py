from flask import Flask, request, jsonify, render_template
import threading
import time
import json
from datetime import datetime
import os
import sys

# AI Model imports
try:
    from transformers import GPT2LMHeadModel, GPT2Tokenizer, pipeline
    HF_AVAILABLE = True
except ImportError:
    print("Warning: transformers not installed. Install with: pip install transformers torch")
    HF_AVAILABLE = False

# OLED Display import
try:
    from oled_display import OLEDDisplay
    OLED_AVAILABLE = True
except ImportError:
    print("Warning: OLED display not available. Install dependencies or run without OLED.")
    OLED_AVAILABLE = False

app = Flask(__name__)

class AIAssistant:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.generator = None
        self.oled = None
        self.chat_history = []
        
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
    
    def load_ai_model(self):
        """Load lightweight AI model from Hugging Face"""
        if not HF_AVAILABLE:
            print("Transformers not available. Using fallback responses.")
            return
        
        try:
            print("Loading AI model... This may take a moment.")
            
            # Use DistilGPT-2 for better performance on Raspberry Pi
            model_name = "distilgpt2"
            
            # Check if model exists locally
            model_path = f"./models/{model_name}"
            if os.path.exists(model_path):
                print(f"Loading model from local path: {model_path}")
                self.tokenizer = GPT2Tokenizer.from_pretrained(model_path)
                self.model = GPT2LMHeadModel.from_pretrained(model_path)
            else:
                print(f"Downloading model: {model_name}")
                self.tokenizer = GPT2Tokenizer.from_pretrained(model_name)
                self.model = GPT2LMHeadModel.from_pretrained(model_name)
                
                # Save model locally for future use
                os.makedirs("./models", exist_ok=True)
                self.tokenizer.save_pretrained(model_path)
                self.model.save_pretrained(model_path)
            
            # Set pad token
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Create text generation pipeline
            self.generator = pipeline(
                'text-generation',
                model=self.model,
                tokenizer=self.tokenizer,
                device=-1,  # Use CPU
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            print("AI model loaded successfully!")
            
        except Exception as e:
            print(f"Error loading AI model: {e}")
            self.model = None
            self.tokenizer = None
            self.generator = None
    
    def generate_response(self, user_input):
        """Generate AI response with improved constraints"""
        try:
            # Show thinking expression
            if self.oled:
                self.oled.show_expression("thinking")
            
            if self.generator:
                # Create a conversational prompt with context
                prompt = f"You are a helpful AI assistant running on a Raspberry Pi. Provide a concise and relevant answer to the following question or statement:\nHuman: {user_input}\nAssistant:"
                
                # Generate response with stricter parameters
                response = self.generator(
                    prompt,
                    max_new_tokens=30,  # Limit new tokens for concise output
                    num_return_sequences=1,
                    temperature=0.6,  # Lower temperature for more coherent responses
                    top_p=0.9,  # Use top-p sampling to focus on likely tokens
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id
                )
                
                # Extract the assistant's response
                full_response = response[0]['generated_text']
                ai_response = full_response.split("Assistant:")[-1].strip()
                
                # Clean up the response
                ai_response = ai_response.split("Human:")[0].strip()
                
                # Truncate at last complete sentence
                sentences = ai_response.split('. ')
                if len(sentences) > 1:
                    ai_response = '. '.join(sentences[:-1]) + '.' if sentences[-1] == '' else ai_response
                
                # Fallback for empty or nonsensical responses
                if not ai_response or len(ai_response) < 5:
                    ai_response = "I'm here to help! Could you please rephrase your question?"
                
            else:
                # Fallback responses when model is not available
                fallback_responses = [
                    "I'm here to help! However, the AI model isn't loaded yet.",
                    "That's an interesting question! The AI model is currently unavailable.",
                    "I'd love to help with that, but I'm running in fallback mode right now.",
                    "Great question! Please make sure the AI model is properly installed."
                ]
                ai_response = fallback_responses[len(user_input) % len(fallback_responses)]
            
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
        """Add conversation to history"""
        self.chat_history.append({
            "timestamp": datetime.now().isoformat(),
            "user": user_input,
            "assistant": ai_response
        })
        
        # Keep only last 50 conversations
        if len(self.chat_history) > 50:
            self.chat_history = self.chat_history[-50:]

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
        
        # Add to history
        assistant.add_to_history(user_input, ai_response)
        
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
    """Get chat history"""
    return jsonify(assistant.chat_history)

@app.route('/status')
def status():
    """Get system status"""
    return jsonify({
        'ai_model_loaded': assistant.generator is not None,
        'oled_available': assistant.oled is not None,
        'chat_history_count': len(assistant.chat_history)
    })

def terminal_interface():
    """Terminal chat interface"""
    print("\n" + "="*50)
    print("🤖 AI Assistant Terminal Interface")
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
            assistant.add_to_history(user_input, ai_response)
            
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
    
    print("Starting AI Assistant...")
    print("Web interface will be available at: http://0.0.0.0:5000")
    print("Terminal interface is running in parallel")
    
    # Start Flask app
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)