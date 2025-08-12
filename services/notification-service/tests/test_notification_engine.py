import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
import json
import uuid

from src.notification_engine import NotificationEngine

@pytest.fixture
def notification_engine():
    """Create notification engine instance"""
    return NotificationEngine()

@pytest.fixture
def mock_db_session():
    """Mock database session"""
    session = Mock()
    session.execute = Mock()
    session.commit = Mock()
    return session

@pytest.fixture
def sample_notification_data():
    """Sample notification data for testing"""
    return {
        "user_id": "user-123",
        "title": "Test Notification",
        "message": "This is a test notification",
        "notification_type": "info",
        "priority": "normal",
        "channels": ["email", "in_app"],
        "metadata": {
            "email": "test@example.com",
            "category": "system"
        }
    }

class TestNotificationEngine:
    """Test cases for NotificationEngine"""
    
    @pytest.mark.asyncio
    async def test_send_notification_success(self, notification_engine, sample_notification_data):
        """Test successful notification sending"""
        with patch('src.notification_engine.get_session') as mock_get_session:
            mock_session = Mock()
            mock_session.execute = Mock()
            mock_session.commit = Mock()
            mock_get_session.return_value = mock_session
            
            # Mock UUID generation
            with patch('uuid.uuid4') as mock_uuid:
                mock_uuid.return_value = "notif-123"
                
                result = await notification_engine.send_notification(
                    sample_notification_data["user_id"],
                    sample_notification_data["title"],
                    sample_notification_data["message"],
                    sample_notification_data["notification_type"],
                    sample_notification_data["priority"],
                    sample_notification_data["channels"],
                    sample_notification_data["metadata"]
                )
                
                assert result == "notif-123"
                assert mock_session.execute.call_count >= 1
                assert mock_session.commit.call_count >= 1
    
    @pytest.mark.asyncio
    async def test_send_notification_default_channels(self, notification_engine):
        """Test notification sending with default channels"""
        with patch('src.notification_engine.get_session') as mock_get_session:
            mock_session = Mock()
            mock_session.execute = Mock()
            mock_session.commit = Mock()
            mock_get_session.return_value = mock_session
            
            with patch('uuid.uuid4') as mock_uuid:
                mock_uuid.return_value = "notif-456"
                
                result = await notification_engine.send_notification(
                    "user-456",
                    "Test Title",
                    "Test Message"
                )
                
                assert result == "notif-456"
                # Should use default channels (in_app)
                assert mock_session.execute.call_count >= 1
    
    @pytest.mark.asyncio
    async def test_send_notification_database_error(self, notification_engine, sample_notification_data):
        """Test notification sending with database error"""
        with patch('src.notification_engine.get_session') as mock_get_session:
            mock_session = Mock()
            mock_session.execute.side_effect = Exception("Database error")
            mock_get_session.return_value = mock_session
            
            with pytest.raises(Exception, match="Database error"):
                await notification_engine.send_notification(
                    sample_notification_data["user_id"],
                    sample_notification_data["title"],
                    sample_notification_data["message"]
                )
    
    @pytest.mark.asyncio
    async def test_bulk_notifications_success(self, notification_engine):
        """Test successful bulk notification sending"""
        user_ids = ["user-1", "user-2", "user-3"]
        
        with patch.object(notification_engine, 'send_notification') as mock_send:
            mock_send.return_value = "notif-id"
            
            result = await notification_engine.send_bulk_notifications(
                user_ids,
                "Bulk Title",
                "Bulk Message"
            )
            
            assert result["total_users"] == 3
            assert result["successful"] == 3
            assert result["failed"] == 0
            assert len(result["notification_ids"]) == 3
            assert mock_send.call_count == 3
    
    @pytest.mark.asyncio
    async def test_bulk_notifications_partial_failure(self, notification_engine):
        """Test bulk notifications with partial failures"""
        user_ids = ["user-1", "user-2", "user-3"]
        
        with patch.object(notification_engine, 'send_notification') as mock_send:
            mock_send.side_effect = [
                "notif-1",
                Exception("User 2 failed"),
                "notif-3"
            ]
            
            result = await notification_engine.send_bulk_notifications(
                user_ids,
                "Bulk Title",
                "Bulk Message"
            )
            
            assert result["total_users"] == 3
            assert result["successful"] == 2
            assert result["failed"] == 1
            assert len(result["errors"]) == 1
            assert result["errors"][0]["user_id"] == "user-2"
    
    @pytest.mark.asyncio
    async def test_schedule_notification_success(self, notification_engine, sample_notification_data):
        """Test successful notification scheduling"""
        scheduled_time = datetime.now() + timedelta(hours=1)
        
        with patch('src.notification_engine.get_session') as mock_get_session:
            mock_session = Mock()
            mock_session.execute = Mock()
            mock_session.commit = Mock()
            mock_get_session.return_value = mock_session
            
            with patch('uuid.uuid4') as mock_uuid:
                mock_uuid.return_value = "scheduled-123"
                
                with patch('asyncio.create_task') as mock_create_task:
                    result = await notification_engine.schedule_notification(
                        sample_notification_data["user_id"],
                        sample_notification_data["title"],
                        sample_notification_data["message"],
                        scheduled_time
                    )
                    
                    assert result == "scheduled-123"
                    assert mock_create_task.call_count == 1
    
    @pytest.mark.asyncio
    async def test_get_user_notifications_success(self, notification_engine):
        """Test successful retrieval of user notifications"""
        with patch('src.notification_engine.get_session') as mock_get_session:
            mock_session = Mock()
            
            # Mock database result
            mock_result = Mock()
            mock_result.fetchall.return_value = [
                Mock(
                    id="notif-1",
                    title="Test 1",
                    message="Message 1",
                    notification_type="info",
                    priority="normal",
                    created_at=datetime.now(),
                    read_at=None,
                    metadata='{"category": "test"}'
                ),
                Mock(
                    id="notif-2",
                    title="Test 2",
                    message="Message 2",
                    notification_type="warning",
                    priority="high",
                    created_at=datetime.now(),
                    read_at=datetime.now(),
                    metadata=None
                )
            ]
            
            mock_session.execute.return_value = mock_result
            mock_get_session.return_value = mock_session
            
            result = await notification_engine.get_user_notifications("user-123")
            
            assert len(result) == 2
            assert result[0]["title"] == "Test 1"
            assert result[1]["title"] == "Test 2"
            assert result[0]["notification_type"] == "info"
            assert result[1]["notification_type"] == "warning"
    
    @pytest.mark.asyncio
    async def test_get_user_notifications_unread_only(self, notification_engine):
        """Test retrieval of unread notifications only"""
        with patch('src.notification_engine.get_session') as mock_get_session:
            mock_session = Mock()
            
            mock_result = Mock()
            mock_result.fetchall.return_value = [
                Mock(
                    id="notif-1",
                    title="Unread",
                    message="Unread message",
                    notification_type="info",
                    priority="normal",
                    created_at=datetime.now(),
                    read_at=None,
                    metadata=None
                )
            ]
            
            mock_session.execute.return_value = mock_result
            mock_get_session.return_value = mock_session
            
            result = await notification_engine.get_user_notifications(
                "user-123", 
                unread_only=True
            )
            
            assert len(result) == 1
            assert result[0]["title"] == "Unread"
    
    @pytest.mark.asyncio
    async def test_mark_notification_read_success(self, notification_engine):
        """Test successful marking of notification as read"""
        with patch('src.notification_engine.get_session') as mock_get_session:
            mock_session = Mock()
            
            mock_result = Mock()
            mock_result.rowcount = 1
            mock_session.execute.return_value = mock_result
            mock_get_session.return_value = mock_session
            
            result = await notification_engine.mark_notification_read(
                "notif-123",
                "user-123"
            )
            
            assert result is True
            assert mock_session.commit.call_count == 1
    
    @pytest.mark.asyncio
    async def test_mark_notification_read_not_found(self, notification_engine):
        """Test marking non-existent notification as read"""
        with patch('src.notification_engine.get_session') as mock_get_session:
            mock_session = Mock()
            
            mock_result = Mock()
            mock_result.rowcount = 0
            mock_session.execute.return_value = mock_result
            mock_get_session.return_value = mock_session
            
            result = await notification_engine.mark_notification_read(
                "notif-999",
                "user-123"
            )
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_get_notification_stats_success(self, notification_engine):
        """Test successful retrieval of notification statistics"""
        with patch('src.notification_engine.get_session') as mock_get_session:
            mock_session = Mock()
            
            mock_result = Mock()
            mock_result.fetchone.return_value = Mock(
                total=10,
                unread=3,
                info=5,
                warning=3,
                error=1,
                success=1
            )
            
            mock_session.execute.return_value = mock_result
            mock_get_session.return_value = mock_session
            
            result = await notification_engine.get_notification_stats("user-123")
            
            assert result["total"] == 10
            assert result["unread"] == 3
            assert result["info"] == 5
            assert result["warning"] == 3
            assert result["error"] == 1
            assert result["success"] == 1
    
    @pytest.mark.asyncio
    async def test_get_notification_stats_no_data(self, notification_engine):
        """Test notification stats when no data exists"""
        with patch('src.notification_engine.get_session') as mock_get_session:
            mock_session = Mock()
            
            mock_result = Mock()
            mock_result.fetchone.return_value = None
            
            mock_session.execute.return_value = mock_result
            mock_get_session.return_value = mock_session
            
            result = await notification_engine.get_notification_stats("user-123")
            
            assert result["total"] == 0
            assert result["unread"] == 0
            assert result["info"] == 0
            assert result["warning"] == 0
            assert result["error"] == 0
            assert result["success"] == 0

