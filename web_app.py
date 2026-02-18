"""
Financial Image Scanner Web Application
Modern Flask web interface for financial document analysis
"""

from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime
from pathlib import Path
import tempfile
from typing import List, Dict, Any

# Import our custom modules
from financial_image_processor import FinancialImageProcessor
from financial_analyzer import FinancialAnalyzer
from financial_report_generator import FinancialReportGenerator

app = Flask(__name__)
app.config['SECRET_KEY'] = 'financial-scanner-secret-key-2024'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize components
processor = FinancialImageProcessor()
analyzer = FinancialAnalyzer()
report_generator = FinancialReportGenerator(analyzer)

# Supported file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'tiff', 'bmp', 'pdf'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_files():
    """Handle file uploads and URL inputs"""
    if request.method == 'POST':
        # Get uploaded files
        files = request.files.getlist('files')
        # Get URLs
        urls = request.form.getlist('urls')
        
        image_paths = []
        
        # Process uploaded files
        for file in files:
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{timestamp}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                image_paths.append(filepath)
        
        # Add URLs (they'll be processed directly)
        image_paths.extend(urls)
        
        if not image_paths:
            flash('No valid files or URLs provided', 'error')
            return redirect(url_for('index'))
        
        # Store paths in session for processing
        session_data = {
            'image_paths': image_paths,
            'upload_time': datetime.now().isoformat(),
            'company_name': request.form.get('company_name', 'Unknown Company'),
            'report_type': request.form.get('report_type', 'quarterly_report')
        }
        
        # Process the images
        try:
            # Process financial documents
            processing_results = processor.process_financial_document(image_paths)
            
            # Generate comprehensive report
            report = report_generator.generate_comprehensive_report(
                metrics=processing_results['extracted_metrics'],
                charts=processing_results['chart_analyses'],
                raw_texts=[text['text'] for text in processing_results['raw_texts']],
                report_type=session_data['report_type'],
                company_name=session_data['company_name']
            )
            
            # Store results for display
            session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_file = os.path.join(app.config['UPLOAD_FOLDER'], f'results_{session_id}.json')
            
            full_results = {
                'session_data': session_data,
                'processing_results': processing_results,
                'report': report,
                'formatted_report': report_generator.format_report_as_text(report)
            }
            
            with open(results_file, 'w') as f:
                json.dump(full_results, f, indent=2, default=str)
            
            return render_template('results.html', 
                                 results=full_results,
                                 session_id=session_id)
            
        except Exception as e:
            flash(f'Error processing files: {str(e)}', 'error')
            return redirect(url_for('index'))
    
    return render_template('upload.html')

@app.route('/analyze', methods=['POST'])
def analyze_images():
    """API endpoint for image analysis"""
    try:
        data = request.get_json()
        image_paths = data.get('image_paths', [])
        company_name = data.get('company_name', 'Unknown Company')
        report_type = data.get('report_type', 'quarterly_report')
        
        if not image_paths:
            return jsonify({'error': 'No image paths provided'}), 400
        
        # Process images
        processing_results = processor.process_financial_document(image_paths)
        
        # Generate report
        report = report_generator.generate_comprehensive_report(
            metrics=processing_results['extracted_metrics'],
            charts=processing_results['chart_analyses'],
            raw_texts=[text['text'] for text in processing_results['raw_texts']],
            report_type=report_type,
            company_name=company_name
        )
        
        return jsonify({
            'success': True,
            'report': report,
            'processing_results': processing_results,
            'formatted_report': report_generator.format_report_as_text(report)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/results/<session_id>')
def view_results(session_id):
    """View analysis results"""
    results_file = os.path.join(app.config['UPLOAD_FOLDER'], f'results_{session_id}.json')
    
    if not os.path.exists(results_file):
        flash('Results not found', 'error')
        return redirect(url_for('index'))
    
    with open(results_file, 'r') as f:
        results = json.load(f)
    
    return render_template('results.html', results=results, session_id=session_id)

@app.route('/download/<session_id>')
def download_report(session_id):
    """Download report as text file"""
    results_file = os.path.join(app.config['UPLOAD_FOLDER'], f'results_{session_id}.json')
    
    if not os.path.exists(results_file):
        flash('Results not found', 'error')
        return redirect(url_for('index'))
    
    with open(results_file, 'r') as f:
        results = json.load(f)
    
    # Create temporary file for download
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
    temp_file.write(results['formatted_report'])
    temp_file.close()
    
    return send_file(temp_file.name, 
                    as_attachment=True, 
                    download_name=f"financial_report_{session_id}.txt")

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'components': {
            'processor': 'available',
            'analyzer': 'available',
            'report_generator': 'available'
        }
    })

@app.route('/demo')
def demo():
    """Demo page with sample data"""
    # Use sample images
    sample_images = [
        'balance_sheet_sample.png',
        'figures_glance_sample.png'
    ]
    
    # Convert to full paths
    current_dir = Path(__file__).parent
    image_paths = [str(current_dir / img) for img in sample_images if (current_dir / img).exists()]
    
    if not image_paths:
        flash('Sample images not found', 'error')
        return redirect(url_for('index'))
    
    try:
        # Process sample images
        processing_results = processor.process_financial_document(image_paths)
        
        # Generate demo report
        report = report_generator.generate_comprehensive_report(
            metrics=processing_results['extracted_metrics'],
            charts=processing_results['chart_analyses'],
            raw_texts=[text['text'] for text in processing_results['raw_texts']],
            report_type='quarterly_report',
            company_name='ABN AMRO Bank'
        )
        
        # Format for display
        formatted_results = {
            'session_data': {
                'company_name': 'ABN AMRO Bank',
                'report_type': 'quarterly_report',
                'upload_time': datetime.now().isoformat()
            },
            'processing_results': processing_results,
            'report': report,
            'formatted_report': report_generator.format_report_as_text(report)
        }
        
        return render_template('results.html', 
                             results=formatted_results,
                             session_id='demo',
                             is_demo=True)
        
    except Exception as e:
        flash(f'Demo error: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    flash('File too large. Maximum size is 16MB.', 'error')
    return redirect(url_for('index'))

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors"""
    return render_template('500.html'), 500

if __name__ == '__main__':
    print("Starting Financial Image Scanner Web Application...")
    print("Access the application at: http://localhost:5000")
    print("Demo available at: http://localhost:5000/demo")
    app.run(debug=True, host='0.0.0.0', port=5000)
