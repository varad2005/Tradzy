# 🔐 Get Your Gmail App Password - Quick Guide

## Why You Need This:
Gmail requires an **App Password** (not your regular password) to send emails from applications.

---

## ⚡ Quick Steps (5 minutes):

### Step 1: Enable 2-Step Verification
1. Go to: **https://myaccount.google.com/security**
2. Find **"2-Step Verification"**
3. Click **"Get Started"** and follow the steps
4. ✅ Complete the setup

### Step 2: Generate App Password
1. Go to: **https://myaccount.google.com/apppasswords**
2. You'll see "App passwords" section
3. Click **"Select app"** → Choose **"Mail"**
4. Click **"Select device"** → Choose **"Other"** → Type **"Tradzy"**
5. Click **"Generate"**
6. 📋 Copy the **16-character password** (looks like: `xxxx xxxx xxxx xxxx`)

### Step 3: Add to .env File
1. Open `.env` file in Tradzy folder
2. Find the line: `MAIL_PASSWORD=YOUR_APP_PASSWORD_HERE`
3. Replace with your password: `MAIL_PASSWORD=xxxx xxxx xxxx xxxx`
4. Save the file

### Step 4: Restart the App
```powershell
# Stop the current app (Ctrl+C in terminal)
# Then restart:
cd Tradzy\backend
python app.py
```

---

## ✅ Test It:

1. Place an order with email: `andhalevarad@gmail.com`
2. Check your Gmail inbox!
3. Check spam folder if not in inbox

---

## 🔍 Alternative Method (If Above Doesn't Work):

If you can't find "App passwords":

1. **Make sure 2FA is enabled** (must be done first)
2. **Direct link**: https://myaccount.google.com/apppasswords
3. If still no access, try: https://support.google.com/accounts/answer/185833

---

## 🎯 Your Current .env Setup:

```
MAIL_USERNAME=andhalevarad@gmail.com
MAIL_PASSWORD=YOUR_APP_PASSWORD_HERE  ← Replace this!
```

---

## 📧 After Setup:

Emails will be sent **from**: `andhalevarad@gmail.com`  
And will show as: **"Tradzy Orders"**

---

**Need help?** Let me know if you get stuck on any step!
