from app.database import SessionLocal, engine
from app import models

# This line ensures tables are created if they don't exist
models.Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    # Check if teams already exist to prevent re-seeding
    if db.query(models.Team).count() == 0:
        print("Seeding database with teams, users, and alerts...")
        
        # --- Create Teams ---
        team_eng = models.Team(name="Engineering")
        team_mkt = models.Team(name="Marketing")
        db.add_all([team_eng, team_mkt])
        db.commit()

        # --- Create Users ---
        user_alice = models.User(name="Alice", email="alice@atomic.com", team_id=team_eng.id)
        user_bob = models.User(name="Bob", email="bob@atomic.com", team_id=team_eng.id)
        user_carol = models.User(name="Carol", email="carol@atomic.com", team_id=team_mkt.id)
        user_dave = models.User(name="Dave", email="dave@atomic.com")
        db.add_all([user_alice, user_bob, user_carol, user_dave])
        db.commit()
        
        # --- Create Alert for Engineering Team (The missing part) ---
        alert1 = models.Alert(title="Deploy Freeze", message="Deploy freeze is now in effect for all backend services.", severity="Warning")
        db.add(alert1)
        db.commit()
        
        visibility1 = models.AlertVisibility(alert_id=alert1.id, visibility_type="TEAM", ref_id=team_eng.id)
        db.add(visibility1)
        db.commit()
        
        print("Database seeded successfully.")
    else:
        print("Database already seeded.")

finally:
    db.close()