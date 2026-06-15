# Course Project: Steam Discount Likelihood Predictor

## Project Overview
This project is a terminal-based utility designed to query the Steam Store Web API, evaluate game parameters, and predict the likelihood of an upcoming price drop (discount) for specific titles. The application integrates SQLite database caching, implements basic cryptographic field security, and computes heuristic scores using game sales history, publisher behaviors, current online player counts, and seasonal trends.

*Note: This application represents a team coursework implementation combining API communications, databases, and practical decision-making heuristics.*

---

## Technical Architecture & Features

### 1. Steam Web API Integrations
The application queries two official Steam API endpoints:
* **Steam App Details API** (`https://store.steampowered.com/api/appdetails`): Fetches pricing overviews, active discount percentages, genres, publishers, and developers.
* **Steam Active Player Count API** (`ISteamUserStats/GetNumberOfCurrentPlayers`): Retrieves real-time player counts to evaluate product popularity.

### 2. Local Database & JSON Caching
To optimize performance and circumvent heavy API rate-limits:
* The application reads a local JSON file `allgame.json` containing mappings of all Steam game titles to their AppIDs.
* The local SQLite database (`steam_data_encrypted.db`) stores this list in the `app_list` table for rapid local lookup using SQL `LIKE` queries.
* Query history and generated predictions are cached in the `games` table.

### 3. Cryptographic Security (Symmetric XOR Cipher)
To demonstrate data security, sensitive fields stored in the SQLite database (such as game name, developer, publisher, genres list, and analysis comments) are protected using a symmetric **XOR cipher** combined with **Base64 encoding**:
* Encryption key: `SECRET_KEY = 57`
* Encryption process:
  $$C_i = P_i \oplus K$$
  where $K$ is the secret key ($57$). The encrypted array is then base64 encoded:
  $$C_{\text{base64}} = \text{Base64}(C)$$
* Decryption occurs transparently when retrieving search history.

### 4. Discount Prediction Heuristic Algorithm
The program calculates the probability score $S \in [0.0, 1.0]$ of a game getting a discount based on a rules engine:
* **Genre Adjustments**: RPG (+8%), Action (+10%), Adventure (+10%), FPS (+5%), Strategy (+5%), Simulation (+5%).
* **Publisher Rules**: EA (+10%), Ubisoft (+10%), Bethesda (+7%), Indie (+5%), Activision (-5%).
* **Current Discount Status**:
  * Currently discounted $\ge 60\%$: Score **-10%** (unlikely to drop further immediately).
  * Discounted between $30\%$ and $60\%$: Score **+5%** (likely part of a larger ongoing promotion).
  * Small discount $<30\%$: Score **+10%** (indicates upcoming deep drops).
  * No discount: Score **+0%** (room for full drop).
* **Seasonality**: Summer Sale (June/July) or Winter Sale (November/December) adds **+10%** to the score.
* **Online Player Count**:
  * Low activity ($<500$ players): Score **+15%** (publisher is incentivized to drop price to boost numbers).
  * High activity ($>5000$ players): Score **-5%** (high organic traffic reduces sales pressure).
* **Random perturbation**: $\pm 5\%$ variability is introduced.

---

## Codebase Components

* **[1.py](1.py)**: The main entry point. Initializes database schemas, populates app lists, provides interactive CLI menus to search history (decrypting fields on the fly), searches games by name/ID, performs API calls, runs the prediction logic, and saves base64-encrypted records.
* **`allgame.json`**: Cached raw database of Steam game titles and AppIDs.
* **`steam_data_encrypted.db`**: Local SQLite database storing search history and game details.

---

## Interactive Menu Options

1. **Analyze New Game**:
   * Search via partial game title (LIKE wildcard query).
   * Selection of correct game from matched titles.
   * Dynamic API fetches, prediction output, and encryption write to SQLite.
2. **View History**:
   * Search encrypted database records via keyword or ID.
   * Decrypts and prints history of analyzed titles.

---

## How to Run

1. Make sure you are in the project folder:
   ```bash
   cd project
   ```
2. Run the program using the local virtual environment:
   ```bash
   ../venv/bin/python 1.py
   ```
