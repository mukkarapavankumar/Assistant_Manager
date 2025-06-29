"""Tests for database models."""

import pytest
from datetime import datetime
import json

from app.models.database import (
    TeamMember, Task, EmailThread, EmailTemplate, 
    KanbanChange, AgentState, WorkflowSettings
)


@pytest.mark.unit
def test_team_member_creation(temp_db, sample_team_member_data):
    """Test creating a team member."""
    member = TeamMember.create(**sample_team_member_data)
    
    assert member.id is not None
    assert member.name == sample_team_member_data['name']
    assert member.email == sample_team_member_data['email']
    assert member.role == sample_team_member_data['role']
    assert member.active == sample_team_member_data['active']
    assert member.response_rate == 0.0  # Default value
    assert member.created_at is not None
    assert member.updated_at is not None


@pytest.mark.unit
def test_task_creation(temp_db, sample_task_data):
    """Test creating a task."""
    # First create a team member
    member = TeamMember.create(
        name='Test User',
        email='test@example.com',
        role='Developer',
        active=True
    )
    
    # Create task
    task_data = sample_task_data.copy()
    task_data['assignee'] = member
    del task_data['assignee_id']
    # Remove tags from creation data to set via property later
    tags = task_data.pop('tags')
    
    task = Task.create(**task_data)
    # Set tags via property setter
    task.tags_list = tags
    task.save()
    
    assert task.id is not None
    assert task.title == sample_task_data['title']
    assert task.description == sample_task_data['description']
    assert task.status == sample_task_data['status']
    assert task.assignee == member
    assert task.priority == sample_task_data['priority']
    assert task.tags_list == sample_task_data['tags']


@pytest.mark.unit
def test_task_tags_property(temp_db):
    """Test task tags property functionality."""
    member = TeamMember.create(
        name='Test User',
        email='test@example.com',
        role='Developer',
        active=True
    )
    
    task = Task.create(
        title='Test Task',
        description='Test description',
        status='todo',
        assignee=member,
        priority='medium',
        tags='["tag1", "tag2", "tag3"]'
    )
    
    # Test getter
    assert task.tags_list == ['tag1', 'tag2', 'tag3']
    
    # Test setter
    task.tags_list = ['new_tag1', 'new_tag2']
    task.save()
    
    # Reload and verify
    task = Task.get_by_id(task.id)
    assert task.tags_list == ['new_tag1', 'new_tag2']


@pytest.mark.unit
def test_task_is_overdue_property(temp_db):
    """Test task overdue property."""
    member = TeamMember.create(
        name='Test User',
        email='test@example.com',
        role='Developer',
        active=True
    )
    
    # Task with past due date
    past_date = datetime(2020, 1, 1)
    overdue_task = Task.create(
        title='Overdue Task',
        description='Test description',
        status='in_progress',
        assignee=member,
        priority='medium',
        due_date=past_date
    )
    
    assert overdue_task.is_overdue is True
    
    # Completed task should not be overdue
    completed_task = Task.create(
        title='Completed Task',
        description='Test description',
        status='done',
        assignee=member,
        priority='medium',
        due_date=past_date
    )
    
    assert completed_task.is_overdue is False


@pytest.mark.unit
def test_email_template_variables_property(temp_db, sample_email_template_data):
    """Test email template variables property."""
    # Remove variables from creation data to set via property later
    template_data = sample_email_template_data.copy()
    variables = template_data.pop('variables')
    
    template = EmailTemplate.create(**template_data)
    # Set variables via property setter
    template.variables_list = variables
    template.save()
    
    # Test getter
    assert template.variables_list == ['name', 'date']
    
    # Test setter
    template.variables_list = ['name', 'email', 'role']
    template.save()
    
    # Reload and verify
    template = EmailTemplate.get_by_id(template.id)
    assert template.variables_list == ['name', 'email', 'role']


@pytest.mark.unit
def test_email_thread_parsed_data_property(temp_db):
    """Test email thread parsed data property."""
    member = TeamMember.create(
        name='Test User',
        email='test@example.com',
        role='Developer',
        active=True
    )
    
    thread = EmailThread.create(
        thread_id='test_thread_1',
        team_member=member,
        subject='Test Subject',
        sent_at=datetime.now(),
        status='sent',
        content='Test email content'
    )
    
    # Test setter
    test_data = {'task_title': 'Test Task', 'priority': 'high'}
    thread.parsed_data = test_data
    thread.save()
    
    # Test getter
    thread = EmailThread.get_by_id(thread.id)
    assert thread.parsed_data == test_data


@pytest.mark.unit
def test_model_timestamps(temp_db, sample_team_member_data):
    """Test that model timestamps are properly set."""
    member = TeamMember.create(**sample_team_member_data)
    
    original_updated = member.updated_at
    
    # Update the member
    member.role = 'Lead Developer'
    member.save()
    
    # Verify updated_at changed
    assert member.updated_at > original_updated