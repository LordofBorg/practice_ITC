import requests
import random
import datetime
import sqlite3
import base64
from contextlib import closing
import json
import os
from typing import List, Dict, Tuple, Any, Optional

# ====== API Endpoints ======
STEAM_APP_DETAILS_URL = "https://store.steampowered.com/api/appdetails"
STEAM_PLAYER_COUNT_URL = "https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/"

DB_PATH = "steam_data_encrypted.db"
SECRET_KEY = 57  # Symmetric XOR encryption key


# ====== Cryptographic Operations (XOR + Base64) ======

def xor_cipher(text: str, key: int = SECRET_KEY) -> str:
    """Applies a simple bitwise XOR symmetric cipher to the text string."""
    return ''.join(chr(ord(c) ^ key) for c in text)


def encrypt_field(data: Optional[str]) -> str:
    """Encrypts a text field using XOR cipher and base64 encoding."""
    if data is None:
        return ""
    encoded = xor_cipher(data)
    return base64.b64encode(encoded.encode()).decode()


def decrypt_field(data: str) -> str:
    """Decrypts a base64-encoded XOR-ciphered text field."""
    if not data:
        return ""
    decoded = base64.b64decode(data.encode()).decode()
    return xor_cipher(decoded)


# ====== Heuristic Scoring Rules ======

GENRE_RULES = {
    "action": {"score": 0.1, "reason": "often part of major sale events"},
    "adventure": {"score": 0.1, "reason": "popular in seasonal promotions"},
    "strategy": {"score": 0.05, "reason": "moderate discounts often occur"},
    "simulation": {"score": 0.05, "reason": "seen in occasional sales"},
    "rpg": {"score": 0.08, "reason": "commonly discounted"},
    "fps": {"score": 0.05, "reason": "used in big publisher sales"},
}

PUBLISHER_RULES = {
    "ea": {"score": 0.1, "reason": "runs big promotions regularly"},
    "ubisoft": {"score": 0.1, "reason": "often discounts its catalog"},
    "activision": {"score": -0.05, "reason": "less frequent deep discounts"},
    "bethesda": {"score": 0.07, "reason": "appears in global sales often"},
    "indie": {"score": 0.05, "reason": "indie discounts can be deep, but irregular"},
}


# ====== Database Connections & Migrations ======

def connect_db() -> sqlite3.Connection:
    """Establishes an SQLite database connection and sets sqlite3.Row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Initializes the SQLite database schema for games and local app list cache."""
    try:
        with closing(connect_db()) as conn:
            c = conn.cursor()
            # Table for query history and predictions
            c.execute("""
                CREATE TABLE IF NOT EXISTS games (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    appid INTEGER,
                    name TEXT,
                    publisher TEXT,
                    developer TEXT,
                    genres TEXT,
                    final_price REAL,
                    normal_price REAL,
                    discount INTEGER,
                    player_count INTEGER,
                    score REAL,
                    date TEXT,
                    notes TEXT
                )
            """)
            # Local cache table for Steam game titles to avoid hitting official API lists
            c.execute("""
                CREATE TABLE IF NOT EXISTS app_list (
                    appid INTEGER PRIMARY KEY,
                    name TEXT
                )
            """)
            conn.commit()
    except Exception as e:
        print(f"Error initializing database schema: {e}")


def populate_app_list_from_json(json_file: str = 'allgame.json') -> None:
    """Loads AppID mapping cache from JSON file into SQLite database app_list table."""
    if not os.path.exists(json_file):
        print(f"Error: JSON file '{json_file}' not found. Cannot populate App List DB.")
        return

    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            apps = data.get('applist', {}).get('apps', [])
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in '{json_file}'.")
        return
    except Exception as e:
        print(f"Unexpected error loading JSON file: {e}")
        return

    total_apps = len(apps)
    if not total_apps:
        print("No apps found in JSON file.")
        return

    app_data = [(app['appid'], app['name']) for app in apps]

    with closing(connect_db()) as conn:
        with conn:
            conn.executemany("INSERT OR REPLACE INTO app_list (appid, name) VALUES (?, ?)", app_data)
            print(f"✅ Database populated with {total_apps} apps from {json_file}.")


# ====== Steam Web API Fetchers ======

def find_appid(game_name: str, exact: bool = False) -> List[Dict[str, Any]]:
    """Searches for AppIDs matching the game title in the local SQLite app_list cache."""
    search_term = game_name.lower().strip()
    if not search_term:
        return []

    with closing(connect_db()) as conn:
        c = conn.cursor()
        if exact:
            query = "SELECT appid, name FROM app_list WHERE LOWER(name) = ? LIMIT 10"
            c.execute(query, (search_term,))
        else:
            query = "SELECT appid, name FROM app_list WHERE LOWER(name) LIKE ? LIMIT 10"
            c.execute(query, (f'%{search_term}%',))

        return [dict(row) for row in c.fetchall()]


