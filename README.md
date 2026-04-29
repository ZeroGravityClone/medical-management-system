# 🏥 Medical Management System with AI Assistant

A modern, desktop-based Medical Management System built with Python and CustomTkinter. Designed for medical centers in Venezuela, this application streamlines patient management, scheduling, and features an integrated AI Medical Assistant powered by the Groq LPU (Llama 3.1).

<img width="846" height="624" alt="3" src="https://github.com/user-attachments/assets/9b74baec-f7ff-479b-8df6-39b8c2e0bcf0" />

## ✨ Features

* **Secure Authentication:** Role-based login system (e.g., Admin, Doctor, Receptionist).
* **Modern UI:** Clean, Aero-inspired graphical interface using CustomTkinter.
* **Patient Management:** Add, update, and organize patient records seamlessly.
* **Smart AI Assistant:** Built-in AI chat using Llama 3.1 (via Groq API) to provide instant medical context, answer queries, and assist staff.
* **Local Database:** Powered by SQLite for lightweight, fast, and portable data storage.

## 🛠️ Tech Stack

* **Language:** Python 3
* **GUI Library:** CustomTkinter / Tkinter
* **Database:** SQLite3
* **AI Integration:** Groq API (Llama 3.1 8B)
* **Other Tools:** Pillow (Image processing), tkcalendar (Date pickers)

## 🚀 Installation & Setup

Follow these steps to run the application on your local machine.

**1. Clone the repository**
```bash
git clone [https://github.com/ZeroGravityClone/medical-management-system.git](https://github.com/ZeroGravityClone/medical-management-system.git)
cd medical-management-system
```

2. Install dependencies
It is recommended to use a virtual environment. Install the required libraries using:

```bash
pip install -r requirements.txt
```

3. Set up the AI Assistant (Groq API)
To use the AI chat feature, you need a free API key from Groq.

Go to the Groq Console and create an API key.

Open the main python script and replace GROQ_API_KEY with your actual key.

4. Run the application
```bash
python "main.py"
```

Default Login Credentials
Since this uses a local SQLite database (sistema_medico.db), you can use the following default credentials to test the system:

Username: ADMIN

Password: 1234

(Note: Please update the default credentials after your first login for security).

📄 License
This project is for educational and community service purposes.
