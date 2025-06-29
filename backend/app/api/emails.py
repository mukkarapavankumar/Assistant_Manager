"""Enhanced API endpoints for email management with template support."""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime, timedelta

from app.models.schemas import (
    EmailThread, APIResponse, TeamMemberCreate, TeamMember, 
    EmailTemplate, EmailTemplateCreate, EmailTemplateUpdate
)
from app.models.database import (
    TeamMember as TeamMemberModel, 
    EmailThread as EmailThreadModel,
    EmailTemplate as EmailTemplateModel,
    WorkflowSettings
)
from app.core.dependencies import get_assistant_agent

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/threads", response_model=List[EmailThread])
async def get_email_threads(
    team_member_id: Optional[int] = Query(None, description="Filter by team member ID"),
    status: Optional[str] = Query(None, description="Filter by email status"),
    limit: int = Query(50, description="Maximum number of threads to return")
):
    """Get email threads with optional filtering."""
    try:
        query = EmailThreadModel.select().join(TeamMemberModel)
        
        if team_member_id:
            query = query.where(EmailThreadModel.team_member == team_member_id)
        
        if status:
            query = query.where(EmailThreadModel.status == status)
        
        threads = list(query.order_by(EmailThreadModel.sent_at.desc()).limit(limit))
        
        result = []
        for thread in threads:
            result.append(EmailThread(
                id=thread.id,
                team_member_id=thread.team_member.id,
                subject=thread.subject,
                sent_at=thread.sent_at,
                response_received=thread.response_received,
                response_at=thread.response_at,
                status=thread.status,
                content=thread.content,
                follow_up_count=thread.follow_up_count,
                template_used=thread.template_used,
                parsed_content=thread.parsed_data,
                team_member={
                    "id": thread.team_member.id,
                    "name": thread.team_member.name,
                    "email": thread.team_member.email,
                    "role": thread.team_member.role,
                    "active": thread.team_member.active,
                    "response_rate": thread.team_member.response_rate,
                    "last_response_at": thread.team_member.last_response_at,
                    "created_at": thread.team_member.created_at,
                    "updated_at": thread.team_member.updated_at
                }
            ))
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting email threads: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/send-updates")
async def send_update_requests(template_id: Optional[int] = None):
    """Send update requests to all active team members using specified template."""
    try:
        agent = get_assistant_agent()
        if not agent:
            raise HTTPException(status_code=503, detail="Agent not available")
        
        # Get active team members
        active_members = list(TeamMemberModel.select().where(TeamMemberModel.active == True))
        member_emails = [member.email for member in active_members]
        
        if not member_emails:
            return APIResponse(
                success=False,
                message="No active team members found"
            )
        
        # Get template if specified
        template_name = "Weekly Update Request"  # Default
        if template_id:
            template = EmailTemplateModel.get_or_none(EmailTemplateModel.id == template_id)
            if template:
                template_name = template.name
        
        # Trigger email sending through agent
        response = await agent.process_message(
            f"Send {template_name} emails to team members: {', '.join(member_emails)}"
        )
        
        return APIResponse(
            success=True,
            message=f"Update requests sent to {len(member_emails)} team members",
            data={"response": response, "recipient_count": len(member_emails), "template": template_name}
        )
        
    except Exception as e:
        logger.error(f"Error sending update requests: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search-contacts")
