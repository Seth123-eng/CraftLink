

from helper_tools.db_helper import Base

from sqlalchemy import (
    Integer, DateTime, ForeignKey, func,
    Text
)
from sqlalchemy.orm import mapped_column

import sqlalchemy as sa


class ReferralsTable(Base):
    
    __tablename__ = "referrals_table"
    id = mapped_column(Integer, sa.Identity(), primary_key=True)
    referred_user_id = mapped_column(Integer, nullable=False, unique=True) #for single user referrals
    reffered_client_email = mapped_column(Text, nullable=False, unique=False)
    date_time = mapped_column(DateTime(timezone=True), nullable=False, default=func.now())
    user_id = mapped_column(Integer, ForeignKey("user_table.id", ondelete="CASCADE"), nullable=False, unique=False) #client sending referral
    
    def __repr__(self):

        return f"<id : {self.id}>"