# 📝 Blog-Application  
A full-stack blog application built using **Django** and **Django Templates**. This application allows users to **create, read, update, and delete** blog posts with authentication, user roles, and media storage.  

## 🚀 Features  
- 🔐 **User Authentication** (JWT-based login & registration)  
- 📝 **CRUD Operations** for blogs (Create, Read, Update, Delete)  
- 🏷️ **User Roles** (Admin, Author, Reader)  
- 📸 **Image Uploads** (AWS S3 for media storage)  
- 🌍 **Responsive UI** (Django templates & Tailwind CSS)  
- 📊 **PostgreSQL Database** for scalable data management  
- ☁️ **Deployed on AWS EC2**  

## 🛠️ Technologies Used  
- **Frontend & Backend:** Django, Django Templates, Tailwind CSS  
- **Database:** PostgreSQL  
- **Authentication:** JWT (JSON Web Tokens)  
- **Media Storage:** AWS S3  
- **Deployment:** AWS EC2 (t2.micro)  

---

## 📦 Installation & Setup  

### **1️⃣ Clone the Repository**  
```sh
git clone <repository-url>
cd django-blog-app
```
### **2️⃣ Set Up Environment Variables**
Create a .env file inside the project directory:
```sh
SECRET_KEY=your_secret_key
POSTGRES_DB=your_db_name
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=your_db_password
DB_HOST=your_db_host
DB_PORT=5432

AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_STORAGE_BUCKET_NAME=your_bucket_name
AWS_S3_REGION_NAME=your_region
```
### **3️⃣ Install Dependencies & Run the Project**
```sh
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Your blog application will be running at http://127.0.0.1:8000/ 🎉