from flask import Flask, render_template, request, jsonify, send_file
import google.generativeai as genai
import wave
import re
from collections import Counter
import os
import datetime
import uuid

app = Flask(__name__)

# Gemini client - Use environment variable for API key in production
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', "AIzaSyBMi7RqQdtvSjqGJFKePfEuAmbojFksIcc")
genai.configure(api_key=GEMINI_API_KEY)

def extract_keywords(text, top_n=10):
    """
    Extract the most important keywords from the generated text
    """
    # Clean the text: remove stage directions, sound effects, and common words
    cleaned_text = text.lower()
    
    # Remove content in parentheses (stage directions)
    cleaned_text = re.sub(r'\([^)]*\)', '', cleaned_text)
    
    # Remove content in square brackets (sound effects)
    cleaned_text = re.sub(r'\[[^\]]*\]', '', cleaned_text)
    
    # Remove common phrases from the prompt
    stop_phrases = ['speech speed should be 5x', 'voiceover:', 'generate', 'script']
    for phrase in stop_phrases:
        cleaned_text = cleaned_text.replace(phrase, '')
    
    # Split into words and filter
    words = re.findall(r'\b[a-zA-Z]{3,}\b', cleaned_text)
    
    # Common stop words to exclude
    stop_words = {
        'the', 'and', 'you', 'that', 'was', 'for', 'are', 'with', 'his', 'they',
        'this', 'have', 'from', 'one', 'had', 'word', 'but', 'not', 'what',
        'all', 'were', 'when', 'your', 'can', 'said', 'there', 'each', 'which',
        'she', 'how', 'will', 'about', 'out', 'many', 'then', 'them', 'these',
        'has', 'her', 'would', 'make', 'like', 'him', 'into', 'time', 'two',
        'more', 'very', 'after', 'words', 'long', 'than', 'way', 'been',
        'its', 'who', 'did', 'get', 'may', 'day', 'use', 'man', 'new', 'now',
        'old', 'see', 'come', 'could', 'people', 'just', 'know', 'take', 'year'
    }
    
    # Filter out stop words and count frequency
    filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
    word_counts = Counter(filtered_words)
    
    # Get top keywords
    keywords = [word for word, count in word_counts.most_common(top_n)]
    
    return keywords

def wave_file(filename, pcm, channels=1, rate=24000, sample_width=2):
    """Save PCM data to a wave file"""
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm)

