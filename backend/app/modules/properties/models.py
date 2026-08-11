from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Property(Base):
    """Propiedad inmobiliaria administrada por TopHouse."""

    __tablename__ = "properties"

    __table_args__ = (
        CheckConstraint(
            "operation_type IN ('sale', 'rent', 'temporary')",
            name="ck_properties_operation_type",
        ),
        CheckConstraint(
            """
            status IN (
                'draft',
                'published',
                'paused',
                'reserved',
                'rented',
                'sold',
                'unavailable'
            )
            """,
            name="ck_properties_status",
        ),
        CheckConstraint(
            "price IS NULL OR price >= 0",
            name="ck_properties_price_non_negative",
        ),
        CheckConstraint(
            "bedrooms IS NULL OR bedrooms >= 0",
            name="ck_properties_bedrooms_non_negative",
        ),
        CheckConstraint(
            "bathrooms IS NULL OR bathrooms >= 0",
            name="ck_properties_bathrooms_non_negative",
        ),
        CheckConstraint(
            "covered_area IS NULL OR covered_area >= 0",
            name="ck_properties_covered_area_non_negative",
        ),
        CheckConstraint(
            "total_area IS NULL OR total_area >= 0",
            name="ck_properties_total_area_non_negative",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    code: Mapped[str] = mapped_column(
        String(32),
        unique=True,
        index=True,
    )

    slug: Mapped[str] = mapped_column(
        String(180),
        unique=True,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(160),
    )

    description: Mapped[str] = mapped_column(
        Text,
    )

    operation_type: Mapped[str] = mapped_column(
        String(20),
        index=True,
    )

    property_type: Mapped[str] = mapped_column(
        String(50),
        index=True,
    )

    price: Mapped[Decimal | None] = mapped_column(
        Numeric(14, 2),
        nullable=True,
        index=True,
    )

    currency: Mapped[str | None] = mapped_column(
        String(3),
        nullable=True,
    )

    city: Mapped[str] = mapped_column(
        String(100),
        index=True,
    )

    zone: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    bedrooms: Mapped[int | None] = mapped_column(
        nullable=True,
    )

    bathrooms: Mapped[int | None] = mapped_column(
        nullable=True,
    )

    covered_area: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        nullable=True,
    )

    total_area: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="draft",
        server_default="draft",
        index=True,
    )

    featured: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default="false",
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
