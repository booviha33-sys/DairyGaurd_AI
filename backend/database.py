from sqlalchemy import create_engine, Column, Integer, String, Float, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./dairyguard.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


class MilkTest(Base):
    __tablename__ = "milk_tests"

    id = Column(Integer, primary_key=True, index=True)

    farmer_id = Column(String, index=True)
    batch_id = Column(String, index=True)

    red = Column(Float)
    green = Column(Float)
    blue = Column(Float)

    temperature = Column(Float)

    quality_score = Column(Float)
    status = Column(String)

    spoilage_risk = Column(String)

    # MBRT prototype fields
    mbrt_time_seconds = Column(Float, nullable=True)
    mbrt_blue_score = Column(Float, nullable=True)
    mbrt_status = Column(String, nullable=True)
    mbrt_image_path = Column(String, nullable=True)

    # Kept for compatibility with old database
    adulteration_status = Column(
        String,
        default="NOT TESTED"
    )


Base.metadata.create_all(bind=engine)


def add_missing_columns():

    inspector = inspect(engine)

    if "milk_tests" not in inspector.get_table_names():
        return

    existing_columns = {
        column["name"]
        for column in inspector.get_columns("milk_tests")
    }

    columns_to_add = {
        "mbrt_time_seconds": "FLOAT",
        "mbrt_blue_score": "FLOAT",
        "mbrt_status": "VARCHAR",
        "mbrt_image_path": "VARCHAR",
    }

    with engine.begin() as connection:

        for column_name, column_type in columns_to_add.items():

            if column_name not in existing_columns:

                connection.execute(
                    text(
                        f"ALTER TABLE milk_tests "
                        f"ADD COLUMN {column_name} {column_type}"
                    )
                )


add_missing_columns()