"""
Plan export functionality for different formats
"""

import json
import csv
import io
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from fastapi.responses import StreamingResponse

logger = logging.getLogger(__name__)

class PlanExporter:
    """
    Export plans to various formats
    """
    
    def __init__(self):
        """Initialize the plan exporter"""
        self.logger = logging.getLogger(__name__)
    
    def export_to_json(self, plans: List[Dict[str, Any]], pretty: bool = True) -> str:
        """
        Export plans to JSON format
        
        Args:
            plans: List of plan dictionaries
            pretty: Whether to format JSON with indentation
            
        Returns:
            str: JSON string representation
        """
        try:
            export_data = {
                "export_info": {
                    "timestamp": datetime.now().isoformat(),
                    "format": "json",
                    "total_plans": len(plans),
                    "exported_by": "AI Task Planning Agent"
                },
                "plans": plans
            }
            
            if pretty:
                return json.dumps(export_data, indent=2, default=str)
            else:
                return json.dumps(export_data, default=str)
                
        except Exception as e:
            self.logger.error(f"Error exporting to JSON: {e}")
            raise
    
    def export_to_csv(self, plans: List[Dict[str, Any]]) -> str:
        """
        Export plans to CSV format
        
        Args:
            plans: List of plan dictionaries
            
        Returns:
            str: CSV string representation
        """
        try:
            if not plans:
                return "No plans to export"
            
            output = io.StringIO()
            
            # Define CSV headers
            headers = [
                'id', 'goal', 'created_at', 'updated_at', 'total_steps', 
                'estimated_duration', 'has_weather_info', 'has_web_research',
                'research_topics', 'steps_summary'
            ]
            
            writer = csv.DictWriter(output, fieldnames=headers)
            writer.writeheader()
            
            for plan in plans:
                # Extract plan data
                plan_data = plan.get('plan_data', {})
                metadata = plan_data.get('metadata', {})
                steps = plan_data.get('steps', [])
                
                # Create steps summary
                steps_summary = '; '.join([
                    f"Step {step.get('step_number', '?')}: {step.get('title', 'Untitled')}"
                    for step in steps
                ])
                
                # Research topics
                research_topics = ', '.join(metadata.get('research_topics', []))
                
                row = {
                    'id': plan.get('id', ''),
                    'goal': plan.get('goal', ''),
                    'created_at': plan.get('created_at', ''),
                    'updated_at': plan.get('updated_at', ''),
                    'total_steps': plan_data.get('total_steps', 0),
                    'estimated_duration': plan_data.get('estimated_total_duration', ''),
                    'has_weather_info': metadata.get('has_weather_info', False),
                    'has_web_research': metadata.get('has_web_research', False),
                    'research_topics': research_topics,
                    'steps_summary': steps_summary
                }
                
                writer.writerow(row)
            
            return output.getvalue()
            
        except Exception as e:
            self.logger.error(f"Error exporting to CSV: {e}")
            raise
    
    def export_to_markdown(self, plans: List[Dict[str, Any]]) -> str:
        """
        Export plans to Markdown format
        
        Args:
            plans: List of plan dictionaries
            
        Returns:
            str: Markdown string representation
        """
        try:
            if not plans:
                return "# No plans to export\n"
            
            md_content = []
            md_content.append("# AI Task Planning Agent - Exported Plans\n")
            md_content.append(f"**Export Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            md_content.append(f"**Total Plans:** {len(plans)}\n")
            md_content.append("---\n")
            
            for i, plan in enumerate(plans, 1):
                plan_data = plan.get('plan_data', {})
                metadata = plan_data.get('metadata', {})
                steps = plan_data.get('steps', [])
                
                # Plan header
                md_content.append(f"## Plan {i}: {plan.get('goal', 'Untitled Plan')}\n")
                
                # Plan metadata
                md_content.append("### Plan Information\n")
                md_content.append(f"- **ID:** {plan.get('id', 'N/A')}\n")
                md_content.append(f"- **Created:** {plan.get('created_at', 'N/A')}\n")
                md_content.append(f"- **Total Steps:** {plan_data.get('total_steps', 0)}\n")
                md_content.append(f"- **Estimated Duration:** {plan_data.get('estimated_total_duration', 'Unknown')}\n")
                md_content.append(f"- **Has Weather Info:** {'Yes' if metadata.get('has_weather_info') else 'No'}\n")
                md_content.append(f"- **Has Web Research:** {'Yes' if metadata.get('has_web_research') else 'No'}\n")
                
                # Research topics
                research_topics = metadata.get('research_topics', [])
                if research_topics:
                    md_content.append(f"- **Research Topics:** {', '.join(research_topics)}\n")
                
                md_content.append("\n")
                
                # Steps
                if steps:
                    md_content.append("### Plan Steps\n")
                    for step in steps:
                        step_num = step.get('step_number', '?')
                        title = step.get('title', 'Untitled Step')
                        description = step.get('description', 'No description')
                        duration = step.get('estimated_duration', 'Unknown')
                        
                        md_content.append(f"#### Step {step_num}: {title}\n")
                        md_content.append(f"**Description:** {description}\n")
                        md_content.append(f"**Estimated Duration:** {duration}\n")
                        
                        # Web research
                        web_research = step.get('web_research', [])
                        if web_research:
                            md_content.append("**Research Results:**\n")
                            for research in web_research[:3]:  # Limit to top 3
                                title_res = research.get('title', 'No title')
                                snippet = research.get('snippet', 'No description')
                                md_content.append(f"- {title_res}: {snippet}\n")
                        
                        # Weather info
                        weather_info = step.get('weather_info')
                        if weather_info:
                            location = weather_info.get('location', 'Unknown')
                            md_content.append(f"**Weather for {location}:**\n")
                            forecasts = weather_info.get('daily_forecasts', [])
                            if forecasts:
                                for forecast in forecasts[:3]:  # First 3 days
                                    date = forecast.get('date', 'Unknown date')
                                    desc = forecast.get('description', 'No description')
                                    temp_range = f"{forecast.get('min_temp', '?')}-{forecast.get('max_temp', '?')}°C"
                                    md_content.append(f"- {date}: {desc}, {temp_range}\n")
                        
                        md_content.append("\n")
                
                md_content.append("---\n")
            
            return ''.join(md_content)
            
        except Exception as e:
            self.logger.error(f"Error exporting to Markdown: {e}")
            raise
    
    def create_streaming_response(self, content: str, filename: str, content_type: str) -> StreamingResponse:
        """
        Create a streaming response for file download
        
        Args:
            content: File content as string
            filename: Name of the file to download
            content_type: MIME type of the content
            
        Returns:
            StreamingResponse: FastAPI streaming response
        """
        def generate():
            yield content.encode('utf-8')
        
        headers = {
            'Content-Disposition': f'attachment; filename="{filename}"'
        }
        
        return StreamingResponse(
            generate(),
            media_type=content_type,
            headers=headers
        )
    
    def get_export_filename(self, format_type: str, plan_count: int) -> str:
        """
        Generate appropriate filename for export
        
        Args:
            format_type: Export format (json, csv, markdown)
            plan_count: Number of plans being exported
            
        Returns:
            str: Generated filename
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if plan_count == 1:
            base_name = f"plan_{timestamp}"
        else:
            base_name = f"plans_{plan_count}_{timestamp}"
        
        extensions = {
            'json': '.json',
            'csv': '.csv',
            'markdown': '.md'
        }
        
        return f"{base_name}{extensions.get(format_type, '.txt')}"
    
    def get_content_type(self, format_type: str) -> str:
        """
        Get MIME content type for format
        
        Args:
            format_type: Export format
            
        Returns:
            str: MIME content type
        """
        content_types = {
            'json': 'application/json',
            'csv': 'text/csv',
            'markdown': 'text/markdown'
        }
        
        return content_types.get(format_type, 'text/plain')

# Global exporter instance
plan_exporter = PlanExporter()