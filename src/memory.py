import sqlite3

def save_conversation(user_input, ai_response):
    try:
        conn = sqlite3.connect("voice_assistant.db")  # Creates a local SQLite database
        cursor = conn.cursor()

        # Create the table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_input TEXT,
                ai_response TEXT
            )
        """)

        # Insert the conversation data
        cursor.execute("INSERT INTO conversations (user_input, ai_response) VALUES (?, ?)", (user_input, ai_response))

        conn.commit()
        cursor.close()
        conn.close()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
