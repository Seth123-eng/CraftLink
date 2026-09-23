

from helper_tools.db_helper import Base

from sqlalchemy import Integer, Text, DateTime, ForeignKey, func, Boolean
from sqlalchemy.orm import mapped_column

import sqlalchemy as sa


class ContactUsTable(Base):
    __tablename__ = "contact_us_table"
    id = mapped_column(Integer, sa.Identity(), primary_key=True)
    message = mapped_column(Text, nullable=False, unique=False)
    is_read = mapped_column(Boolean, nullable=False, default=False)
    date_time = mapped_column(DateTime(timezone=True), nullable=False, default=func.now())
    user_id = mapped_column(Integer, ForeignKey("user_table.id", ondelete="CASCADE"), nullable=False, unique=False)

    def __repr__(self):
        return f"<id : {self.id}>"