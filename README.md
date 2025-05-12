![Screenshot 2025-05-12 230326](https://github.com/user-attachments/assets/9913b133-f70a-4340-b651-178fca5c2b39)
# Student Management System (STDMS) 🏫

This is a Django-based web application designed to manage student records, attendance, marks, assignments, and announcements in an educational institution.

---

## 🔧 Features

- **Student Login** – View subjects, marks, announcements, attendance  
- **Teacher Login** – Generate QR for attendance, manage marks, assignments, announcements  
- **Admin Panel** – Manage students/teachers, upload CSV, edit/delete records  
- **QR-based Attendance System** with geolocation validation  
- **Celery + Redis** integration to automatically mark absent students  
- **CSV Upload** for bulk student, teacher, and marks management  
- **Role-based Authentication** for Admin, Teacher, and Student  

---

## 🛠️ Tech Stack

- **Backend:** Django 5.1.6, Celery  
- **Database:** MySQL  
- **Frontend:** HTML, CSS (via Django templates)  
- **Queue:** Redis  
- **Other:** SSL support for local testing, logging, environment separation  

---

## 🚀 How to Run Locally

1. Clone the repo:
    ```bash
    git clone https://github.com/your-username/student-management-system.git
    cd student-management-system
    ```

2. Create virtual environment & install dependencies:
    ```bash
    python -m venv venv
    source venv/bin/activate  # Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

3. Set up MySQL database:
    - Create a DB named `student_management_system`
    - Update DB credentials in `settings.py`

4. Run migrations:
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

5. Create a superuser:
    ```bash
    python manage.py createsuperuser
    ```

6. Start Redis:
    ```bash
    sudo service redis-server start
    ```

7. Start Django app & Celery:
    ```bash
    python manage.py runserver
    celery -A stdms worker --loglevel=info
    ```

8. (Optional) Run with SSL:
    ```bash
    python manage.py runsslserver --certificate certs/cert.pem --key certs/key.pem 127.0.0.1:8000
    ```
Screenshots shows the description about Login Page , Dashboard  and functionality of Admin , Student and Teacher! 
---
![Screenshot 2025-05-05 160030](https://github.com/user-attachments/assets/5e7d8462-72a9-4b1b-b9eb-f6804bb5587f)
![Screenshot 2025-05-05 151717](https://github.com/user-attachments/assets/b648c696-00f1-4a8c-99d0-c4aadf1886a0)
![Screenshot 2025-05-05 151702](https://github.com/user-attachments/assets/72fa6363-9375-4e06-a735-201a4ad85230)
![Screenshot 2025-05-05 151643](https://github.com/user-attachments/assets/adb74da5-a9e6-4ce9-884c-a791165c960f)
![Screenshot 2025-05-05 151608](https://github.com/user-attachments/assets/9cb507eb-7af9-42e0-a9f1-b91971fb2b7f)
![Screenshot 2025-05-05 151521](https://github.com/user-attachments/assets/f9aef994-351b-4385-8cd4-145d3a560428)
![Screenshot 2025-05-05 151446](https://github.com/user-attachments/assets/76469922-a8c9-421b-8175-25e3bb1d3621)
![Screenshot 2025-05-05 151410](https://github.com/user-attachments/assets/3ce6c44c-6784-4f6f-80ca-4ff86110ba9b)
![Screenshot 2025-05-05 150704](https://github.com/user-attachments/assets/9cd52e75-4760-4d9f-b828-e2a8b2c447b4)
VIsual representation of Attendance 
![Screenshot 2025-05-05 150238](https://github.com/user-attachments/assets/8dd90a70-4e46-4f35-aa00-01f23646a23c)




