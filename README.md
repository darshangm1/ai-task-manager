# 🎯 AI Task Manager - Professional Edition

A comprehensive, production-ready task management application with AI-powered task parsing, dark/light themes, productivity tracking, and email reminders.

## ✨ Features

### 🎨 Core Features
- **AI Task Parsing**: Natural language task creation using OpenAI GPT-4 with intelligent fallback
- **Voice Recognition**: Hands-free task creation with Web Speech API
- **CRUD Operations**: Complete task lifecycle management (Create, Read, Update, Delete)
- **Task Categories**: Auto-categorized tasks (Work, Personal, Study, Health) with color-coded badges
- **Priority Levels**: High, Medium, Low priority with visual indicators
- **Dark/Light Mode**: Persistent theme system across all pages

### 🔍 Advanced Features
- **Smart Search**: Real-time task filtering with instant results
- **Multi-Filter System**: Filter by priority, status, category simultaneously
- **Sort Options**: Sort by newest, oldest, priority, or due date
- **Toast Notifications**: Modern, non-intrusive feedback system
- **Task Completion Toggle**: Quick checkbox-based completion with visual feedback

### 📊 Analytics & Tracking
- **Interactive Charts**: Chart.js powered priority distribution and completion status
- **Productivity Score**: Real-time completion percentage calculation
- **Streak System**: Daily task completion tracking with gamification badges:
  - 🔥 Starting Streak (1-4 days)
  - 🏆 Bronze Streak (5-9 days)
  - ⭐ Silver Streak (10-29 days)
  - 💎 Diamond Streak (30+ days)
- **Smart Statistics**: Total tasks, high priority count, completed tasks, streak, productivity

### 🔔 Reminder System
- **Browser Notifications**: Popup alerts 15 minutes before task due time
- **Email Reminders**: Automated email notifications 1 hour before tasks (configurable)
- **Continuous Checking**: Background reminder service checks every 30 seconds

### 👤 User Management
- **Secure Authentication**: Password hashing with werkzeug security
- **Profile Settings**: Update name and profile picture
- **Avatar Display**: Personalized profile pictures in topbar
- **Password Management**: Change password with verification
- **Session Persistence**: Secure session-based authentication

### 🎨 Professional UI/UX
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Animated Modals**: Smooth transitions and interactions
- **Custom Scrollbars**: Themed scrollbar design
- **Pending/Completed Sections**: Visual task organization
- **Category Badges**: Color-coded task categories with icons
- **Priority Indicators**: Visual priority badges

## 🚀 Setup Instructions

### Prerequisites
- Python 3.8 or higher
- Modern web browser (Chrome, Firefox, Edge, Safari)

### Installation

1. **Clone or download the project**
   ```bash
   cd c:\AI_Project
   ```

2. **Install Python dependencies**
   ```bash
   pip install flask flask-cors openai
   ```

3. **Configure OpenAI API (Optional)**
   - Set your OpenAI API key as environment variable:
     ```bash
     # Windows
     set OPENAI_API_KEY=your-api-key-here
     
     # Linux/Mac
     export OPENAI_API_KEY=your-api-key-here
     ```
   - Or add to system environment variables permanently
   - **Note**: App works without API key using fallback parser

