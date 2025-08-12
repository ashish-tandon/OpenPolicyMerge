import logging
import asyncio
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from sqlalchemy import text
from .database import get_session
import uuid
import json

logger = logging.getLogger(__name__)

class NotificationEngine:
    """Comprehensive notification delivery engine"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.max_retries = 3
        self.retry_delay = 5  # seconds
    
    async def send_notification(self, user_id: str, title: str, message: str, 
                               notification_type: str = "info", priority: str = "normal",
                               channels: List[str] = None, metadata: Optional[Dict] = None) -> str:
        """
        Send notification to user through specified channels
        
        Args:
            user_id: Target user ID
            title: Notification title
            message: Notification message
            notification_type: Type of notification (info, warning, error, success)
            priority: Priority level (low, normal, high, urgent)
            channels: List of delivery channels (email, push, sms, in_app)
            metadata: Additional notification metadata
        
        Returns:
            Notification ID if successful
        """
        try:
            # Default channels if none specified
            if not channels:
                channels = ["in_app"]
            
            # Create notification record
            notification_id = await self._create_notification_record(
                user_id, title, message, notification_type, priority, channels, metadata
            )
            
            # Send through each channel
            delivery_results = []
            for channel in channels:
                result = await self._deliver_notification(
                    notification_id, user_id, title, message, 
                    notification_type, priority, channel, metadata
                )
                delivery_results.append(result)
            
            # Update notification status
            await self._update_notification_status(notification_id, delivery_results)
            
            logger.info(f"Notification {notification_id} sent to user {user_id} through {len(channels)} channels")
            return notification_id
            
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            raise
    
    async def send_bulk_notifications(self, user_ids: List[str], title: str, message: str,
                                    notification_type: str = "info", priority: str = "normal",
                                    channels: List[str] = None, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Send notifications to multiple users
        
        Args:
            user_ids: List of target user IDs
            title: Notification title
            message: Notification message
            notification_type: Type of notification
            priority: Priority level
            channels: List of delivery channels
            metadata: Additional notification metadata
        
        Returns:
            Summary of bulk notification results
        """
        try:
            results = {
                "total_users": len(user_ids),
                "successful": 0,
                "failed": 0,
                "notification_ids": [],
                "errors": []
            }
            
            # Process notifications concurrently
            tasks = []
            for user_id in user_ids:
                task = self.send_notification(
                    user_id, title, message, notification_type, priority, channels, metadata
                )
                tasks.append(task)
            
            # Execute all notifications
            notification_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for i, result in enumerate(notification_results):
                if isinstance(result, Exception):
                    results["failed"] += 1
                    results["errors"].append({
                        "user_id": user_ids[i],
                        "error": str(result)
                    })
                else:
                    results["successful"] += 1
                    results["notification_ids"].append(result)
            
            logger.info(f"Bulk notification completed: {results['successful']} successful, {results['failed']} failed")
            return results
            
        except Exception as e:
            logger.error(f"Bulk notification failed: {e}")
            raise
    
    async def schedule_notification(self, user_id: str, title: str, message: str,
                                  scheduled_time: datetime, notification_type: str = "info",
                                  priority: str = "normal", channels: List[str] = None,
                                  metadata: Optional[Dict] = None) -> str:
        """
        Schedule notification for future delivery
        
        Args:
            user_id: Target user ID
            title: Notification title
            message: Notification message
            scheduled_time: When to deliver the notification
            notification_type: Type of notification
            priority: Priority level
            channels: List of delivery channels
            metadata: Additional notification metadata
        
        Returns:
            Scheduled notification ID
        """
        try:
            # Create scheduled notification record
            notification_id = await self._create_scheduled_notification(
                user_id, title, message, scheduled_time, notification_type, 
                priority, channels, metadata
            )
            
            # Schedule delivery task
            asyncio.create_task(self._deliver_scheduled_notification(notification_id, scheduled_time))
            
            logger.info(f"Notification {notification_id} scheduled for {scheduled_time}")
            return notification_id
            
        except Exception as e:
            logger.error(f"Failed to schedule notification: {e}")
            raise
    
    async def get_user_notifications(self, user_id: str, limit: int = 50, 
                                   offset: int = 0, unread_only: bool = False) -> List[Dict[str, Any]]:
        """
        Get notifications for a specific user
        
        Args:
            user_id: User ID
            limit: Maximum number of notifications to return
            offset: Pagination offset
            unread_only: Return only unread notifications
        
        Returns:
            List of user notifications
        """
        try:
            session = get_session()
            
            # Build query
            query = """
                SELECT id, title, message, notification_type, priority, 
                       created_at, read_at, metadata
                FROM notifications.notifications 
                WHERE user_id = :user_id
            """
            
            if unread_only:
                query += " AND read_at IS NULL"
            
            query += " ORDER BY created_at DESC LIMIT :limit OFFSET :offset"
            
            result = session.execute(
                text(query),
                {"user_id": user_id, "limit": limit, "offset": offset}
            ).fetchall()
            
            notifications = []
            for row in result:
                notification = dict(row)
                notification['created_at'] = notification['created_at'].isoformat() if notification['created_at'] else None
                notification['read_at'] = notification['read_at'].isoformat() if notification['read_at'] else None
                notifications.append(notification)
            
            return notifications
            
        except Exception as e:
            logger.error(f"Failed to get user notifications: {e}")
            return []
    
    async def mark_notification_read(self, notification_id: str, user_id: str) -> bool:
        """
        Mark notification as read
        
        Args:
            notification_id: Notification ID
            user_id: User ID
        
        Returns:
            True if successful, False otherwise
        """
        try:
            session = get_session()
            
            result = session.execute(
                text("""
                    UPDATE notifications.notifications 
                    SET read_at = NOW() 
                    WHERE id = :notification_id AND user_id = :user_id
                """),
                {"notification_id": notification_id, "user_id": user_id}
            )
            
            session.commit()
            
            if result.rowcount > 0:
                logger.info(f"Notification {notification_id} marked as read by user {user_id}")
                return True
            else:
                logger.warning(f"Notification {notification_id} not found or not owned by user {user_id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to mark notification as read: {e}")
            return False
    
    async def get_notification_stats(self, user_id: str) -> Dict[str, Any]:
        """
        Get notification statistics for a user
        
        Args:
            user_id: User ID
        
        Returns:
            Notification statistics
        """
        try:
            session = get_session()
            
            result = session.execute(
                text("""
                    SELECT 
                        COUNT(*) as total,
                        COUNT(CASE WHEN read_at IS NULL THEN 1 END) as unread,
                        COUNT(CASE WHEN notification_type = 'info' THEN 1 END) as info,
                        COUNT(CASE WHEN notification_type = 'warning' THEN 1 END) as warning,
                        COUNT(CASE WHEN notification_type = 'error' THEN 1 END) as error,
                        COUNT(CASE WHEN notification_type = 'success' THEN 1 END) as success
                    FROM notifications.notifications 
                    WHERE user_id = :user_id
                """),
                {"user_id": user_id}
            ).fetchone()
            
            if result:
                return dict(result)
            else:
                return {
                    "total": 0, "unread": 0, "info": 0, 
                    "warning": 0, "error": 0, "success": 0
                }
                
        except Exception as e:
            logger.error(f"Failed to get notification stats: {e}")
            return {}
    
    async def _create_notification_record(self, user_id: str, title: str, message: str,
                                        notification_type: str, priority: str,
                                        channels: List[str], metadata: Optional[Dict]) -> str:
        """Create notification record in database"""
        try:
            session = get_session()
            
            notification_id = str(uuid.uuid4())
            
            session.execute(
                text("""
                    INSERT INTO notifications.notifications 
                    (id, user_id, title, message, notification_type, priority, 
                     channels, metadata, created_at, updated_at)
                    VALUES (:id, :user_id, :title, :message, :notification_type, 
                           :priority, :channels, :metadata, NOW(), NOW())
                """),
                {
                    "id": notification_id,
                    "user_id": user_id,
                    "title": title,
                    "message": message,
                    "notification_type": notification_type,
                    "priority": priority,
                    "channels": json.dumps(channels),
                    "metadata": json.dumps(metadata) if metadata else None
                }
            )
            
            session.commit()
            return notification_id
            
        except Exception as e:
            logger.error(f"Failed to create notification record: {e}")
            raise
    
    async def _deliver_notification(self, notification_id: str, user_id: str, title: str,
                                  message: str, notification_type: str, priority: str,
                                  channel: str, metadata: Optional[Dict]) -> Dict[str, Any]:
        """Deliver notification through specific channel"""
        try:
            start_time = datetime.now()
            
            # Channel-specific delivery logic
            if channel == "email":
                result = await self._send_email_notification(user_id, title, message, metadata)
            elif channel == "push":
                result = await self._send_push_notification(user_id, title, message, metadata)
            elif channel == "sms":
                result = await self._send_sms_notification(user_id, title, message, metadata)
            elif channel == "in_app":
                result = await self._send_in_app_notification(user_id, title, message, metadata)
            else:
                result = {"success": False, "error": f"Unsupported channel: {channel}"}
            
            # Calculate delivery duration
            duration = (datetime.now() - start_time).total_seconds()
            
            # Record delivery attempt
            await self._record_delivery_attempt(
                notification_id, channel, result["success"], 
                result.get("error"), duration
            )
            
            return {
                "channel": channel,
                "success": result["success"],
                "error": result.get("error"),
                "duration": duration
            }
            
        except Exception as e:
            logger.error(f"Failed to deliver notification through {channel}: {e}")
            return {
                "channel": channel,
                "success": False,
                "error": str(e),
                "duration": 0
            }
    
    async def _send_email_notification(self, user_id: str, title: str, message: str, 
                                     metadata: Optional[Dict]) -> Dict[str, Any]:
        """Send email notification"""
        try:
            # Get user email from metadata or user service
            user_email = metadata.get("email") if metadata else None
            
            if not user_email:
                # In a real implementation, fetch from user service
                user_email = f"user-{user_id}@example.com"
            
            # Simulate email sending
            await asyncio.sleep(0.1)  # Simulate network delay
            
            logger.info(f"Email notification sent to {user_email}: {title}")
            
            return {"success": True, "email": user_email}
            
        except Exception as e:
            logger.error(f"Email notification failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _send_push_notification(self, user_id: str, title: str, message: str,
                                    metadata: Optional[Dict]) -> Dict[str, Any]:
        """Send push notification"""
        try:
            # Get device tokens from metadata or user service
            device_tokens = metadata.get("device_tokens", []) if metadata else []
            
            if not device_tokens:
                # In a real implementation, fetch from user service
                device_tokens = [f"device-{user_id}-{i}" for i in range(2)]
            
            # Simulate push notification sending
            await asyncio.sleep(0.05)  # Simulate network delay
            
            logger.info(f"Push notification sent to {len(device_tokens)} devices: {title}")
            
            return {"success": True, "devices": len(device_tokens)}
            
        except Exception as e:
            logger.error(f"Push notification failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _send_sms_notification(self, user_id: str, title: str, message: str,
                                   metadata: Optional[Dict]) -> Dict[str, Any]:
        """Send SMS notification"""
        try:
            # Get phone number from metadata or user service
            phone_number = metadata.get("phone_number") if metadata else None
            
            if not phone_number:
                # In a real implementation, fetch from user service
                phone_number = f"+1-555-{user_id[-4:]}"
            
            # Simulate SMS sending
            await asyncio.sleep(0.02)  # Simulate network delay
            
            logger.info(f"SMS notification sent to {phone_number}: {title}")
            
            return {"success": True, "phone": phone_number}
            
        except Exception as e:
            logger.error(f"SMS notification failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _send_in_app_notification(self, user_id: str, title: str, message: str,
                                      metadata: Optional[Dict]) -> Dict[str, Any]:
        """Send in-app notification"""
        try:
            # In-app notifications are stored in the database
            # No external delivery needed
            
            logger.info(f"In-app notification stored for user {user_id}: {title}")
            
            return {"success": True}
            
        except Exception as e:
            logger.error(f"In-app notification failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _create_scheduled_notification(self, user_id: str, title: str, message: str,
                                           scheduled_time: datetime, notification_type: str,
                                           priority: str, channels: List[str],
                                           metadata: Optional[Dict]) -> str:
        """Create scheduled notification record"""
        try:
            session = get_session()
            
            notification_id = str(uuid.uuid4())
            
            session.execute(
                text("""
                    INSERT INTO notifications.scheduled_notifications 
                    (id, user_id, title, message, notification_type, priority,
                     channels, metadata, scheduled_time, created_at)
                    VALUES (:id, :user_id, :title, :message, :notification_type,
                           :priority, :channels, :metadata, :scheduled_time, NOW())
                """),
                {
                    "id": notification_id,
                    "user_id": user_id,
                    "title": title,
                    "message": message,
                    "notification_type": notification_type,
                    "priority": priority,
                    "channels": json.dumps(channels),
                    "metadata": json.dumps(metadata) if metadata else None,
                    "scheduled_time": scheduled_time
                }
            )
            
            session.commit()
            return notification_id
            
        except Exception as e:
            logger.error(f"Failed to create scheduled notification: {e}")
            raise
    
    async def _deliver_scheduled_notification(self, notification_id: str, scheduled_time: datetime):
        """Deliver scheduled notification at specified time"""
        try:
            # Calculate delay until scheduled time
            now = datetime.now()
            if scheduled_time > now:
                delay = (scheduled_time - now).total_seconds()
                await asyncio.sleep(delay)
            
            # Get scheduled notification details
            session = get_session()
            result = session.execute(
                text("""
                    SELECT user_id, title, message, notification_type, priority,
                           channels, metadata
                    FROM notifications.scheduled_notifications 
                    WHERE id = :notification_id
                """),
                {"notification_id": notification_id}
            ).fetchone()
            
            if result:
                notification_data = dict(result)
                
                # Send the notification
                await self.send_notification(
                    notification_data["user_id"],
                    notification_data["title"],
                    notification_data["message"],
                    notification_data["notification_type"],
                    notification_data["priority"],
                    json.loads(notification_data["channels"]),
                    json.loads(notification_data["metadata"]) if notification_data["metadata"] else None
                )
                
                # Mark as delivered
                session.execute(
                    text("""
                        UPDATE notifications.scheduled_notifications 
                        SET delivered_at = NOW() 
                        WHERE id = :notification_id
                    """),
                    {"notification_id": notification_id}
                )
                session.commit()
                
                logger.info(f"Scheduled notification {notification_id} delivered successfully")
            
        except Exception as e:
            logger.error(f"Failed to deliver scheduled notification {notification_id}: {e}")
    
    async def _update_notification_status(self, notification_id: str, delivery_results: List[Dict[str, Any]]):
        """Update notification delivery status"""
        try:
            session = get_session()
            
            # Calculate overall success
            successful_deliveries = sum(1 for result in delivery_results if result["success"])
            total_channels = len(delivery_results)
            
            status = "delivered" if successful_deliveries > 0 else "failed"
            
            session.execute(
                text("""
                    UPDATE notifications.notifications 
                    SET status = :status, delivered_at = NOW(), updated_at = NOW()
                    WHERE id = :notification_id
                """),
                {"status": status, "notification_id": notification_id}
            )
            
            session.commit()
            
        except Exception as e:
            logger.error(f"Failed to update notification status: {e}")
    
    async def _record_delivery_attempt(self, notification_id: str, channel: str, 
                                     success: bool, error: Optional[str], duration: float):
        """Record delivery attempt in database"""
        try:
            session = get_session()
            
            session.execute(
                text("""
                    INSERT INTO notifications.delivery_attempts 
                    (id, notification_id, channel, success, error_message, duration, created_at)
                    VALUES (:id, :notification_id, :channel, :success, :error, :duration, NOW())
                """),
                {
                    "id": str(uuid.uuid4()),
                    "notification_id": notification_id,
                    "channel": channel,
                    "success": success,
                    "error": error,
                    "duration": duration
                }
            )
            
            session.commit()
            
        except Exception as e:
            logger.error(f"Failed to record delivery attempt: {e}")
