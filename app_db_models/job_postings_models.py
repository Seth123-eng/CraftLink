

from helper_tools.db_helper import Base

from sqlalchemy import Integer, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import mapped_column

import sqlalchemy as sa



class JobPostingsTable(Base):
    __tablename__ = "job_postings_table"
    id = mapped_column(Integer, sa.Identity(), primary_key=True)
    job_description = mapped_column(Text, nullable=False, unique=False)
    job_category = mapped_column(Text, nullable=False, unique=False)
    status = mapped_column(Text, default="active")
    user_id = mapped_column(Integer, ForeignKey("user_table.id", ondelete="CASCADE"), nullable=False, unique=False)
    date_time = mapped_column(DateTime(timezone=True), nullable=False, default=func.now())
    

    def __repr__(self):
        return f"<id : {self.id}>"