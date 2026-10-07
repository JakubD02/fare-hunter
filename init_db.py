from app.database import engine
from app.models.base import Base
from scripts.seed_data import seed_data


def init_db():
    Base.metadata.create_all(engine)
    seed_data()


if __name__ == "__main__":
    init_db()