def get_steam_info(appid: int) -> Optional[Dict[str, Any]]:
    """Queries Steam App Details Web API for price, genres, developer, and publisher."""
    try:
        r = requests.get(f"{STEAM_APP_DETAILS_URL}?appids={appid}&cc=ua&l=en")
        r.raise_for_status()
        data = r.json().get(str(appid), {}).get("data", {})
        if not data or "price_overview" not in data:
            return None
        price_info = data["price_overview"]
        return {
            "final_price": price_info["final"] / 100.0,
            "normal_price": price_info["initial"] / 100.0,
            "discount": price_info["discount_percent"],
            "genres": [g["description"] for g in data.get("genres", [])],
            "publisher": data.get("publishers", ["Unknown"])[0],
            "developer": data.get("developers", ["Unknown"])[0]
        }
    except Exception:
        return None


def get_player_count(appid: int) -> Optional[int]:
    """Queries official Steam API for active player online count."""
    try:
        r = requests.get(f"{STEAM_PLAYER_COUNT_URL}?appid={appid}")
        r.raise_for_status()
        return r.json().get("response", {}).get("player_count", None)
    except Exception:
        return None


# ====== Sales Analysis Engine ======

def analyze_discount(game_info: Dict[str, Any], player_count: Optional[int]) -> Tuple[float, str]:
    """Computes a heuristic score representing the likelihood of an upcoming discount."""
    score = 0.5
    reasons = []

    # 1. Evaluate genre rules
    for g in game_info.get("genres", []):
        gl = g.lower()
        if gl in GENRE_RULES:
            score += GENRE_RULES[gl]["score"]
            reasons.append(f"As a {g} game, it {GENRE_RULES[gl]['reason']}.")

    # 2. Evaluate publisher rules
    pub = game_info.get("publisher", "").lower()
    matched = False
    for key in PUBLISHER_RULES:
        if key in pub:
            score += PUBLISHER_RULES[key]["score"]
            reasons.append(f"Publisher '{game_info.get('publisher')}' {PUBLISHER_RULES[key]['reason']}.")
            matched = True
            break
    if not matched:
        reasons.append(f"Publisher '{game_info.get('publisher')}' has unpredictable discount behavior.")

    # 3. Evaluate current discount state
    current_discount = game_info.get("discount", 0)
    if current_discount > 0:
        if current_discount >= 60:
            reasons.append(f"Current sale is already deep ({current_discount}%), further increase might be limited.")
            score -= 0.1
        elif current_discount >= 30:
            reasons.append(f"Moderate discount now ({current_discount}%), likely part of seasonal promotion.")
            score += 0.05
        else:
            reasons.append(f"Discount now is small ({current_discount}%), likely to get deeper in upcoming sales.")
            score += 0.1
    else:
        reasons.append("No discount currently, which leaves full room for a possible drop.")

    # 4. Seasonal trends
    m = datetime.datetime.now().month
    if m in [6, 7]:
        reasons.append("Summer Sale season coming, good chance for deals.")
        score += 0.1
    elif m in [11, 12]:
        reasons.append("Winter/End-year sales ahead, higher chance of discounts.")
        score += 0.1

    # 5. Online player count popularity factor
    if player_count is not None:
        if player_count < 500:
            reasons.append(f"Online is low ({player_count} players) — likely candidate for upcoming discount.")
            score += 0.15
        elif player_count < 5000:
            reasons.append(f"Moderate player base ({player_count}), may benefit from sales.")
            score += 0.05
        else:
            reasons.append(f"High player count ({player_count}), unlikely to discount soon.")
            score -= 0.05
    else:
        reasons.append("Could not retrieve player count — skipping online-based prediction.")

    # 6. Apply small random perturbation
    score += random.uniform(-0.05, 0.05)
    score = round(max(0.0, min(1.0, score)), 2)

    explanation = (
        f"Predicted discount likelihood: {int(score * 100)}%.\n"
        "Analysis:\n" + "\n".join(f" - {r}" for r in reasons) +
        "\nBased on price, genre, publisher, season, and online activity."
    )
    return score, explanation


# ====== Data Persistence Layer (SQLite) ======

