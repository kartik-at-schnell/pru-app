from sqlalchemy import Column, Integer, String, Text, DateTime, func
from app.database import Base

class SystemLog(Base):
    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True, index=True)
    level = Column(String(50), nullable=False)  # INFO, ERROR, WARNING, CRITICAL
    message = Column(Text, nullable=False)
    module = Column(String(100), nullable=True)
    function_name = Column(String(100), nullable=True)
    line_number = Column(Integer, nullable=True)
    stack_trace = Column(Text, nullable=True)
    user_id = Column(String(100), nullable=True)
    request_data = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), default=func.now())

    def __repr__(self):
        return f"<SystemLog(id={self.id}, level='{self.level}', message='{self.message[:50]}...')>"
