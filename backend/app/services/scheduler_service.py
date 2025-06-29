"""Scheduler service for automated workflows."""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional
import schedule

logger = logging.getLogger(__name__)

class SchedulerService:
    """Service for scheduling automated workflows."""
    
    def __init__(self, agent):
        self.agent = agent
        self.is_running = False
        self.scheduler_task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start the scheduler service."""
        try:
            self.is_running = True
            
            # Schedule weekly update requests (Mondays at 9 AM)
            schedule.every().monday.at("09:00").do(self._trigger_weekly_updates)
            
            # Schedule daily deadline checks (every day at 8 AM)
            schedule.every().day.at("08:00").do(self._trigger_deadline_check)
            
            # Schedule kanban maintenance (every 4 hours)
            schedule.every(4).hours.do(self._trigger_kanban_maintenance)
            
            # Start scheduler loop
            self.scheduler_task = asyncio.create_task(self._scheduler_loop())
            
            logger.info("Scheduler service started")
            
        except Exception as e:
            logger.error(f"Failed to start scheduler service: {e}")
            raise
    
    async def stop(self):
        """Stop the scheduler service."""
        try:
            self.is_running = False
            
            if self.scheduler_task:
                self.scheduler_task.cancel()
                try:
                    await self.scheduler_task
                except asyncio.CancelledError:
                    pass
            
            schedule.clear()
            logger.info("Scheduler service stopped")
            
        except Exception as e:
            logger.error(f"Error stopping scheduler service: {e}")
    
    async def _scheduler_loop(self):
        """Main scheduler loop."""
        while self.is_running:
            try:
                schedule.run_pending()
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                await asyncio.sleep(60)
    
    def _trigger_weekly_updates(self):
        """Trigger weekly update workflow."""
        if self.agent and self.agent.is_active:
            asyncio.create_task(
                self.agent.process_message("Please send weekly update requests to all team members")
            )
            logger.info("Triggered weekly update workflow")
    
    def _trigger_deadline_check(self):
        """Trigger deadline check workflow."""
        if self.agent and self.agent.is_active:
            asyncio.create_task(
                self.agent.process_message("Check for overdue tasks and send reminders")
            )
            logger.info("Triggered deadline check workflow")
    
    def _trigger_kanban_maintenance(self):
        """Trigger kanban maintenance workflow."""
        if self.agent and self.agent.is_active:
            asyncio.create_task(
                self.agent.process_message("Update and synchronize the kanban board")
            )
            logger.info("Triggered kanban maintenance workflow")