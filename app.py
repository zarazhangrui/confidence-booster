from flask import Flask, request, render_template, jsonify
import os
from werkzeug.utils import secure_filename
import PyPDF2
from docx import Document
from openai import OpenAI
from dotenv import load_dotenv
from flask_cors import CORS
from usage_limits import check_rate_limit, track_token_usage, get_usage_stats, count_tokens
from admin_auth import requires_auth

load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc'}

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def extract_text_from_docx(file_path):
    doc = Document(file_path)
    return " ".join([paragraph.text for paragraph in doc.paragraphs])

def generate_confidence_boost(resume_text):
    try:
        # Truncate resume text if it's too long (to speed up processing)
        max_resume_length = 2000
        if len(resume_text) > max_resume_length:
            resume_text = resume_text[:max_resume_length] + "..."

        prompt = f"""Analyze this resume and write a genuine, sincere 300-500 word essay that focuses on the person's underlying qualities, character strengths, and their professional evolution. 

        Important Guidelines:
        1. DO NOT repeat or directly reference specific roles, titles, or achievements from the resume
        2. Instead, INFER and discuss their personal qualities such as:
           - Adaptability shown through career transitions
           - Problem-solving abilities demonstrated by their responsibilities
           - Leadership potential evident in their progression
           - Growth mindset revealed by their educational choices
           - Resilience shown in their professional journey

        3. Take a "big picture" view:
           - Analyze their overall career trajectory and what it reveals about them
           - Consider what skills and determination it took to move between their roles
           - Reflect on how their educational background shaped their path
           - Highlight the personal growth evident in their journey

        4. Make them feel genuinely good about:
           - How far they've come in their professional journey
           - The unique perspective they've gained from their experiences
           - The transferable strengths they've developed
           - Their potential for future growth

        Resume to analyze:
        {resume_text}

        Remember: Focus on WHO they are and WHAT they're capable of, not just WHAT they've done. Help them see their own potential through the lens of their journey so far."""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Faster model
            messages=[
                {"role": "system", "content": "You are an insightful career coach who specializes in helping people recognize their deeper strengths and unique value. You focus on personal qualities and potential rather than just achievements."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=600  # Increased for longer response
        )
        
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error in generate_confidence_boost: {str(e)}")
        return f"Error generating confidence boost: {str(e)}"

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy'}), 200

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
@requires_auth
def admin():
    """Admin dashboard"""
    return render_template('admin.html')

@app.route('/admin/api/stats')
@requires_auth
def admin_stats():
    """Get current usage statistics"""
    return jsonify(get_usage_stats())

@app.route('/usage')
def usage():
    """Get current usage statistics"""
    return jsonify(get_usage_stats())

@app.route('/upload', methods=['POST'])
@check_rate_limit()
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            try:
                # Extract text based on file type
                if filename.endswith('.pdf'):
                    text = extract_text_from_pdf(filepath)
                else:  # docx
                    text = extract_text_from_docx(filepath)
                
                # Count input tokens
                input_tokens = count_tokens(text)
                
                # Generate confidence boost
                confidence_boost = generate_confidence_boost(text)
                
                # Count output tokens
                output_tokens = count_tokens(confidence_boost)
                
                # Track total token usage (ignore if Redis is down)
                try:
                    total_tokens = input_tokens + output_tokens
                    track_token_usage(total_tokens)
                except:
                    pass  # Continue even if token tracking fails
                
                # Clean up - delete the uploaded file
                os.remove(filepath)
                
                return jsonify({
                    'message': confidence_boost,
                    'token_usage': {
                        'input_tokens': input_tokens,
                        'output_tokens': output_tokens,
                        'total_tokens': input_tokens + output_tokens
                    }
                })
                
            except Exception as e:
                # Clean up file in case of error
                if os.path.exists(filepath):
                    os.remove(filepath)
                return jsonify({'error': str(e)}), 500
                
        return jsonify({'error': 'Invalid file type'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5005)
