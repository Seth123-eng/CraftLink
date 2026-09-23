
from helper_tools.db_helper import Base

from sqlalchemy import Integer, Text, DateTime, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

import sqlalchemy as sa


from .payment_info_model import PaymentsTable, TotalPaymentsTable
from .file_model import FileTable
from .chats_model import ChatsTable
from .skill_set_model import SkillSetTable
from .complaints_report_model import ComplaintsTable
from .rating_model import RatingsTable
from .notification_model import NotificationTable
from .job_postings_models import JobPostingsTable
from .connects_model import ConnectsManagement, ConnectsTable
from .contact_us_model import ContactUsTable
from .refferals_model import ReferralsTable


class UserTable(Base):
    __tablename__ = "user_table"
    id = mapped_column(Integer, sa.Identity(), primary_key=True)
    email = mapped_column(Text, nullable=False)
    user_name = mapped_column(Text, nullable=False)
    time_zone = mapped_column(String(30), nullable=False)
    password_hash =  mapped_column(Text, nullable=False)
    account_status = mapped_column(Text, nullable=False, default="inactive") #active, inactive
    account_type = mapped_column(Text, nullable=False) #client, technician, admin
    account_class = mapped_column(Text, nullable=False) #freemium, premium
    failed_login_attempts = mapped_column(Integer, unique=False, nullable=False, default=0)
    account_created_datetime = mapped_column(DateTime(timezone = True), nullable=False)
    account_locked_datetime = mapped_column(DateTime(timezone = True), nullable=True)
    account_locked = mapped_column(Boolean, nullable=False, default=False)
    is_account_scheduled_for_deletion = mapped_column(Boolean, nullable=False, default=False)
    account_scheduled_for_deletion_datetime = mapped_column(DateTime(timezone = True), nullable=True)


    connects_table_refernce:Mapped["ConnectsTable"] = relationship(
        backref="user_table",
        foreign_keys="ConnectsTable.user_id",
        passive_deletes=True,
        cascade="all, delete-orphan"
    )

    payments_table_reference:Mapped["PaymentsTable"] = relationship(
        backref="user_table",
        foreign_keys="PaymentsTable.user_id",
        passive_deletes=True,
        cascade="all, delete-orphan"
    )

    file_table_relationship:Mapped["FileTable"] = relationship(
        backref="user_table",
        foreign_keys="FileTable.user_id",
        passive_deletes=True,
        cascade="all, delete-orphan"
    )

    chats_table_relationship:Mapped["ChatsTable"] = relationship(
        backref="user_table",
        foreign_keys="ChatsTable.sender_id",
        passive_deletes=True,
        cascade="all, delete-orphan"
    )

    skill_sets_table_relationship:Mapped["SkillSetTable"] = relationship(
        backref="user_table",
        foreign_keys="SkillSetTable.user_id",
        passive_deletes=True,
        cascade="all, delete-orphan"
    )

    complaints_table_relationship:Mapped["ComplaintsTable"] = relationship(
        backref="user_table",
        foreign_keys="ComplaintsTable.user_id",
        passive_deletes=True,
        cascade="all, delete-orphan"
    )

    rating_table_relationship:Mapped["RatingsTable"] = relationship(
        backref="user_table",
        foreign_keys="RatingsTable.user_id",
        passive_deletes=True,
        cascade="all, delete-orphan"
    )

    notification_table_relationship:Mapped["NotificationTable"] = relationship(
        backref="user_table",
        foreign_keys="NotificationTable.user_id",
        passive_deletes=True,
        cascade="all, delete-orphan"
    )

    job_postings_table_relationship:Mapped["JobPostingsTable"] = relationship(
        backref="user_table",
        foreign_keys="JobPostingsTable.user_id",
        passive_deletes=True,
        cascade="all, delete-orphan"
    )

    connects_management_table_relationship:Mapped["ConnectsManagement"] = relationship(
        backref="user_table",
        foreign_keys="ConnectsManagement.user_id",
        passive_deletes=True,
        cascade="all, delete-orphan"
    )

    contact_us_table_relationship:Mapped["ContactUsTable"] = relationship(
        backref="user_table",
        foreign_keys="ContactUsTable.user_id",
        passive_deletes=True,
        cascade="all, delete-orphan"
    )

    connects_table_relationship:Mapped["TotalPaymentsTable"] = relationship(
        backref="user_table",
        foreign_keys="TotalPaymentsTable.user_id",
        passive_deletes=True,
        cascade="all, delete-orphan"
    )

    refferals_table_relationship:Mapped["ReferralsTable"] = relationship(
        backref="user_table",
        foreign_keys="ReferralsTable.user_id",
        passive_deletes=True,
        cascade="all, delete-orphan"
    )


    def __repr__(self):
        return f"<id : {self.id}>"