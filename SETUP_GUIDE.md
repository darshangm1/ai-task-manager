# 🚀 Quick Setup Guide - AI Task Manager

## ⚡ Quick Start (3 Steps)

### 1. Install Dependencies
```bash
pip install flask flask-cors openai
```

### 2. Run the Application
```bash
python app.py
```

### 3. Access Dashboard
Open browser: `http://127.0.0.1:5000`

## 🎯 New Features Added

### ✅ Completed Features

#### 1. **Toast Notification System**
- Modern, non-intrusive notifications
- Success ✅, Error ❌, Info ℹ️ types
- Auto-dismiss after 4 seconds
- Replaces all alert() popups

#### 2. **Search & Filter System**
- **Search Bar**: Real-time filtering by task name
- **Priority Filter**: All/High/Medium/Low
- **Status Filter**: All/Pending/Completed
- **Category Filter**: All/Work/Personal/Study/Health  
- **Sort Options**: Newest, Oldest, Priority, Due Date

#### 3. **Task Categories**
- 🏢 **Work** (Blue): meetings, projects, reports
- 👤 **Personal** (Purple): shopping, family, appointments
- 📚 **Study** (Orange): homework, exams, research
- 💪 **Health** (Green): gym, doctor, exercise
- AI auto-detects category from task description
- Color-coded badges on each task

#### 4. **Profile Settings**
- Update display name
- Change profile picture (URL)
- Avatar display in topbar
- Email shown (read-only)
- Real-time preview of avatar

#### 5. **Productivity Score & Streak**
- **Productivity**: (Completed ÷ Total) × 100%
- **Streak Counter**: Daily task completion tracking
- **Badges**: 🔥 (1-4 days), 🏆 (5-9), ⭐ (10-29), 💎 (30+)
- Automatic streak calculation
- Resets if you miss a day

#### 6. **Email Reminder System**
- Sends email 1 hour before task due time
- Beautiful HTML email template
- Configurable SMTP settings
- Gmail-ready with App Password support

#### 7. **Enhanced UI**
- 5 stat cards: Total, High Priority, Completed, Streak, Productivity
- Collapsible feature guide
- Professional animations
- Responsive design

## 📧 Email Configuration (Optional)

### Gmail Setup (Recommended)

