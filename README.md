# Complaint Similarity & Priority Search System

**Department of Bachelor of Computer Applications (BCA) — Semester V**  
**KLE Technological University, Vidyanagar, Hubballi**  
**Course Project: Theme 2 · Search and Ranking System**

* **Submitted By:**
  * Ayeesha N (USN: `01FE24ICA024`) — Member 1
  * Mahek M (USN: `01FE24ICA052`) — Member 2
* **Project Guide:** Prof. Prajna Bhat

---

## 1. Project Overview

The **Complaint Similarity & Priority Search System** is an intelligent web application designed to manage, cluster, and prioritize institutional complaints. The system processes incoming issues in FIFO arrival order, groups semantically related complaints using NLP (TF-IDF vectorization and Cosine Similarity), dynamically evaluates priority based on four weighted factors, and routes issues to appropriate service departments.

---

## 2. Module Division & Team Responsibilities

### Member 1: Ayeesha N
* **Module 1: User & Complaint Management**
  * User registration, authentication, and session handling (`UserMixin`).
  * Complaint submission with server-side validation.
  * Personal dashboard and real-time status tracking.
* **Module 2: Admin & Complaint Management**
  * Administrative dashboard with key metrics and Chart.js visualizations.
  * Multi-criteria search and compound filtering (Category, Location, Priority, Status).
  * Lifecycle status transitions with full audit history (`ComplaintHistory`).
* **Git Branch:** `feature/member1-web-management`

### Member 2: Mahek M
* **Module 3: Complaint Similarity Search**
  * Natural language preprocessing using NLTK (lowercasing, punctuation stripping, stop-word removal, stemming).
  * TF-IDF vectorization across complaint descriptions using Scikit-learn.
  * Cosine similarity scoring against category candidates and threshold clustering into `IssueGroup` records.
  * Evidence logging in `similarity_records`.
* **Module 4: Priority Search & Ranking**
  * 4-factor normalization (Count, Severity, Affected Users, Recency).
  * Weighted priority score evaluation ($0.00$ to $100.00$) and discrete level assignment (`Low`, `Medium`, `High`, `Critical`).
  * Gate 1 search ranking: Priority Level $\rightarrow$ Similarity Score $\rightarrow$ Recency $\rightarrow$ ID.
* **Git Branch:** `feature/member2-nlp-engines`

---

## 3. Database Architecture (MySQL)

The system uses a shared MySQL database (`complaint_db`) with strict relational integrity:

1. **`departments`**: Institutional departments (`department_id` PK, `department_name`, `description`).
2. **`categories`**: Specific complaint domains (`category_id` PK, `department_id` FK, `category_name`).
3. **`users`**: System actors supporting roles `user`, `admin`, `staff` (`user_id` PK, `department_id` FK nullable).
4. **`issue_groups`**: Recurring issue clusters (`group_id` PK, `category_id` FK, `group_title`, `complaint_count`).
5. **`complaints`**: **The single shared model** (`complaint_id` PK, `user_id` FK, `category_id` FK, `group_id` FK, separate `queue_status` and `resolution_status`).
6. **`similarity_records`**: Mathematical comparison audit log (`similarity_id` PK, `complaint_id` FK, `group_id` FK, `similarity_score`).
7. **`complaint_history`**: Audit trail for all status changes (`history_id` PK, `complaint_id` FK, `actor_id` FK, `status_type`).

---

## 4. Setup & Installation Instructions

### Step 1: Clone and Open Repository
Ensure you are in the project root directory:
```bash
cd C:\Users\ayees\Documents\complaint_similarity_and_priority_search_system
```

### Step 2: Create Python Virtual Environment
```bash
python -m venv venv
```

Activate the virtual environment:
* **Windows (Command Prompt):**
  ```cmd
  venv\Scripts\activate
  ```
* **Windows (PowerShell):**
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```

### Step 3: Install Required Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Local MySQL Database
1. Open MySQL Command Line Client or MySQL Workbench.
2. Create the project database:
   ```sql
   CREATE DATABASE complaint_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
3. Copy the environment template:
   * On Windows: `copy .env.example .env`
4. Open `.env` and fill in your local MySQL credentials:
   ```env
   DB_HOST=localhost
   DB_PORT=3306
   DB_USER=root
   DB_PASSWORD=your_actual_mysql_password
   DB_NAME=complaint_db
   ```

### Step 5: Verify Priority Calculation Engine & Rules
Run the included unit test suite to verify mathematical constraints:
```bash
python -m unittest tests/test_priority_rules.py
```
*(All tests should pass, confirming weights sum to 1.0, normalization bounds remain $[0, 100]$, and classifications match approved thresholds).*

### Step 6: Start the Application
```bash
python run.py
```
* On startup, the application connects to MySQL, automatically executes `db.create_all()` to generate all 7 tables, and seeds the initial default departments and categories.
* Open your browser and navigate to: **`http://127.0.0.1:5000`**

---

## 5. Git Collaboration Guidelines

1. **Always work on your designated feature branch:**
   * Ayeesha: `git checkout -b feature/member1-web-management`
   * Mahek: `git checkout -b feature/member2-nlp-engines`
2. **Never commit `.env` or database credentials.**
3. **Do not modify `app/models.py` without team alignment.** The shared models are locked as the single source of truth.
4. **Member 1 uses the mock in `app/services/pipeline.py`** during UI development; **Member 2 replaces it** upon completing Modules 3 and 4.
