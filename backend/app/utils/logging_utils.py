import traceback
from sqlalchemy.orm import Session
from app.models.system_logs import SystemLog
from app.database import SessionLocal

def log_error(db: Session, error: Exception, module: str, function: str, user_id: str = None, data: str = None):
    # db param is kept for compatibility but not used for writing the log
    # We use a separate session to ensure the log is committed even if the main transaction is rolled back.
    log_db = SessionLocal()
    try:
        log = SystemLog(
            level="ERROR",
            message=str(error),
            module=module,
            function_name=function,
            stack_trace=traceback.format_exc(),
            user_id=user_id,
            request_data=data
        )
        log_db.add(log)
        log_db.commit()
    except Exception as logging_error:
        # Fallback if logging to DB fails, print to stderr or do nothing to avoid loop
        print(f"Failed to log error to database: {logging_error}")
    finally:
        log_db.close()
