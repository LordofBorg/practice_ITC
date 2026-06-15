# National Aerospace University "Kharkiv Aviation Institute" (KHAI)
## Information Theory and Coding Coursework

This repository contains the practical lab assignments and the course project completed as part of the **Information Theory and Coding** curriculum at NAU "KHAI" (Department of Computer Systems, Networks and Cybersecurity).

---

## 📂 Repository Index & Roadmap

The codebase covers core areas of information theory, compression algorithms, error-correcting codes, and practical API-driven applications. Each module includes a dedicated `README.md` detailing the underlying mathematical model, algorithms, code structure, and visual output charts.

| Module | Title / Topic | Key Mathematical & Algorithmic Concepts | Local Documentation |
| :--- | :--- | :--- | :---: |
| **[practice1](practice1)** | **Entropy & Information Estimation** | Shannon Entropy, relative character frequencies, natural language comparison, BeautifulSoup web scraping | [README](practice1/README.md) |
| **[practice2](practice2)** | **Sources with Memory** | Joint Probability Matrix, Row/Column Marginals, Conditional Entropies, Entropy Chain Rules | [README](practice2/README.md) |
| **[practice3](practice3)** | **Shannon-Fano Compression & Speed** | Shannon-Fano prefix coding, cumulative probability sorting, symbol duration weights, transmission speed | [README](practice3/README.md) |
| **[practice4](practice4)** | **Channel Capacity & Noise Losses** | Mutual Information, Noisy Symmetric Channel capacity, Sinkhorn-Knopp (IPF) matrix normalization | [README](practice4/README.md) |
| **[practice5](practice5)** | **Huffman & Arithmetic Compression** | Huffman Block Coding ($L=1..4$), code redundancy, adaptive Arithmetic Coding (high-precision Decimal scaling) | [README](practice5/README.md) |
| **[practice6](practice6)** | **Hamming Codes** | Systematic Generator Matrix $G$, Parity Check Matrix $H$, Syndrome calculation, single-error correction | [README](practice6/README.md) |
| **[practice7](practice7)** | **Cyclic Codes (CRC)** | Polynomial division over $GF(2)$ using bitwise XOR, systematic code generation, remainder syndrome decoding | [README](practice7/README.md) |
| **[project](project)** | **Steam Discount Likelihood Predictor** | Steam Store API integration, SQLite caching database, XOR database cipher, discount decision heuristics | [README](project/README.md) |

---

## ⚙️ Setup & Local Execution

Follow these steps to set up the dependencies and run the scripts in a isolated virtual environment.

### 1. Clone the Repository
```bash
git clone https://github.com/LordofBorg/khai-information-theory-and-coding-labs.git
cd khai-information-theory-and-coding-labs
```

### 2. Set Up Virtual Environment & Dependencies
Create a virtual environment and install the required scientific and utility libraries (`numpy`, `scipy`, `matplotlib`, `beautifulsoup4`, `requests`):
```bash
# Create local virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Linux/macOS
# or: venv\Scripts\activate  # On Windows

# Install requirements
pip install -r requirements.txt
```

### 3. Run the Applications
* **To run a specific practice lab (e.g., Practice 1 - Text Entropy)**:
  ```bash
  python practice1/1.py
  ```
* **To run the web scraper (Practice 1 - Website Entropy)**:
  ```bash
  python practice1/2.py
  ```
* **To run the Steam Discount Predictor project**:
  ```bash
  cd project
  python 1.py
  ```

---

## 👥 Coursework Credits
The materials and implementations in this repository were developed by **Team No. 2** (Student Group) as part of the academic curriculum.

*Department of Computer Systems, Networks and Cybersecurity*
*NAU KHAI, Kharkiv — 2025*

