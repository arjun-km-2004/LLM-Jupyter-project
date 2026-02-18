"""
LLM Integration for Financial Analysis
Handles AI-powered analysis of extracted financial data
"""

import os
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import re

# LLM Libraries
try:
    import openai
    from anthropic import Anthropic
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    print("Warning: LLM libraries not available. Install with: pip install openai anthropic")

from financial_image_processor import FinancialMetric, ChartData

@dataclass
class AnalysisPrompt:
    """Data class for analysis prompts"""
    role: str
    context: str
    task: str
    output_format: str

class FinancialAnalyzer:
    """Main class for AI-powered financial analysis"""
    
    def __init__(self, api_provider: str = "openai", api_key: Optional[str] = None):
        self.api_provider = api_provider
        self.api_key = api_key or os.getenv(f"{api_provider.upper()}_API_KEY")
        self.client = None
        self._initialize_client()
        
        # Predefined prompts for different analysis types
        self.prompts = {
            'executive_summary': AnalysisPrompt(
                role="Senior Financial Analyst",
                context="You are analyzing financial documents for executive decision-making.",
                task="Create a concise executive summary highlighting key financial metrics, trends, and actionable insights.",
                output_format="structured_summary"
            ),
            'detailed_analysis': AnalysisPrompt(
                role="Equity Research Analyst", 
                context="You are conducting detailed financial analysis for investment recommendations.",
                task="Provide comprehensive analysis of financial performance, including strengths, weaknesses, opportunities, and threats.",
                output_format="detailed_report"
            ),
            'risk_assessment': AnalysisPrompt(
                role="Risk Manager",
                context="You are assessing financial risks and vulnerabilities.",
                task="Identify and evaluate key financial risks, including liquidity, credit, market, and operational risks.",
                output_format="risk_report"
            ),
            'trend_analysis': AnalysisPrompt(
                role="Quantitative Analyst",
                context="You are analyzing financial trends and patterns.",
                task="Analyze trends across multiple periods and provide forward-looking insights.",
                output_format="trend_report"
            )
        }
    
    def _initialize_client(self):
        """Initialize the LLM client based on provider"""
        if not LLM_AVAILABLE or not self.api_key:
            print("LLM not available - will use rule-based analysis")
            return
        
        try:
            if self.api_provider == "openai":
                self.client = openai.OpenAI(api_key=self.api_key)
            elif self.api_provider == "anthropic":
                self.client = Anthropic(api_key=self.api_key)
            else:
                raise ValueError(f"Unsupported provider: {self.api_provider}")
        except Exception as e:
            print(f"Failed to initialize {self.api_provider} client: {str(e)}")
    
    def create_analysis_prompt(self, 
                             metrics: List[FinancialMetric], 
                             charts: List[ChartData], 
                             raw_texts: List[str],
                             analysis_type: str = "executive_summary") -> str:
        """Create a comprehensive analysis prompt"""
        
        prompt_template = self.prompts.get(analysis_type, self.prompts['executive_summary'])
        
        # Format metrics for prompt
        metrics_text = "\n".join([
            f"- {metric.name}: {metric.value} {metric.unit} ({metric.period})"
            for metric in metrics
        ])
        
        # Format chart analyses
        charts_text = "\n".join([
            f"- Chart: {chart.title} (Type: {chart.chart_type})\n"
            f"  Trend: {chart.trend}\n"
            f"  Insights: {', '.join(chart.insights[:3])}"
            for chart in charts
        ])
        
        # Combine raw texts (limit length)
        combined_text = "\n\n".join([text[:1000] + "..." if len(text) > 1000 else text for text in raw_texts])
        
        full_prompt = f"""
{prompt_template.role} Context: {prompt_template.context}

Task: {prompt_template.task}

Financial Data:
{metrics_text}

Chart Analysis:
{charts_text}

Document Text:
{combined_text}

Please provide a comprehensive analysis following this structure:
1. Key Financial Metrics Summary
2. Income and Expense Analysis  
3. Balance Sheet Highlights
4. Credit Quality Assessment
5. Strategic and Operational Updates
6. Market Conditions and Outlook
7. Investment Recommendation

Format the output as a professional financial report with clear headings and bullet points.
"""
        
        return full_prompt
    
    def call_llm(self, prompt: str, max_tokens: int = 2000) -> str:
        """Call the LLM API for analysis"""
        if not self.client:
            return self._rule_based_analysis(prompt)
        
        try:
            if self.api_provider == "openai":
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=0.3
                )
                return response.choices[0].message.content
                
            elif self.api_provider == "anthropic":
                response = self.client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=max_tokens,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text
                
        except Exception as e:
            print(f"LLM API call failed: {str(e)}")
            return self._rule_based_analysis(prompt)
    
    def _rule_based_analysis(self, prompt: str) -> str:
        """Fallback rule-based analysis when LLM is not available"""
        
        # Extract key information from prompt using regex
        metrics = self._extract_metrics_from_prompt(prompt)
        trends = self._extract_trends_from_prompt(prompt)
        
        analysis = f"""
# Financial Analysis Summary

## Key Financial Metrics
{self._format_metrics_summary(metrics)}

## Trend Analysis
{self._format_trend_analysis(trends)}

## Investment Recommendation
Based on the available data, this analysis suggests:
- Monitor key financial metrics closely
- Review trend patterns for investment decisions
- Consider additional data sources for comprehensive analysis

*Note: This is a rule-based analysis. For more sophisticated insights, please configure LLM API access.*
"""
        
        return analysis
    
    def _extract_metrics_from_prompt(self, prompt: str) -> List[Dict[str, Any]]:
        """Extract financial metrics from prompt text"""
        metrics = []
        
        # Look for common financial metric patterns
        patterns = {
            'net_profit': r'net profit[:\s]*\$?([\d,]+\.?\d*)',
            'revenue': r'revenue[:\s]*\$?([\d,]+\.?\d*)',
            'eps': r'eps?[:\s]*\$?([\d,]+\.?\d*)',
            'roe': r'roe[:\s]*([\d,]+\.?\d*)%?',
            'assets': r'total assets[:\s]*\$?([\d,]+\.?\d*)',
            'liabilities': r'total liabilities[:\s]*\$?([\d,]+\.?\d*)',
            'equity': r'total equity[:\s]*\$?([\d,]+\.?\d*)'
        }
        
        for metric_type, pattern in patterns.items():
            matches = re.findall(pattern, prompt, re.IGNORECASE)
            for match in matches:
                try:
                    value = float(match.replace(',', ''))
                    metrics.append({
                        'type': metric_type,
                        'value': value,
                        'unit': 'currency' if metric_type in ['net_profit', 'revenue', 'assets', 'liabilities', 'equity'] else 'percentage' if metric_type == 'roe' else 'units'
                    })
                except ValueError:
                    continue
        
        return metrics
    
    def _extract_trends_from_prompt(self, prompt: str) -> List[str]:
        """Extract trend information from prompt"""
        trend_words = ['increase', 'decrease', 'growth', 'decline', 'up', 'down', 'rise', 'fall', 'improve', 'worsen']
        found_trends = []
        
        for word in trend_words:
            if word in prompt.lower():
                found_trends.append(word)
        
        return found_trends
    
    def _format_metrics_summary(self, metrics: List[Dict[str, Any]]) -> str:
        """Format metrics into readable summary"""
        if not metrics:
            return "No specific metrics identified in the document."
        
        summary = []
        for metric in metrics[:5]:  # Limit to top 5 metrics
            metric_name = metric['type'].replace('_', ' ').title()
            value_str = f"${metric['value']:,.2f}" if metric['unit'] == 'currency' else f"{metric['value']:.2f}%"
            summary.append(f"- {metric_name}: {value_str}")
        
        return "\n".join(summary)
    
    def _format_trend_analysis(self, trends: List[str]) -> str:
        """Format trend analysis"""
        if not trends:
            return "No clear trend patterns identified."
        
        trend_summary = "Identified trends: " + ", ".join(trends)
        
        # Add interpretation
        if any(word in trends for word in ['increase', 'growth', 'rise', 'improve']):
            trend_summary += "\nOverall positive momentum detected."
        elif any(word in trends for word in ['decrease', 'decline', 'fall', 'worsen']):
            trend_summary += "\nNegative trends require attention."
        else:
            trend_summary += "\nMixed or stable trends observed."
        
        return trend_summary
    
    def analyze_financial_data(self, 
                              metrics: List[FinancialMetric], 
                              charts: List[ChartData], 
                              raw_texts: List[str],
                              analysis_type: str = "executive_summary") -> Dict[str, Any]:
        """Main method to analyze financial data"""
        
        # Create analysis prompt
        prompt = self.create_analysis_prompt(metrics, charts, raw_texts, analysis_type)
        
        # Get analysis from LLM
        analysis_text = self.call_llm(prompt)
        
        # Structure the results
        result = {
            'analysis_type': analysis_type,
            'raw_analysis': analysis_text,
            'metrics_count': len(metrics),
            'charts_count': len(charts),
            'text_sources': len(raw_texts),
            'llm_used': self.client is not None,
            'structured_summary': self._structure_analysis(analysis_text)
        }
        
        return result
    
    def _structure_analysis(self, analysis_text: str) -> Dict[str, str]:
        """Structure the analysis text into sections"""
        sections = {}
        
        # Common section headers
        section_patterns = {
            'key_financial_metrics': r'(?i)(key financial metrics|financial metrics|metrics summary)',
            'income_expenses': r'(?i)(income and expenses|income statement|revenue)',
            'balance_sheet': r'(?i)(balance sheet|assets and liabilities)',
            'credit_quality': r'(?i)(credit quality|risk assessment|credit risk)',
            'strategic_updates': r'(?i)(strategic|operational|business updates)',
            'market_outlook': r'(?i)(market conditions|outlook|future)',
            'recommendation': r'(?i)(recommendation|conclusion|investment advice)'
        }
        
        # Split analysis into sections
        lines = analysis_text.split('\n')
        current_section = 'introduction'
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check for section headers
            section_found = False
            for section_key, pattern in section_patterns.items():
                if re.search(pattern, line):
                    # Save previous section
                    if current_content:
                        sections[current_section] = '\n'.join(current_content).strip()
                    
                    # Start new section
                    current_section = section_key
                    current_content = [line]
                    section_found = True
                    break
            
            if not section_found:
                current_content.append(line)
        
        # Save last section
        if current_content:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return sections
    
    def generate_investment_recommendation(self, analysis_result: Dict[str, Any]) -> str:
        """Generate investment recommendation based on analysis"""
        
        if not analysis_result.get('llm_used'):
            return "Limited data available for investment recommendation. Configure LLM access for detailed recommendations."
        
        structured_summary = analysis_result.get('structured_summary', {})
        
        # Extract key indicators
        key_metrics = structured_summary.get('key_financial_metrics', '')
        market_outlook = structured_summary.get('market_outlook', '')
        
        # Simple recommendation logic (would be more sophisticated with LLM)
        recommendation_prompt = f"""
Based on the following financial analysis, provide a clear investment recommendation (OVERWEIGHT, NEUTRAL, or UNDERWEIGHT) with brief justification:

Key Metrics:
{key_metrics}

Market Outlook:
{market_outlook}

Format: RECOMMENDATION: [OVERWEIGHT/NEUTRAL/UNDERWEIGHT] - [Brief justification]
"""
        
        return self.call_llm(recommendation_prompt, max_tokens=200)
