# Hate Speech Bot – Documentation

## 🧠 Application Overview

The Hate Speech Bot is a complete system for the automated detection of hate speech within **Telegram**. It functions as a monitoring and analysis tool that enables:

- Automatic **interception and analysis of user messages** in group chats
- When hate speech is detected, it records information about the **user and the message into a database**
- Displays violators through a **real-time web interface**

### System Components:
1. **Telegram Bot**: Intercepts messages and uses a fine-tuned LLM model to classify whether the message contains hate speech.
2. **MySQL Database**: Stores user information, messages, and incident timestamps.
3. **Web Application (Flask)**: Displays a real-time table of violations, updated every 5 seconds.

---

## 🧱 List of Used Docker Containers

| Container                           | Description |
|-------------------------------------|-------------|
| `tetianamohorian/hate-speech-bot`   | Contains the Telegram bot, classification model (e.g. fine-tuned BERT), and Flask frontend |
| `mysql:8`                           | Relational database for storing violator records |

---

## ☸️ List of Kubernetes Objects

| Object                    | Description |
|---------------------------|-------------|
| `Namespace: botspace`     | Isolated space for all app-related objects |
| `Deployment: bot-deployment` | Deploys the container with the bot |
| `Deployment: flask-web`   | Deploys the Flask web server |
| `StatefulSet: mysql`      | Ensures persistent and consistent MySQL operation |
| `PersistentVolume`        | Stores database data outside the pod |
| `PersistentVolumeClaim`   | Requests disk space for the database |
| `Service: mysql`          | Internal service for accessing the database |
| `Service: flask-service`  | Port-forward service for accessing the web |
| `ConfigMap: init-sql`     | Contains initial SQL schema scripts |
| `Secret: bot-secret`      | Secure storage of sensitive data like the Telegram token |

---

## 🌐 Virtual Networks and Storage

- All pods communicate over an internal network in `botspace`, minimizing data leakage risks
- `PersistentVolume` attached to MySQL ensures data preservation even after pod restarts

---

## ⚙️ Container Configuration

- **Flask Web**: Runs on port `5000`, accessible via `flask-service`. Automatically updates via JavaScript (AJAX `fetch`) every 5 seconds
- **Telegram Bot**: Runs in a separate thread, classifies messages using a PyTorch model or HuggingFace Transformers, and logs results into the database
- **MySQL**: Initialized with an `initContainer` that runs a script from the `ConfigMap`

---

## 🚀 Usage Guide

### 1. Prepare the Application:

```bash
./prepare-app.sh
```

- Builds the Docker image
- Pushes it to Docker Hub

---

### 2. Start the Application:

```bash
./start-app.sh
```

- Creates Kubernetes objects
- Starts port-forwarding for Flask web on `localhost:8888`

---

### 3. Stop Port-Forwarding:

```bash
pkill -f "kubectl port-forward"
```

- Terminates temporary access via port-forward

---

### 4. Remove the Application:

```bash
./stop-app.sh
```

- Deletes the entire `botspace`, including database and services

---

## 🌍 Accessing the Web Interface

After launching the app, open a browser:

```
http://localhost:8888
```

- A table of violators will be displayed
- Data updates automatically every 5 seconds

---

## 📦 Technologies Used

- **Python, Flask, PyTorch / Transformers** – text analysis and classification
- **Docker, Docker Hub** – containerization
- **Kubernetes** – orchestration, scaling, and network isolation
- **MySQL** – relational data storage
- **JavaScript (AJAX)** – real-time frontend updates
