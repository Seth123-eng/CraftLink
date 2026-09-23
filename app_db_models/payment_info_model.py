

from helper_tools.db_helper import Base

from sqlalchemy import Integer, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import mapped_column

import sqlalchemy as sa



class PaymentsTable(Base):
    __tablename__ = "payments_table"
    id = mapped_column(Integer, sa.Identity(), primary_key=True)
    is_received = mapped_column(Boolean, nullable=False, default=True)
    phone_number = mapped_column(Text, nullable=False)
    payment_type = mapped_column(Text, nullable=False, default="mpesa") #mpesa
    business_short_code = mapped_column(Text, nullable=False)
    amount = mapped_column(Integer, nullable=False)
    mpesa_receipt_number = mapped_column(Text, nullable=False)
    result_code = mapped_column(Integer, nullable=False)
    date_time = mapped_column(DateTime(timezone=True), nullable=False)
    transaction_date = mapped_column(Text, nullable=False) #returns as integer fro mpesa, too long for int32, hence stored as string
    user_id = mapped_column(Integer, ForeignKey("user_table.id", ondelete="CASCADE"), nullable=False, unique=False)

    
    def __repr__(self):        
        return f"<id : {self.id}>"
    

class TotalPaymentsTable(Base):
    __tablename__ = "total_payments_table"
    id = mapped_column(Integer, sa.Identity(), primary_key=True)
    amount = mapped_column(Integer, nullable=False, default=0)
    is_received = mapped_column(Boolean, nullable=False, default=True)
    account = mapped_column(Text, nullable=False, default="craftlink") #craftlink, client(for other users)
    date_time = mapped_column(DateTime(timezone=True), nullable=False)
    user_id = mapped_column(Integer, ForeignKey("user_table.id", ondelete="CASCADE"), nullable=False, unique=False)

    def __repr__(self):
        return f"<id : {self.id}>"