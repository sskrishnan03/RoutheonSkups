#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test script to verify explore page functionality"""
import sys
import os
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from flask_login import login_user
from models import User

def test_explore_page():
    app = create_app()
    
    with app.app_context():
        # Get a test user
        user = User.query.first()
        if not user:
            print("❌ No users found in database")
            return False
        
        with app.test_client() as client:
            # Login the user
            with client.session_transaction() as sess:
                sess['_user_id'] = str(user.id)
            
            # Test explore page loads
            response = client.get('/explore')
            if response.status_code != 200:
                print(f"❌ Explore page failed to load: {response.status_code}")
                return False
            
            # Check if explore.html is rendered
            if b'Explore Destinations' not in response.data:
                print("❌ Explore page content missing")
                return False
            
            # Check if JavaScript is present
            if b'fetchDestinations' not in response.data:
                print("❌ JavaScript function missing")
                return False
            
            # Check if results container exists
            if b'results-container' not in response.data:
                print("❌ Results container missing")
                return False
            
            # Test API endpoint
            response = client.get('/api/explore-destinations?state=Tamil%20Nadu&category=Beach')
            if response.status_code != 200:
                print(f"❌ API endpoint failed: {response.status_code}")
                return False
            
            # Check if response is JSON
            try:
                import json
                data = json.loads(response.data)
                if 'destinations' not in data:
                    print("❌ API response missing destinations")
                    return False
                
                if len(data['destinations']) == 0:
                    print("⚠️  API returned no destinations")
                else:
                    print(f"✅ API returned {len(data['destinations'])} destinations")
                    
            except json.JSONDecodeError:
                print("❌ API response is not valid JSON")
                return False
            
            print("✅ All explore page tests passed")
            return True

if __name__ == '__main__':
    success = test_explore_page()
    sys.exit(0 if success else 1)
