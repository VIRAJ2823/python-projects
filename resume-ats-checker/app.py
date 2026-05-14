# app.py
# Main Flask application

from flask import Flask, render_template, request, jsonify
from extractor import extract_text
from ats_checker import analyze_resume
from keywords import JOB_KEYWORDS
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max

# Create uploads folder if not exists
os.makedirs('uploads', exist_ok=True)

# ===== HOME PAGE =====
@app.route('/')
def index():
    job_roles = list(JOB_KEYWORDS.keys())
    return render_template('index.html', job_roles=job_roles)

# ===== ANALYZE RESUME =====
@app.route('/analyze', methods=['POST'])
def analyze():
    # Check file uploaded
    if 'resume' not in request.files:
        return jsonify({'success': False, 'message': 'No file uploaded'})

    file     = request.files['resume']
    job_role = request.form.get('job_role', '')

    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'})

    if not job_role:
        return jsonify({'success': False, 'message': 'Please select a job role'})

    # Check file type
    allowed = {'.pdf', '.docx'}
    ext     = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed:
        return jsonify({'success': False, 'message': 'Only PDF and DOCX files allowed'})

    # Save file temporarily
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    # Extract text
    resume_text = extract_text(filepath)

    # Delete file after extraction
    os.remove(filepath)

    if not resume_text.strip():
        return jsonify({'success': False, 'message': 'Could not read resume. Try a different file.'})

    # Analyze
    result = analyze_resume(resume_text, job_role)
    return jsonify({'success': True, 'result': result})

# ===== RUN =====
if __name__ == '__main__':
    app.run(debug=True)