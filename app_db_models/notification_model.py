
from sqlalchemy import Integer, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import mapped_column

import sqlalchemy as sa

from helper_tools.db_helper import Base

class NotificationTable(Base):
    
    __tablename__ = "notification_table"
    id = mapped_column(Integer, sa.Identity(), primary_key=True, autoincrement=True)
    msg = mapped_column(Text, nullable=False, unique=False)
    link = mapped_column(Text, nullable=True, unique=False)
    created_time = mapped_column(DateTime(timezone = True), unique=False, nullable=False)
    unread = mapped_column(Boolean, nullable=False, unique=False, default=True)
    user_id = mapped_column(Integer, ForeignKey("user_table.id", ondelete="CASCADE"), nullable=False, unique=False) #notified member
    
    def __repr__(self):
        return f"<notification_table_id : {self.id}>"