# Financial Image Scanner - AI-Powered Financial Document Analysis

A comprehensive system for extracting and analyzing financial information from document images using advanced OCR, chart analysis, and AI-powered insights.

## 🚀 Features

### Core Capabilities
- **📷 Advanced Image Processing**: Support for multiple formats (PNG, JPG, PDF, TIFF, BMP)
- **🔤 OCR Text Extraction**: High-accuracy text extraction from financial documents
- **📊 Chart & Graph Analysis**: Intelligent analysis of financial visualizations
- **🧠 AI-Powered Insights**: Context-aware financial analysis using LLMs
- **📋 Comprehensive Reporting**: Professional financial reports with investment recommendations

### Web Application Features
- **🌐 Modern Web Interface**: Responsive design with drag-and-drop upload
- **🔗 URL Support**: Process documents from online sources
- **📱 Mobile Friendly**: Works on all devices
- **💾 Export Options**: Download reports in multiple formats
- **🎯 Demo Mode**: Try with sample data

## 📦 Installation

### Quick Start
```bash
# Clone the repository
git clone <repository-url>
cd financial-image-scanner

# Install basic requirements
pip install -r requirements.txt

# Start the web application
python web_app.py
```

### Detailed Installation

#### 1. Basic Requirements
```bash
pip install flask pillow pandas numpy requests
```

#### 2. OCR Support (Recommended)
```bash
pip install pytesseract opencv-python

# Install Tesseract OCR engine
# Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
# macOS: brew install tesseract
# Ubuntu: sudo apt-get install tesseract-ocr
```

#### 3. LLM Integration (Optional)
```bash
# For OpenAI GPT support
pip install openai
export OPENAI_API_KEY='your-openai-api-key'

# For Anthropic Claude support
pip install anthropic
export ANTHROPIC_API_KEY='your-anthropic-api-key'
```

## 🎯 Usage

### Web Application
1. **Start the application**: `python web_app.py`
2. **Open browser**: Navigate to `http://localhost:5000`
3. **Upload documents**: Use drag-and-drop or file selection
4. **Add URLs**: Optionally add document URLs
5. **Configure analysis**: Set company name and report type
6. **Get results**: View comprehensive financial analysis

### Python API
```python
from financial_image_processor import FinancialImageProcessor
from financial_analyzer import FinancialAnalyzer
from financial_report_generator import FinancialReportGenerator

# Initialize components
processor = FinancialImageProcessor()
analyzer = FinancialAnalyzer()
report_generator = FinancialReportGenerator(analyzer)

# Process documents
results = processor.process_financial_document([
    'balance_sheet.png',
    'financial_chart.png'
])

# Generate comprehensive report
report = report_generator.generate_comprehensive_report(
    metrics=results['extracted_metrics'],
    charts=results['chart_analyses'],
    raw_texts=[text['text'] for text in results['raw_texts']],
    company_name='Your Company',
    report_type='quarterly_report'
)

# Display report
print(report_generator.format_report_as_text(report))
```

### Jupyter Notebook
Run the provided `Financial_Image_Scans.ipynb` notebook for an interactive demonstration of all features.

## 📊 Report Structure

The system generates comprehensive financial reports with the following sections:

### 1. Executive Summary
- Overall assessment and key highlights
- Chart insights and trends
- Investment recommendation overview

### 2. Key Financial Metrics
- Profitability metrics (Net Profit, ROE, EPS)
- Efficiency ratios (Cost/Income, Operating Margin)
- Capital adequacy (CET1 Ratio, Leverage Ratio)

### 3. Income and Expenses
- Revenue analysis and trends
- Operating expense breakdown
- Margin analysis and efficiency

### 4. Balance Sheet Highlights
- Asset composition and growth
- Liability management
- Equity and capital structure

### 5. Credit Quality
- Risk metrics and provisions
- Credit portfolio analysis
- Asset quality indicators

### 6. Strategic and Operational Updates
- Business initiatives
- Digital transformation
- Sustainable finance

### 7. Market Conditions and Outlook
- Macroeconomic factors
- Industry trends
- Forward guidance

