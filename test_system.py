#!/usr/bin/env python3
"""
System Test Script for AI Assistant
Tests all components before running the main application
"""

import sys
import os
import time

def test_imports():
    """Test all required imports"""
    print("🧪 Testing Python imports...")
    
    try:
        import flask
        print("✅ Flask imported successfully")
    except ImportError as e:
        print(f"❌ Flask import failed: {e}")
        return False
    
    try:
        import transformers
        import torch
        print("✅ AI libraries imported successfully")
    except ImportError as e:
        print(f"⚠️  AI libraries not available: {e}")
        print("   The system will run with fallback responses")
    
    try:
        import board
        import digitalio
        import adafruit_ssd1306
        from PIL import Image, ImageDraw
        print("✅ OLED libraries imported successfully")
    except ImportError as e:
        print(f"⚠️  OLED libraries not available: {e}")
        print("   The system will run without OLED display")
    
    return True

def test_oled_display():
    """Test OLED display functionality"""
    print("\n🖥️  Testing OLED display...")
    
    try:
        from oled_display import OLEDDisplay
        oled = OLEDDisplay()
        
        print("✅ OLED display initialized")
        
        # Test expressions
        expressions = ["idle", "listening", "thinking", "speaking"]
        for expr in expressions:
            print(f"   Testing expression: {expr}")
            oled.show_expression(expr)
            time.sleep(1)
        
        oled.show_expression("idle")
        print("✅ OLED expressions test completed")
        return True
        
    except Exception as e:
        print(f"⚠️  OLED test failed: {e}")
        return False

def test_ai_model():
    """Test AI model loading"""
    print("\n🤖 Testing AI model...")
    
    try:
        from transformers import GPT2LMHeadModel, GPT2Tokenizer
        
        model_name = "distilgpt2"
        print(f"   Loading model: {model_name}")
        
        tokenizer = GPT2Tokenizer.from_pretrained(model_name)
        model = GPT2LMHeadModel.from_pretrained(model_name)
        
        print("✅ AI model loaded successfully")
        
        # Test generation
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        inputs = tokenizer.encode("Hello, I am", return_tensors="pt")
        with torch.no_grad():
            outputs = model.generate(inputs, max_length=20, do_sample=True)
        
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print(f"   Test generation: {response}")
        print("✅ AI model generation test completed")
        return True
        
    except Exception as e:
        print(f"⚠️  AI model test failed: {e}")
        return False

def test_flask_app():
    """Test Flask application"""
    print("\n🌐 Testing Flask application...")
    
    try:
        # Import without running
        import app
        print("✅ Flask app imported successfully")
        
        # Test routes exist
        routes = [rule.rule for rule in app.app.url_map.iter_rules()]
        expected_routes = ['/', '/chat', '/history', '/status']
        
        for route in expected_routes:
            if route in routes:
                print(f"✅ Route {route} exists")
            else:
                print(f"❌ Route {route} missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Flask app test failed: {e}")
        return False

def test_file_structure():
    """Test project file structure"""
    print("\n📁 Testing file structure...")
    
    required_files = [
        'app.py',
        'oled_display.py',
        'requirements.txt',
        'templates/index.html',
        'static/style.css',
        'static/script.js'
    ]
    
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} missing")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🚀 AI Assistant System Test")
    print("===========================")
    
    tests = [
        ("File Structure", test_file_structure),
        ("Python Imports", test_imports),
        ("Flask Application", test_flask_app),
        ("OLED Display", test_oled_display),
        ("AI Model", test_ai_model),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    print("\n📊 Test Results Summary:")
    print("========================")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nTests passed: {passed}/{len(results)}")
    
    if passed == len(results):
        print("\n🎉 All tests passed! System is ready to run.")
        print("Start with: python app.py")
    else:
        print("\n⚠️  Some tests failed. Check the issues above.")
        print("The system may still work with limited functionality.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
