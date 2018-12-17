import sqlite3
from animator import create_app
import os

app = create_app()
b = os.path.join(app.instance_path, 'anime.sqlite')
print(b)
conn = sqlite3.connect(b)
c = conn.cursor()

# Insert a row of data
c.execute("INSERT OR REPLACE INTO profile(mal_username, profile_id, list) VALUES (?, ?, ?)", ('1', '2', '3'))

# Save (commit) the changes
conn.commit()

# We can also close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.
conn.close()
