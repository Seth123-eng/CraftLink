

from helper_tools.db_helper import Base

from sqlalchemy import (
    Integer, DateTime, ForeignKey, func
)
from sqlalchemy.orm import mapped_column

import sqlalchemy as sa

class RatingsTable(Base):
    
    __tablename__ = "ratings_table"
    id = mapped_column(Integer, sa.Identity(), primary_key=True)
    rating = mapped_column(Integer, nullable=False)
    user_rated_id = mapped_column(Integer, nullable=False, unique=False)
    user_id = mapped_column(Integer, ForeignKey("user_table.id", ondelete="CASCADE"), nullable=False, unique=False)
    date_time = mapped_column(DateTime(timezone=True), nullable=False, default=func.now())


    def __repr__(self):
        return f"<id : {self.id}>"