class TestNotificationDelivery:
    """Test cases for notification delivery methods"""
    
    @pytest.mark.asyncio
    async def test_email_notification_delivery(self, notification_engine):
        """Test email notification delivery"""
        with patch.object(notification_engine, '_send_email_notification') as mock_email:
            mock_email.return_value = {"success": True, "email": "test@example.com"}
            
            result = await notification_engine._deliver_notification(
                "notif-123",
                "user-123",
                "Test Title",
                "Test Message",
                "info",
                "normal",
                "email",
                {"email": "test@example.com"}
            )
            
            assert result["channel"] == "email"
            assert result["success"] is True
            assert result["error"] is None
            assert result["duration"] > 0
    
    @pytest.mark.asyncio
    async def test_push_notification_delivery(self, notification_engine):
        """Test push notification delivery"""
        with patch.object(notification_engine, '_send_push_notification') as mock_push:
            mock_push.return_value = {"success": True, "devices": 2}
            
            result = await notification_engine._deliver_notification(
                "notif-123",
                "user-123",
                "Test Title",
                "Test Message",
                "info",
                "normal",
                "push",
                {"device_tokens": ["token1", "token2"]}
            )
            
            assert result["channel"] == "push"
            assert result["success"] is True
            assert result["error"] is None
            assert result["duration"] > 0
    
    @pytest.mark.asyncio
    async def test_sms_notification_delivery(self, notification_engine):
        """Test SMS notification delivery"""
        with patch.object(notification_engine, '_send_sms_notification') as mock_sms:
            mock_sms.return_value = {"success": True, "phone": "+1234567890"}
            
            result = await notification_engine._deliver_notification(
                "notif-123",
                "user-123",
                "Test Title",
                "Test Message",
                "info",
                "normal",
                "sms",
                {"phone_number": "+1234567890"}
            )
            
            assert result["channel"] == "sms"
            assert result["success"] is True
            assert result["error"] is None
            assert result["duration"] > 0
    
    @pytest.mark.asyncio
    async def test_in_app_notification_delivery(self, notification_engine):
        """Test in-app notification delivery"""
        with patch.object(notification_engine, '_send_in_app_notification') as mock_in_app:
            mock_in_app.return_value = {"success": True}
            
            result = await notification_engine._deliver_notification(
                "notif-123",
                "user-123",
                "Test Title",
                "Test Message",
                "info",
                "normal",
                "in_app",
                None
            )
            
            assert result["channel"] == "in_app"
            assert result["success"] is True
            assert result["error"] is None
            assert result["duration"] > 0
    
    @pytest.mark.asyncio
    async def test_unsupported_channel_delivery(self, notification_engine):
        """Test delivery through unsupported channel"""
        result = await notification_engine._deliver_notification(
            "notif-123",
            "user-123",
            "Test Title",
            "Test Message",
            "info",
            "normal",
            "unsupported",
            None
        )
        
        assert result["channel"] == "unsupported"
        assert result["success"] is False
        assert "Unsupported channel" in result["error"]
        assert result["duration"] == 0

