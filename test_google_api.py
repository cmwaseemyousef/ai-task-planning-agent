#!/usr/bin/env python3
"""
Test the new Google API key
"""

import requests

def test_google_api():
    api_key = 'AIzaSyDlu-fReCTgUZAtct9JzgEbkP8Qi1yKY5I'
    url = 'https://www.googleapis.com/customsearch/v1'
    
    print("🔍 Testing new Google API key...")
    print("=" * 50)
    
    try:
        response = requests.get(
            url + '?key=' + api_key + '&cx=test&q=test', 
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response body: {response.text}")
        
        if response.status_code == 403:
            error_data = response.json().get('error', {})
            message = error_data.get('message', '')
            
            if 'Custom Search API has not been used' in message:
                print("✅ API key is valid!")
                print("❗ Need to enable Custom Search API in Google Cloud Console")
                print("   Go to: https://console.developers.google.com/apis/api/customsearch.googleapis.com")
                
            elif 'Daily Limit Exceeded' in message:
                print("⚠️  API key valid but daily limit exceeded")
                
            else:
                print(f"❌ Error: {message}")
                
        elif response.status_code == 400:
            error_data = response.json().get('error', {})
            message = error_data.get('message', '')
            
            if 'Invalid Value' in message or 'invalid argument' in message.lower():
                print("✅ API key is valid and working!")
                print("❗ Just needs a proper Custom Search Engine ID")
                print("   The key authenticated successfully with Google's servers")
                
        elif response.status_code == 200:
            print("✅ API key and setup working perfectly!")
            
        else:
            print(f"Unexpected response: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ Error testing API: {e}")

if __name__ == "__main__":
    test_google_api()