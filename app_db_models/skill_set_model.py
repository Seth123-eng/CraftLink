

from helper_tools.db_helper import Base

from sqlalchemy import (
    Integer, Text, DateTime, ForeignKey, func
)
from sqlalchemy.orm import mapped_column

import sqlalchemy as sa

class SkillSetTable(Base):
    __tablename__ = "skill_sets_table"
    id = mapped_column(Integer, sa.Identity(), primary_key=True)
    skill_set = mapped_column(Text, nullable=False)
    user_id = mapped_column(Integer, ForeignKey("user_table.id", ondelete="CASCADE"), nullable=False, unique=False)
    date_time = mapped_column(DateTime(timezone=True), nullable=False, default=func.now())

    def __repr__(self):
        return f"<id : {self.id}>"