class TestNotificationChannels:
    """Test cases for specific notification channels"""
    
    @pytest.mark.asyncio
    async def test_email_notification_success(self, notification_engine):
        """Test successful email notification"""
        result = await notification_engine._send_email_notification(
            "user-123",
            "Test Title",
            "Test Message",
            {"email": "test@example.com"}
        )
        
        assert result["success"] is True
        assert result["email"] == "test@example.com"
    
    @pytest.mark.asyncio
    async def test_email_notification_fallback(self, notification_engine):
        """Test email notification with fallback email"""
        result = await notification_engine._send_email_notification(
            "user-123",
            "Test Title",
            "Test Message",
            None
        )
        
        assert result["success"] is True
        assert "user-123@example.com" in result["email"]
    
    @pytest.mark.asyncio
    async def test_push_notification_success(self, notification_engine):
        """Test successful push notification"""
        result = await notification_engine._send_push_notification(
            "user-123",
            "Test Title",
            "Test Message",
            {"device_tokens": ["token1", "token2"]}
        )
        
        assert result["success"] is True
        assert result["devices"] == 2
    
    @pytest.mark.asyncio
    async def test_push_notification_fallback(self, notification_engine):
        """Test push notification with fallback tokens"""
        result = await notification_engine._send_push_notification(
            "user-123",
            "Test Title",
            "Test Message",
            None
        )
        
        assert result["success"] is True
        assert result["devices"] == 2
    
    @pytest.mark.asyncio
    async def test_sms_notification_success(self, notification_engine):
        """Test successful SMS notification"""
        result = await notification_engine._send_sms_notification(
            "user-123",
            "Test Title",
            "Test Message",
            {"phone_number": "+1234567890"}
        )
        
        assert result["success"] is True
        assert result["phone"] == "+1234567890"
    
    @pytest.mark.asyncio
    async def test_sms_notification_fallback(self, notification_engine):
        """Test SMS notification with fallback number"""
        result = await notification_engine._send_sms_notification(
            "user-123",
            "Test Title",
            "Test Message",
            None
        )
        
        assert result["success"] is True
        assert "+1-555-" in result["phone"]
    
    @pytest.mark.asyncio
    async def test_in_app_notification_success(self, notification_engine):
        """Test successful in-app notification"""
        result = await notification_engine._send_in_app_notification(
            "user-123",
            "Test Title",
            "Test Message",
            None
        )
        
        assert result["success"] is True