async def search_outlook_contacts(
    search_term: str = Query(..., description="Search term for contacts"),
    limit: int = Query(20, description="Maximum number of results"),
    include_no_email: bool = Query(True, description="Include contacts without email addresses")
):
    """Search Outlook contacts and address book."""
    try:
        agent = get_assistant_agent()
        if not agent:
            raise HTTPException(status_code=503, detail="Agent not available")
        
        # Access email tools through agent
        email_tools = agent.email_tools
        
        # Try Outlook search first
        try:
            contacts = email_tools.search_outlook_contacts(search_term)
            
            # Separate contacts with and without emails
            contacts_with_email = [c for c in contacts if c.get('email')]
            contacts_without_email = [c for c in contacts if not c.get('email')]
            
            # Build response message
            if contacts_with_email:
                message = f"Found {len(contacts_with_email)} contacts with email addresses"
                if contacts_without_email and include_no_email:
                    message += f" and {len(contacts_without_email)} contacts without email addresses"
            elif contacts_without_email and include_no_email:
                message = f"Found {len(contacts_without_email)} contacts (none have email addresses)"
            else:
                message = "No contacts found with email addresses"
            
            # Prepare final contacts list
            final_contacts = []
            if contacts_with_email:
                final_contacts.extend(contacts_with_email)
            
            if include_no_email and contacts_without_email:
                final_contacts.extend(contacts_without_email)
            
            # Limit results
            final_contacts = final_contacts[:limit]
            
            return APIResponse(
                success=True,
                message=message,
                data={
                    "contacts": final_contacts,
                    "source": "outlook",
                    "stats": {
                        "total_found": len(contacts),
                        "with_email": len(contacts_with_email),
                        "without_email": len(contacts_without_email),
                        "returned": len(final_contacts)
                    },
                    "note": "Contacts without email addresses cannot be used for sending emails" if contacts_without_email else None
                }
            )
            
        except Exception as outlook_error:
            logger.warning(f"Outlook search failed: {outlook_error}")
        
        # Fallback: Search in existing team members database
        try:
            from app.models.database import TeamMember as TeamMemberModel
            
            # Search in team members database
            search_lower = search_term.lower()
            db_query = TeamMemberModel.select().where(
                (TeamMemberModel.name.contains(search_term)) |
                (TeamMemberModel.email.contains(search_term))
            ).limit(limit)
            
            db_contacts = []
            for member in db_query:
                db_contacts.append({
                    'name': member.name,
                    'email': member.email,
                    'company': '',
                    'department': '',
                    'job_title': member.role,
                    'source': 'team_database',
                    'active': member.active
                })
            
            # If we have database results, return them
            if db_contacts:
                return APIResponse(
                    success=True,
                    message=f"Found {len(db_contacts)} contacts from team database (Outlook search failed)",
                    data={
                        "contacts": db_contacts, 
                        "source": "team_database", 
                        "outlook_available": False,
                        "stats": {
                            "total_found": len(db_contacts),
                            "with_email": len(db_contacts),
                            "without_email": 0,
                            "returned": len(db_contacts)
                        }
                    }
                )
            
            # No results anywhere
            return APIResponse(
                success=True,
                message=f"No contacts found matching '{search_term}'",
                data={
                    "contacts": [], 
                    "source": "none", 
                    "outlook_available": False,
                    "searched_term": search_term,
                    "suggestion": "Try a different search term or check if the contact exists in your Outlook contacts",
                    "stats": {
                        "total_found": 0,
                        "with_email": 0,
                        "without_email": 0,
                        "returned": 0
                    }
                }
            )
            
        except Exception as db_error:
            logger.error(f"Database search also failed: {db_error}")
            raise HTTPException(
                status_code=500, 
                detail=f"Search service unavailable. Outlook: unavailable, Database: {str(db_error)}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in search-contacts endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Search service error: {str(e)}")

@router.post("/team-members", response_model=TeamMember)
async def add_team_member(member_data: TeamMemberCreate):
    """Add a new team member."""
    try:
        # Check if member already exists
        existing_member = TeamMemberModel.get_or_none(TeamMemberModel.email == member_data.email)
        if existing_member:
            if existing_member.active:
                raise HTTPException(status_code=400, detail="Team member already exists and is active")
            else:
                # Reactivate existing member
                existing_member.active = True
                existing_member.name = member_data.name
                existing_member.role = member_data.role
                existing_member.save()
                
                return TeamMember(
                    id=existing_member.id,
                    email=existing_member.email,
                    name=existing_member.name,
                    role=existing_member.role,
                    active=existing_member.active,
                    response_rate=existing_member.response_rate,
                    last_response_at=existing_member.last_response_at,
                    created_at=existing_member.created_at,
                    updated_at=existing_member.updated_at
                )
        
        # Create new team member
        new_member = TeamMemberModel.create(
            email=member_data.email,
            name=member_data.name,
            role=member_data.role,
            active=member_data.active
        )
        
        return TeamMember(
            id=new_member.id,
            email=new_member.email,
            name=new_member.name,
            role=new_member.role,
            active=new_member.active,
            response_rate=new_member.response_rate,
            last_response_at=new_member.last_response_at,
            created_at=new_member.created_at,
            updated_at=new_member.updated_at
        )
        
    except Exception as e:
        logger.error(f"Error adding team member: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/team-members", response_model=List[TeamMember])
async def get_team_members(
    active_only: bool = Query(True, description="Return only active members")
):
    """Get all team members."""
    try:
        query = TeamMemberModel.select()
        
        if active_only:
            query = query.where(TeamMemberModel.active == True)
        
        members = list(query.order_by(TeamMemberModel.name))
        
        return [
            TeamMember(
                id=member.id,
                email=member.email,
                name=member.name,
                role=member.role,
                active=member.active,
                response_rate=member.response_rate,
                last_response_at=member.last_response_at,
                created_at=member.created_at,
                updated_at=member.updated_at
            )
            for member in members
        ]
        
    except Exception as e:
        logger.error(f"Error getting team members: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/team-members/{member_id}")
