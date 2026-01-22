from sqlalchemy import ForeignKey, String, BigInteger
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.models.mixins.created_updated import CreatedUpdated
from app.models.mixins.int_id_pk import IntIdPk


class RefreshSession(IntIdPk, CreatedUpdated, Base):
    __tablename__ = "refresh_session"
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    refresh_token: Mapped[str] = mapped_column(String, nullable=False)
    user_agent: Mapped[str] = mapped_column(String(200), nullable=False)
    fingerprint: Mapped[str] = mapped_column(String, nullable=False)
    ip: Mapped[str] = mapped_column(String(15), nullable=False)
    expires_in: Mapped[int] = mapped_column(BigInteger, nullable=False)

    user: Mapped["User"] = relationship(back_populates="refresh_sessions")
