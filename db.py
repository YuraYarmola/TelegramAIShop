import sqlite3


class FlowerDatabase:
    def __init__(self, db_name="flowers.db"):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self.create_table_if_not_exists()

    def create_table_if_not_exists(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS flowers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                count INTEGER NOT NULL,
                cost FLOAT NOT NULL
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL,
                message TEXT,
                is_user BOOLEAN
            )
        ''')

        self.cursor.execute('''
                    CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER NOT NULL,
    flower_id INTEGER,
    number INTEGER NOT NULL,
    delivery_price FLOAT NOT NULL,
    address TEXT NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (flower_id) REFERENCES flowers(id)
)''')

        self.connection.commit()

        self.cursor.execute('SELECT COUNT(*) FROM flowers')
        if self.cursor.fetchone()[0] == 0:
            self.insert_test_data()

    def insert_test_data(self):
        test_data = [
            ("Rose", 10, 100),
            ("Tulip", 15, 70),
            ("Daisy", 20, 40),
            ("Lily", 25, 120),
            ("Sunflower", 30, 100),
            ("Orchid", 8, 107),
            ("Marigold", 12, 120),
            ("Carnation", 22, 110),
            ("Chrysanthemum", 18, 101),
            ("Lavender", 16, 106),
            ("Iris", 14, 103),
            ("Peony", 9, 106),
            ("Violet", 13, 107),
            ("Poppy", 11, 109),
            ("Begonia", 19, 104)
        ]
        self.cursor.executemany("INSERT INTO flowers (name, count, cost) VALUES (?, ?, ?)", test_data)
        self.connection.commit()

    def get_all_flowers(self):
        self.cursor.execute('SELECT * FROM flowers')
        return self.cursor.fetchall()

    def add_message_buffer(self, message, chat_id, is_user=True):
        self.cursor.execute('INSERT INTO messages (chat_id, message, is_user) VALUES (?, ?, ?)', (chat_id, message, is_user))
        self.connection.commit()

        self.cursor.execute('SELECT COUNT(*) FROM messages WHERE chat_id = ?', (chat_id,))
        count = self.cursor.fetchone()[0]

        if count > 20:
            self.cursor.execute(
                'DELETE FROM messages WHERE id IN (SELECT id FROM messages WHERE chat_id = ? ORDER BY id ASC LIMIT ?)',
                (chat_id, count - 20))
            self.connection.commit()

    def delete_message_buffer(self, chat_id):
        self.cursor.execute(
            'DELETE FROM messages WHERE chat_id = ?',
            (chat_id,))
        self.connection.commit()

    def get_all_messages(self, chat_id):
        self.cursor.execute('SELECT * FROM messages WHERE chat_id = ?', (chat_id,))
        return self.cursor.fetchall()

    def create_order(self, chat_id, flower_id, number, delivery_price, address, status="created"):
        self.cursor.execute('INSERT INTO orders (chat_id, flower_id, number, delivery_price, address, status) VALUES (?, ?, ?, ?, ?, ?)', (chat_id, flower_id, number, delivery_price, address, status))
        self.connection.commit()

    def get_orders(self, chat_id):
        self.cursor.execute('SELECT * FROM orders WHERE chat_id = ?', (chat_id,))
        return self.cursor.fetchall()

    def close(self):
        self.connection.close()


if __name__ == '__main__':
    db = FlowerDatabase()
    flowers = db.get_all_flowers()
    for flower in flowers:
        print(flower)

    db.close()
