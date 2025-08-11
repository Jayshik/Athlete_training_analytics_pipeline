from sqlmodel import create_engine


def get_db_engine(turso_database_url: str, turso_auth_token: str, **kwargs):
    return create_engine(
        f"sqlite+{turso_database_url}/?authToken={turso_auth_token}&secure=true",
        connect_args={"check_same_thread": False},
        **kwargs,
    )
