from pathlib import Path

from dotenv import dotenv_values
from sqlmodel import SQLModel

import graig_nlp.db as db

env_path = Path(__file__).parents[0].joinpath(".env")


def main():
    env = dotenv_values(env_path)
    engine = db.get_db_engine(env["TURSO_DATABASE_URL"], env["TURSO_AUTH_TOKEN"])
    SQLModel.metadata.create_all(engine)


if __name__ == "__main__":
    main()
