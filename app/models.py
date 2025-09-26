import datetime
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from .database import Base

class Team(Base):
    __tablename__ = 'teams'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    users = relationship("User", back_populates="team")

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=True)
    team = relationship("Team", back_populates="users")

class Alert(Base):
    __tablename__ = 'alerts'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    message = Column(String)
    severity = Column(String)
    start_time = Column(DateTime, default=datetime.datetime.utcnow)
    expiry_time = Column(DateTime, nullable=True)
    reminders_enabled = Column(Boolean, default=True)
    archived = Column(Boolean, default=False)
    visibility = relationship("AlertVisibility", back_populates="alert", cascade="all, delete-orphan")

class AlertVisibility(Base):
    __tablename__ = 'alert_visibility'
    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, ForeignKey('alerts.id'))
    visibility_type = Column(String)  # 'ORGANIZATION', 'TEAM', or 'USER'
    ref_id = Column(Integer, nullable=True)  # team_id or user_id
    alert = relationship("Alert", back_populates="visibility")

class UserAlertPreference(Base):
    __tablename__ = 'user_alert_preferences'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    alert_id = Column(Integer, ForeignKey('alerts.id'))
    state = Column(String, default='UNREAD')  # 'UNREAD', 'READ', 'SNOOZED'
    snoozed_until = Column(DateTime, nullable=True)

class NotificationDelivery(Base):
    __tablename__ = 'notification_deliveries'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    alert_id = Column(Integer, ForeignKey('alerts.id'))
    sent_at = Column(DateTime, default=datetime.datetime.utcnow)