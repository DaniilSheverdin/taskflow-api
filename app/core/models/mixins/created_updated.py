from sqlalchemy import TIMESTAMP, func, DateTime
from sqlalchemy.orm import Mapped, mapped_column


class CreatedUpdated:
    created_at: Mapped[DateTime] = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(
        TIMESTAMP, server_default=func.now(), onupdate=func.now()
    )
