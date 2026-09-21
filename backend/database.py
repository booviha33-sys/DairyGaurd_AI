from sqlalchemy import create_engine, Column, Integer, String, Float
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

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    farmer_id = Column(
        String,
        index=True
    )

    batch_id = Column(
        String,
        index=True
    )

    red = Column(Float)

    green = Column(Float)

    blue = Column(Float)

    temperature = Column(Float)

    quality_score = Column(Float)

    status = Column(String)

    spoilage_risk = Column(String)

    adulteration_status = Column(String)


Base.metadata.create_all(
    bind=engine
)