async def update_team_member(member_id: int, updates: dict):
    """Update team member information."""
    try:
        member = TeamMemberModel.get_or_none(TeamMemberModel.id == member_id)
        if not member:
            raise HTTPException(status_code=404, detail="Team member not found")
        
        # Update allowed fields
        allowed_fields = ['name', 'role', 'active']
        for field, value in updates.items():
            if field in allowed_fields:
                setattr(member, field, value)
        
        member.save()
        
        return APIResponse(
            success=True,
            message="Team member updated successfully",
            data={
                "id": member.id,
                "name": member.name,
                "email": member.email,
                "role": member.role,
                "active": member.active
            }
        )
        
    except Exception as e:
        logger.error(f"Error updating team member: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/team-members/{member_id}")
async def remove_team_member(member_id: int, permanent: bool = Query(False, description="Permanently delete instead of deactivating")):
    """Remove or deactivate a team member."""
    try:
        member = TeamMemberModel.get_or_none(TeamMemberModel.id == member_id)
        if not member:
            raise HTTPException(status_code=404, detail="Team member not found")
        
        if permanent:
            # Permanently delete (also deletes related records due to foreign key constraints)
            member.delete_instance(recursive=True)
            message = "Team member permanently deleted"
        else:
            # Just deactivate
            member.active = False
            member.save()
            message = "Team member deactivated"
        
        return APIResponse(
            success=True,
            message=message
        )
        
    except Exception as e:
        logger.error(f"Error removing team member: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/check-responses")
async def check_email_responses():
    """Manually trigger checking for new email responses."""
    try:
        agent = get_assistant_agent()
        if not agent:
            raise HTTPException(status_code=503, detail="Agent not available")
        
        # Trigger response checking through agent
        response = await agent.process_message(
            "Check for new email responses from team members in the last 24 hours"
        )
        
        return APIResponse(
            success=True,
            message="Email response check completed",
            data={"response": response}
        )
        
    except Exception as e:
        logger.error(f"Error checking email responses: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics")
