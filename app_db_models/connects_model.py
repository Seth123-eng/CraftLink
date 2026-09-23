

from helper_tools.db_helper import Base

from sqlalchemy import (
    Integer, DateTime, ForeignKey, func, Float
)
from sqlalchemy.orm import mapped_column

import sqlalchemy as sa


#tracks users connects
class ConnectsTable(Base):

    __tablename__ = "connects_table"
    id = mapped_column(Integer, sa.Identity(), primary_key=True)
    available_connects = mapped_column(Float, nullable=False, default=0) #referral connects add to this
    connects_from_referral = mapped_column(Float, nullable=False, default=False)
    date_time = mapped_column(DateTime(timezone=True), nullable=False, default=func.now())
    user_id = mapped_column(Integer, ForeignKey("user_table.id", ondelete="CASCADE"), nullable=False, unique=True)

    def __repr__(self):
        return f"<id : {self.id}>"
    

#for admin management and changes
class ConnectsManagement(Base):

    __tablename__ = "connects_management"

    id = mapped_column(Integer, sa.Identity(), primary_key=True)
    connects = mapped_column(Integer, nullable=False, default=0)
    connects_cost = mapped_column(Float, nullable=False, default=0)
    date_time= mapped_column(DateTime(timezone=True), nullable=False, default=func.now())
    user_id = mapped_column(Integer, ForeignKey("user_table.id", ondelete="CASCADE"), nullable=False, unique=False)


    def __repr__(self) -> str:
        return f"<id : {self.id}>"