def save_result(
    appid: int,
    name: str,
    info: Dict[str, Any],
    player_count: Optional[int],
    score: float,
    notes: str
) -> None:
    """Encrypts game statistics and commits a new record into the SQLite history cache."""
    with closing(connect_db()) as conn:
        c = conn.cursor()
        c.execute("""
            INSERT INTO games (appid, name, publisher, developer, genres, final_price,
                               normal_price, discount, player_count, score, date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            appid,
            encrypt_field(name),
            encrypt_field(info["publisher"]),
            encrypt_field(info["developer"]),
            encrypt_field(", ".join(info["genres"])),
            info["final_price"],
            info["normal_price"],
            info["discount"],
            player_count,
            score,
            datetime.datetime.now().isoformat(),
            encrypt_field(notes)
        ))
        conn.commit()


def search_history_keyword(keyword: str) -> List[Dict[str, Any]]:
    """Retrieves and decrypts database records whose game names match the keyword."""
    with closing(connect_db()) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM games ORDER BY date DESC LIMIT 450")
        rows = [dict(r) for r in c.fetchall()]
        result = []
        for r in rows:
            name = decrypt_field(r["name"])
            if keyword.lower() in name.lower():
                r["name"] = name
                r["publisher"] = decrypt_field(r["publisher"])
                r["developer"] = decrypt_field(r["developer"])
                r["genres"] = decrypt_field(r["genres"])
                r["notes"] = decrypt_field(r["notes"])
                result.append(r)
        return result


def search_history_id(id: int) -> List[Dict[str, Any]]:
    """Retrieves and decrypts database records whose Steam AppIDs match the search ID."""
    with closing(connect_db()) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM games ORDER BY date DESC LIMIT 450")
        rows = [dict(r) for r in c.fetchall()]
        result = []
        for r in rows:
            r_id = r["appid"]
            if id == r_id:
                r["name"] = decrypt_field(r["name"])
                r["publisher"] = decrypt_field(r["publisher"])
                r["developer"] = decrypt_field(r["developer"])
                r["genres"] = decrypt_field(r["genres"])
                r["notes"] = decrypt_field(r["notes"])
                result.append(r)
        return result


# ====== Command-line Interface Entry ======

def main() -> None:
    init_db()
    populate_app_list_from_json()
    print("-" * 30)

    choice = input("1 - Analyze new game, 2 - View history: ").strip()

    if choice == "2":
        try:
            tip = int(input("Enter type of search — [1] keyword, [2] ID? : "))
        except ValueError:
            print("Invalid input. Selection must be a number.")
            return

        if tip == 1:
            kw = input("Enter keyword for search: ").strip()
            results = search_history_keyword(kw)
            if not results:
                print("No results found.")
            else:
                print("\n=== Search results ===")
                for r in results:
                    print(f"[{r['date'][:19]}] {r['name']} ({r['discount']}%) → Likelihood: {int(r['score'] * 100)}%")
        else:
            kw = input("Enter ID for search: ").strip()
            try:
                results = search_history_id(int(kw))
            except ValueError:
                print("Invalid ID format.")
                return
            if not results:
                print("No results found.")
            else:
                print("\n=== Search results ===")
                for r in results:
                    print(f"[{r['date'][:19]}] {r['name']} ({r['discount']}%) → Likelihood: {int(r['score'] * 100)}%")
        return

    mode = input("Search type — [1] partial name, [2] exact name, [3] AppID? ").strip()
    if mode != "3":
        exact = (mode == "2")
        game_name = input("Enter game name: ").strip()
        matches = find_appid(game_name, exact)
        if not matches:
            print("Game not found in Steam App List.")
            return

        if len(matches) > 1:
            print("\nMultiple matches found:")
            for i, m in enumerate(matches, 1):
                print(f"[{i}] {m['name']} (AppID: {m['appid']})")

            while True:
                try:
                    choice_num = int(input("\nEnter selection index: "))
                    if 1 <= choice_num <= len(matches):
                        appid = matches[choice_num - 1]["appid"]
                        name = matches[choice_num - 1]["name"]
                        break
                    print("Invalid index choice. Try again.")
                except ValueError:
                    print("Invalid input. Please enter a valid number.")
        else:
            appid = matches[0]["appid"]
            name = matches[0]["name"]
    else:
        try:
            appid = int(input("Enter the AppID of the game: "))
        except ValueError:
            print("AppID must be a numeric integer.")
            return
        name = "---"

    info = get_steam_info(appid)
    if not info:
        print("Failed to retrieve product details from Steam Web API.")
        return

    players = get_player_count(appid)
    score, explanation = analyze_discount(info, players)

    print(f"\n🎮 {name} | {info['final_price']}$ ({info['discount']}%)\n")
    print(f"Publisher: {info['publisher']} | Developer: {info['developer']}")
    print(f"Genres: {', '.join(info['genres'])}")
    if players is not None:
        print(f"Players: {players}")
    print(f"🤖 Discount chance: {int(score * 100)}%")
    print(explanation)
    print(f"🔗 https://store.steampowered.com/app/{appid}/")

    save_result(appid, name, info, players, score, explanation)
    print("\n✅ Encrypted data saved to database!")


if __name__ == "__main__":
    main()