async def get_email_statistics():
    """Get email communication statistics."""
    try:
        # Get statistics from database
        total_threads = EmailThreadModel.select().count()
        responded_threads = EmailThreadModel.select().where(EmailThreadModel.response_received == True).count()
        pending_threads = EmailThreadModel.select().where(EmailThreadModel.response_received == False).count()
        
        # Calculate response rate
        response_rate = (responded_threads / total_threads * 100) if total_threads > 0 else 0
        
        # Get recent activity (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        recent_threads = EmailThreadModel.select().where(EmailThreadModel.sent_at >= week_ago).count()
        recent_responses = EmailThreadModel.select().where(
            EmailThreadModel.response_at >= week_ago
        ).count()
        
        # Get template usage
        template_usage = {}
        for template in EmailTemplateModel.select().where(EmailTemplateModel.active == True):
            template_usage[template.name] = template.usage_count
        
        return APIResponse(
            success=True,
            message="Email statistics retrieved",
            data={
                "total_threads": total_threads,
                "responded_threads": responded_threads,
                "pending_threads": pending_threads,
                "response_rate": round(response_rate, 1),
                "recent_activity": {
                    "emails_sent_week": recent_threads,
                    "responses_received_week": recent_responses
                },
                "template_usage": template_usage
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting email statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Email Template Management

@router.get("/templates", response_model=List[EmailTemplate])
async def get_email_templates(
    template_type: Optional[str] = Query(None, description="Filter by template type"),
    active_only: bool = Query(True, description="Return only active templates")
):
    """Get all email templates."""
    try:
        query = EmailTemplateModel.select()
        
        if template_type:
            query = query.where(EmailTemplateModel.template_type == template_type)
        
        if active_only:
            query = query.where(EmailTemplateModel.active == True)
        
        templates = list(query.order_by(EmailTemplateModel.name))
        
        return [
            EmailTemplate(
                id=template.id,
                name=template.name,
                subject=template.subject,
                content=template.content,
                template_type=template.template_type,
                variables=template.variables_list,
                active=template.active,
                usage_count=template.usage_count,
                created_at=template.created_at,
                updated_at=template.updated_at
            )
            for template in templates
        ]
        
    except Exception as e:
        logger.error(f"Error getting email templates: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/templates", response_model=EmailTemplate)
async def create_email_template(template_data: EmailTemplateCreate):
    """Create a new email template."""
    try:
        # Check if template with same name exists
        existing_template = EmailTemplateModel.get_or_none(EmailTemplateModel.name == template_data.name)
        if existing_template:
            raise HTTPException(status_code=400, detail="Template with this name already exists")
        
        # Create new template
        new_template = EmailTemplateModel.create(
            name=template_data.name,
            subject=template_data.subject,
            content=template_data.content,
            template_type=template_data.template_type,
            variables=json.dumps(template_data.variables),
            active=template_data.active,
            usage_count=0
        )
        
        return EmailTemplate(
            id=new_template.id,
            name=new_template.name,
            subject=new_template.subject,
            content=new_template.content,
            template_type=new_template.template_type,
            variables=new_template.variables_list,
            active=new_template.active,
            usage_count=new_template.usage_count,
            created_at=new_template.created_at,
            updated_at=new_template.updated_at
        )
        
    except Exception as e:
        logger.error(f"Error creating email template: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/templates/{template_id}", response_model=EmailTemplate)
async def update_email_template(template_id: int, template_data: EmailTemplateUpdate):
    """Update an existing email template."""
    try:
        template = EmailTemplateModel.get_or_none(EmailTemplateModel.id == template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Update fields
        update_data = template_data.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            if field == 'variables':
                template.variables = json.dumps(value)
            else:
                setattr(template, field, value)
        
        template.save()
        
        return EmailTemplate(
            id=template.id,
            name=template.name,
            subject=template.subject,
            content=template.content,
            template_type=template.template_type,
            variables=template.variables_list,
            active=template.active,
            usage_count=template.usage_count,
            created_at=template.created_at,
            updated_at=template.updated_at
        )
        
    except Exception as e:
        logger.error(f"Error updating email template: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/templates/{template_id}")
async def delete_email_template(template_id: int):
    """Delete an email template."""
    try:
        template = EmailTemplateModel.get_or_none(EmailTemplateModel.id == template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        template.delete_instance()
        
        return APIResponse(
            success=True,
            message="Email template deleted successfully"
        )
        
    except Exception as e:
        logger.error(f"Error deleting email template: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/templates/{template_id}/duplicate")
async def duplicate_email_template(template_id: int):
    """Duplicate an existing email template."""
    try:
        template = EmailTemplateModel.get_or_none(EmailTemplateModel.id == template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Create duplicate with modified name
        duplicate_name = f"{template.name} (Copy)"
        counter = 1
        while EmailTemplateModel.get_or_none(EmailTemplateModel.name == duplicate_name):
            duplicate_name = f"{template.name} (Copy {counter})"
            counter += 1
        
        new_template = EmailTemplateModel.create(
            name=duplicate_name,
            subject=template.subject,
            content=template.content,
            template_type=template.template_type,
            variables=template.variables,
            active=False,  # Start as inactive
            usage_count=0
        )
        
        return EmailTemplate(
            id=new_template.id,
            name=new_template.name,
            subject=new_template.subject,
            content=new_template.content,
            template_type=new_template.template_type,
            variables=new_template.variables_list,
            active=new_template.active,
            usage_count=new_template.usage_count,
            created_at=new_template.created_at,
            updated_at=new_template.updated_at
        )
        
    except Exception as e:
        logger.error(f"Error duplicating email template: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/settings")
async def get_email_settings():
    """Get email-related workflow settings."""
    try:
        settings = {}
        
        email_settings = [
            'email_check_interval',
            'max_follow_ups',
            'reminder_days',
            'email_signature',
            'business_hours_start',
            'business_hours_end'
        ]
        
        for setting_key in email_settings:
            setting = WorkflowSettings.get_or_none(WorkflowSettings.setting_key == setting_key)
            if setting:
                try:
                    if setting.setting_type == 'number':
                        settings[setting_key] = int(setting.setting_value)
                    elif setting.setting_type == 'boolean':
                        settings[setting_key] = setting.setting_value.lower() == 'true'
                    else:
                        settings[setting_key] = json.loads(setting.setting_value)
                except:
                    settings[setting_key] = setting.setting_value
        
        return APIResponse(
            success=True,
            message="Email settings retrieved",
            data=settings
        )
        
    except Exception as e:
        logger.error(f"Error getting email settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/settings")
async def update_email_settings(settings_data: Dict[str, Any]):
    """Update email-related workflow settings."""
    try:
        updated_count = 0
        
        for setting_key, value in settings_data.items():
            setting = WorkflowSettings.get_or_none(WorkflowSettings.setting_key == setting_key)
            if setting:
                if setting.setting_type == 'number':
                    setting.setting_value = str(value)
                elif setting.setting_type == 'boolean':
                    setting.setting_value = str(value).lower()
                else:
                    setting.setting_value = json.dumps(value)
                
                setting.save()
                updated_count += 1
        
        return APIResponse(
            success=True,
            message=f"Updated {updated_count} email settings",
            data={"updated_count": updated_count}
        )
        
    except Exception as e:
        logger.error(f"Error updating email settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))