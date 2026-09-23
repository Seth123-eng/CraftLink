

from helper_tools.db_helper import Base

from sqlalchemy import (
    Integer, Text, DateTime, ForeignKey, func, Boolean
)
from sqlalchemy.orm import mapped_column

import sqlalchemy as sa



class ChatsTable(Base):
    __tablename__ = "chats_table"
    id = mapped_column(Integer, sa.Identity(), primary_key=True)
    room = mapped_column(Text, nullable=False, unique=False)
    chat_cleared_by = mapped_column(Integer, nullable=True, unique=False)
    sender_id = mapped_column(Integer, ForeignKey("user_table.id", ondelete="CASCADE"), nullable=False, unique=False)
    receiver_id = mapped_column(Integer, nullable=False, unique=False)
    date_time = mapped_column(DateTime(timezone=True), nullable=False, default=func.now())
    message = mapped_column(Text, nullable=False, unique=False)
    is_seen = mapped_column(Boolean, nullable=False, unique=False)


    def __repr__(self):
        return f"<id : {self.id}>"