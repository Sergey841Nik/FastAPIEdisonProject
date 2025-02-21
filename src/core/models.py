from sqlalchemy import MetaData, Table, Column, Integer, String, ForeignKey

metadata = MetaData()


user_table = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("first_name", String(100)),
    Column("last_name", String(100)),
    Column("email", String(100)),
    Column("password", String(100)),
    Column("roles_id", ForeignKey("roles.id"), default=1),
)

roles_table = Table(
    "roles",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(100)),
    Column("users_id", ForeignKey("users.id", ondelete="CASCADE")),
)
