"""Email automation tools using pywin32 Outlook COM interface."""

import win32com.client
import pythoncom
from langchain.tools import BaseTool
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
import json
import re
from email.utils import parseaddr

from app.models.database import TeamMember, EmailThread, EmailTemplate
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)

class OutlookService:
    """Service for Outlook COM automation."""
    
    def __init__(self):
        self.outlook = None
        self.namespace = None
        self.inbox = None
        self.sent_items = None
        self.llm_service = None
    
    def initialize(self):
        """Initialize Outlook COM connection."""
        try:
            # Initialize COM
            pythoncom.CoInitialize()
            
            # Connect to Outlook
            self.outlook = win32com.client.Dispatch("Outlook.Application")
            self.namespace = self.outlook.GetNamespace("MAPI")
            
            # Get default folders
            self.inbox = self.namespace.GetDefaultFolder(6)  # olFolderInbox
            self.sent_items = self.namespace.GetDefaultFolder(5)  # olFolderSentMail
            
            # Initialize LLM service for email parsing
            self.llm_service = LLMService()
            
            logger.info("Outlook COM connection established successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Outlook COM: {e}")
            return False
    
    def search_contacts(self, search_term: str) -> List[Dict[str, Any]]:
        """Search Outlook contacts and address book."""
        try:
            contacts = []
            
            # Search in Local Contacts folder first (this works!)
            try:
                contacts_folder = self.namespace.GetDefaultFolder(10)  # olFolderContacts
                contact_items = contacts_folder.Items
                
                logger.info(f"Searching through {contact_items.Count} local contacts for '{search_term}'")
                
                for contact in contact_items:
                    try:
                        if hasattr(contact, 'Email1Address') and contact.Email1Address:
                            name = getattr(contact, 'FullName', '') or getattr(contact, 'CompanyName', '')
                            email = contact.Email1Address
                            
                            if (search_term.lower() in name.lower() or 
                                search_term.lower() in email.lower()):
                                contacts.append({
                                    'name': name,
                                    'email': email,
                                    'company': getattr(contact, 'CompanyName', ''),
                                    'department': getattr(contact, 'Department', ''),
                                    'job_title': getattr(contact, 'JobTitle', ''),
                                    'source': 'local_contacts'
                                })
                        elif not hasattr(contact, 'Email1Address') or not contact.Email1Address:
                            # Handle contacts without email
                            name = getattr(contact, 'FullName', '') or getattr(contact, 'CompanyName', '')
                            if name and search_term.lower() in name.lower():
                                contacts.append({
                                    'name': name,
                                    'email': '',  # No email available
                                    'company': getattr(contact, 'CompanyName', ''),
                                    'department': getattr(contact, 'Department', ''),
                                    'job_title': getattr(contact, 'JobTitle', ''),
                                    'source': 'local_contacts_no_email'
                                })
                    except Exception as e:
                        logger.debug(f"Error processing local contact: {e}")
                        continue
                
                logger.info(f"Found {len(contacts)} matches in local contacts")
                
            except Exception as e:
                logger.error(f"Error searching local contacts: {e}")
            
            # Try Global Address List (GAL) if local search returned few results
            # This may fail due to permissions, but we'll try anyway
            if len(contacts) < 10:  # Only try GAL if we have few local results
                try:
                    logger.info("Trying Global Address List (GAL) search...")
                    address_lists = self.namespace.AddressLists
                    
                    for addr_list in address_lists:
                        if "Global Address List" in addr_list.Name or "GAL" in addr_list.Name:
                            try:
                                entries = addr_list.AddressEntries
                                logger.info(f"Searching {entries.Count} GAL entries")
                                
                                for entry in entries:
                                    try:
                                        name = entry.Name
                                        if search_term.lower() in name.lower():
                                            # Try to get email address
                                            email = ""
                                            try:
                                                if hasattr(entry, 'GetExchangeUser'):
                                                    exchange_user = entry.GetExchangeUser()
                                                    if exchange_user and hasattr(exchange_user, 'PrimarySmtpAddress'):
                                                        email = exchange_user.PrimarySmtpAddress
                                            except:
                                                pass
                                            
                                            if email:  # Only add if we have an email
                                                contacts.append({
                                                    'name': name,
                                                    'email': email,
                                                    'company': getattr(exchange_user, 'CompanyName', '') if 'exchange_user' in locals() else '',
                                                    'department': getattr(exchange_user, 'Department', '') if 'exchange_user' in locals() else '',
                                                    'job_title': getattr(exchange_user, 'JobTitle', '') if 'exchange_user' in locals() else '',
                                                    'source': 'gal'
                                                })
                                    except Exception as e:
                                        logger.debug(f"Error processing GAL entry: {e}")
                                        continue
                                        
                            except Exception as e:
                                logger.warning(f"GAL access failed (this is normal in many environments): {e}")
                                break
                            
                except Exception as e:
                    logger.warning(f"Error accessing GAL (this is normal in many environments): {e}")
            
            # Remove duplicates based on email
            unique_contacts = {}
            for contact in contacts:
                email_key = contact['email'].lower() if contact['email'] else f"no_email_{contact['name'].lower()}"
                if email_key not in unique_contacts:
                    unique_contacts[email_key] = contact
            
            final_contacts = list(unique_contacts.values())[:20]  # Limit to 20 results
            
            logger.info(f"Returning {len(final_contacts)} unique contacts")
            return final_contacts
            
        except Exception as e:
            logger.error(f"Error searching contacts: {e}")
            return []
    
    def send_email(self, to_addresses: List[str], subject: str, body: str, 
                   cc_addresses: List[str] = None, bcc_addresses: List[str] = None) -> Dict[str, Any]:
        """Send email using Outlook."""
        try:
            # Create mail item
            mail = self.outlook.CreateItem(0)  # olMailItem
            
            # Set recipients
            mail.To = "; ".join(to_addresses)
            if cc_addresses:
                mail.CC = "; ".join(cc_addresses)
            if bcc_addresses:
                mail.BCC = "; ".join(bcc_addresses)
            
            # Set subject and body
            mail.Subject = subject
            mail.Body = body
            
            # Send email
            mail.Send()
            
            logger.info(f"Email sent successfully to {len(to_addresses)} recipients")
            
            return {
                'success': True,
                'message': f'Email sent to {len(to_addresses)} recipients',
                'recipients': to_addresses,
                'subject': subject,
                'sent_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return {
                'success': False,
                'error': str(e),
                'recipients': to_addresses,
                'subject': subject
            }
    
    def get_recent_emails(self, since_date: datetime, from_addresses: List[str] = None) -> List[Dict[str, Any]]:
        """Get recent emails from inbox."""
        try:
            emails = []
            
            # Build filter string
            filter_date = since_date.strftime("%m/%d/%Y %H:%M %p")
            filter_str = f"[ReceivedTime] >= '{filter_date}'"
            
            # Get emails from inbox
            items = self.inbox.Items
            items.Sort("[ReceivedTime]", True)  # Sort by received time, descending
            
            # Apply filter
            filtered_items = items.Restrict(filter_str)
            
            for mail in filtered_items:
                try:
                    sender_email = self._extract_email_address(mail.SenderEmailAddress, mail.SenderName)
                    
                    # Filter by sender if specified
                    if from_addresses and sender_email.lower() not in [addr.lower() for addr in from_addresses]:
                        continue
                    
                    email_data = {
                        'subject': mail.Subject,
                        'sender_name': mail.SenderName,
                        'sender_email': sender_email,
                        'received_time': mail.ReceivedTime,
                        'body': mail.Body,
                        'conversation_id': getattr(mail, 'ConversationID', ''),
                        'entry_id': mail.EntryID,
                        'size': mail.Size,
                        'importance': mail.Importance,
                        'read': mail.UnRead == False
                    }
                    
                    emails.append(email_data)
                    
                except Exception as e:
                    logger.debug(f"Error processing email: {e}")
                    continue
            
            logger.info(f"Retrieved {len(emails)} recent emails")
            return emails
            
        except Exception as e:
            logger.error(f"Error retrieving emails: {e}")
            return []
    
    def _extract_email_address(self, sender_email: str, sender_name: str) -> str:
        """Extract email address from Outlook sender information."""
        try:
            # If it's an Exchange address, try to resolve it
            if sender_email.startswith('/O=') or sender_email.startswith('/o='):
                try:
                    # Try to get SMTP address from Exchange
                    recipient = self.namespace.CreateRecipient(sender_name)
                    recipient.Resolve()
                    if recipient.Resolved:
                        exchange_user = recipient.AddressEntry.GetExchangeUser()
                        if exchange_user and hasattr(exchange_user, 'PrimarySmtpAddress'):
                            return exchange_user.PrimarySmtpAddress
                except:
                    pass
                
                # Fallback: extract from sender name if it contains email
                email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', sender_name)
                if email_match:
                    return email_match.group()
                
                return sender_email  # Return as-is if can't resolve
            
            # Regular email address
            return sender_email
            
        except Exception as e:
            logger.debug(f"Error extracting email address: {e}")
            return sender_email
    
    def mark_email_as_read(self, entry_id: str):
        """Mark email as read."""
        try:
            mail = self.namespace.GetItemFromID(entry_id)
            mail.UnRead = False
            mail.Save()
        except Exception as e:
            logger.error(f"Error marking email as read: {e}")
    
    def cleanup(self):
        """Cleanup COM resources."""
        try:
            if self.outlook:
                self.outlook = None
            pythoncom.CoUninitialize()
        except Exception as e:
            logger.error(f"Error during COM cleanup: {e}")

