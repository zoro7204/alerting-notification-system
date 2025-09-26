from sqlalchemy.orm import Session
from . import models, schemas
from sqlalchemy import or_
import datetime
from sqlalchemy import func

# Placeholder functions for now. We will implement these step-by-step.

def create_alert(db: Session, alert: schemas.AlertCreate):
    # Create the main Alert object without the visibility rules
    db_alert = models.Alert(
        title=alert.title,
        message=alert.message,
        severity=alert.severity,
        reminders_enabled=alert.reminders_enabled,
        start_time=alert.start_time,
        expiry_time=alert.expiry_time
    )
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)

    # Now, create the visibility rules associated with this alert
    for visibility_rule in alert.visibility:
        db_visibility = models.AlertVisibility(
            alert_id=db_alert.id,
            visibility_type=visibility_rule.visibility_type,
            ref_id=visibility_rule.ref_id
        )
        db.add(db_visibility)
    
    db.commit()
    db.refresh(db_alert)
    return db_alert

def get_alerts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Alert).offset(skip).limit(limit).all()

def get_user_alerts(db: Session, user_id: int):
    now = datetime.datetime.utcnow()
    
    # First, get the user's details to find their team
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return []

    # Find all alerts that are active and visible to this user
    visible_alerts = db.query(models.Alert).join(models.AlertVisibility).filter(
        models.Alert.archived == False,
        models.Alert.start_time <= now,
        (models.Alert.expiry_time == None) | (models.Alert.expiry_time > now),
        or_(
            # Organization-wide alerts
            models.AlertVisibility.visibility_type == 'ORGANIZATION',
            # Team-specific alerts
            (models.AlertVisibility.visibility_type == 'TEAM') & (models.AlertVisibility.ref_id == user.team_id),
            # User-specific alerts
            (models.AlertVisibility.visibility_type == 'USER') & (models.AlertVisibility.ref_id == user.id)
        )
    ).distinct().all()

    return visible_alerts
def update_alert_preference(db: Session, user_id: int, alert_id: int, state: str, snoozed_until: datetime.datetime = None):
    # Find the existing preference for this user and alert
    preference = db.query(models.UserAlertPreference).filter_by(
        user_id=user_id, 
        alert_id=alert_id
    ).first()

    if preference:
        # If it exists, update it
        preference.state = state
        preference.snoozed_until = snoozed_until
    else:
        # If it doesn't exist, create a new one
        preference = models.UserAlertPreference(
            user_id=user_id,
            alert_id=alert_id,
            state=state,
            snoozed_until=snoozed_until
        )
        db.add(preference)
    
    db.commit()
    db.refresh(preference)
    return preference

def trigger_reminders_logic(db: Session):
    now = datetime.datetime.utcnow()
    new_deliveries = []

    # 1. Get all active alerts
    active_alerts = db.query(models.Alert).filter(
        models.Alert.archived == False,
        models.Alert.reminders_enabled == True,
        models.Alert.start_time <= now,
        (models.Alert.expiry_time == None) | (models.Alert.expiry_time > now)
    ).all()

    for alert in active_alerts:
        # 2. Get all target users for this alert
        visibility_rules = alert.visibility
        target_user_ids = set()

        for rule in visibility_rules:
            if rule.visibility_type == 'ORGANIZATION':
                all_users = db.query(models.User).all()
                for user in all_users:
                    target_user_ids.add(user.id)
            elif rule.visibility_type == 'TEAM':
                team_users = db.query(models.User).filter(models.User.team_id == rule.ref_id).all()
                for user in team_users:
                    target_user_ids.add(user.id)
            elif rule.visibility_type == 'USER':
                target_user_ids.add(rule.ref_id)

        # 3. For each target user, check eligibility and create delivery log
        for user_id in target_user_ids:
            preference = db.query(models.UserAlertPreference).filter_by(user_id=user_id, alert_id=alert.id).first()

            is_eligible = True
            if preference:
                if preference.state == 'READ':
                    is_eligible = False
                # THIS IS THE CORRECTED LINE:
                if preference.state == 'SNOOZED' and preference.snoozed_until and preference.snoozed_until > now:
                    is_eligible = False
            
            if is_eligible:
                # 4. Create a new delivery log
                new_delivery = models.NotificationDelivery(user_id=user_id, alert_id=alert.id)
                db.add(new_delivery)
                new_deliveries.append(new_delivery)

    db.commit()
    return new_deliveries

def get_analytics_summary(db: Session):
    total_alerts = db.query(models.Alert).count()
    
    # Count alerts that have at least one delivery log
    alerts_delivered_count = db.query(func.count(models.NotificationDelivery.alert_id.distinct())).scalar()
    
    # Count read states
    alerts_read_count = db.query(models.UserAlertPreference).filter(models.UserAlertPreference.state == 'READ').count()
    
    # Count snoozed states
    alerts_snoozed_count = db.query(models.UserAlertPreference).filter(models.UserAlertPreference.state == 'SNOOZED').count()
    
    # Breakdown by severity
    severity_breakdown = db.query(models.Alert.severity, func.count(models.Alert.id)).group_by(models.Alert.severity).all()
    
    summary = {
        "total_alerts_created": total_alerts,
        "total_alerts_delivered": alerts_delivered_count,
        "total_alerts_read": alerts_read_count,
        "total_alerts_snoozed": alerts_snoozed_count,
        "breakdown_by_severity": {severity: count for severity, count in severity_breakdown}
    }
    return summary

def update_alert(db: Session, alert_id: int, alert_update: schemas.AlertUpdate):
    db_alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if not db_alert:
        return None
    
    # Get the update data as a dict, excluding any fields that were not set
    update_data = alert_update.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(db_alert, key, value)
        
    db.commit()
    db.refresh(db_alert)
    return db_alert