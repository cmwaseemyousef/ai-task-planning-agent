#!/usr/bin/env python3
"""
Quick test of the web search functionality
"""

import sys
sys.path.append('.')

from tools.web_search import WebSearchTool

def test_search():
    search_tool = WebSearchTool()
    results = search_tool.search('Jaipur tourism')
    
    print("🔍 Mock Search Results for 'Jaipur tourism':")
    print("=" * 50)
    
    for i, result in enumerate(results[:3], 1):
        print(f"{i}. {result['title']}")
        print(f"   {result['snippet'][:100]}...")
        print(f"   Source: {result['source']}")
        print()

if __name__ == "__main__":
    test_search()