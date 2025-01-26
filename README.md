# 🚗 Car Rental Management System

## 📜 Table of Contents
1. [📖 Project Description](#-project-description)
2. [✨ Features](#-features)
3. [🛠️ Technologies Used](#%EF%B8%8F-technologies-used)
4. [📥 Installation](#-installation)
5. [🤝 Contributing](#-contributing)
6. [📜 License](#-license)

---

## 📖 Project Description
This project is a **🚗 Car Rental Management System** that uses role-based authorization to let the user access and perform operations depending on their role. To sum it up, T
the project contains authentication, autherization, CRUD operations on a No-SQL database, live notification feature and optinally can use kafka zookeeper to log system events.

---

## ✨ Features
- **🔒 User Authentication:** Secure 🔑 login and 📝 registration system for customers and employees.
- **🚗 Vehicle Management:** Add ➕, edit ✏️, and remove ❌ cars from the fleet with details like ✅ availability, 💵 rental rates, and 🔧 branch name.
- **📅 Reservation Management:** Book 🛒, approve ✅, and reject ❌ reservations with real-time ⏱️ notification on availability status and reservation approvals.
- and more!!! Please check the Swagger documentation for more detailed and technical ellaborations!

---

## 🛠️ Technologies Used
- **Backend:** 🐍 Python's FastAPI
- **Database:** 🗄️ MongoDB
- **Authentication:** 🔐 JWT-based authentication

---

## 📥 Installation

### Prerequisites
Ensure you have the following:
- 🐍 Python 3.9 or above
<br> and check out the `requirments.txt` file!!!

### Steps
1. Clone the repository:
   ```bash
   git clone 
   cd car-rental-management
   ```
2. Modify the `.env` file.
3. Download the requirments from the `requirments.txt` using:
   ```bash
   pip install -r requirements.txt
   ```
4. Download [Kafka zookeeper](https://kafka.apache.org/downloads) (PS: [a great yt tutorial here!](https://youtu.be/w6A-uDEb7JY))...
5. If you do not have Java please install it for Kafka to work. (PS: I ran into `Error: missing 'server'` heres [another yt tutorial!](https://youtu.be/EVsdfMsQxhQ))
6. Start Kafka Zookeeper (modify paths according to where you installed kafka)
   ```bash
   C:\kafka_2.12-3.9.0\bin\windows\zookeeper-server-start.bat C:\kafka_2.12-3.9.0\config\zookeeper.properties # if virtual env active please deactivate
   ```
   and Kafka Server...
   ```bash
   C:\kafka_2.12-3.9.0\bin\windows\kafka-server-start.bat C:\kafka_2.12-3.9.0\config\server.properties
   ```
7. Start MongoDB server (changes according to your setup)
   ```bash
   C:\DEVEL\stage\var\scripts\start-mongodb.bat
   ```
8. Now you can run the application using...
   ```bash
   .\.venv\Scripts\uvicorn main:app --reload # PS: sometimes doesnt work in powershell try cmd 
   ```

---

## 🤝 Contributing
PLEASE feel welcome to contribute 🛠️ to improve this project! To contribute:
1. Fork the repository 🍴.
2. Create a new branch 🌿:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Commit your changes 📝:
   ```bash
   git commit -m "Add your message here"
   ```
4. Push to the branch 🚀:
   ```bash
   git push origin feature/your-feature-name
   ```
5. Submit a pull request 🔄.

---

## 📜 License
This project is licensed under the [MIT License](LICENSE).
