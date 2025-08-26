from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Numeric, Text, Float, UniqueConstraint, JSON
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.db.base import Base


# helpers
now = datetime.utcnow


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(32), unique=True, nullable=True, index=True)
    dob: Mapped[str | None] = mapped_column(String(32), nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(16), default="user")
    is_email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_phone_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    external_pos_customer_id: Mapped[str | None] = mapped_column(String(64), nullable=True)

    devices: Mapped[list["Device"]] = relationship("Device", back_populates="user")
    orders: Mapped[list["Order"]] = relationship("Order", back_populates="user")


class Device(Base):
    __tablename__ = "devices"
    __table_args__ = (
        UniqueConstraint("fcm_token", name="uq_devices_fcm_token"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    platform: Mapped[str] = mapped_column(String(16))  # android|ios|web
    fcm_token: Mapped[str] = mapped_column(String(512))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)

    user: Mapped[User | None] = relationship("User", back_populates="devices")


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    sort: Mapped[int] = mapped_column(Integer, default=0)

    items: Mapped[list["MenuItem"]] = relationship("MenuItem", back_populates="category")


class MenuItem(Base):
    __tablename__ = "menu_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[float] = mapped_column(Numeric(10, 2))
    image_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    external_pos_id: Mapped[str | None] = mapped_column(String(64), nullable=True)

    category: Mapped[Category | None] = relationship("Category", back_populates="items")


class Promocode(Base):
    __tablename__ = "promocodes"

    code: Mapped[str] = mapped_column(String(64), primary_key=True)
    kind: Mapped[str] = mapped_column(String(16))  # percent|amount
    value: Mapped[float] = mapped_column(Numeric(10, 2))
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    valid_from: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    valid_to: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    max_redemptions: Mapped[int | None] = mapped_column(Integer, nullable=True)
    per_user_limit: Mapped[int | None] = mapped_column(Integer, nullable=True)
    min_subtotal: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    created_by: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)


class PromoBatch(Base):
    __tablename__ = "promo_batches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    prefix: Mapped[str] = mapped_column(String(16))
    length: Mapped[int] = mapped_column(Integer)
    count: Mapped[int] = mapped_column(Integer)
    created_by: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)


class Order(Base):
    __tablename__ = "orders"
    __table_args__ = (
        UniqueConstraint("number", name="uq_orders_number"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    number: Mapped[str] = mapped_column(String(32), unique=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    fulfillment: Mapped[str] = mapped_column(String(16))  # delivery|pickup
    address_text: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    lng: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(16), default="NEW")  # NEW|COOKING|ON_WAY|DELIVERED|CANCELLED
    subtotal: Mapped[float] = mapped_column(Numeric(10, 2))
    discount: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    total: Mapped[float] = mapped_column(Numeric(10, 2))
    promocode_code: Mapped[str | None] = mapped_column(ForeignKey("promocodes.code"), nullable=True)
    paid: Mapped[bool] = mapped_column(Boolean, default=False)
    payment_method: Mapped[str] = mapped_column(String(16), default="cod")  # cod|online
    utm_source: Mapped[str | None] = mapped_column(String(64), nullable=True)
    utm_medium: Mapped[str | None] = mapped_column(String(64), nullable=True)
    utm_campaign: Mapped[str | None] = mapped_column(String(64), nullable=True)
    ga_client_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    external_pos_id: Mapped[str | None] = mapped_column(String(64), nullable=True)

    user: Mapped[User | None] = relationship("User", back_populates="orders")
    items: Mapped[list["OrderItem"]] = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"))
    item_id: Mapped[int | None] = mapped_column(ForeignKey("menu_items.id", ondelete="SET NULL"), nullable=True)
    name_snapshot: Mapped[str] = mapped_column(String(255))
    qty: Mapped[int] = mapped_column(Integer)
    price_at_moment: Mapped[float] = mapped_column(Numeric(10, 2))

    order: Mapped[Order] = relationship("Order", back_populates="items")




class EmailVerification(Base):
    __tablename__ = "email_verifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    email: Mapped[str] = mapped_column(String(255))
    token_hash: Mapped[str] = mapped_column(String(255))
    code_hash: Mapped[str] = mapped_column(String(255))
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    used: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)


class EmailEvent(Base):
    __tablename__ = "email_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    svix_id: Mapped[str] = mapped_column(String(255), unique=True)  # Unique event ID from Svix
    type: Mapped[str] = mapped_column(String(64))  # email.sent, email.opened, etc.
    email_id: Mapped[str | None] = mapped_column(String(255), nullable=True)  # Resend email ID
    recipient: Mapped[str | None] = mapped_column(String(255), nullable=True)
    subject: Mapped[str | None] = mapped_column(String(512), nullable=True)
    link: Mapped[str | None] = mapped_column(String(1024), nullable=True)  # For click events
    meta: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # Additional event data
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)












