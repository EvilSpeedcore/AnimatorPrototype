import asyncio
from . import db
from animator import create_app

loop = asyncio.get_event_loop()

db.DBController.update(
    loop,
    """
    INSERT OR REPLACE INTO profile(mal_username, profile_id, list)
    VALUES (?, ?, ?)
    """,
    ('123121', '4444', '31232312'))


app = create_app()

