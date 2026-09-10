import sqlite3

checkpoint_conn = sqlite3.connect(
    "sessions/checkpoint.db",
    check_same_thread=False
)