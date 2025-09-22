from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData
from src.core.config import settings

engine = create_async_engine(
	url=settings.POSTGRES_URL
)

SessionLocal = async_sessionmaker(
	bind=engine,
	expire_on_commit=False
)

class Base(DeclarativeBase):
	metadata = MetaData(
		naming_convention={
			"all_column_names": lambda constraint, table: "_".join(
				[column.name for column in constraint.columns.values()]
			),
			"ix": "ix__%(table_name)s__%(all_column_names)s",
			"uq": "uq__%(table_name)s__%(all_column_names)s",
			"ck": "ck__%(table_name)s__%(constraint_name)s",
			"fk": "fk__%(table_name)s__%(all_column_names)s__%(referred_table_name)s",
			"pk": "pk__%(table_name)s",
		}
	)

