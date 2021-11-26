import asyncio
from os import getenv
from uuid import uuid4

import asyncpg
from passlib.hash import bcrypt


async def main():
    DB_URL = getenv("DB_URL")

    if getenv("MONOCHROME_TEST"):
        USERNAME = "admin"
        PASSWORD = "pass"
        uuid = "c603ef4f-08f9-4130-a770-3a34defa44b3"
    else:
        USERNAME = input("Username: ")
        PASSWORD = input("Password: ")
        uuid = uuid4()

    if not DB_URL:
        raise OSError("A DB_URL is required to add an admin user")
    else:
        DB_URL = DB_URL.replace("+asyncpg", "")

    hashed_password = bcrypt.hash(PASSWORD)

    conn = await asyncpg.connect(DB_URL)

    query = """INSERT INTO "user" (version, id, username, hashed_password, role) VALUES(1, $1, $2, $3, $4);"""

    await conn.execute(query, uuid, USERNAME, hashed_password, "admin")

    await conn.close()


asyncio.get_event_loop().run_until_complete(main())
