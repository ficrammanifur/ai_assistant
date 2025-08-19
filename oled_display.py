"""
OLED Display Controller for AI Assistant Expressions
Supports 128x64 OLED displays using SSD1306
"""

import time
import threading
from PIL import Image, ImageDraw, ImageFont

try:
    import board
    import digitalio
    import adafruit_ssd1306
    OLED_HARDWARE_AVAILABLE = True
except ImportError:
    print("Warning: OLED hardware libraries not available")
    print("Install with: pip install adafruit-circuitpython-ssd1306 adafruit-blinka")
    OLED_HARDWARE_AVAILABLE = False

class OLEDDisplay:
    def __init__(self, width=128, height=64):
        self.width = width
        self.height = height
        self.display = None
        self.current_expression = "idle"
        self.animation_thread = None
        self.stop_animation = False
        
        # Initialize hardware display
        self.init_display()
        
        # Expression parameters
        self.expressions = {
            "idle": {"eyes": "normal", "mouth": "straight"},
            "listening": {"eyes": "normal", "mouth": "straight"},
            "thinking": {"eyes": "blink", "mouth": "dots"},
            "speaking": {"eyes": "normal", "mouth": "smile"}
        }
    
    def init_display(self):
        """Initialize the OLED display"""
        if not OLED_HARDWARE_AVAILABLE:
            print("OLED Display: Running in simulation mode")
            return
        
        try:
            # Initialize I2C
            i2c = board.I2C()
            
            # Initialize display
            self.display = adafruit_ssd1306.SSD1306_I2C(
                self.width, self.height, i2c, addr=0x3C
            )
            
            # Clear display
            self.display.fill(0)
            self.display.show()
            
            print("OLED Display initialized successfully")
            
        except Exception as e:
            print(f"OLED Display initialization failed: {e}")
            self.display = None
    
    def create_face_image(self, expression_type):
        """Create a face image based on expression type"""
        # Create image
        image = Image.new('1', (self.width, self.height))
        draw = ImageDraw.Draw(image)
        
        # Face parameters
        eye_y = 20
        left_eye_x = 35
        right_eye_x = 85
        mouth_y = 45
        mouth_x = self.width // 2
        
        expression = self.expressions.get(expression_type, self.expressions["idle"])
        
        # Draw eyes
        if expression["eyes"] == "normal":
            # Normal open eyes
            draw.ellipse([left_eye_x-8, eye_y-6, left_eye_x+8, eye_y+6], fill=1)
            draw.ellipse([right_eye_x-8, eye_y-6, right_eye_x+8, eye_y+6], fill=1)
            # Pupils
            draw.ellipse([left_eye_x-3, eye_y-3, left_eye_x+3, eye_y+3], fill=0)
            draw.ellipse([right_eye_x-3, eye_y-3, right_eye_x+3, eye_y+3], fill=0)
            
        elif expression["eyes"] == "blink":
            # Blinking eyes (lines)
            draw.line([left_eye_x-8, eye_y, left_eye_x+8, eye_y], fill=1, width=2)
            draw.line([right_eye_x-8, eye_y, right_eye_x+8, eye_y], fill=1, width=2)
        
        # Draw mouth
        if expression["mouth"] == "straight":
            # Straight mouth
            draw.line([mouth_x-15, mouth_y, mouth_x+15, mouth_y], fill=1, width=2)
            
        elif expression["mouth"] == "smile":
            # Smiling mouth (U shape)
            draw.arc([mouth_x-15, mouth_y-5, mouth_x+15, mouth_y+10], 0, 180, fill=1, width=2)
            
        elif expression["mouth"] == "dots":
            # Thinking dots
            draw.ellipse([mouth_x-12, mouth_y-2, mouth_x-8, mouth_y+2], fill=1)
            draw.ellipse([mouth_x-4, mouth_y-2, mouth_x, mouth_y+2], fill=1)
            draw.ellipse([mouth_x+4, mouth_y-2, mouth_x+8, mouth_y+2], fill=1)
        
        return image
    
    def show_expression(self, expression_type):
        """Display an expression on the OLED"""
        self.current_expression = expression_type
        
        # Stop any running animation
        self.stop_animation = True
        if self.animation_thread and self.animation_thread.is_alive():
            self.animation_thread.join(timeout=0.5)
        
        if expression_type == "thinking":
            # Start blinking animation for thinking
            self.stop_animation = False
            self.animation_thread = threading.Thread(target=self._thinking_animation)
            self.animation_thread.start()
        else:
            # Show static expression
            self._display_static_expression(expression_type)
    
    def _display_static_expression(self, expression_type):
        """Display a static expression"""
        try:
            image = self.create_face_image(expression_type)
            
            if self.display:
                # Display on hardware
                self.display.image(image)
                self.display.show()
            else:
                # Simulate display in console
                self._print_ascii_face(expression_type)
                
        except Exception as e:
            print(f"Error displaying expression: {e}")
    
    def _thinking_animation(self):
        """Animate thinking expression with blinking"""
        blink_states = ["normal", "blink"]
        blink_index = 0
        
        while not self.stop_animation:
            try:
                # Create thinking expression with alternating blink
                expression = {
                    "eyes": blink_states[blink_index],
                    "mouth": "dots"
                }
                
                # Create custom image for animation
                image = Image.new('1', (self.width, self.height))
                draw = ImageDraw.Draw(image)
                
                # Draw animated eyes
                eye_y = 20
                left_eye_x = 35
                right_eye_x = 85
                
                if expression["eyes"] == "normal":
                    draw.ellipse([left_eye_x-8, eye_y-6, left_eye_x+8, eye_y+6], fill=1)
                    draw.ellipse([right_eye_x-8, eye_y-6, right_eye_x+8, eye_y+6], fill=1)
                    draw.ellipse([left_eye_x-3, eye_y-3, left_eye_x+3, eye_y+3], fill=0)
                    draw.ellipse([right_eye_x-3, eye_y-3, right_eye_x+3, eye_y+3], fill=0)
                else:
                    draw.line([left_eye_x-8, eye_y, left_eye_x+8, eye_y], fill=1, width=2)
                    draw.line([right_eye_x-8, eye_y, right_eye_x+8, eye_y], fill=1, width=2)
                
                # Draw thinking dots
                mouth_y = 45
                mouth_x = self.width // 2
                draw.ellipse([mouth_x-12, mouth_y-2, mouth_x-8, mouth_y+2], fill=1)
                draw.ellipse([mouth_x-4, mouth_y-2, mouth_x, mouth_y+2], fill=1)
                draw.ellipse([mouth_x+4, mouth_y-2, mouth_x+8, mouth_y+2], fill=1)
                
                if self.display:
                    self.display.image(image)
                    self.display.show()
                else:
                    self._print_ascii_face("thinking")
                
                blink_index = (blink_index + 1) % len(blink_states)
                time.sleep(0.8)
                
            except Exception as e:
                print(f"Animation error: {e}")
                break
    
    def _print_ascii_face(self, expression_type):
        """Print ASCII representation of face for simulation"""
        faces = {
            "idle": "  O   O  \n    -    ",
            "listening": "  O   O  \n    -    ",
            "thinking": "  -   -  \n   ...   ",
            "speaking": "  O   O  \n   \\_/   "
        }
        
        face = faces.get(expression_type, faces["idle"])
        print(f"\n[OLED] {expression_type.upper()}:")
        print(face)
        print()
    
    def clear(self):
        """Clear the display"""
        if self.display:
            self.display.fill(0)
            self.display.show()
        else:
            print("[OLED] Display cleared")
    
    def test_expressions(self):
        """Test all expressions"""
        expressions = ["idle", "listening", "thinking", "speaking"]
        
        for expr in expressions:
            print(f"Testing expression: {expr}")
            self.show_expression(expr)
            time.sleep(3)
        
        self.show_expression("idle")

if __name__ == "__main__":
    # Test the OLED display
    oled = OLEDDisplay()
    oled.test_expressions()
