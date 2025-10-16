"""Add encryption and security columns to existing database."""
from sqlalchemy import text
from core.database import engine, SessionLocal

def migrate():
    db = SessionLocal()
    try:
        print("🔄 Running database migration...")
        
        with engine.connect() as conn:
            # Add is_encrypted column to certificates
            try:
                conn.execute(text("ALTER TABLE certificates ADD COLUMN is_encrypted BOOLEAN DEFAULT 0"))
                conn.commit()
                print("✅ Added is_encrypted to certificates")
            except Exception as e:
                if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                    print("ℹ️  is_encrypted already exists in certificates")
                else:
                    print(f"⚠️  Error adding is_encrypted: {e}")
            
            # Add config_encrypted column to nebula_configs
            try:
                conn.execute(text("ALTER TABLE nebula_configs ADD COLUMN config_encrypted BOOLEAN DEFAULT 0"))
                conn.commit()
                print("✅ Added config_encrypted to nebula_configs")
            except Exception as e:
                if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                    print("ℹ️  config_encrypted already exists in nebula_configs")
                else:
                    print(f"⚠️  Error adding config_encrypted: {e}")
            
            # Add 2FA columns to users
            try:
                conn.execute(text("ALTER TABLE users ADD COLUMN two_factor_enabled BOOLEAN DEFAULT 0"))
                conn.commit()
                print("✅ Added two_factor_enabled to users")
            except Exception as e:
                if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                    print("ℹ️  two_factor_enabled already exists in users")
                else:
                    print(f"⚠️  Error adding two_factor_enabled: {e}")
            
            try:
                conn.execute(text("ALTER TABLE users ADD COLUMN two_factor_secret VARCHAR(255)"))
                conn.commit()
                print("✅ Added two_factor_secret to users")
            except Exception as e:
                if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                    print("ℹ️  two_factor_secret already exists in users")
                else:
                    print(f"⚠️  Error adding two_factor_secret: {e}")
        
        # Create new tables (SessionToken if it doesn't exist)
        from core.database import Base
        Base.metadata.create_all(bind=engine)
        print("✅ Created/verified session_tokens table")
        
        print("\n" + "="*60)
        print("✅ Migration complete!")
        print("="*60)
        print("⚠️  Note: Existing private keys are NOT encrypted.")
        print("   They will be encrypted when you re-create them.")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Migration error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
