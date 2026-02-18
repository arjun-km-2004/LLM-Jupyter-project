"""
Financial Image Scanner - Core Module
Handles OCR, chart analysis, and financial document processing
"""

import os
import re
import requests
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from PIL import Image
import pandas as pd
import numpy as np

# OCR Libraries
try:
    import pytesseract
    import cv2
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("Warning: OCR libraries not available. Install with: pip install pytesseract opencv-python")

# Chart Analysis Libraries
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    CHART_ANALYSIS_AVAILABLE = True
except ImportError:
    CHART_ANALYSIS_AVAILABLE = False

@dataclass
class FinancialMetric:
    """Data class for financial metrics"""
    name: str
    value: float
    unit: str
    period: str
    trend: Optional[str] = None

@dataclass
class ChartData:
    """Data class for chart analysis results"""
    chart_type: str
    title: str
    x_axis_label: str
    y_axis_label: str
    data_points: List[Dict[str, Any]]
    trend: str
    insights: List[str]

class FinancialImageProcessor:
    """Main class for processing financial document images"""
    
    def __init__(self):
        self.supported_formats = ['.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.pdf']
        self.financial_keywords = [
            'revenue', 'net profit', 'income', 'eps', 'roe', 'roa', 'assets',
            'liabilities', 'equity', 'cash flow', 'operating expenses', 'margin',
            'ratio', 'percentage', 'growth', 'decline', 'increase', 'decrease'
        ]
        
    def load_images_from_paths(self, image_paths: List[str]) -> List[Image.Image]:
        """Load images from file paths or URLs"""
        images = []
        
        for path in image_paths:
            try:
                if path.startswith(('http://', 'https://')):
                    # Load from URL
                    response = requests.get(path, stream=True)
                    response.raise_for_status()
                    img = Image.open(response.raw)
                else:
                    # Load from local file
                    img_path = Path(path)
                    if not img_path.exists():
                        raise FileNotFoundError(f"Image not found: {path}")
                    img = Image.open(img_path)
                
                images.append(img)
                print(f"Successfully loaded: {path}")
                
            except Exception as e:
                print(f"Error loading image {path}: {str(e)}")
                continue
                
        return images
    
    def extract_text_with_ocr(self, image: Image.Image) -> str:
        """Extract text from image using OCR"""
        if not OCR_AVAILABLE:
            return "OCR not available - install pytesseract and opencv-python"
        
        try:
            # Convert PIL Image to OpenCV format
            img_array = np.array(image)
            
            # Preprocessing for better OCR
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array
            
            # Apply thresholding
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Extract text
            text = pytesseract.image_to_string(thresh)
            return text
            
        except Exception as e:
            return f"OCR Error: {str(e)}"
    
    def parse_financial_metrics(self, text: str) -> List[FinancialMetric]:
        """Parse financial metrics from extracted text"""
        metrics = []
        
        # Common patterns for financial data
        patterns = {
            'net_profit': r'net profit[:\s]*\$?([\d,]+\.?\d*)\s*(million|billion|thousand)?',
            'revenue': r'revenue[:\s]*\$?([\d,]+\.?\d*)\s*(million|billion|thousand)?',
            'eps': r'eps?[:\s]*\$?([\d,]+\.?\d*)',
            'roe': r'roe[:\s]*([\d,]+\.?\d*)%?',
            'assets': r'total assets[:\s]*\$?([\d,]+\.?\d*)\s*(million|billion|thousand)?',
            'liabilities': r'total liabilities[:\s]*\$?([\d,]+\.?\d*)\s*(million|billion|thousand)?',
            'equity': r'total equity[:\s]*\$?([\d,]+\.?\d*)\s*(million|billion|thousand)?',
            'ratio': r'([\d,]+\.?\d*)%?\s*(ratio|margin)'
        }
        
        for metric_type, pattern in patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    value = match[0]
                    unit = match[1] if len(match) > 1 else ''
                else:
                    value = match
                    unit = ''
                
                try:
                    numeric_value = float(value.replace(',', ''))
                    metrics.append(FinancialMetric(
                        name=metric_type.replace('_', ' ').title(),
                        value=numeric_value,
                        unit=unit,
                        period="current"  # Would need more sophisticated parsing for periods
                    ))
                except ValueError:
                    continue
        
        return metrics
    
    def analyze_chart(self, image: Image.Image) -> ChartData:
        """Analyze charts and graphs in the image"""
        if not CHART_ANALYSIS_AVAILABLE:
            return ChartData(
                chart_type="unknown",
                title="Chart analysis not available",
                x_axis_label="",
                y_axis_label="",
                data_points=[],
                trend="unknown",
                insights=["Install matplotlib for chart analysis"]
            )
        
        try:
            # Basic chart type detection based on image characteristics
            img_array = np.array(image)
            
            # Simple heuristic for chart type detection
            if self._is_bar_chart(img_array):
                chart_type = "bar_chart"
            elif self._is_line_chart(img_array):
                chart_type = "line_chart"
            elif self._is_pie_chart(img_array):
                chart_type = "pie_chart"
            else:
                chart_type = "unknown"
            
            # Extract text for labels and title
            text = self.extract_text_with_ocr(image)
            title = self._extract_title(text)
            x_axis_label, y_axis_label = self._extract_axis_labels(text)
            
            # Generate insights based on chart type and text
            insights = self._generate_chart_insights(chart_type, text)
            
            return ChartData(
                chart_type=chart_type,
                title=title,
                x_axis_label=x_axis_label,
                y_axis_label=y_axis_label,
                data_points=[],  # Would need more sophisticated parsing
                trend=self._detect_trend(text),
                insights=insights
            )
            
        except Exception as e:
            return ChartData(
                chart_type="error",
                title=f"Chart analysis failed: {str(e)}",
                x_axis_label="",
                y_axis_label="",
                data_points=[],
                trend="unknown",
                insights=["Error analyzing chart"]
            )
    
    def _is_bar_chart(self, img_array: np.ndarray) -> bool:
        """Simple heuristic to detect bar charts"""
        # Look for vertical rectangular shapes
        return "bar" in self.extract_text_with_ocr(Image.fromarray(img_array)).lower()
    
    def _is_line_chart(self, img_array: np.ndarray) -> bool:
        """Simple heuristic to detect line charts"""
        return "line" in self.extract_text_with_ocr(Image.fromarray(img_array)).lower()
    
    def _is_pie_chart(self, img_array: np.ndarray) -> bool:
        """Simple heuristic to detect pie charts"""
        return "pie" in self.extract_text_with_ocr(Image.fromarray(img_array)).lower()
    
    def _extract_title(self, text: str) -> str:
        """Extract chart title from text"""
        lines = text.split('\n')
        for line in lines[:3]:  # Usually in first few lines
            if any(keyword in line.lower() for keyword in ['chart', 'graph', 'figure']):
                return line.strip()
        return "Untitled Chart"
    
    def _extract_axis_labels(self, text: str) -> Tuple[str, str]:
        """Extract x and y axis labels"""
        lines = text.split('\n')
        x_label, y_label = "", ""
        
        for line in lines:
            if 'axis' in line.lower() or any(keyword in line.lower() for keyword in ['time', 'year', 'quarter', 'month']):
                x_label = line.strip()
            elif '%' in line or 'ratio' in line.lower() or 'value' in line.lower():
                y_label = line.strip()
        
        return x_label, y_label
    
    def _generate_chart_insights(self, chart_type: str, text: str) -> List[str]:
        """Generate insights based on chart analysis"""
        insights = []
        
        # Look for trend indicators
        trend_words = ['increase', 'decrease', 'growth', 'decline', 'up', 'down', 'rise', 'fall']
        found_trends = [word for word in trend_words if word in text.lower()]
        
        if found_trends:
            insights.append(f"Chart shows {' and '.join(found_trends[:2])} patterns")
        
        # Look for percentage changes
        percentages = re.findall(r'(\d+\.?\d*)%', text)
        if percentages:
            insights.append(f"Key percentage values: {', '.join(percentages[:3])}%")
        
        # Chart type specific insights
        if chart_type == "bar_chart":
            insights.append("Bar chart suitable for comparing discrete categories")
        elif chart_type == "line_chart":
            insights.append("Line chart ideal for showing trends over time")
        elif chart_type == "pie_chart":
            insights.append("Pie chart shows proportional distribution")
        
        return insights
    
    def _detect_trend(self, text: str) -> str:
        """Detect overall trend from text"""
        positive_words = ['increase', 'growth', 'rise', 'up', 'improve', 'gain']
        negative_words = ['decrease', 'decline', 'fall', 'down', 'drop', 'loss']
        
        pos_count = sum(1 for word in positive_words if word in text.lower())
        neg_count = sum(1 for word in negative_words if word in text.lower())
        
        if pos_count > neg_count:
            return "upward"
        elif neg_count > pos_count:
            return "downward"
        else:
            return "stable"
    
    def process_financial_document(self, image_paths: List[str]) -> Dict[str, Any]:
        """Main method to process financial document images"""
        results = {
            'images_processed': 0,
            'extracted_metrics': [],
            'chart_analyses': [],
            'raw_texts': [],
            'errors': []
        }
        
        images = self.load_images_from_paths(image_paths)
        
        for i, image in enumerate(images):
            try:
                # Extract text using OCR
                text = self.extract_text_with_ocr(image)
                results['raw_texts'].append({
                    'image_index': i,
                    'text': text
                })
                
                # Parse financial metrics
                metrics = self.parse_financial_metrics(text)
                results['extracted_metrics'].extend(metrics)
                
                # Analyze charts
                chart_analysis = self.analyze_chart(image)
                results['chart_analyses'].append(chart_analysis)
                
                results['images_processed'] += 1
                
            except Exception as e:
                results['errors'].append({
                    'image_index': i,
                    'error': str(e)
                })
        
        return results