class TestNotificationScheduling:
    """Test cases for notification scheduling"""
    
    @pytest.mark.asyncio
    async def test_scheduled_notification_delivery(self, notification_engine):
        """Test scheduled notification delivery"""
        scheduled_time = datetime.now() + timedelta(seconds=1)
        
        with patch('src.notification_engine.get_session') as mock_get_session:
            mock_session = Mock()
            
            mock_result = Mock()
            mock_result.fetchone.return_value = Mock(
                user_id="user-123",
                title="Scheduled Title",
                message="Scheduled Message",
                notification_type="info",
                priority="normal",
                channels='["in_app"]',
                metadata=None
            )
            
            mock_session.execute.return_value = mock_result
            mock_get_session.return_value = mock_session
            
            with patch.object(notification_engine, 'send_notification') as mock_send:
                mock_send.return_value = "delivered-123"
                
                # Start the scheduled delivery task
                task = asyncio.create_task(
                    notification_engine._deliver_scheduled_notification(
                        "scheduled-123",
                        scheduled_time
                    )
                )
                
                # Wait for completion
                await asyncio.wait_for(task, timeout=5.0)
                
                # Verify the notification was sent
                mock_send.assert_called_once()
                assert mock_session.commit.call_count >= 1

class TestErrorHandling:
    """Test cases for error handling"""
    
    @pytest.mark.asyncio
    async def test_delivery_error_handling(self, notification_engine):
        """Test error handling during notification delivery"""
        with patch.object(notification_engine, '_send_email_notification') as mock_email:
            mock_email.side_effect = Exception("Email service unavailable")
            
            result = await notification_engine._deliver_notification(
                "notif-123",
                "user-123",
                "Test Title",
                "Test Message",
                "info",
                "normal",
                "email",
                None
            )
            
            assert result["channel"] == "email"
            assert result["success"] is False
            assert "Email service unavailable" in result["error"]
            assert result["duration"] == 0
    
    @pytest.mark.asyncio
    async def test_database_error_handling(self, notification_engine):
        """Test error handling during database operations"""
        with patch('src.notification_engine.get_session') as mock_get_session:
            mock_session = Mock()
            mock_session.execute.side_effect = Exception("Database connection failed")
            mock_get_session.return_value = mock_session
            
            with pytest.raises(Exception, match="Database connection failed"):
                await notification_engine.send_notification(
                    "user-123",
                    "Test Title",
                    "Test Message"
                )

if __name__ == "__main__":
    pytest.main([__file__])
