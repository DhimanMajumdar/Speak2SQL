# 🤖 Speak2SQL – AI-Powered Data Analyst  
Transform natural language questions into SQL queries, execute them on a live SQLite database, and visualize the results with clear explanations.

Built using **Python**, **Streamlit**, **LangChain**, **Llama 3 / DeepSeek**, and an **AI-driven SQL reasoning pipeline**.

---

## 📸 Demo

![](images/one)
![](images/two)
![](images/three)
![](images/four)
![](images/five)
![](images/six)

## 🚀 Features

### 🔹 1. Natural Language → SQL  
Ask anything like:  
- *"How many products did Alice buy in June?"*  
- *"Total revenue generated from Electronics?"*  
- *"Which customer has spent the most?"*

The AI model generates clean SQL, which is executed on the SQLite database.

---

### 🔹 2. Live Query Execution  
Every query is securely executed on your local `amazon.db`, returning structured results.

---

### 🔹 3. Visual Charts  
Auto-plots results using Matplotlib when the output is chart-friendly  
(bar, line, pie, comparison, etc.).

---

### 🔹 4. Clean Explanations  
After SQL execution, the app:  
- Explains what the query means  
- Explains the returned result  
- Breaks down the logic like a human data analyst  

---


## 🛠️ Tech Stack

| Layer | Tools |
|-------|-------|
| **LLM** | Llama-3 via Ollama |
| **Orchestration** | LangChain |
| **Backend** | Python, SQLite3 |
| **Frontend** | Streamlit |
| **Visualization** | Matplotlib |
| **Environment** | venv + pip |

---

## 📂 Database Schema

The SQLite database includes:

- **customers** – customer details  
- **orders** – orders placed  
- **products** – product catalog  
- **order_items** – product↔order mapping  

---

## 🔧 How to Run

```bash
git clone https://github.com/yourusername/Speak2SQL
cd Speak2SQL

python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

pip install -r requirements.txt

streamlit run app.py