1. **Enable 2-Factor Authentication**
   - Go to [Google Account Security](https://myaccount.google.com/security)
   - Enable 2-Step Verification

2. **Generate App Password**
   - Visit [App Passwords](https://myaccount.google.com/apppasswords)
   - Select "Mail" and "Windows Computer" (or Other)
   - Copy the 16-character password

3. **Configure app.py**
   ```python
   EMAIL_ENABLED = True
   SMTP_SERVER = "smtp.gmail.com"
   SMTP_PORT = 587
   SENDER_EMAIL = "youremail@gmail.com"
   SENDER_PASSWORD = "your-16-char-app-password"
   ```

4. **Restart Flask**
   ```bash
   python app.py
   ```

### Testing Email Reminders

1. Create a task with time 1 hour from now
2. Call the endpoint:
   ```bash
   curl -X POST http://127.0.0.1:5000/check_email_reminders
   ```
3. Check your email inbox

### Automatic Email Reminders

**Option 1: Task Scheduler (Windows)**
1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Daily at every hour
4. Action: Start program
   - Program: `curl.exe`
   - Arguments: `-X POST http://127.0.0.1:5000/check_email_reminders`

**Option 2: Cron Job (Linux/Mac)**
```bash
# Edit crontab
crontab -e

# Add this line (runs every hour)
0 * * * * curl -X POST http://127.0.0.1:5000/check_email_reminders
```

**Option 3: Python Script**
Create `email_scheduler.py`:
```python
import schedule
import time
import requests

def check_reminders():
    try:
        response = requests.post("http://127.0.0.1:5000/check_email_reminders")
        print(f"Checked reminders: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

# Run every hour
schedule.every().hour.do(check_reminders)

print("Email reminder scheduler started...")
while True:
    schedule.run_pending()
    time.sleep(60)
```

Run it:
```bash
pip install schedule requests
python email_scheduler.py
```

## 🎨 Customization Guide

### Change Theme Colors

Edit [dashboard.html](templates/dashboard.html) CSS variables (line ~6):
```css
:root {
    --bg-primary: #0f172a;      /* Main background */
    --bg-secondary: #1e293b;    /* Card backgrounds */
    --text-primary: #f1f5f9;    /* Main text */
    --text-secondary: #94a3b8;  /* Secondary text */
    --accent: #16a34a;          /* Accent color (green) */
}
```

### Add New Task Category

1. **Update Fallback Parser** (app.py, line ~90):
```python
def parse_task_fallback(text):
    # Add your category keywords
    if any(word in lower for word in ["gym", "workout", "fitness"]):
        category = "Fitness"
```

2. **Add to Edit Modal** (dashboard.html, line ~620):
```html
<option value="Fitness">🏋️ Fitness</option>
```

3. **Add CSS Style** (dashboard.html, line ~310):
```css
.category-fitness {
    background: linear-gradient(135deg, #ff6b6b, #ee5a6f);
}
```

4. **Add to Filter Dropdown** (dashboard.html, line ~540):
```html
<option value="Fitness">🏋️ Fitness</option>
```

## 🎯 Feature Usage

### Creating Smart Tasks

Type natural language in the input box:
```
Meeting with John tomorrow at 3pm high priority work
Project deadline on Friday at 5pm high priority 
Gym on Monday at 6am medium priority health
Study for exam next Thursday high priority
```

AI extracts:
- Task name
- Date (tomorrow, Friday, Monday, next Thursday)
- Time (3pm, 5pm, 6am)
- Priority (high, medium)
- Category (work, health, study)

### Using Voice Input

1. Click 🎤 **Start** button
2. Speak naturally: "Team meeting tomorrow at 2 PM high priority"
3. Click ⏹ **Stop** when done
4. Click ➕ **Add Task** to create
5. Voice text appears in input field for editing before adding

### Profile Picture Setup

**Option 1: Use Image URL**
1. Upload image to [Imgur](https://imgur.com/) or [Imgbb](https://imgbb.com/)
2. Copy direct link
3. Paste in Profile Settings → Profile Picture URL

**Option 2: Use UI Avatars (Automatic)**
- Leave URL empty
- System generates avatar with your initials
- Colors automatically assigned

### Understanding Streak System

**How It Works:**
- Complete at least 1 task each day
- Streak increments if you complete task on consecutive days
- Missing a day resets streak to 0
- Streak updates when you mark task as complete

**Badges:**
- 🔥 **Starting** (1-4 days): Keep going!
- 🏆 **Bronze** (5-9 days): Great job!
- ⭐ **Silver** (10-29 days): Impressive!
- 💎 **Diamond** (30+ days): You're a productivity master!

### Analytics Interpretation

**Priority Distribution Chart:**
- Shows breakdown of High/Medium/Low priority tasks
- Helps balance workload
- Larger high priority section = more urgent tasks

**Completion Status Chart:**
- Shows Pending vs Completed tasks
- Quick visual of progress
- Higher completed bar = productive day!

## 🛠️ Troubleshooting

### Issue: Voice Recognition Not Working

**Solutions:**
- Use Chrome browser (best Web Speech API support)
- Grant microphone permissions
- Use HTTPS or localhost (security requirement)
- Check system microphone settings

### Issue: Tasks Not Saving

**Check:**
1. Console for JavaScript errors (F12 → Console)
2. Backend running (terminal should show Flask logs)
3. Network tab for failed requests (F12 → Network)
4. Session expired (logout and login again)

### Issue: Theme Not Persisting

**Fix:**
1. Enable browser localStorage
2. Clear site data: F12 → Application → Clear storage
3. Disable private/incognito mode
4. Try different browser

### Issue: Streak Not Updating

**Verify:**
1. Task completion time (must be marked complete today)
2. Database last_task_date column exists: `python clean_db.py` (WARNING: deletes data)
3. Console errors after toggling task
4. Refresh page after completing task

### Issue: Email Not Sending

**Common Causes:**
1. `EMAIL_ENABLED = False` in app.py
2. Incorrect Gmail App Password (must be 16 characters, no spaces)
3. 2FA not enabled on Google Account
4. Firewall blocking port 587
5. SMTP credentials incorrect

**Debug Steps:**
1. Check terminal for error messages
2. Verify email configuration in app.py
3. Test with Gmail's SMTP
4. Try different email provider

### Issue: Filters Not Working

**Check:**
1. Browser console for errors
2. JavaScript enabled in browser
3. Clear browser cache
4. Try different filter combinations

## 📱 Browser Compatibility

| Browser | Voice | Notifications | Charts | Theme |
|---------|-------|---------------|--------|-------|
| Chrome  | ✅ Excellent | ✅ Yes | ✅ Yes | ✅ Yes |
| Edge    | ✅ Excellent | ✅ Yes | ✅ Yes | ✅ Yes |
| Firefox | ⚠️ Limited  | ✅ Yes | ✅ Yes | ✅ Yes |
| Safari  | ⚠️ iOS only | ⚠️ Limited | ✅ Yes | ✅ Yes |

**Recommendation**: Chrome or Edge for best experience

## 🔒 Security Notes

- Passwords hashed with werkzeug.security
- Session-based authentication (no JWT needed)
- CORS restricted to localhost
- SQL injection protected (parameterized queries)
- XSS protection via proper escaping

**Production Recommendations:**
- Change `app.secret_key` to random string
- Use environment variables for secrets
- Enable HTTPS with SSL certificate
- Use PostgreSQL instead of SQLite
- Add rate limiting for API endpoints
- Implement CSRF protection

## 📊 Database Backup

### Backup Database
```bash
# Create backup
copy tasks.db tasks_backup_2024.db

# Or use timestamp
copy tasks.db tasks_backup_%date%.db
```

### Restore Database
```bash
copy tasks_backup_2024.db tasks.db
```

### Export Tasks (Manual)
```bash
sqlite3 tasks.db
.mode csv
.output tasks_export.csv
SELECT * FROM tasks;
.quit
```

## 🚀 Performance Tips

1. **Database**: SQLite perfect for <100k records
2. **Frontend**: No build step needed (vanilla JS)
3. **Charts**: Cached in browser
4. **Images**: Use CDN for profile pictures
5. **Email**: Consider queue for bulk sends

## 📝 Development Roadmap

Potential future enhancements:
- [ ] Recurring tasks
- [ ] Task attachments
- [ ] Team collaboration
- [ ] Mobile app
- [ ] Calendar integration
- [ ] Export to PDF
- [ ] Task templates
- [ ] Time tracking
- [ ] Subtasks
- [ ] Dark mode for email templates

## 🎓 Learning Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Chart.js Docs](https://www.chartjs.org/docs/)
- [Web Speech API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API)
- [SQLite Tutorial](https://www.sqlitetutorial.net/)
- [JavaScript Fetch API](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API)

## 💬 Support

For issues or questions:
1. Check this guide and README.md
2. Review browser console (F12)
3. Check Flask terminal logs
4. Verify all dependencies installed
5. Try clean database: `python clean_db.py`

---

**Happy Task Managing! 🎯**
