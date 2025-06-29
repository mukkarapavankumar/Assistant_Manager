#!/usr/bin/env python3
"""Test script to simulate drag and drop API calls."""

import requests
import json

def test_api_calls():
    """Test the exact API calls made during drag and drop."""
    
    print("=== Testing Kanban API ===")
    
    # Test 1: Get board data
    print("1. Getting board data...")
    try:
        response = requests.get('http://localhost:8000/api/kanban/board')
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            board_data = response.json()
            print("   Board data retrieved successfully")
            
            # Find the first task
            task = None
            for column in board_data['columns']:
                if column['tasks']:
                    task = column['tasks'][0]
                    break
            
            if task:
                print(f"   Found task: ID={task['id']}, Status={task['status']}")
                
                # Test 2: Update task status (simulate drag and drop)
                new_status = 'review' if task['status'] != 'review' else 'done'
                update_data = {'status': new_status}
                
                print(f"\n2. Updating task {task['id']} to status: {new_status}")
                print(f"   Update data: {update_data}")
                
                update_response = requests.put(
                    f"http://localhost:8000/api/kanban/tasks/{task['id']}",
                    json=update_data,
                    headers={'Content-Type': 'application/json'}
                )
                
                print(f"   Update status: {update_response.status_code}")
                
                if update_response.status_code == 200:
                    print("   ✓ Task update successful!")
                    result = update_response.json()
                    print(f"   New status: {result['status']}")
                else:
                    print("   ✗ Task update failed!")
                    print(f"   Error response: {update_response.text}")
                    
                    # Try to get more details about the error
                    try:
                        error_details = update_response.json()
                        print(f"   Error details: {json.dumps(error_details, indent=2)}")
                    except:
                        pass
                
            else:
                print("   No tasks found on the board")
        else:
            print(f"   ✗ Failed to get board data: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("   ✗ Could not connect to the backend server")
        print("   Make sure the backend is running on http://localhost:8000")
    except Exception as e:
        print(f"   ✗ Unexpected error: {e}")

if __name__ == "__main__":
    test_api_calls() 