## 🔧 Configuration

### Environment Variables
```bash
# LLM API Keys (optional)
export OPENAI_API_KEY='your-openai-key'
export ANTHROPIC_API_KEY='your-anthropic-key'

# Flask Configuration
export FLASK_ENV='development'  # or 'production'
export SECRET_KEY='your-secret-key'
```

### Supported File Formats
- **Images**: PNG, JPG, JPEG, TIFF, BMP
- **Documents**: PDF (via image conversion)
- **URLs**: Direct HTTP/HTTPS image links

### Report Types
- **Quarterly Report**: Q-over-Q analysis
- **Annual Report**: Year-over-year comprehensive analysis
- **Investment Analysis**: Investment-focused recommendations

## 🏗️ Architecture

### Core Components

#### FinancialImageProcessor
- Image loading and preprocessing
- OCR text extraction
- Chart type detection
- Financial metric parsing

#### FinancialAnalyzer
- LLM integration (OpenAI/Anthropic)
- Rule-based fallback analysis
- Investment recommendation generation
- Trend analysis

#### FinancialReportGenerator
- Structured report generation
- Multiple report templates
- Formatting and export
- Executive summary creation

#### Web Application
- Flask-based REST API
- Modern responsive UI
- File upload handling
- Progress tracking

## 📈 Sample Output

```
Summary of ABN AMRO Bank Quarterly Report (Q3 2024)

Key Financial Metrics
● Net Profit: EUR 690 million, down from EUR 759 million in Q3 2023.
● Earnings Per Share (EPS): EUR 0.78, slightly below EUR 0.85 in Q3 2023.
● Return on Equity: 11.6%, within the target of 9–10%.
● Cost/Income Ratio: Improved to 59.2%, nearing the long-term target of 60%.
● Common Equity Tier 1 (CET1) Ratio: 14.1%, reflecting a strong capital position.

Investment Recommendation
OVERWEIGHT - Strong financial performance with positive momentum across key metrics
```

## 🚀 Deployment

### Development
```bash
python web_app.py
```

### Production
```bash
# Using Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 web_app:app

# Using Docker
docker build -t financial-scanner .
docker run -p 5000:5000 financial-scanner
```

### Docker Configuration
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "web_app:app"]
```

## 🔍 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Home page |
| GET | `/upload` | Upload interface |
| POST | `/upload` | Process documents |
| GET | `/results/<id>` | View analysis results |
| GET | `/download/<id>` | Download report |
| GET | `/demo` | Demo with sample data |
| POST | `/api/analyze` | JSON API for analysis |
| GET | `/api/health` | Health check |

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=.

# Test specific components
pytest test_image_processor.py
pytest test_analyzer.py
pytest test_report_generator.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

### Common Issues

#### OCR Not Working
- Ensure Tesseract is installed
- Check image quality and resolution
- Verify supported file formats

#### LLM Integration
- Verify API keys are set correctly
- Check internet connection
- Monitor API usage limits

#### Memory Issues
- Reduce image sizes before processing
- Process documents in batches
- Increase system RAM if needed

### Getting Help
- Check the troubleshooting guide
- Review the API documentation
- Open an issue on GitHub

## 🔄 Changelog

### v2.0.0 (Current)
- ✅ Complete system rewrite
- ✅ Advanced OCR integration
- ✅ LLM-powered analysis
- ✅ Modern web interface
- ✅ Comprehensive reporting
- ✅ URL support
- ✅ Multiple report types

### v1.0.0 (Original)
- ✅ Basic image processing
- ✅ Simulated analysis
- ✅ Jupyter notebook interface

## 🎯 Future Roadmap

- [ ] Real-time financial data integration
- [ ] Advanced chart pattern recognition
- [ ] Multi-language support
- [ ] Batch processing capabilities
- [ ] Integration with financial data APIs
- [ ] Mobile application
- [ ] Advanced risk modeling
- [ ] Portfolio analysis features

---

**Financial Image Scanner** - Transform financial documents into actionable insights with AI-powered analysis.
