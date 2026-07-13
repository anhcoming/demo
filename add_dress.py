import sqlite3
import sys

def add_dress(name, category, size, color, price, deposit, image_url):
    try:
        conn = sqlite3.connect('rental_shop.db')
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO dresses (name, category, size, color, price, deposit, image_url, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'Sẵn sàng')
        """, (name, category, size, color, price, deposit, image_url))
        conn.commit()
        dress_id = cursor.lastrowid
        conn.close()
        print(f"SUCCESS: Added dress '{name}' with ID {dress_id}")
        return dress_id
    except Exception as e:
        print(f"ERROR: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 8:
        print("Usage: python3 add_dress.py <name> <category> <size> <color> <price> <deposit> <image_url>")
    else:
        name = sys.argv[1]
        category = sys.argv[2]
        size = sys.argv[3]
        color = sys.argv[4]
        price = int(sys.argv[5])
        deposit = int(sys.argv[6])
        image_url = sys.argv[7]
        add_dress(name, category, size, color, price, deposit, image_url)
