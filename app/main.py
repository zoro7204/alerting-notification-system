from typing import List
from fastapi import Depends, FastAPI, HTTPException, Body
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine
import datetime

# This command creates all the database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency to get a DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- API Endpoints ---

# Admin Endpoints
@app.post("/admin/alerts", response_model=schemas.Alert)
def create_new_alert(alert: schemas.AlertCreate, db: Session = Depends(get_db)):
    return crud.create_alert(db=db, alert=alert)

@app.put("/admin/alerts/{alert_id}", response_model=schemas.Alert)
def update_alert(alert_id: int, alert_update: schemas.AlertUpdate = Body(...), db: Session = Depends(get_db)):
    db_alert = crud.update_alert(db=db, alert_id=alert_id, alert_update=alert_update)
    if db_alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    return db_alert

@app.get("/admin/alerts", response_model=List[schemas.Alert])
def read_alerts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    alerts = crud.get_alerts(db, skip=skip, limit=limit)
    return alerts

@app.post("/admin/trigger-reminders", response_model=schemas.TriggerResponse)
def trigger_reminders(db: Session = Depends(get_db)):
    new_deliveries = crud.trigger_reminders_logic(db=db)
    return {"status": "ok", "message": f"{len(new_deliveries)} new reminder notifications sent."}

# User Endpoints
@app.get("/users/{user_id}/alerts", response_model=List[schemas.UserAlert])
def read_user_alerts(user_id: int, db: Session = Depends(get_db)):
    alerts = crud.get_user_alerts(db=db, user_id=user_id)
    
    response_alerts = []
    for alert in alerts:
        preference = db.query(models.UserAlertPreference).filter_by(user_id=user_id, alert_id=alert.id).first()
        
        user_alert = schemas.UserAlert.from_orm(alert)
        if preference:
            user_alert.user_state = preference.state
            user_alert.snoozed_until = preference.snoozed_until
        
        response_alerts.append(user_alert)

    return response_alerts

@app.post("/users/{user_id}/alerts/{alert_id}/read", response_model=schemas.UserAlertPreference)
def mark_alert_as_read(user_id: int, alert_id: int, db: Session = Depends(get_db)):
    preference = crud.update_alert_preference(
        db=db, 
        user_id=user_id, 
        alert_id=alert_id, 
        state="READ"
    )
    return preference

@app.post("/users/{user_id}/alerts/{alert_id}/snooze", response_model=schemas.UserAlertPreference)
def snooze_alert(user_id: int, alert_id: int, db: Session = Depends(get_db)):
    now = datetime.datetime.utcnow()
    end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    preference = crud.update_alert_preference(
        db=db,
        user_id=user_id,
        alert_id=alert_id,
        state="SNOOZED",
        snoozed_until=end_of_day
    )
    return preference

# Analytics Endpoint
@app.get("/analytics/summary")
def get_summary(db: Session = Depends(get_db)):
    summary = crud.get_analytics_summary(db=db)
    return summary