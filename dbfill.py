import psycopg2

import wordlist
import utils
import secrets

DEFAULT_COLLECTION = "hungry-tuber"

conn = psycopg2.connect(secrets.POSTGRES_URL)
cursor = conn.cursor()

for word in wordlist.words:
    w = utils.canonicalize_word(word.word)

    cursor.execute("""
        select 1 from words
        where collection = %s
        and word = %s
    """, (DEFAULT_COLLECTION, w,))

    if cursor.fetchall():
        cursor.execute("""
            update words
            set definition = %s, mtime = now(), deleted = %s
            where collection = %s and word = %s
        """, (word.definition, False, DEFAULT_COLLECTION, w,))
    else:
        cursor.execute("""
            INSERT INTO words (collection, word, definition, ctime, mtime, deleted)
            VALUES            (%s, %s, %s, now(), now(), %s)
        """, (DEFAULT_COLLECTION, w, word.definition, False))

conn.commit()
