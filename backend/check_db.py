#!/usr/bin/env python3
"""Simple script to check database tables and create test data."""

import sqlite3
import asyncio
from app.models.database import db, MODELS, TeamMember, Task

def check_database():
    """Check if database tables exist and have data."""
    print("=== Database Check ===")
    
    # Check tables using sqlite3 directly
    conn = sqlite3.connect('assistant_manager.db')
    cursor = conn.cursor()
    
    print("Database tables:")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    for table in tables:
        print(f"- {table[0]}")
    
    print("\nTable record counts:")
    
    # Check each table
    table_names = ['team_members', 'tasks', 'email_threads', 'kanban_changes', 
                   'agent_states', 'agent_activities', 'email_templates', 'workflow_settings']
    
    for table_name in table_names:
        try:
            cursor.execute(f"SELECT COUNT(1) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"- {table_name}: {count} records")
        except Exception as e:
            print(f"- {table_name}: ERROR - {e}")
    
    conn.close()

def create_test_data():
    """Create test team member and task data."""
    print("\n=== Creating Test Data ===")
    
    try:
        # Connect to database
        db.connect(reuse_if_open=True)
        
        # Create test team member if none exist
        member_count = TeamMember.select().count()
        if member_count == 0:
            print("Creating test team member...")
            test_member = TeamMember.create(
                email="test@example.com",
                name="Test User",
                role="Developer",
                active=True
            )
            print(f"Created team member: {test_member.name} (ID: {test_member.id})")
        else:
            test_member = TeamMember.select().first()
            print(f"Using existing team member: {test_member.name} (ID: {test_member.id})")
        
        # Create test task if none exist
        task_count = Task.select().count()
        if task_count == 0:
            print("Creating test task...")
            test_task = Task.create(
                title="Test Task",
                description="This is a test task for the kanban board",
                status="todo",
                assignee=test_member,
                priority="medium",
                order=0
            )
            print(f"Created task: {test_task.title} (ID: {test_task.id})")
        else:
            test_task = Task.select().first()
            print(f"Using existing task: {test_task.title} (ID: {test_task.id})")
        
        # Verify task can be updated
        print("Testing task update...")
        test_task.status = "in_progress"
        test_task.save()
        print(f"Successfully updated task status to: {test_task.status}")
        
        db.close()
        
    except Exception as e:
        print(f"Error creating test data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_database()
    create_test_data()
    print("\n=== Database check complete ===") 