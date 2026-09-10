## Repository

```
git clone https://github.com/Ihcarp443/scheme-bot.git
cd scheme-bot
```

---

# Project Structure

```text
scheme-bot/
│
├──govt_chatbot-main/frontend/my_app          # Next.js Frontend
├── backend_main/my_app          # FastAPI Backend
├── README.md
└── ...
```

---

# Prerequisites

Before setting up the project, ensure you have the following installed:

* Python 3.10 or above
* Node.js (v18 or above recommended)
* npm
* Git

---

# Project Setup

## Step 1: Create a Virtual Environment

From the project root directory:

### Windows

```bash
python -m venv venv
```

### Linux / macOS

```bash
python3 -m venv venv
```

---

## Step 2: Activate the Virtual Environment

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

---

## Step 3: Install Backend Dependencies

Navigate to the backend folder.

```bash
cd backend_main
```

Install the required Python packages.

```bash
pip install -r requirements.txt
```

---

## Step 4: Install Frontend Dependencies

Navigate to the frontend folder.

```bash
cd ..govt_chatbot-main/frontend/my-app
```

Install all Node.js dependencies.

```bash
npm install
```

---

## Step 5: Configure Environment Variables

### Backend

Inside the **backend_main** folder, create a file named:

```text
.env
```

Add the required backend environment variables.

Example:

```env
HF_TOKEN=

SARVAM_API_KEY=

```

---

### Frontend

Inside the **govt_chatbot-main/frontend/my-app** folder, create a file named:

```text
.env
```

Add the required frontend environment variables.

Example:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

> Replace the values above with the appropriate environment variables for your setup.

---

## Step 6: Configure Database Files


Inside the **backend_main** directory, inside data folder :

```text
backend/
└── data/
```

Copy the **Scheme_DB folder provided separately** into this folder.

The final structure should look like:

```text
backend/
│
├── data/
│   ├── Scheme_DB
│   └── schemes
│
├── main.py
├── requirements.txt
└── ...
```

> **Note:** The required database folder is not included in the repository and must be copied manually before running the backend.

---

# Running the Application

## Start the Backend

Open a terminal.

```bash
cd backend
```

Activate the virtual environment if it is not already active.

Windows:

```bash
..\venv\Scripts\activate
```

Linux/macOS:

```bash
source ../venv/bin/activate
```

Run the FastAPI server.

```bash
uvicorn main:app
```

The backend will be available at:

```
http://localhost:8000
```

Swagger documentation(To check all the available APIs):

```
http://localhost:8000/docs (Directly paste this URL in your browser)
```

---

## Start the Frontend

Open another terminal.

```bash
cd govt_chatbot-main/frontend/my-app
```

Run:

```bash
npm run dev
```

The frontend will be available at:

```
http://localhost:3000
```

---

# Common Commands

### Install new Python packages

```bash
pip install <package_name>
pip freeze > requirements.txt
```

### Install new frontend packages

```bash
npm install <package_name>
```

---

# Notes

* Ensure all required environment variables are configured before starting the application.
* Ensure the required database files are copied into the `backend/DB` folder before running the backend.

---

# Repository

```
https://github.com/Ihcarp443/scheme-bot.git
```