4. **Configure Email Reminders (Optional)**
   - Open `app.py`
   - Find the email configuration section (around line 27):
     ```python
     EMAIL_ENABLED = True  # Change to True
     SMTP_SERVER = "smtp.gmail.com"
     SMTP_PORT = 587
     SENDER_EMAIL = "your-email@gmail.com"  # Your Gmail
     SENDER_PASSWORD = "your-app-password"  # Gmail App Password
     ```
   - **Gmail Setup**: Enable 2FA and generate App Password at [Google Account Security](https://myaccount.google.com/security)

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the application**
   - Open browser and go to: `http://127.0.0.1:5000`
   - Create account on signup page
   - Login and start managing tasks!

## 📖 Usage Guide

### Creating Tasks

**Method 1: AI Text Input**
- Type natural language: "Meeting with team tomorrow at 3pm high priority work"
- AI automatically extracts: task name, date, time, priority, category

**Method 2: Voice Input**
- Click microphone icon 🎙️
- Speak your task naturally
- Click stop when done
- Task is auto-parsed and created

**Method 3: Manual Entry**
- Create task first
- Click "Edit" to set date, time, priority, category manually

### Task Management

- **Complete Task**: Click checkbox next to task name
- **Edit Task**: Click "Edit" button, modify details, save
- **Delete Task**: Click "Delete" button (confirmation via toast)
- **View Analytics**: Scroll down to see charts and statistics

### Filtering & Search

- **Search**: Type in search bar to filter by task name
- **Filter by Priority**: Select All/High/Medium/Low
- **Filter by Status**: Select All/Pending/Completed
- **Filter by Category**: Select All/Work/Personal/Study/Health
- **Sort Tasks**: Choose newest, oldest, priority, or due date

### Profile Settings

1. Click your avatar in top-right corner
2. Select "⚙️ Profile Settings"
3. Update name or profile picture URL
4. Changes reflect immediately across dashboard

### Theme Toggle

- Click 🌙/☀️ icon in top-right to switch themes
- Theme preference saved automatically
- Works across login, signup, and dashboard pages

## 🎯 Task Category Detection

The AI automatically categorizes tasks based on keywords:

- **🏢 Work**: meeting, project, deadline, report, presentation, client, email
- **👤 Personal**: shopping, family, birthday, call, appointment, cleaning
- **📚 Study**: homework, assignment, exam, study, research, class, lecture
- **💪 Health**: gym, workout, doctor, exercise, meditation, health, medicine

## 📊 Productivity Features

### Streak System
- Complete at least one task daily to maintain streak
- Consecutive days increase streak counter
- Breaking streak (missing a day) resets to 0
- Gamification badges motivate consistency

### Productivity Score
- Calculated as: (Completed Tasks / Total Tasks) × 100
- Updates in real-time as tasks are completed
- Visual percentage display in statistics section

### Analytics Charts
- **Priority Distribution**: Pie chart showing High/Medium/Low distribution
- **Completion Status**: Bar chart showing Pending vs Completed
- Theme-aware colors matching dark/light mode

## 🔔 Reminder Configuration

### Browser Notifications
- Automatically requests permission on first load
- Checks every 30 seconds for upcoming tasks
- Alerts 15 minutes before due time
- No configuration needed

### Email Reminders
1. Configure SMTP settings in `app.py` (see step 4 above)
2. Email sent automatically 1 hour before task due time
3. Beautiful HTML email template with task details
4. Endpoint: `/check_email_reminders` (can be called by cron job)

**Automated Email Setup (Advanced)**:
- Use Task Scheduler (Windows) or cron (Linux/Mac) to call endpoint every hour
- Example cron job:
  ```bash
  0 * * * * curl -X POST http://127.0.0.1:5000/check_email_reminders
  ```

## 🗂️ File Structure

```
AI_Project/
├── app.py                    # Flask backend API (19 endpoints)
├── tasks.db                  # SQLite database (auto-created)
├── templates/
│   ├── dashboard.html        # Main task dashboard
│   ├── login.html           # Login page
│   └── signup.html          # Signup page
├── clean_db.py              # Database cleanup utility
└── README.md                # This file
```

## 🔧 Database Schema

### Users Table
- `id`: Primary key
- `name`: User's display name
- `email`: Unique email (login credential)
- `password`: Hashed password
- `profile_picture`: Avatar URL
- `streak`: Daily completion streak count
- `last_task_date`: Last task completion date

### Tasks Table
- `id`: Primary key
- `user_id`: Foreign key to users
- `task`: Task description
- `date`: Due date (YYYY-MM-DD)
- `time`: Due time (HH:MM)
- `priority`: High/Medium/Low
- `completed`: 0 (pending) or 1 (completed)
- `created_at`: Timestamp
- `category`: Work/Personal/Study/Health

## 🛠️ API Endpoints

### Authentication
- `POST /signup` - Create new account
- `POST /login` - User login
- `POST /logout` - User logout
- `GET /me` - Get current user info

### Tasks
- `POST /ai` - Create task (AI parsing)
- `GET /tasks` - Get all user tasks
- `POST /toggle_completed/<id>` - Toggle completion status
- `POST /edit/<id>` - Update task
- `DELETE /delete/<id>` - Delete task
- `POST /update_priority/<id>/<priority>` - Update priority

### User Profile
- `POST /change_password` - Change password
- `POST /update_profile` - Update name
- `POST /update_profile_picture` - Update avatar

### Reminders
- `POST /check_email_reminders` - Trigger email reminder check

## 🎨 Customization

### Theme Colors
Edit CSS variables in `dashboard.html` (around line 6):
```css
:root {
    --bg-primary: #0f172a;
    --bg-secondary: #1e293b;
    --text-primary: #f1f5f9;
    --accent: #16a34a;
}
```

### Email Template
Customize HTML email in `send_email_reminder()` function in `app.py`

### Task Categories
Add new categories in:
1. `parse_task_fallback()` function in `app.py`
2. Edit modal dropdown in `dashboard.html`
3. Category filter dropdown in filter bar
4. CSS color styles for new category

## 🐛 Troubleshooting

### Database Issues
```bash
python clean_db.py  # Resets database (WARNING: deletes all data)
```

### Voice Recognition Not Working
- Ensure HTTPS or localhost (required by browser)
- Grant microphone permissions
- Try Chrome (best support for Web Speech API)

### Email Not Sending
- Verify SMTP credentials
- Enable "Less secure app access" or use App Password (Gmail)
- Check firewall/antivirus blocking port 587
- Set `EMAIL_ENABLED = True` in app.py

### Theme Not Saving
- Enable browser localStorage
- Clear browser cache and try again
- Check browser console for errors

## 🚀 Performance Tips

1. **Database**: Indexes on user_id and completed columns for faster queries
2. **Frontend**: Chart.js loaded via CDN (no build step needed)
3. **Backend**: SQLite perfect for single-user/small team deployments
4. **Reminders**: Browser notifications more efficient than email for frequent checks

## 📝 Future Enhancements (Ideas)

- Recurring tasks (daily, weekly, monthly)
- Task attachments and notes
- Collaborative tasks (team sharing)
- Mobile app version
- Export tasks to CSV/PDF
- Task templates library
- Integration with calendar apps
- Advanced analytics (weekly/monthly reports)
- Task time tracking
- Subtasks and checklists

## 🎓 Tech Stack

- **Backend**: Flask 3.x, SQLite3, Python 3.8+
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Charts**: Chart.js 4.x
- **AI**: OpenAI GPT-4 API
- **Voice**: Web Speech API
- **Security**: Werkzeug password hashing, Flask sessions
- **Email**: smtplib (standard library)

## 📄 License

This project is for educational and portfolio purposes. Feel free to modify and use as needed.

## 👨‍💻 Author

Created as a professional portfolio project demonstrating full-stack development skills, UI/UX design, and modern web technologies.

## 🙏 Acknowledgments

- OpenAI for GPT-4 API
- Chart.js for beautiful visualizations
- Flask community for excellent documentation
- Material Design for UI inspiration

---

**Made with ❤️ using Flask, JavaScript, and AI**
