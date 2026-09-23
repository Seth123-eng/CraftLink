



from helper_tools.db_helper import Base

from sqlalchemy import (
    Integer, Text, DateTime, ForeignKey, func, 
    Boolean
)
from sqlalchemy.orm import mapped_column

import sqlalchemy as sa

class ComplaintsTable(Base):
    __tablename__ = "complaints_table"
    id = mapped_column(Integer, sa.Identity(), primary_key=True)
    complaint_type = mapped_column(Text, nullable=False)
    complaint_info = mapped_column(Text, nullable=False)
    complained_to = mapped_column(Integer, nullable=False)
    is_read=mapped_column(Boolean, nullable=False, default=False)
    user_id = mapped_column(Integer, ForeignKey("user_table.id", ondelete="CASCADE"), nullable=False, unique=False)
    date_time = mapped_column(DateTime(timezone=True), nullable=False, default=func.now())

    def __repr__(self):
        return f"<id : {self.id}>"