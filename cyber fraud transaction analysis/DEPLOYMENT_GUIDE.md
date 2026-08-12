# DEPLOYMENT GUIDE: PUBLISHING YOUR CYBER FRAUD DETECTION SYSTEM TO A LIVE PUBLIC URL

This guide explains how to convert your local Flask web application (`http://127.0.0.1:5000`) into a **live public URL** accessible from any device (phone, laptop, examiner's computer) anywhere in the world.

---

## ⚡ METHOD 1: INSTANT LIVE PUBLIC URL (RECOMMENDED FOR VIVA / PRESENTATION)

Use **ngrok** to generate a secure HTTPS public URL pointing directly to your local running app in 60 seconds.

### Step 1: Install `pyngrok`
In your terminal, run:
```bash
py -m pip install pyngrok
```

### Step 2: Start Your Flask Application
In one terminal window, run:
```bash
py main.py
```

### Step 3: Launch Public Tunnel
Open a second terminal window and run:
```bash
py -c "from pyngrok import ngrok; public_url = ngrok.connect(5000); print('\n🌐 YOUR LIVE PUBLIC URL IS:', public_url)"
```

### Output Example:
```text
🌐 YOUR LIVE PUBLIC URL IS: NgrokTunnel: "https://a1b2-34-56-78-90.ngrok-free.app" -> "http://localhost:5000"
```

You can share this `https://...ngrok-free.app` URL with anyone! Anyone opening this link on mobile or desktop will see your live **Cyber Fraud Detection SOC Dashboard**.

---

## 🌐 METHOD 2: 24/7 PERMANENT CLOUD HOSTING (RENDER.COM - FREE TIER)

To host your application 24/7 permanently on the cloud without leaving your laptop turned on, use **Render.com** (Free Python Hosting).

### Step 1: Add a `Procfile` and `wsgi.py`
Create a file named `Procfile` in your project folder with this content:
```text
web: gunicorn main:app
```

Add `gunicorn` to `requirements.txt`:
```bash
py -m pip install gunicorn
```

### Step 2: Push Project to GitHub
1. Create a repository on GitHub (e.g. `cyber-fraud-detection`).
2. Initialize git and push your project code:
```bash
git init
git add .
git commit -m "Initial commit of Cyber Fraud Detection System"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/cyber-fraud-detection.git
git push -u origin main
```

> **Note**: If `models/random_forest_model.pkl` is > 100MB, Render will train the model automatically on first boot because `main.py` generates the `.pkl` file if missing.

### Step 3: Deploy on Render.com
1. Go to [https://render.com](https://render.com) and create a free account.
2. Click **New +** -> **Web Service**.
3. Connect your GitHub repository `cyber-fraud-detection`.
4. Configure settings:
   - **Name**: `cyber-fraud-detection`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn main:app`
5. Click **Create Web Service**.

Within 2-3 minutes, Render will build your application and give you a permanent live URL:
`https://cyber-fraud-detection.onrender.com`

---

## 📱 SUMMARY OF LIVE DEPLOYMENT OPTIONS

| Feature | Method 1: pyngrok / Local Tunnel | Method 2: Render.com Cloud |
| :--- | :--- | :--- |
| **Setup Time** | 1 Minute | 5 Minutes |
| **Prerequisites** | Running locally on laptop | GitHub Account |
| **Cost** | 100% Free | 100% Free |
| **Best For** | Live Viva, Seminar, Demonstration | Permanent Portfolio / Resume link |
| **URL Type** | `https://xxxx.ngrok-free.app` | `https://xxxx.onrender.com` |
