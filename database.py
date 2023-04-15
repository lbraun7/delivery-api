from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

import os

PASSWORD = os.environ.get("PASSWORD")

engine = create_engine(
    f'postgresql://postgres:{PASSWORD}@localhost/pizza_delivery',
    echo = True
)

Base = declarative_base()

Session = sessionmaker()