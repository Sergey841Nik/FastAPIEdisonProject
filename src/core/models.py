from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
    String,
    LargeBinary,
    ForeignKey,
    text,
)

metadata = MetaData()


user_table = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(100)),
    Column("email", String(100), unique=True),
    Column("password", LargeBinary()),
    Column("roles_id", ForeignKey("roles.id")),
)

roles_table = Table(
    "roles",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(100)),
)
