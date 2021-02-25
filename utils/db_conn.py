from pathlib import Path

import sqlalchemy


def get(db_path: Path, enable_logging: bool = False) -> sqlalchemy.engine.Connection:
    engine: sqlalchemy.engine.Engine = sqlalchemy.create_engine(
        'sqlite:///' + db_path.resolve().as_posix(),
        echo=enable_logging
    )
    return engine.connect()
