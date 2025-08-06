#!/usr/bin/env python3
"""
Console Log Capture System
==========================

Captures detailed console logs during workflow execution and integrates them into output files.
This ensures all validation/rejection details are preserved in the txt files.
"""

import sys
import io
from typing import List, Dict, Any
from datetime import datetime

class ConsoleLogCapture:
    """Captures console output for integration into output files"""
    
    def __init__(self):
        self.captured_logs = []
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        
    def start_capture(self):
        """Start capturing console output"""
        self.log_buffer = io.StringIO()
        sys.stdout = self._create_tee_writer(sys.stdout, self.log_buffer)
        sys.stderr = self._create_tee_writer(sys.stderr, self.log_buffer)
        
    def stop_capture(self):
        """Stop capturing and return logs"""
        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr
        
        captured_content = self.log_buffer.getvalue()
        self.captured_logs.append({
            'timestamp': datetime.now(),
            'content': captured_content
        })
        
        return captured_content
    
    def _create_tee_writer(self, original_stream, capture_stream):
        """Create a writer that outputs to both original and capture streams"""
        class TeeWriter:
            def __init__(self, stream1, stream2):
                self.stream1 = stream1
                self.stream2 = stream2
                
            def write(self, text):
                self.stream1.write(text)
                self.stream2.write(text)
                
            def flush(self):
                self.stream1.flush()
                self.stream2.flush()
                
            def __getattr__(self, name):
                return getattr(self.stream1, name)
        
        return TeeWriter(original_stream, capture_stream)
    
    def extract_research_validation_logs(self, console_content: str) -> Dict[str, List[str]]:
        """Extract specific validation and rejection logs from console content"""
        
        validation_logs = {
            'company_validations': [],
            'interviewer_validations': [],
            'tavily_queries': [],
            'linkedin_searches': [],
            'citation_processing': [],
            'validation_results': []
        }
        
        lines = console_content.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            # Detect sections
            if '=== COMPANY ANALYSIS AGENT ACTIVATED ===' in line:
                current_section = 'company'
            elif '=== INTERVIEWER ANALYSIS AGENT' in line:
                current_section = 'interviewer'
            elif 'Company Validation Results:' in line or 'Validation Results:' in line:
                current_section = 'validation_results'
            
            # Capture all validation details
            if '✅ VALIDATED:' in line or '❌ REJECTED:' in line:
                validation_logs['validation_results'].append(line)
                if current_section == 'company':
                    validation_logs['company_validations'].append(line)
                elif current_section == 'interviewer':
                    validation_logs['interviewer_validations'].append(line)
            
            # Capture specific patterns
            if 'Fresh Tavily search' in line or '🔍 Query:' in line:
                validation_logs['tavily_queries'].append(line)
            
            if 'LinkedIn Search:' in line or '✅ LinkedIn Profile Found:' in line or '🎯 LinkedIn Post' in line:
                validation_logs['linkedin_searches'].append(line)
            
            if '📝 Processing citation' in line or '✅ Added citation:' in line or '🚫 Filtered out' in line:
                validation_logs['citation_processing'].append(line)
        
        return validation_logs
    
    def format_validation_logs_for_file(self, validation_logs: Dict[str, List[str]]) -> str:
        """Format validation logs for inclusion in output file"""
        
        formatted = []
        
        # Add all validation results first
        if validation_logs['validation_results']:
            formatted.append("📊 DETAILED VALIDATION RESULTS:")
            for log in validation_logs['validation_results']:
                formatted.append(f"   {log}")
            formatted.append("")
        
        if validation_logs['company_validations']:
            formatted.append("🏢 COMPANY VALIDATION RESULTS:")
            for log in validation_logs['company_validations']:
                formatted.append(f"   {log}")
            formatted.append("")
        
        if validation_logs['interviewer_validations']:
            formatted.append("👤 INTERVIEWER VALIDATION RESULTS:")
            for log in validation_logs['interviewer_validations']:
                formatted.append(f"   {log}")
            formatted.append("")
        
        if validation_logs['tavily_queries']:
            formatted.append("🔍 TAVILY SEARCH QUERIES:")
            for log in validation_logs['tavily_queries'][:15]:  # Show more queries
                formatted.append(f"   {log}")
            if len(validation_logs['tavily_queries']) > 15:
                formatted.append(f"   ... and {len(validation_logs['tavily_queries']) - 15} more queries")
            formatted.append("")
        
        if validation_logs['linkedin_searches']:
            formatted.append("🔗 LINKEDIN SEARCH DETAILS:")
            for log in validation_logs['linkedin_searches'][:20]:  # Show more results
                formatted.append(f"   {log}")
            if len(validation_logs['linkedin_searches']) > 20:
                formatted.append(f"   ... and {len(validation_logs['linkedin_searches']) - 20} more results")
            formatted.append("")
        
        if validation_logs['citation_processing']:
            formatted.append("📝 CITATION PROCESSING DETAILS:")
            for log in validation_logs['citation_processing']:
                formatted.append(f"   {log}")
            formatted.append("")
        
        return '\n'.join(formatted)


# Global instance for easy access
_log_capture = ConsoleLogCapture()

def start_log_capture():
    """Start capturing console logs"""
    global _log_capture
    _log_capture.start_capture()

def stop_log_capture():
    """Stop capturing and return logs"""
    global _log_capture
    return _log_capture.stop_capture()

def get_validation_logs_for_file(console_content: str) -> str:
    """Get formatted validation logs for file inclusion"""
    global _log_capture
    validation_logs = _log_capture.extract_research_validation_logs(console_content)
    return _log_capture.format_validation_logs_for_file(validation_logs)