class EmailTools:
    """Collection of email-related tools for the agent."""
    
    def __init__(self):
        self.outlook_service = OutlookService()
        self.llm_service = None
    
    async def initialize(self):
        """Initialize email tools."""
        try:
            success = self.outlook_service.initialize()
            if not success:
                raise Exception("Failed to initialize Outlook service")
            
            self.llm_service = LLMService()
            await self.llm_service.initialize()
            
            logger.info("Email tools initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize email tools: {e}")
            raise
    
    @property
    def send_team_update_request(self):
        """Tool for sending update requests to team members."""
        
        class SendUpdateRequestTool(BaseTool):
            name = "send_team_update_request"
            description = "Send weekly update request emails to specified team members"
            
            def __init__(self, email_tools):
                super().__init__()
                self.email_tools = email_tools
            
            def _run(self, team_members: List[str], template: str, subject: str) -> str:
                try:
                    # Get email template
                    template_obj = EmailTemplate.get_or_none(EmailTemplate.name == template)
                    if not template_obj:
                        template_obj = EmailTemplate.get_or_none(EmailTemplate.template_type == 'update_request')
                    
                    if not template_obj:
                        return "Error: No email template found"
                    
                    sent_count = 0
                    errors = []
                    
                    for member_email in team_members:
                        try:
                            # Get team member info
                            member = TeamMember.get_or_none(TeamMember.email == member_email)
                            if not member:
                                errors.append(f"Team member not found: {member_email}")
                                continue
                            
                            # Generate personalized email content
                            context = {
                                'name': member.name,
                                'date': datetime.now().strftime('%B %d, %Y'),
                                'role': member.role
                            }
                            
                            # Replace template variables
                            email_subject = template_obj.subject
                            email_body = template_obj.content
                            
                            for var, value in context.items():
                                email_subject = email_subject.replace(f'{{{{{var}}}}}', str(value))
                                email_body = email_body.replace(f'{{{{{var}}}}}', str(value))
                            
                            # Send email
                            result = self.email_tools.outlook_service.send_email(
                                to_addresses=[member_email],
                                subject=email_subject,
                                body=email_body
                            )
                            
                            if result['success']:
                                # Create email thread record
                                EmailThread.create(
                                    thread_id=f"update_request_{member.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                                    team_member=member,
                                    subject=email_subject,
                                    sent_at=datetime.now(),
                                    status='sent',
                                    content=email_body,
                                    follow_up_count=0
                                )
                                sent_count += 1
                            else:
                                errors.append(f"Failed to send to {member_email}: {result.get('error', 'Unknown error')}")
                                
                        except Exception as e:
                            errors.append(f"Error sending to {member_email}: {str(e)}")
                    
                    result_msg = f"Successfully sent update requests to {sent_count} team members"
                    if errors:
                        result_msg += f". Errors: {'; '.join(errors)}"
                    
                    logger.info(result_msg)
                    return result_msg
                    
                except Exception as e:
                    error_msg = f"Error in send_team_update_request: {str(e)}"
                    logger.error(error_msg)
                    return error_msg
            
            async def _arun(self, team_members: List[str], template: str, subject: str) -> str:
                return self._run(team_members, template, subject)
        
        return SendUpdateRequestTool(self)
    
    @property
    def monitor_inbox_responses(self):
        """Tool for monitoring email responses."""
        
        class MonitorInboxTool(BaseTool):
            name = "monitor_inbox_responses"
            description = "Monitor and collect email responses from team members"
            
            def __init__(self, email_tools):
                super().__init__()
                self.email_tools = email_tools
            
            def _run(self, since_timestamp: datetime) -> List[Dict]:
                try:
                    # Get team member emails
                    team_members = list(TeamMember.select().where(TeamMember.active == True))
                    team_emails = [member.email for member in team_members]
                    
                    # Get recent emails from team members
                    emails = self.email_tools.outlook_service.get_recent_emails(
                        since_date=since_timestamp,
                        from_addresses=team_emails
                    )
                    
                    responses = []
                    
                    for email in emails:
                        try:
                            # Find corresponding team member
                            member = TeamMember.get_or_none(TeamMember.email == email['sender_email'])
                            if not member:
                                continue
                            
                            # Check if this is a response to our request
                            subject_lower = email['subject'].lower()
                            if any(keyword in subject_lower for keyword in ['update', 'status', 'progress', 're:']):
                                
                                # Update or create email thread
                                thread = EmailThread.get_or_none(
                                    EmailThread.team_member == member,
                                    EmailThread.response_received == False
                                )
                                
                                if thread:
                                    thread.response_received = True
                                    thread.response_at = email['received_time']
                                    thread.status = 'replied'
                                    thread.save()
                                
                                responses.append({
                                    'sender': email['sender_email'],
                                    'sender_name': email['sender_name'],
                                    'subject': email['subject'],
                                    'content': email['body'],
                                    'received_time': email['received_time'],
                                    'team_member_id': member.id,
                                    'entry_id': email['entry_id']
                                })
                                
                                # Mark email as read
                                self.email_tools.outlook_service.mark_email_as_read(email['entry_id'])
                        
                        except Exception as e:
                            logger.error(f"Error processing email response: {e}")
                            continue
                    
                    logger.info(f"Found {len(responses)} new responses from team members")
                    return responses
                    
                except Exception as e:
                    logger.error(f"Error monitoring inbox: {e}")
                    return []
            
            async def _arun(self, since_timestamp: datetime) -> List[Dict]:
                return self._run(since_timestamp)
        
        return MonitorInboxTool(self)
    
    @property
    def parse_email_content(self):
        """Tool for parsing email content."""
        
        class ParseEmailTool(BaseTool):
            name = "parse_email_content"
            description = "Parse email responses to extract structured task information"
            
            def __init__(self, email_tools):
                super().__init__()
                self.email_tools = email_tools
            
            def _run(self, email_content: str) -> Dict[str, Any]:
                try:
                    if not self.email_tools.llm_service:
                        return self._fallback_parsing(email_content)
                    
                    # Use LLM to parse email content
                    parsed_data = asyncio.run(
                        self.email_tools.llm_service.parse_email_content(email_content)
                    )
                    
                    if not parsed_data:
                        return self._fallback_parsing(email_content)
                    
                    return parsed_data
                    
                except Exception as e:
                    logger.error(f"Error parsing email content: {e}")
                    return self._fallback_parsing(email_content)
            
            def _fallback_parsing(self, email_content: str) -> Dict[str, Any]:
                """Fallback parsing when LLM is not available."""
                content_lower = email_content.lower()
                
                # Extract basic information
                result = {
                    'task_title': 'Email Update',
                    'description': email_content[:200] + "..." if len(email_content) > 200 else email_content,
                    'status': 'in_progress',
                    'priority': 'medium'
                }
                
                # Simple status detection
                if any(word in content_lower for word in ['done', 'completed', 'finished', 'complete']):
                    result['status'] = 'done'
                elif any(word in content_lower for word in ['blocked', 'stuck', 'issue', 'problem']):
                    result['status'] = 'blocked'
                elif any(word in content_lower for word in ['review', 'feedback', 'check']):
                    result['status'] = 'review'
                elif any(word in content_lower for word in ['starting', 'begin', 'todo', 'plan']):
                    result['status'] = 'todo'
                
                # Simple priority detection
                if any(word in content_lower for word in ['urgent', 'asap', 'critical', 'emergency']):
                    result['priority'] = 'urgent'
                elif any(word in content_lower for word in ['high', 'important', 'priority']):
                    result['priority'] = 'high'
                elif any(word in content_lower for word in ['low', 'minor', 'later']):
                    result['priority'] = 'low'
                
                return result
            
            async def _arun(self, email_content: str) -> Dict[str, Any]:
                return self._run(email_content)
        
        return ParseEmailTool(self)
    
    @property
    def send_follow_up_email(self):
        """Tool for sending follow-up emails."""
        
        class SendFollowUpTool(BaseTool):
            name = "send_follow_up_email"
            description = "Send follow-up reminders for overdue tasks or missing responses"
            
            def __init__(self, email_tools):
                super().__init__()
                self.email_tools = email_tools
            
            def _run(self, recipient: str, task_info: Dict, template: str) -> str:
                try:
                    # Get team member
                    member = TeamMember.get_or_none(TeamMember.email == recipient)
                    if not member:
                        return f"Error: Team member not found: {recipient}"
                    
                    # Get email template
                    template_obj = EmailTemplate.get_or_none(EmailTemplate.name == template)
                    if not template_obj:
                        template_obj = EmailTemplate.get_or_none(EmailTemplate.template_type == 'reminder')
                    
                    if not template_obj:
                        return "Error: No reminder template found"
                    
                    # Prepare context
                    context = {
                        'name': member.name,
                        'task_name': task_info.get('title', 'Task'),
                        'due_date': task_info.get('due_date', 'Soon'),
                        'status': task_info.get('status', 'Unknown'),
                        'priority': task_info.get('priority', 'Medium')
                    }
                    
                    # Replace template variables
                    email_subject = template_obj.subject
                    email_body = template_obj.content
                    
                    for var, value in context.items():
                        email_subject = email_subject.replace(f'{{{{{var}}}}}', str(value))
                        email_body = email_body.replace(f'{{{{{var}}}}}', str(value))
                    
                    # Send email
                    result = self.email_tools.outlook_service.send_email(
                        to_addresses=[recipient],
                        subject=email_subject,
                        body=email_body
                    )
                    
                    if result['success']:
                        # Update follow-up count
                        thread = EmailThread.get_or_none(
                            EmailThread.team_member == member,
                            EmailThread.response_received == False
                        )
                        
                        if thread:
                            thread.follow_up_count += 1
                            thread.save()
                        
                        return f"Follow-up email sent to {recipient}"
                    else:
                        return f"Failed to send follow-up to {recipient}: {result.get('error', 'Unknown error')}"
                        
                except Exception as e:
                    error_msg = f"Error sending follow-up email: {str(e)}"
                    logger.error(error_msg)
                    return error_msg
            
            async def _arun(self, recipient: str, task_info: Dict, template: str) -> str:
                return self._run(recipient, task_info, template)
        
        return SendFollowUpTool(self)
    
    async def get_active_team_members(self) -> List[Dict[str, Any]]:
        """Get list of active team members from database."""
        try:
            members = list(TeamMember.select().where(TeamMember.active == True))
            return [
                {
                    'id': member.id,
                    'name': member.name,
                    'email': member.email,
                    'role': member.role,
                    'response_rate': member.response_rate,
                    'last_response_at': member.last_response_at
                }
                for member in members
            ]
        except Exception as e:
            logger.error(f"Error getting active team members: {e}")
            return []
    
    def search_outlook_contacts(self, search_term: str) -> List[Dict[str, Any]]:
        """Search Outlook contacts for potential team members."""
        try:
            return self.outlook_service.search_contacts(search_term)
        except Exception as e:
            logger.error(f"Error searching Outlook contacts: {e}")
            return []
    
    async def cleanup(self):
        """Cleanup email tools resources."""
        try:
            self.outlook_service.cleanup()
            if self.llm_service:
                await self.llm_service.cleanup()
        except Exception as e:
            logger.error(f"Error during email tools cleanup: {e}")