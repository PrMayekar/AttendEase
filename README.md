# Attendance Optimization System
 
A Django-based web application that helps students track their attendance and stay above the required **75% threshold** throughout the semester.
 
Students upload their attendance record, timetable, and academic calendar. The system processes these files, calculates subject-wise attendance, flags subjects at risk, and generates a personalized recovery plan.
 
---
 
## Features
 
- Upload attendance record (JPG), timetable, and academic calendar (PDF)
- OCR-based automatic data extraction from uploaded files
- Subject-wise attendance percentage calculation
- Detects subjects below the 75% threshold
- Calculates how many lectures a student must attend to recover attendance
- Predicts future attendance based on different scenarios
- Recommends optimal days to skip using clustering (grouping holidays and weekends)
- Interactive dashboard with charts and color-coded indicators
- Teacher/Admin portal to view and verify student attendance
- Export recovery plan as PDF or CSV
---
 
## Tech Stack
 
| Layer | Technology |
|---|---|
| Backend | Python, Django 5.x |
| Frontend | HTML, CSS, JavaScript, Bootstrap, Chart.js |
| Database | MySQL |
| ORM | Django ORM |
| API | Django REST Framework |
| OCR | Optical Character Recognition (image parsing) |
| Task Queue | Django Celery (alerts and background jobs) |
 
---
 
## Formulas Used
 
**Attendance Percentage**
```
Attendance% = (Lectures Attended / Total Lectures Conducted) × 100
```
 
**Lectures Needed to Recover (reach 75%)**
```
x ≥ (0.75 × T − A) / (1 − 0.75)
 
where A = lectures attended, T = total conducted, x = lectures needed
```
 
**Future Attendance Prediction**
```
Best case  (attends all upcoming U): (A + U) / (T + U) × 100
Worst case (misses all upcoming U): A / (T + U) × 100
Partial    (attends k of U):        (A + k) / (T + U) × 100
```
 
---
 
## Screenshots
 
> Add your screenshots here after running the application.
 
```
screenshots/
├── dashboard.png
├── upload.png
├── recovery_plan.png
└── teacher_portal.png
```
 
![Dashboard](screenshots/dashboard.png)
![Recovery Plan](screenshots/recovery_plan.png)
![Upload Screen](screenshots/upload.png)
![Teacher Portal](screenshots/teacher_portal.png)
 
---
 
## Getting Started
 
```bash
# Clone the repo
git clone https://github.com/your-username/attendance-optimization-system.git
cd attendance-optimization-system
 
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
 
# Install dependencies
pip install -r requirements.txt
 
# Configure your .env file with DB credentials and secret key
 
# Run migrations
python manage.py migrate
 
# Start server
python manage.py runserver
```
 
---
