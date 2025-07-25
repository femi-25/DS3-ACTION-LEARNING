# 👾 Airflow Deployment Guide for Social-Media-Preferences Project

## 📌 Project Overview

The aim of the following README is to guide you in your **Apache Airflow** deployment with **Docker** 🐋 in your local **Windows** machine. My recommendation is to work with the **CMD** 🗿.

We are using the latest Airflow image available at **DockerHub**: 2.10.5

## ⚙️ Prerequisites

Before deploying Airflow, ensure the following requirements are met:

### 1️⃣ Enable WSL 2 (Windows Subsystem for Linux)

- Open **PowerShell** as Administrator and run:
  ```powershell
  wsl --install
  ```
- If WSL is already installed, ensure it is set to version 2:
  ```powershell
  wsl --set-default-version 2
  ```
- Restart your system if required.

### 2️⃣ Install Docker

- Download and install **Docker Desktop** from [Docker’s official website](https://www.docker.com/products/docker-desktop/).
- Ensure **WSL 2 backend** is enabled in Docker settings.

### 3️⃣ Check Port 8080 Availability

- Airflow uses port **8080** by default. Ensure no other service is running on this port:
  ```powershell
  netstat -an | findstr :8080
  ```
- If occupied, terminate the process using:
  ```powershell
  taskkill /PID <process_id> /F
  ```

## 🛠️ Deploying Airflow with Docker

### 1️⃣ Ensure You Have the Latest Main Branch

⚠️ **Warning:** Make sure to pull the latest main branch before proceeding.

### 2️⃣ Verify Required Files Exist

Ensure the following files and directories are in the **airflow** folder:

- `.dockerignore`
- `.gitignore`
- `config/`
- `dags/`
  - `ingestion_dag.py`
  - `prediction_dag.py`
- `data/`
  - `good_data/`
  - `bad_data/`
  - `raw_data/`
- `docker-compose.yaml`
- `Dockerfile`
- `logs/`
- `plugins/`
- `README.md`
- `requirements.txt`
- `scripts/random_file.sh`

📢 **Ignore the dummie files, it's just a way to include every folder you need when pulling the latest main**

### Navigate to the Airflow Root Folder

Before proceeding, navigate with your terminal to the **Airflow root folder**.

### 3️⃣ Initialize Airflow Database

```sh
docker compose up airflow-init
```

### 4️⃣ Start Airflow Services

```sh
docker compose up --build -d
```

### 5️⃣ Access Airflow UI

- Open **[http://localhost:8080](http://localhost:8080)** in a browser.
- Login credentials:
  - **Username:** airflow
  - **Password:** airflow

## 📡 Creating Airflow Connections with External Systems

Airflow can interact with external systems such as DBs, Cloud Computing services (for example AWS, GCP), APIs, etc. via its operators, hooks, or your custom functions. 

To be able to connect Airflow with these external systems you need to create an Airflow Connection for every external system you wish to interact with, there are several ways to achieve this, it can be done with the **Airflow CLI**, or with the **Airflow GUI**. This time we are going to use the GUI.

### 1️⃣ Navigate to Connections 

Once you have logged in your Airflow instance:

- Navigate to **Admin** > clic on **Connections**.
- Clic on the blue square button with the white `+`.

### 2️⃣ Create the Airflow connections in the GUI
For this project we need to configure **3 connections**, use the picklist to select the following connections (one by one), you can also type the connection's names in the picklist, at the bottom there's a save button 💾.

- **File (Path)** connection to manage local files. 💽
  - _**Connection Id:**_ fs_conn_good_data 
  - _**Path:**_ /
- **HTTP** connection to reach our predictions API. 🌐
  - _**Connection Id:**_ fs_conn_good_data
  - _**Host:**_ _Your IPv4 Address_
  - _**Port:**_ _The assigned port of the Application_
- **Postgres** connection to interact with our Postgres Database. 🐘
  - _**Connection Id:**_ pg_conn_dsp
  - _**Host:**_ _Your IPv4 Address_
  - _**Database:**_ _The name of the database to establish the connection_
  - _**Login:**_ _Your username to authenticate in the DB_
  - _**Password:**_ _Your password to authenticate in the DB_



📢 **Check your IPv4 address every time you connect to a different internet network, and update your Airflow Connections accordingly.**

## 📜 Explanation of DAGs

### **1️⃣ ingestion\_dag.py**

#### 📌 Summary

This DAG is responsible for ingesting CSV data from the **raw\_data** folder.

#### 🛠️ Tasks

1. **read\_data**
   - Picks a random CSV file from `/opt/airflow/data/raw_data`.
   - Reads its contents into a DuckDB temporary database.
   - Pushes the DataFrame to XCom (`ti.xcom_push`).
   - Returns the file path via XCom.
2. **save\_file**
   - Retrieves the file path from XCom (`ti.xcom_pull`).
   - Moves the file to `/opt/airflow/data/good_data`.

#### 🔄 Execution Order

```
read_data → save_file
```

---

### **2️⃣ prediction\_dag.py**

#### 📌 Summary

This DAG automates predictions using an external **FastAPI** service.

#### 🛠️ Tasks

1. **check\_for\_new\_data**

   - Scans `/opt/airflow/data/good_data` for new CSV files.
   - Compares against `prediction_checklist.txt`.
   - Pushes new file paths to XCom if they exist.
   - Skips task if no new files are found.

2. **make\_predictions**

   - Retrieves new file paths from XCom.
   - Reads CSV files into DuckDB.
   - Converts data into JSON.
   - Sends it to the **FastAPI** prediction service.
   - Appends processed file names to `prediction_checklist.txt` if successful.

#### 🔄 Execution Order

```
check_for_new_data → make_predictions
```

---

## 🔹 Understanding `ti` (Task Instance) and XComs

### 📌 What is `ti`?

`ti` stands for **Task Instance**. It provides access to task execution metadata (refer to Python **kwargs).

### 🔗 How `XCom` Works

**XCom** (Cross-Communication) is used to pass data between tasks within the same runtime.

- **Push Data:**
  ```python
  ti.xcom_push(key='new_raw_data', value=df)
  ```
- **Pull Data:**
  ```python
  ti.xcom_pull(key='new_raw_data')
  ```

## 🎯 Final Notes

- **Airflow DAGs run on a schedule defined in ****************************`schedule`**************************** parameter.**
- **Use Airflow UI to monitor DAG execution.**
- **Check logs for debugging in case of errors.**
- **[Check the official Airflow Documentation when in doubt](https://airflow.apache.org/docs/)**
- **[Check Airflow's best practices when feeling to confident](https://airflow.apache.org/docs/apache-airflow/2.2.5/best-practices.html)**

Thank you for reading 🗿.