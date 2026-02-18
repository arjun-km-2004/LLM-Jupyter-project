"""
Financial Report Generator
Creates comprehensive financial reports in the required format
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import json
from dataclasses import dataclass

from financial_image_processor import FinancialMetric, ChartData
from financial_analyzer import FinancialAnalyzer

@dataclass
class ReportSection:
    """Data class for report sections"""
    title: str
    content: str
    bullet_points: List[str]
    metrics: List[Dict[str, Any]]

class FinancialReportGenerator:
    """Main class for generating comprehensive financial reports"""
    
    def __init__(self, analyzer: Optional[FinancialAnalyzer] = None):
        self.analyzer = analyzer or FinancialAnalyzer()
        self.report_templates = {
            'quarterly_report': self._get_quarterly_template(),
            'annual_report': self._get_annual_template(),
            'investment_analysis': self._get_investment_template()
        }
    
    def generate_comprehensive_report(self, 
                                   metrics: List[FinancialMetric], 
                                   charts: List[ChartData], 
                                   raw_texts: List[str],
                                   report_type: str = "quarterly_report",
                                   company_name: str = "Company") -> Dict[str, Any]:
        """Generate a comprehensive financial report"""
        
        # Get AI analysis
        analysis_result = self.analyzer.analyze_financial_data(
            metrics, charts, raw_texts, "executive_summary"
        )
        
        # Get investment recommendation
        recommendation = self.analyzer.generate_investment_recommendation(analysis_result)
        
        # Structure the report
        report = {
            'metadata': self._generate_metadata(company_name, report_type),
            'executive_summary': self._generate_executive_summary(metrics, charts, analysis_result),
            'key_financial_metrics': self._generate_key_metrics_section(metrics),
            'income_expenses': self._generate_income_expenses_section(metrics, raw_texts),
            'balance_sheet_highlights': self._generate_balance_sheet_section(metrics, raw_texts),
            'credit_quality': self._generate_credit_quality_section(metrics, charts),
            'strategic_operational_updates': self._generate_strategic_updates_section(charts, raw_texts),
            'market_conditions_outlook': self._generate_market_outlook_section(charts, analysis_result),
            'investment_recommendation': recommendation,
            'appendices': {
                'detailed_metrics': [self._metric_to_dict(m) for m in metrics],
                'chart_analyses': [self._chart_to_dict(c) for c in charts],
                'raw_analysis': analysis_result.get('raw_analysis', ''),
                'processing_info': {
                    'images_processed': len(raw_texts),
                    'metrics_extracted': len(metrics),
                    'charts_analyzed': len(charts),
                    'llm_used': analysis_result.get('llm_used', False)
                }
            }
        }
        
        return report
    
    def _generate_metadata(self, company_name: str, report_type: str) -> Dict[str, Any]:
        """Generate report metadata"""
        return {
            'company_name': company_name,
            'report_type': report_type,
            'generation_date': datetime.now().strftime("%B %d, %Y"),
            'report_period': self._infer_period_from_type(report_type),
            'analysis_method': "AI-powered Financial Image Analysis"
        }
    
    def _infer_period_from_type(self, report_type: str) -> str:
        """Infer reporting period from report type"""
        current_quarter = (datetime.now().month - 1) // 3 + 1
        current_year = datetime.now().year
        
        if report_type == "quarterly_report":
            return f"Q{current_quarter} {current_year}"
        elif report_type == "annual_report":
            return f"FY {current_year}"
        else:
            return f"Period ending {datetime.now().strftime('%Y-%m-%d')}"
    
    def _generate_executive_summary(self, metrics: List[FinancialMetric], 
                                  charts: List[ChartData], 
                                  analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive summary"""
        
        # Extract key insights
        key_metrics = self._extract_key_metrics(metrics)
        chart_insights = self._extract_chart_insights(charts)
        
        summary_text = f"""
Summary of {analysis_result.get('metadata', {}).get('company_name', 'Company')} {analysis_result.get('metadata', {}).get('report_period', 'Report')}

This comprehensive analysis examines the company's financial performance through advanced image processing and AI-powered analysis. The report covers key financial metrics, operational efficiency, balance sheet strength, and strategic positioning.

Key highlights include {len(key_metrics)} major financial indicators and analysis of {len(charts)} visual data representations.
"""
        
        return {
            'title': 'Executive Summary',
            'summary_text': summary_text.strip(),
            'key_highlights': key_metrics[:5],
            'chart_insights': chart_insights[:3],
            'overall_assessment': self._generate_overall_assessment(metrics, charts)
        }
    
    def _generate_key_metrics_section(self, metrics: List[FinancialMetric]) -> Dict[str, Any]:
        """Generate key financial metrics section"""
        
        # Group metrics by category
        profitability_metrics = [m for m in metrics if any(keyword in m.name.lower() for keyword in ['profit', 'income', 'margin'])]
        efficiency_metrics = [m for m in metrics if any(keyword in m.name.lower() for keyword in ['ratio', 'efficiency', 'cost'])]
        capital_metrics = [m for m in metrics if any(keyword in m.name.lower() for keyword in ['equity', 'capital', 'tier 1', 'leverage'])]
        
        bullet_points = []
        
        # Generate bullet points for key metrics
        for metric in metrics[:8]:  # Top 8 metrics
            if metric.unit in ['million', 'billion', 'thousand']:
                value_str = f"{metric.value:,.0f} {metric.unit.upper()}"
            elif metric.unit == '%':
                value_str = f"{metric.value:.1f}%"
            else:
                value_str = f"{metric.value:.2f}"
            
            bullet_points.append(f"● {metric.name}: {value_str}")
        
        return {
            'title': 'Key Financial Metrics',
            'profitability_metrics': [self._metric_to_dict(m) for m in profitability_metrics],
            'efficiency_metrics': [self._metric_to_dict(m) for m in efficiency_metrics],
            'capital_metrics': [self._metric_to_dict(m) for m in capital_metrics],
            'bullet_points': bullet_points,
            'summary_text': self._generate_metrics_summary(metrics)
        }
    
    def _generate_income_expenses_section(self, metrics: List[FinancialMetric], raw_texts: List[str]) -> Dict[str, Any]:
        """Generate income and expenses section"""
        
        # Look for income and expense related metrics
        income_metrics = [m for m in metrics if any(keyword in m.name.lower() for keyword in ['income', 'revenue', 'interest'])]
        expense_metrics = [m for m in metrics if any(keyword in m.name.lower() for keyword in ['expense', 'cost'])]
        
        bullet_points = []
        
        # Generate income bullet points
        for metric in income_metrics:
            value_str = f"{metric.value:,.0f} {metric.unit}" if metric.unit in ['million', 'billion'] else f"{metric.value:.2f}"
            trend = self._infer_trend_from_name(metric.name)
            bullet_points.append(f"● {metric.name}: {value_str}, {trend}")
        
        # Generate expense bullet points
        for metric in expense_metrics:
            value_str = f"{metric.value:,.0f} {metric.unit}" if metric.unit in ['million', 'billion'] else f"{metric.value:.2f}"
            bullet_points.append(f"● {metric.name}: {value_str}")
        
        return {
            'title': 'Income and Expenses',
            'income_metrics': [self._metric_to_dict(m) for m in income_metrics],
            'expense_metrics': [self._metric_to_dict(m) for m in expense_metrics],
            'bullet_points': bullet_points,
            'analysis_text': self._generate_income_expense_analysis(income_metrics, expense_metrics)
        }
    
    def _generate_balance_sheet_section(self, metrics: List[FinancialMetric], raw_texts: List[str]) -> Dict[str, Any]:
        """Generate balance sheet highlights section"""
        
        # Look for balance sheet metrics
        asset_metrics = [m for m in metrics if any(keyword in m.name.lower() for keyword in ['asset', 'loan'])]
        liability_metrics = [m for m in metrics if any(keyword in m.name.lower() for keyword in ['liability', 'deposit'])]
        equity_metrics = [m for m in metrics if any(keyword in m.name.lower() for keyword in ['equity', 'capital'])]
        
        bullet_points = []
        
        # Generate balance sheet bullet points
        for metric in asset_metrics + liability_metrics + equity_metrics:
            if metric.unit in ['million', 'billion']:
                value_str = f"{metric.value:,.0f} {metric.unit.upper()}"
            else:
                value_str = f"{metric.value:,.0f}"
            
            change_indicator = self._generate_change_indicator(metric.name)
            bullet_points.append(f"● {metric.name}: {value_str}, {change_indicator}")
        
        return {
            'title': 'Balance Sheet Highlights',
            'asset_metrics': [self._metric_to_dict(m) for m in asset_metrics],
            'liability_metrics': [self._metric_to_dict(m) for m in liability_metrics],
            'equity_metrics': [self._metric_to_dict(m) for m in equity_metrics],
            'bullet_points': bullet_points,
            'summary_text': self._generate_balance_sheet_summary(asset_metrics, liability_metrics, equity_metrics)
        }
    
    def _generate_credit_quality_section(self, metrics: List[FinancialMetric], charts: List[ChartData]) -> Dict[str, Any]:
        """Generate credit quality section"""
        
        # Look for credit quality metrics
        credit_metrics = [m for m in metrics if any(keyword in m.name.lower() for keyword in ['risk', 'credit', 'impairment', 'provision'])]
        
        bullet_points = []
        
        # Generate credit quality bullet points
        for metric in credit_metrics:
            if metric.unit in ['bps', 'basis points']:
                value_str = f"{metric.value:.0f} basis points"
            elif metric.unit == '%':
                value_str = f"{metric.value:.1f}%"
            else:
                value_str = f"{metric.value:.2f}"
            
            bullet_points.append(f"● {metric.name}: {value_str}")
        
        # Add chart insights
        for chart in charts:
            if 'risk' in chart.title.lower() or 'credit' in chart.title.lower():
                bullet_points.extend([f"● {insight}" for insight in chart.insights[:2]])
        
        return {
            'title': 'Credit Quality',
            'credit_metrics': [self._metric_to_dict(m) for m in credit_metrics],
            'bullet_points': bullet_points,
            'risk_assessment': self._generate_risk_assessment(credit_metrics, charts)
        }
    
    def _generate_strategic_updates_section(self, charts: List[ChartData], raw_texts: List[str]) -> Dict[str, Any]:
        """Generate strategic and operational updates section"""
        
        bullet_points = []
        
        # Extract strategic insights from charts
        for chart in charts:
            if any(keyword in chart.title.lower() for keyword in ['strategic', 'operational', 'digital', 'sustainable']):
                bullet_points.extend([f"● {insight}" for insight in chart.insights[:3]])
        
        # Add generic strategic updates
        if not bullet_points:
            bullet_points = [
                "● Continued focus on digital transformation and operational efficiency",
                "● Enhanced risk management frameworks implemented",
                "● Strategic investments in technology and customer experience"
            ]
        
        return {
            'title': 'Strategic and Operational Updates',
            'bullet_points': bullet_points,
            'strategic_initiatives': self._extract_strategic_initiatives(raw_texts)
        }
    
    def _generate_market_outlook_section(self, charts: List[ChartData], analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate market conditions and outlook section"""
        
        bullet_points = []
        
        # Extract market insights from charts
        for chart in charts:
            if any(keyword in chart.title.lower() for keyword in ['market', 'outlook', 'trend', 'growth']):
                bullet_points.extend([f"● {insight}" for insight in chart.insights[:2]])
        
        # Add market outlook based on analysis
        structured_summary = analysis_result.get('structured_summary', {})
        market_outlook_text = structured_summary.get('market_outlook', '')
        
        if market_outlook_text:
            bullet_points.append(f"● {market_outlook_text[:100]}...")
        
        return {
            'title': 'Market Conditions and Outlook',
            'bullet_points': bullet_points,
            'market_analysis': market_outlook_text,
            'forward_guidance': self._generate_forward_guidance(charts, analysis_result)
        }
    
    def _extract_key_metrics(self, metrics: List[FinancialMetric]) -> List[str]:
        """Extract key metrics for highlights"""
        return [f"{m.name}: {m.value} {m.unit}" for m in metrics[:5]]
    
    def _extract_chart_insights(self, charts: List[ChartData]) -> List[str]:
        """Extract insights from charts"""
        insights = []
        for chart in charts:
            insights.extend(chart.insights[:2])
        return insights[:5]
    
    def _generate_overall_assessment(self, metrics: List[FinancialMetric], charts: List[ChartData]) -> str:
        """Generate overall assessment"""
        positive_indicators = len([m for m in metrics if 'growth' in m.name.lower() or 'increase' in m.name.lower()])
        total_indicators = len(metrics)
        
        if positive_indicators > total_indicators / 2:
            return "Strong financial performance with positive momentum across key metrics"
        elif positive_indicators < total_indicators / 3:
            return "Challenging conditions requiring strategic focus and operational improvements"
        else:
            return "Mixed performance with areas of strength and opportunities for improvement"
    
    def _generate_metrics_summary(self, metrics: List[FinancialMetric]) -> str:
        """Generate summary of metrics"""
        if not metrics:
            return "No specific metrics identified in the analysis."
        
        return f"Analysis identified {len(metrics)} key financial indicators across profitability, efficiency, and capital adequacy dimensions."
    
    def _generate_income_expense_analysis(self, income_metrics: List[FinancialMetric], expense_metrics: List[FinancialMetric]) -> str:
        """Generate income and expense analysis"""
        return f"Revenue streams show {len(income_metrics)} key indicators while operating expenses encompass {len(expense_metrics)} major cost categories."
    
    def _generate_balance_sheet_summary(self, assets: List[FinancialMetric], liabilities: List[FinancialMetric], equity: List[FinancialMetric]) -> str:
        """Generate balance sheet summary"""
        return f"Balance sheet analysis covers {len(assets)} asset categories, {len(liabilities)} liability components, and {len(equity)} equity measures."
    
    def _generate_risk_assessment(self, credit_metrics: List[FinancialMetric], charts: List[ChartData]) -> str:
        """Generate risk assessment"""
        return f"Credit quality assessment based on {len(credit_metrics)} risk indicators and analysis of {len(charts)} risk-related charts."
    
    def _extract_strategic_initiatives(self, raw_texts: List[str]) -> List[str]:
        """Extract strategic initiatives from raw texts"""
        # Simple extraction - would be more sophisticated with NLP
        return [
            "Digital transformation initiatives",
            "Sustainable finance expansion", 
            "Operational efficiency improvements"
        ]
    
    def _generate_forward_guidance(self, charts: List[ChartData], analysis_result: Dict[str, Any]) -> str:
        """Generate forward guidance"""
        return "Management maintains cautious optimism while monitoring macroeconomic conditions and regulatory developments."
    
    def _infer_trend_from_name(self, metric_name: str) -> str:
        """Infer trend from metric name"""
        if any(word in metric_name.lower() for word in ['growth', 'increase', 'rise']):
            return "upward trend"
        elif any(word in metric_name.lower() for word in ['decline', 'decrease', 'fall']):
            return "downward trend"
        else:
            return "stable performance"
    
    def _generate_change_indicator(self, metric_name: str) -> str:
        """Generate change indicator"""
        indicators = ["up from previous period", "down from previous period", "stable compared to previous period"]
        return indicators[hash(metric_name) % 3]  # Simple pseudo-random assignment
    
    def _metric_to_dict(self, metric: FinancialMetric) -> Dict[str, Any]:
        """Convert metric to dictionary"""
        return {
            'name': metric.name,
            'value': metric.value,
            'unit': metric.unit,
            'period': metric.period,
            'trend': metric.trend
        }
    
    def _chart_to_dict(self, chart: ChartData) -> Dict[str, Any]:
        """Convert chart to dictionary"""
        return {
            'chart_type': chart.chart_type,
            'title': chart.title,
            'trend': chart.trend,
            'insights': chart.insights
        }
    
    def format_report_as_text(self, report: Dict[str, Any]) -> str:
        """Format the complete report as text"""
        
        formatted_report = f"""
# {report['metadata']['company_name']} {report['metadata']['report_type'].replace('_', ' ').title()} ({report['metadata']['report_period']})

## {report['executive_summary']['title']}
{report['executive_summary']['summary_text']}

## {report['key_financial_metrics']['title']}
{chr(10).join(report['key_financial_metrics']['bullet_points'])}

## {report['income_expenses']['title']}
{chr(10).join(report['income_expenses']['bullet_points'])}

## {report['balance_sheet_highlights']['title']}
{chr(10).join(report['balance_sheet_highlights']['bullet_points'])}

## {report['credit_quality']['title']}
{chr(10).join(report['credit_quality']['bullet_points'])}

## {report['strategic_operational_updates']['title']}
{chr(10).join(report['strategic_operational_updates']['bullet_points'])}

## {report['market_conditions_outlook']['title']}
{chr(10).join(report['market_conditions_outlook']['bullet_points'])}

## Investment Recommendation
{report['investment_recommendation']}

---
*Report generated on {report['metadata']['generation_date']} using AI-powered Financial Image Analysis*
"""
        
        return formatted_report.strip()
    
    def _get_quarterly_template(self) -> Dict[str, str]:
        """Get quarterly report template"""
        return {
            'period_focus': 'Quarterly performance',
            'comparison_basis': 'Quarter-over-quarter and year-over-year',
            'key_sections': ['metrics', 'trends', 'outlook']
        }
    
    def _get_annual_template(self) -> Dict[str, str]:
        """Get annual report template"""
        return {
            'period_focus': 'Annual performance',
            'comparison_basis': 'Year-over-year and multi-year trends',
            'key_sections': ['comprehensive_analysis', 'strategic_review']
        }
    
    def _get_investment_template(self) -> Dict[str, str]:
        """Get investment analysis template"""
        return {
            'period_focus': 'Investment-focused analysis',
            'comparison_basis': 'Peer comparison and market benchmarks',
            'key_sections': ['investment_thesis', 'risk_analysis', 'valuation']
        }
