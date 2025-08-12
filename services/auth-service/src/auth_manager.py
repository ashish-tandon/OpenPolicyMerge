import jwt
import bcrypt
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Union
from sqlalchemy import text
from .database import get_session
import uuid
import json

logger = logging.getLogger(__name__)

class AuthManager:
    """Authentication and authorization manager"""
    
    def __init__(self, secret_key: str, algorithm: str = "HS256", 
                 access_token_expire_minutes: int = 30):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
    
    async def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate user with username and password
        
        Args:
            username: User's username
            password: User's password
        
        Returns:
            User data if authentication successful, None otherwise
        """
        try:
            session = get_session()
            
            # Get user from database
            result = session.execute(
                text("""
                    SELECT id, username, email, password_hash, first_name, last_name,
                           is_active, is_verified, last_login
                    FROM auth.users 
                    WHERE username = :username AND is_active = true
                """),
                {"username": username}
            ).fetchone()
            
            if not result:
                return None
            
            user_data = dict(result)
            
            # Verify password
            if not self._verify_password(password, user_data['password_hash']):
                return None
            
            # Update last login
            session.execute(
                text("UPDATE auth.users SET last_login = NOW() WHERE id = :user_id"),
                {"user_id": user_data['id']}
            )
            session.commit()
            
            # Get user roles
            roles = await self._get_user_roles(user_data['id'])
            user_data['roles'] = roles
            
            return user_data
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None
    
    async def create_user(self, username: str, email: str, password: str,
                         first_name: str = None, last_name: str = None) -> Optional[str]:
        """
        Create a new user
        
        Args:
            username: Username for the new user
            email: Email for the new user
            password: Password for the new user
            first_name: User's first name
            last_name: User's last name
        
        Returns:
            User ID if creation successful, None otherwise
        """
        try:
            session = get_session()
            
            # Check if username or email already exists
            existing = session.execute(
                text("""
                    SELECT id FROM auth.users 
                    WHERE username = :username OR email = :email
                """),
                {"username": username, "email": email}
            ).fetchone()
            
            if existing:
                logger.warning(f"User with username {username} or email {email} already exists")
                return None
            
            # Hash password
            password_hash = self._hash_password(password)
            
            # Create user
            user_id = str(uuid.uuid4())
            session.execute(
                text("""
                    INSERT INTO auth.users 
                    (id, username, email, password_hash, first_name, last_name, 
                     is_active, is_verified, created_at, updated_at)
                    VALUES (:id, :username, :email, :password_hash, :first_name, 
                           :last_name, true, false, NOW(), NOW())
                """),
                {
                    "id": user_id,
                    "username": username,
                    "email": email,
                    "password_hash": password_hash,
                    "first_name": first_name,
                    "last_name": last_name
                }
            )
            
            # Assign default role (user)
            await self._assign_default_role(user_id)
            
            session.commit()
            logger.info(f"User {username} created successfully")
            
            return user_id
            
        except Exception as e:
            logger.error(f"User creation error: {e}")
            return None
    
    async def create_access_token(self, user_data: Dict[str, Any]) -> str:
        """
        Create JWT access token for user
        
        Args:
            user_data: User data to include in token
        
        Returns:
            JWT access token
        """
        try:
            # Prepare token data
            to_encode = {
                "sub": user_data["id"],
                "username": user_data["username"],
                "email": user_data["email"],
                "roles": user_data.get("roles", []),
                "exp": datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes),
                "iat": datetime.utcnow()
            }
            
            # Create token
            token = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            
            # Store session in database
            await self._store_user_session(user_data["id"], token)
            
            return token
            
        except Exception as e:
            logger.error(f"Token creation error: {e}")
            raise
    
    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify and decode JWT token
        
        Args:
            token: JWT token to verify
        
        Returns:
            Decoded token data if valid, None otherwise
        """
        try:
            # Decode token
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Check if token is expired
            if datetime.fromtimestamp(payload["exp"]) < datetime.utcnow():
                return None
            
            # Verify session exists in database
            if not await self._verify_session(token):
                return None
            
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.JWTError as e:
            logger.warning(f"Invalid token: {e}")
            return None
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            return None
    
    async def refresh_token(self, token: str) -> Optional[str]:
        """
        Refresh access token
        
        Args:
            token: Current access token
        
        Returns:
            New access token if refresh successful, None otherwise
        """
        try:
            # Verify current token
            payload = await self.verify_token(token)
            if not payload:
                return None
            
            # Get user data
            session = get_session()
            result = session.execute(
                text("SELECT id, username, email FROM auth.users WHERE id = :user_id"),
                {"user_id": payload["sub"]}
            ).fetchone()
            
            if not result:
                return None
            
            user_data = dict(result)
            user_data["roles"] = payload.get("roles", [])
            
            # Create new token
            new_token = await self.create_access_token(user_data)
            
            # Invalidate old token
            await self._invalidate_session(token)
            
            return new_token
            
        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            return None
    
    async def change_password(self, user_id: str, current_password: str, 
                            new_password: str) -> bool:
        """
        Change user password
        
        Args:
            user_id: User ID
            current_password: Current password
            new_password: New password
        
        Returns:
            True if password changed successfully, False otherwise
        """
        try:
            session = get_session()
            
            # Get current password hash
            result = session.execute(
                text("SELECT password_hash FROM auth.users WHERE id = :user_id"),
                {"user_id": user_id}
            ).fetchone()
            
            if not result:
                return False
            
            current_hash = result[0]
            
            # Verify current password
            if not self._verify_password(current_password, current_hash):
                return False
            
            # Hash new password
            new_hash = self._hash_password(new_password)
            
            # Update password
            session.execute(
                text("""
                    UPDATE auth.users 
                    SET password_hash = :new_hash, updated_at = NOW()
                    WHERE id = :user_id
                """),
                {"new_hash": new_hash, "user_id": user_id}
            )
            
            session.commit()
            logger.info(f"Password changed for user {user_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Password change error: {e}")
            return False
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user by ID
        
        Args:
            user_id: User ID
        
        Returns:
            User data if found, None otherwise
        """
        try:
            session = get_session()
            
            result = session.execute(
                text("""
                    SELECT id, username, email, first_name, last_name,
                           is_active, is_verified, last_login, created_at
                    FROM auth.users 
                    WHERE id = :user_id
                """),
                {"user_id": user_id}
            ).fetchone()
            
            if not result:
                return None
            
            user_data = dict(result)
            user_data['roles'] = await self._get_user_roles(user_id)
            
            return user_data
            
        except Exception as e:
            logger.error(f"Get user error: {e}")
            return None
    
    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def _verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    async def _get_user_roles(self, user_id: str) -> list:
        """Get user roles"""
        try:
            session = get_session()
            
            result = session.execute(
                text("""
                    SELECT r.name, r.permissions
                    FROM auth.user_roles ur
                    JOIN auth.roles r ON ur.role_id = r.id
                    WHERE ur.user_id = :user_id
                """),
                {"user_id": user_id}
            ).fetchall()
            
            roles = []
            for row in result:
                role_data = dict(row)
                if role_data.get('permissions'):
                    try:
                        role_data['permissions'] = json.loads(role_data['permissions'])
                    except:
                        role_data['permissions'] = []
                roles.append(role_data)
            
            return roles
            
        except Exception as e:
            logger.error(f"Get user roles error: {e}")
            return []
    
    async def _assign_default_role(self, user_id: str):
        """Assign default 'user' role to new user"""
        try:
            session = get_session()
            
            # Get default role ID
            result = session.execute(
                text("SELECT id FROM auth.roles WHERE name = 'user'"),
            ).fetchone()
            
            if result:
                role_id = result[0]
                session.execute(
                    text("""
                        INSERT INTO auth.user_roles (id, user_id, role_id, assigned_at)
                        VALUES (:id, :user_id, :role_id, NOW())
                    """),
                    {
                        "id": str(uuid.uuid4()),
                        "user_id": user_id,
                        "role_id": role_id
                    }
                )
            
        except Exception as e:
            logger.error(f"Assign default role error: {e}")
    
    async def _store_user_session(self, user_id: str, token: str):
        """Store user session in database"""
        try:
            session = get_session()
            
            # Calculate expiration
            expires_at = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
            
            session.execute(
                text("""
                    INSERT INTO auth.user_sessions 
                    (id, user_id, session_token, expires_at, is_active, created_at)
                    VALUES (:id, :user_id, :token, :expires_at, true, NOW())
                """),
                {
                    "id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "token": token,
                    "expires_at": expires_at
                }
            )
            
            session.commit()
            
        except Exception as e:
            logger.error(f"Store session error: {e}")
    
    async def _verify_session(self, token: str) -> bool:
        """Verify session exists and is active"""
        try:
            session = get_session()
            
            result = session.execute(
                text("""
                    SELECT id FROM auth.user_sessions 
                    WHERE session_token = :token 
                    AND is_active = true 
                    AND expires_at > NOW()
                """),
                {"token": token}
            ).fetchone()
            
            return result is not None
            
        except Exception as e:
            logger.error(f"Verify session error: {e}")
            return False
    
    async def _invalidate_session(self, token: str):
        """Invalidate user session"""
        try:
            session = get_session()
            
            session.execute(
                text("""
                    UPDATE auth.user_sessions 
                    SET is_active = false 
                    WHERE session_token = :token
                """),
                {"token": token}
            )
            
            session.commit()
            
        except Exception as e:
            logger.error(f"Invalidate session error: {e}")
    
    async def logout(self, token: str) -> bool:
        """
        Logout user by invalidating session
        
        Args:
            token: Access token to invalidate
        
        Returns:
            True if logout successful, False otherwise
        """
        try:
            await self._invalidate_session(token)
            return True
        except Exception as e:
            logger.error(f"Logout error: {e}")
            return False