def generate_tts_script_and_audio(topic_option=None, custom_prompt=None):
    """Generate TTS script and audio, return script, keywords, and filename"""
    
    try:
        # Base prompt for script generation
        base_prompt = """
Generate a short, creative, and funny 30-second reel script in a curious tone for speech generation for a fast-paced Instagram reel. 
add "Speech speed should be 5x" in every output.
The script must ONLY be about ONE of the following topics:
1. A list of random, surprising, or weird facts (could be historical, science-based, or internet trends).
2. A short, humorous and quirky fictional mini-story.
3. A light, curious, and slightly funny take on a recent geopolitical event or news trend (must be non-offensive and friendly).

The script should be formatted for a VOICEOVER with stage directions in parentheses (e.g., (soft laugh), (pause), (playful chuckle)) to indicate emotions, pauses, and tone shifts. 
Include SOUND EFFECT suggestions in ALL CAPS inside square brackets [e.g., [BEEP], [WAVES], [DRUM ROLL]] wherever relevant for comedic or dramatic effect.

Style rules:
- Humor should be light, friendly, and relatable—similar to casual Instagram reel background audio.
- Can reference recent internet memes, viral trends, or pop culture moments if relevant to the topic.
- Maintain natural pauses, laughter cues, and changes in tone.
- Keep it around 80–120 words so it fits in ~30 seconds.
- Always open with a hook that makes people curious.

Example:
(Playful chuckle)  
Voiceover: You know octopuses have three hearts… (pause) and two of them stop beating when they swim?  
[LITTLE SPLASH SOUND]  
Voiceover: Yeah… so basically, cardio day is a literal heartbreaker for them. (laugh)

Now, generate the script.
"""
        
        # Use custom prompt if provided, otherwise use base prompt
        prompt = custom_prompt if custom_prompt else base_prompt
        
        # Generate script
        print(f"Generating script with prompt: {prompt[:100]}...")
        model = genai.GenerativeModel("gemini-1.5-flash")
        script_response = model.generate_content(prompt)
        
        if not script_response or not script_response.text:
            raise Exception("Failed to generate script - empty response from Gemini")
        
        generated_text = script_response.text
        print(f"Generated script: {generated_text[:100]}...")
        
        keywords_list = extract_keywords(generated_text)
        
        # For now, use basic TTS since advanced TTS with Gemini API is complex
        # We'll use a simple text-to-speech approach
        print("Generating TTS audio...")
        
        # Use pyttsx3 for TTS as fallback
        try:
            import pyttsx3
            engine = pyttsx3.init()
            
            # Configure voice settings
            voices = engine.getProperty('voices')
            if voices:
                # Try to use a female voice if available
                for voice in voices:
                    if 'female' in voice.name.lower() or 'zira' in voice.name.lower() or 'hazel' in voice.name.lower():
                        engine.setProperty('voice', voice.id)
                        break
            
            engine.setProperty('rate', 150)    # Speed of speech
            engine.setProperty('volume', 0.8)  # Volume level
            
            # Generate unique filename
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            filename = f"tts_audio_{timestamp}_{unique_id}.wav"
            
            # Save audio file
            engine.save_to_file(generated_text, filename)
            engine.runAndWait()
            
            print(f"Audio saved to: {filename}")
            
        except Exception as tts_error:
            print(f"TTS Error: {tts_error}")
            # Fallback: create a simple audio file placeholder
            filename = f"tts_audio_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
            # Create a simple placeholder file if TTS fails
            with open(filename, 'wb') as f:
                # Create a minimal WAV file header (silence)
                import struct
                sample_rate = 22050
                duration = 1  # 1 second of silence
                samples = sample_rate * duration
                
                # WAV header
                f.write(b'RIFF')
                f.write(struct.pack('<I', 36 + samples * 2))
                f.write(b'WAVE')
                f.write(b'fmt ')
                f.write(struct.pack('<I', 16))
                f.write(struct.pack('<H', 1))  # PCM
                f.write(struct.pack('<H', 1))  # mono
                f.write(struct.pack('<I', sample_rate))
                f.write(struct.pack('<I', sample_rate * 2))
                f.write(struct.pack('<H', 2))
                f.write(struct.pack('<H', 16))
                f.write(b'data')
                f.write(struct.pack('<I', samples * 2))
                
                # Silent audio data
                for _ in range(samples):
                    f.write(struct.pack('<h', 0))
        
        return {
            'script': generated_text,
            'keywords': keywords_list,
            'filename': filename,
            'success': True
        }
        
    except Exception as e:
        print(f"Error in generate_tts_script_and_audio: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'script': '',
            'keywords': [],
            'filename': ''
        }

@app.route('/')
def index():
    """Main page with TTS interface"""
    return render_template('index.html')

@app.route('/health')
def health_check():
    """Health check endpoint for Render"""
    return jsonify({'status': 'healthy', 'service': 'gemini-tts-app'})

@app.route('/debug')
def debug_page():
    """Debug test page"""
    return send_file('debug_test.html')

@app.route('/generate', methods=['POST'])
def generate_audio():
    """Generate TTS audio and return details"""
    try:
        print(f"Generate endpoint called - Request headers: {dict(request.headers)}")
        print(f"Request content type: {request.content_type}")
        print(f"Request is_json: {request.is_json}")
        
        # Handle both JSON and form data
        if request.is_json:
            data = request.get_json() or {}
            print(f"JSON data received: {data}")
        else:
            data = request.form.to_dict()
            print(f"Form data received: {data}")
        
        custom_prompt = data.get('custom_prompt', '').strip()
        print(f"Custom prompt: '{custom_prompt}'")
        
        # Generate TTS
        print("Starting TTS generation...")
        result = generate_tts_script_and_audio(custom_prompt=custom_prompt if custom_prompt else None)
        print(f"TTS generation completed. Result success: {result.get('success')}")
        
        # Ensure the response is properly formatted
        if not isinstance(result, dict):
            raise ValueError("Invalid result format from TTS generation")
        
        # Add CORS headers for browser compatibility
        response = jsonify(result)
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        
        return response
    
    except Exception as e:
        print(f"Error in generate_audio: {str(e)}")  # Log error for debugging
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        
        error_response = jsonify({
            'success': False,
            'error': str(e)
        })
        error_response.headers.add('Access-Control-Allow-Origin', '*')
        return error_response, 500

@app.route('/download/<filename>')
def download_audio(filename):
    """Download the generated audio file"""
    try:
        if os.path.exists(filename):
            return send_file(filename, as_attachment=True, download_name=filename)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/files')
def list_files():
    """List all generated audio files"""
    try:
        audio_files = [f for f in os.listdir('.') if f.startswith('tts_audio_') and f.endswith('.wav')]
        audio_files.sort(reverse=True)  # Most recent first
        return jsonify({'files': audio_files})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # For development
    app.run(debug=True, host='0.0.0.0', port=5000)
else:
    # For production (Render will use gunicorn)
    app.debug = False
