from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from lib.constants import DB_URI
from lib.models import Base

engine = create_engine(DB_URI)
Base.metadata.create_all(engine)
Session = sessionmaker(engine)
