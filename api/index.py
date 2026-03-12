# ===============================
# VITAL ARC - HEART HEALTH TRACKER
# Single Jupyter Notebook Cell
# ===============================

import os
import io
import csv
import sqlite3
import traceback
from datetime import datetime, timezone, timedelta

from flask import Flask, request, redirect, render_template_string, session, send_file, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

# Heavy imports moved to function scope:
# pd, np, LogisticRegression, reportlab


# Create Flask app
app = Flask(__name__)

# ================================
# LOGO (embedded as base64)
# ================================
LOGO_B64 = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAUDBAQEAwUEBAQFBQUGBwwIBwcHBw8LCwkMEQ8SEhEPERETFhwXExQaFRERGCEYGh0dHx8fExciJCIeJBweHx7/2wBDAQUFBQcGBw4ICA4eFBEUHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh7/wAARCAB4AHgDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD5wFPUUwU9a2MiQCnCkXpThVoBwFPApq08UyAxS4paWgBhFNIqSmmgCMimNUjcUw0hojYVG3WpWqJutSykMNFBopAC1IOtRr2p69aAJRTgaYDQW6AcmrWoMl3CtTSdF1LU0aW3g2wIcPPKwSNfqzYA/OpY7ay0NFl1aIXWoMAyWRJCxehlI5z/ALAwfUjpVTUdZv8AU5FN1OSicRxqAscY9FUcKPoK9Klg1FXq/cedUxM5aUtu7/Q200TRLcYvvEMbv3W0gaXH4naPyJp/2Lwl937fquf732VMfl5lc4knFPD11KFJbRRzNVXvN/gbz6Fo1xxYeIYg56JdwtFn8RuX8yKytX0TUtMVZLm3Jhf7k0ZDxv8ARlyD+dVzIR0NWdN1m+05m+zzfu34kicBo5B6Mp4P41EsPRn0sa05Vo9b+v8AmjKJFNJrfurKy1mJ7jSYvs96oLS2WSQ4HVoieT/unkdie3Ok9j1rza+HlReuz6nfSqKa8wPSomqQmo2NczNkMbmikaikMENPFQrUikUCJC2FrU0100nTxrEqhrqUlbBGGQuOGlI9jwvvk/w1l2kD3t/b2URAeeRUBPbJ60viC+S91R/s+RawgQ26+ka8D8T1PuTXpYKmknVfojkxD5mqf3kfmvLK0kjs7MdzMxyST3NTIwqs/wC7PlfxD731rpfB/g3X/Ezn+y7F5I1Pzyn5UX6sePwruhCU3ZGFScKceaTsjIV6kDmvRG+DXihoGayk0++lQZaGC6VnH4HFcWNA1Yat/ZRsLj7Zv8vyPLO/d6Y65rV4eouhjRxFCtfkknYoB+aRjXptv8FvFRt0kvX06wkcZWG5u1Rz+HNcr4x8EeIfCzj+1bB44m4SVSGjb6MOPwqvYStc2pVqU3aMkzm45pYJkmidkdSGVlOCCO4NaGtLHqNl/bNuipMrBL2NRgbj0kA7Buc+h+oqLSLdb+RrAjEsgPkH/bHRfx6fXFR6NcJa6j5NzkW84MM4/wBhu/1Bww9xUukpw5ZbP8zr5NbrdGbuyKaxp95BJZ309pLw8LlG+oOKiJr5ycHCTi90bjWNFITRUjGA0/OBUSmlY8UAX9Ak8u6vLvvbWUrqfRmGwfq9Z2lgPdgsMqgLn6AZ/pVjTHxaawB1NmP/AEdHVXRjk3QHUWzkflXuYZfuqa9fzOKfxTZs+C9Kk1/xRZ6YrYNxKAzYztHVj+Aya7f4l+MZLedvCvh9zZaTYfuSsRwZmHDMxHXnP161z3wQuorf4hWDSnG7eoJ9SjYrD8Txy2/iO/gmz5iXDq2fXca7ot08NzR3bOSVJVcVae0VderNXwm2v3msxR6F9rlvslo1tyd/AySMewr1Y/GJIfD5updNj/4TNI/so1IxjiL+9/v9un+FZP7Okdtph1PxPfExxW6pbxv6PI4Bx+GPzrm/iH4enT4oXuj2cXzXF3+4QekhBUf+PV0RhUVJS3v/AF/kTKlSxGIdOcdI9fzXpsYGoaxqGoXb3V3dzTTOdzO7lmJ+pru/hf4zle5Twt4ika90O/IhaKU58pjwrKT05x/OuL8YeHb3wxrD6ZfNG7qoZZIjlHUjIKnuP8Kr+GYJrnXrGCAEyyToqY9SwxU03UVRRkz1fq8KlPTY0vE2lTeGfG09grnda3OY26ZGcqfyxTPifYJp3jK+iiUKjuJVA7BwGx+td94u0r/hI/jBcyBf9BtPKa8l/hUKoyCfU4x/+o1558S9Vj1fxVdX0JzE7Yj/AN0cA/kK6K9Hkoyb6tGtKDbTfbUyvEzeZeWt3/z8WsbsfVgNpP5qazs5q7rx/wBA0j1+zt+XmvWcpyK+VzFJYh+dvyBq2g4mimk80VwgMBpW6UwGlzxQBNox3X8trn/j6tpIR/vFcr/48BVbw5LHHq8KTECKQ+XJn+6w2n+dRu8kE0dxE22SNg6kdiDkU3XI1S8F3AMW90PNjx/Dk/Mv4HI/KvZwNX90mt4P8Gc84Xk13O502/8ABWm3YM1rqkV3A/34n2lWB6jnrXRzL4HudP8A7fvdI16eCaQhrlpQ25++Tuzn615XqDC/tk1JOZQAlyO+7oH/AOBfzz6it/wB4nj0wy6Zqkf2jSrsbZozzsP94f57DuBXvQxkZVPZzSUXs7fccjwra5k3f1On8ReMfD8fhePw/wCF7a7toHuRPMZyMkgccgnPb8hXpVslpfatpPj66Obe30gzSt3Myj+fJx/u14l4v8LyaWRf2En2vTJvmimTnAPQH/Hv9cgXIfG0ieAz4cWKQTFthl3/AC+Vu3bceu7v6VpGvKlOUa+mmn/AOunhYtJw/q+53Fz438F+JLS2fxfp1/LqFuGj32pVVKlsjuP859as26fD+HS28QWWga8LWBwPPMwUB+wBD5zyOlefeCPCk+sOb++k+x6VD801w5wCB1C57+/b8gZ/iB4rg1IQ6Po8f2fSLMbYoxx5h/vn9cfUnqTVRrSjD2tRW7HpU8PGK02L/ijx3JqFmdI0Oxj0uwc4dIzl5c/3m7/5yTXEanIGuyqnITC5+gxT7Y/Z4DePw3Kwj1Pr9B/OmaOiS3huLgZt7cebL7gdF/E4H41xVas61lJ6v8Ebcqih3iNtl3bWfe3t0Rh6MRuP6sapqeKhluJLy9mupDlpHLE/U1JnHSvl8XVVavKa2OGb1FY80UwmiucgaDS0gpfpQAyVcim2skTwtp924SJ23RSHpFJ0yf8AZPAP0B7U9hxVeePIrahXlRnzL5+YSjzKwyN7rS71kkTa6/K6NyGB7H1BqybZLkebYEk9WgJ+dfp/eH61HHcxvCtrqCNJGgxHKv34vb3X2P4YpJLCeNPPtnFzCOfMh52/UdV/GvapyjUjeHvR7dV/X3Cjo9dzf8K+Kr7RS1rMgubJ+JLeTke+M9D/AJNdAjeBWf8AtYtMF6mxwc7v8Px/wrgk1K4IxOsdwBx+9QMfz6/rUq30PX+z7fP1f/4qvQoY/khyyakltzLY66bSOj8UeLr7W1SzhQWthHgRW8XA46Zx1P6egrJS3S2Hm35KnqsIPzt9f7o+vNVP7SnC4gWO3B/55IFP59f1p8FjcSp9ouGFvAefNmOAfoOrfhWU60q0+b4n+CNubqx7yXGo3aRxpuY/KiKMBR6D0FLqtzHDbrpdo4dQ26eVekj+3+yO34nvUVxqEcULWemKwVxiSZvvyD09h7fmTVOGPHua8zF4xRi4Qd293+iMqtXoieFdq0/NIOKDXjnKGaKSigQUtIKXtQAGmsM06g0DK0seahTzoJBJBI8bjoynBq6RmmMme1OMpRd4uzC4n9pXLf8AHzBbXPvJENx/EYP60o1CD/oFWuf96T/4qmmLNJ5Q9K6lmGIW7v6pMadtiUatcr/x7W1tbH1SIbh+JyarTPcXMhkuJXkY9SxyalWMelSKoFZ1cVWqq05afgNyZFFFgdKmUYpQMClFYWJDpRRRQACiiigQgooooAWkJoooGGaKKKACjiiigApaKKBBRRRQMKKKKACiiigD/9k="

# =========================
# CONFIGURATION VARIABLES
# =========================
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "heart.csv")
DB_FILE = os.path.join(os.path.dirname(__file__), "..", "heart_app.db")
SECRET_KEY = "heart_secret_2025"
app.secret_key = SECRET_KEY

# Global startup flag
_app_ready = False

def ensure_startup():
    global _app_ready, MODEL, COL_NAMES
    if _app_ready:
        return
    
    print("--- [LAZY STARTUP] Starting heavy initialization... ---")
    
    # 1. Train Model
    try:
        import pandas as pd
        from sklearn.linear_model import LogisticRegression
        
        print("--- [LAZY STARTUP] Loading data and training model... ---")
        temp_df = pd.read_csv(DATA_PATH)
        temp_X  = temp_df.drop("target", axis=1)
        temp_y  = temp_df["target"]
        temp_X  = temp_X.fillna(temp_X.median())
        
        temp_model = LogisticRegression(max_iter=3000)
        temp_model.fit(temp_X, temp_y)
        
        MODEL = temp_model
        COL_NAMES = list(temp_X.columns)
        print("--- [LAZY STARTUP] Model training complete. ---")
    except Exception as e:
        print(f"--- [LAZY STARTUP] ERROR TRAINING MODEL: {e} ---")
        # Keep placeholders if it fails
        if 'MODEL' not in globals() or MODEL is None:
            MODEL = None
            COL_NAMES = []


    # 2. Database Checks
    try:
        print("--- [LAZY STARTUP] Checking database... ---")
        if _os.path.exists(DB_FILE):
            _c = None
            try:
                import sqlite3 as _sq
                _c = _sq.connect(DB_FILE)
                _c.execute("SELECT id FROM users LIMIT 1")
                print("--- [LAZY STARTUP] DB File exists and is readable. ---")
            except Exception as _e:
                print(f"--- [LAZY STARTUP] DB Check failed: {_e}. Recreating... ---")
                if _c: _c.close()
                try: _os.remove(DB_FILE)
                except: pass
            finally:
                if _c: _c.close()

        init_db()
        setup_admin()
        migrate_db()
        print("--- [LAZY STARTUP] Database initialization complete. ---")
    except Exception as e:
        print(f"--- [LAZY STARTUP] DATABASE ERROR: {e} ---")

    _app_ready = True
    print("--- [LAZY STARTUP] All systems READY. ---")

# Placeholder globals (re-initialized in ensure_startup)
MODEL = None
COL_NAMES = []


# ================================
# EMAIL HELPER
# ================================
@app.errorhandler(Exception)
def handle_exception(e):
    # Log the full traceback to the terminal
    print("GLOBAL ERROR CAUGHT:")
    traceback.print_exc()
    # Return a JSON response for API calls or a string for browser calls
    if request.path.startswith("/api/"):
        return jsonify({"status": "error", "message": str(e), "trace": traceback.format_exc()}), 500
    return f"<h2>Internal Server Error</h2><pre>{traceback.format_exc()}</pre>", 500

# ================================
# VISIT TRACKING MIDDLEWARE
# ================================
@app.before_request
def track_visits():
    # Trigger lazy startup on first request
    ensure_startup()
    
    # Ignore certain paths
    ignored_paths = ["/api/", "/static/", "/favicon.ico", "LOGO", "png", "jpg", "jpeg"]
    if any(p in request.path for p in ignored_paths):
        return

    # Only track successful GET requests to actual pages
    if request.method == "GET":
        today = datetime.now().strftime("%Y-%m-%d")
        try:
            con = get_db()
            # Ensure the table entry for today exists
            row = con.execute("SELECT id, visit_count FROM site_visits WHERE visit_date=?", (today,)).fetchone()
            if row:
                con.execute("UPDATE site_visits SET visit_count = visit_count + 1 WHERE id=?", (row["id"],))
            else:
                con.execute("INSERT INTO site_visits (visit_date, visit_count) VALUES (?, 1)", (today,))
            con.commit()
            con.close()
        except Exception as e:
            # If tracking fails, log the error but don't break the site
            print(f"--- VISIT TRACKING ERROR ({today}): {str(e)} ---")
# EMAIL HELPER
# ================================
def send_email(to_email, subject, body):
    import smtplib
    from email.mime.text import MIMEText
    
    gmail_user = os.getenv("GMAIL_USER")
    gmail_pass = os.getenv("GMAIL_PASS")
    
    if not gmail_user or not gmail_pass:
        msg = "Email error: GMAIL_USER or GMAIL_PASS not set."
        print(msg)
        return False, msg
    
    try:
        msg = MIMEText(body, 'html')
        msg['Subject'] = subject
        msg['From'] = gmail_user
        msg['To'] = to_email
        
        # Using Port 587 with STARTTLS
        server = smtplib.SMTP('smtp.gmail.com', 587, timeout=15)
        server.starttls()
        server.login(gmail_user, gmail_pass)
        server.send_message(msg)
        server.quit()
        return True, "Success"
    except Exception as e:
        err = f"SMTP error: {str(e)}"
        print(f"Email error for {to_email}: {err}")
        return False, err


# ================================
# HELPERS
# ================================
def get_recommendations(vals, pred):
    chol, trestbps = vals[4], vals[3]
    if pred == 1:
        foods     = ["Leafy greens (spinach, kale)", "Fatty fish (salmon, mackerel)",
                     "Berries (blueberries, strawberries)", "Nuts (almonds, walnuts)",
                     "Olive oil", "Avocados", "Sweet potatoes"]
        exercises = ["Walking 30 min daily", "Swimming 3x/week",
                     "Yoga for stress relief", "Light cycling"]
    else:
        foods     = ["Continue balanced diet", "Fresh fruits daily",
                     "Vegetables variety", "Lean proteins"]
        exercises = ["Jogging 3x/week", "Strength training 2x/week",
                     "Cycling", "Sports activities"]
    if chol > 240:
        foods.insert(0, "REDUCE: Red meat, fried foods")
    if trestbps > 140:
        foods.insert(0, "REDUCE: Salt intake")
    return foods, exercises

def calc_health_score(row):
    score = 100
    if row["prediction"] == 1: score -= 30
    if row["chol"]     > 240:  score -= 10
    if row["chol"]     > 200:  score -= 5
    if row["trestbps"] > 140:  score -= 10
    if row["trestbps"] > 120:  score -= 5
    if row["thalach"]  < 100:  score -= 10
    if row["fbs"]      == 1:   score -= 5
    if row["exang"]    == 1:   score -= 5
    if row["age"]      > 60:   score -= 5
    return max(0, score)

def calc_bmi(weight_kg, height_cm):
    h   = height_cm / 100
    bmi = round(weight_kg / (h * h), 1)
    if   bmi < 18.5: cat = "Underweight"
    elif bmi < 25:   cat = "Normal"
    elif bmi < 30:   cat = "Overweight"
    else:            cat = "Obese"
    return bmi, cat

def get_dark(u):
    try:
        con = get_db()
        row = con.execute("SELECT dark_mode FROM users WHERE username=?", (u,)).fetchone()
        con.close()
        return row["dark_mode"] if row else 0
    except:
        return 0

# ================================
# PDF GENERATION
# ================================
def generate_pdf(username, pd_data):
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    
    buffer = io.BytesIO()
    doc    = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)

    story  = []
    styles = getSampleStyleSheet()

    def mk_style(name, size, clr, bold=True, align=TA_CENTER):
        return ParagraphStyle(name, parent=styles["Normal"], fontSize=size,
                              textColor=clr, alignment=align,
                              fontName="Helvetica-Bold" if bold else "Helvetica")

    story.append(Paragraph("VITAL ARC - PREDICTION REPORT",
                            mk_style("t", 22, colors.HexColor("#667eea"))))
    story.append(Spacer(1, 0.2*inch))

    def section(title):
        story.append(Spacer(1, 0.15*inch))
        story.append(Paragraph(title, mk_style("h", 14, colors.HexColor("#667eea"), align=0)))
        story.append(Spacer(1, 0.08*inch))

    def simple_table(data, col_widths):
        t = Table(data, colWidths=col_widths)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f0f0f0")),
            ("FONTNAME",   (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTSIZE",   (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0,0), (-1,-1), 6),
            ("TOPPADDING",    (0,0), (-1,-1), 6),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        return t

    section("Patient Information")
    story.append(simple_table([
        ["Name:",      username],
        ["Date:",      str(pd_data["timestamp"]).split()[0]],
        ["Report ID:", "VA-" + str(pd_data["id"]).zfill(6)],
    ], [2*inch, 4*inch]))

    section("Prediction Result")
    rl   = str(pd_data["risk_level"])
    rc   = colors.HexColor("#00b894") if "LOW" in rl else colors.HexColor("#d63031")
    rt   = Table([["RISK LEVEL: " + rl]], colWidths=[6*inch])
    rt.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), rc),
        ("TEXTCOLOR",  (0,0), (-1,-1), colors.white),
        ("ALIGN",      (0,0), (-1,-1), "CENTER"),
        ("FONTNAME",   (0,0), (-1,-1), "Helvetica-Bold"),
        ("FONTSIZE",   (0,0), (-1,-1), 16),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10),
        ("TOPPADDING",    (0,0), (-1,-1), 10)
    ]))
    story.append(rt)

    section("Health Metrics")
    metrics = [
        ["Metric", "Value", "Unit"],
        ["Age",             str(int(pd_data["age"])),      "years"],
        ["Gender",          "Male" if pd_data["sex"]==1 else "Female", "-"],
        ["Resting BP",      str(int(pd_data["trestbps"])), "mm Hg"],
        ["Cholesterol",     str(int(pd_data["chol"])),     "mg/dl"],
        ["Max Heart Rate",  str(int(pd_data["thalach"])),  "bpm"],
        ["ST Depression",   str(round(pd_data["oldpeak"],1)), "-"],
    ]
    mt = Table(metrics, colWidths=[2.5*inch, 2*inch, 1.5*inch])
    mt.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#667eea")),
        ("TEXTCOLOR",  (0,0), (-1,0), colors.white),
        ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
        ("ALIGN",      (0,0), (-1,-1), "CENTER"),
        ("FONTSIZE",   (0,0), (-1,-1), 10),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("TOPPADDING",    (0,0), (-1,-1), 6),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0,1), (-1,-1),
         [colors.white, colors.HexColor("#f8f9fa")]),
    ]))
    story.append(mt)

    vals = [pd_data["age"], pd_data["sex"], pd_data["cp"], pd_data["trestbps"],
            pd_data["chol"], pd_data["fbs"], pd_data["restecg"], pd_data["thalach"],
            pd_data["exang"], pd_data["oldpeak"], pd_data["slope"], pd_data["ca"], pd_data["thal"]]
    foods, exercises = get_recommendations(vals, pd_data["prediction"])

    section("Recommendations")
    ns = ParagraphStyle("ns", parent=styles["Normal"], fontSize=10, leading=14)
    story.append(Paragraph("<b>Recommended Foods:</b>", ns))
    for f in foods:
        story.append(Paragraph("  - " + f, ns))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("<b>Recommended Exercises:</b>", ns))
    for e in exercises:
        story.append(Paragraph("  - " + e, ns))

    ds = ParagraphStyle("ds", parent=styles["Normal"], fontSize=8,
                        textColor=colors.grey, alignment=TA_CENTER, leading=10)
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph(
        "<b>DISCLAIMER:</b> This report is generated by Vital Arc's machine learning model and should "
        "not replace professional medical advice. Consult a qualified healthcare provider.", ds))
    doc.build(story)
    buffer.seek(0)
    return buffer

# ================================
# FLASK APP (already created above at line 28)
# ================================

@app.errorhandler(500)
def internal_error(e):
    tb = traceback.format_exc()
    return "<pre style='padding:20px;color:red;'><b>500 Internal Server Error</b>\n\n" + tb + "</pre>", 500

# ================================
# SHARED CSS
# ================================
COMMON_CSS = """<style>
:root{--bg:#f0f2ff;--card:#ffffff;--text:#333;--sub:#666;--border:#e0e0e0;
  --accent:#667eea;--accent2:#764ba2;--nav:#ffffff;--inp:#ffffff;--alt:#f8f9fa;}
body.dark{--bg:#0f1117;--card:#1e2130;--text:#e0e0e0;--sub:#aaa;--border:#2a2d3e;
  --nav:#1a1d2e;--inp:#252840;--alt:#252840;}
*{margin:0;padding:0;box-sizing:border-box;}
body{font-family:'Segoe UI',Arial,sans-serif;background:var(--bg);color:var(--text);
  min-height:100vh;transition:background .3s,color .3s;}
.navbar{background:var(--nav);padding:14px 28px;border-radius:14px;margin-bottom:20px;
  display:flex;justify-content:space-between;align-items:center;
  box-shadow:0 4px 14px rgba(0,0,0,.12);}
.navbar-brand{display:flex;align-items:center;gap:12px;}
.navbar-brand img{width:48px;height:48px;border-radius:10px;object-fit:cover;
  box-shadow:0 2px 8px rgba(102,126,234,.4);}
.navbar-brand h2{color:var(--accent);font-size:22px;letter-spacing:-.5px;}
.navbar-brand span{font-size:11px;color:var(--sub);display:block;margin-top:-2px;
  font-weight:normal;letter-spacing:.5px;}
.nav-links a{margin-left:12px;color:var(--accent);text-decoration:none;font-weight:bold;
  padding:7px 13px;border-radius:8px;transition:all .2s;}
.nav-links a:hover{background:var(--accent);color:#fff;}
.card{background:var(--card);padding:26px;border-radius:14px;
  box-shadow:0 6px 20px rgba(0,0,0,.1);margin-bottom:20px;}
input,select,textarea{width:100%;padding:11px;margin:7px 0;border:2px solid var(--border);
  border-radius:9px;font-size:14px;background:var(--inp);color:var(--text);transition:.2s;}
input:focus,select:focus{outline:none;border-color:var(--accent);}
.btn{padding:12px 22px;background:linear-gradient(135deg,var(--accent),var(--accent2));
  color:#fff;border:none;border-radius:10px;font-size:14px;font-weight:bold;
  cursor:pointer;transition:transform .2s;display:inline-block;}
.btn:hover{transform:translateY(-2px);}
.btn-sm{padding:6px 14px;font-size:12px;border-radius:7px;}
.btn-outline{background:transparent;border:2px solid var(--accent);color:var(--accent);}
.btn-danger{background:linear-gradient(135deg,#e17055,#d63031);}
.btn-green{background:linear-gradient(135deg,#00b894,#00cec9);}
.g2{display:grid;grid-template-columns:1fr 1fr;gap:20px;}
.g3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:20px;}
.g4{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;}
.sc{background:var(--card);padding:20px;border-radius:14px;
  box-shadow:0 4px 14px rgba(0,0,0,.08);text-align:center;}
.sc h4{color:var(--sub);font-size:13px;margin-bottom:8px;}
.sc .val{font-size:28px;font-weight:bold;color:var(--accent);}
.badge{padding:4px 13px;border-radius:20px;font-weight:bold;font-size:12px;}
.bl{background:#55efc4;color:#00864e;} .bh{background:#fab1a0;color:#9b1c1c;}
.lr{color:#00b894;} .hr{color:#d63031;}
.pw{max-width:1300px;margin:0 auto;padding:20px;}
.tgl-wrap{display:flex;align-items:center;gap:8px;}
.tgl{position:relative;width:50px;height:26px;}
.tgl input{opacity:0;width:0;height:0;}
.sld{position:absolute;top:0;left:0;right:0;bottom:0;background:#ccc;
  border-radius:26px;cursor:pointer;transition:.3s;}
.sld:before{content:"";position:absolute;height:20px;width:20px;left:3px;bottom:3px;
  background:#fff;border-radius:50%;transition:.3s;}
input:checked+.sld{background:var(--accent);}
input:checked+.sld:before{transform:translateX(24px);}
.bar{background:var(--border);border-radius:10px;height:13px;overflow:hidden;margin:7px 0;}
.bar-fill{height:100%;border-radius:10px;transition:width .4s;}
label.lbl{display:block;color:var(--sub);font-size:12px;font-weight:bold;margin-bottom:3px;}
table{width:100%;border-collapse:collapse;}
th{background:linear-gradient(135deg,var(--accent),var(--accent2));
  color:#fff;padding:12px;text-align:left;}
td{padding:11px;border-bottom:1px solid var(--border);color:var(--text);}
tr:nth-child(even) td{background:var(--alt);}
tr:hover td{background:rgba(102,126,234,.07);}
.ai{background:#e3f2fd;color:#1565c0;padding:11px;border-radius:9px;margin-bottom:14px;}
.as{background:#e8f5e9;color:#1b5e20;padding:11px;border-radius:9px;margin-bottom:14px;}
.ad{background:#fce4ec;color:#880e4f;padding:11px;border-radius:9px;margin-bottom:14px;}
@media(max-width:800px){.g2,.g3,.g4{grid-template-columns:1fr;}}
</style>"""

# ================================
# BASE TEMPLATE BUILDER
# ================================
def base_html(title, content, user="", dark=0):
    dm_cls = "dark" if dark else ""
    return (
        "<!DOCTYPE html><html><head>"
        "<meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
        "<title>" + title + " - Vital Arc</title>"
        + COMMON_CSS +
        "</head><body class='" + dm_cls + "'>"
        "<div class='pw'>"
        "<div class='navbar'>"
        "<div class='navbar-brand'>"
        "<img src='" + LOGO_B64 + "' alt='Vital Arc Logo'>"
        "<div>"
        "<h2>Vital Arc</h2>"
        "<span>Heart Health Tracker</span>"
        "</div>"
        "</div>"
        "<div class='nav-links' style='display:flex;align-items:center;gap:4px;flex-wrap:wrap;'>"
        "<a href='/dashboard'>Home</a>"
        "<a href='/predict'>Predict</a>"
        "<a href='/history'>History</a>"
        "<a href='/profile'>Profile</a>"
        "<a href='/logout'>Logout</a>"
        "</div></div>"
        + content +
        "</div>"
        "<script>"
        "function toggleDark(){"
        "fetch('/toggle_dark',{method:'POST'}).then(()=>location.reload());}"
        "</script>"
        "</body></html>"
    )


# ================================
# REMINDER TRIGGER (For Cron)
# ================================
@app.route("/api/trigger_reminders")
def trigger_reminders():
    # This route will be called by your cron job to send pending reminders
    con = sqlite3.connect(DB_FILE)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    
    # Join with users table to get the email address
    cur.execute("""
        SELECT r.*, u.email 
        FROM reminders r 
        JOIN users u ON r.username = u.username 
        WHERE r.email_sent = 0
    """)
    reminders = cur.fetchall()
    
    success_count = 0
    errors = []
    
    for r in reminders:
        # Skip if user has no email set
        if not r['email']:
            errors.append(f"ID {r['id']}: No email address listed for user {r['username']}")
            continue

        subject = "VitalArc Health Reminder"
        body = f"Hello! This is your reminder: {r['message']}"
        success, error_msg = send_email(r['email'], subject, body)
        
        if success:
            cur.execute("UPDATE reminders SET email_sent = 1 WHERE id = ?", (r['id'],))
            success_count += 1
        else:
            errors.append(f"ID {r['id']}: {error_msg}")
    
    con.commit()
    con.close()
    
    return jsonify({
        "status": "done",
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "processed": len(reminders),
        "sent_successfully": success_count,
        "failed": len(reminders) - success_count,
        "errors": errors
    })

# ================================
# DEBUG ROUTE
# ================================
@app.route("/api/debug")
def debug_route():
    import sqlite3
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    
    db_stats = {}
    samples = []
    try:
        cur.execute("SELECT COUNT(*) FROM reminders")
        db_stats['total_reminders'] = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM reminders WHERE email_sent = 0")
        db_stats['pending_reminders'] = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM users")
        db_stats['total_users'] = cur.fetchone()[0]
        
        # New: Get some sample reminders and check their email status
        cur.execute("""
            SELECT r.id, r.username, r.email_sent, u.email 
            FROM reminders r 
            LEFT JOIN users u ON r.username = u.username 
            LIMIT 5
        """)
        for d in cur.fetchall():
            samples.append({
                "id": d[0], "user": d[1], "sent": d[2], "has_email": bool(d[3])
            })

    except Exception as e:
        db_stats['error'] = str(e)
    con.close()

    # Connectivity Check
    import socket
    conn_results = {}
    for port in [587, 465]:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        try:
            s.connect(("smtp.gmail.com", port))
            conn_results[f"port_{port}"] = "OPEN"
            s.close()
        except Exception as e:
            conn_results[f"port_{port}"] = f"BLOCKED: {str(e)}"

    return jsonify({
        "GMAIL_USER_SET": bool(os.getenv("GMAIL_USER")),
        "GMAIL_PASS_SET": bool(os.getenv("GMAIL_PASS")),
        "SMTP_CONNECTIVITY": conn_results,
        "DB_FILE_PATH": DB_FILE,
        "DB_EXISTS": os.path.exists(DB_FILE),
        "DB_SAMPLES": samples,
        "DB_STATS": db_stats,
        "SERVER_TIME_UTC": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "VAR_DEPLOY_STAMP": "2026-03-11_v3_GMAIL_SMTP"
    })

LOGIN_TMPL = """<!DOCTYPE html><html><head><title>Login - Vital Arc</title>
<style>*{margin:0;padding:0;box-sizing:border-box;}
body{font-family:'Segoe UI',sans-serif;height:100vh;display:flex;align-items:center;
justify-content:center;background:linear-gradient(135deg,#667eea,#764ba2);}
.box{background:#fff;padding:40px;border-radius:20px;box-shadow:0 20px 60px rgba(0,0,0,.3);width:420px;}
.logo-wrap{text-align:center;margin-bottom:18px;}
.logo-wrap img{width:80px;height:80px;border-radius:16px;object-fit:cover;
  box-shadow:0 4px 16px rgba(102,126,234,.5);}
h1{text-align:center;color:#667eea;margin-bottom:4px;font-size:26px;}
.subtitle{text-align:center;color:#888;margin-bottom:24px;font-size:13px;
  letter-spacing:.5px;font-weight:600;}
p{text-align:center;color:#888;margin-bottom:26px;font-size:14px;}
input{width:100%;padding:13px;margin:8px 0;border:2px solid #e0e0e0;border-radius:9px;font-size:14px;}
input:focus{outline:none;border-color:#667eea;}
.btn{width:100%;padding:13px;background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;
border:none;border-radius:9px;font-size:15px;font-weight:bold;cursor:pointer;margin-top:10px;}
.lnk{text-align:center;margin-top:18px;} .lnk a{color:#667eea;text-decoration:none;font-weight:bold;}
.err{background:#fee;color:#c00;padding:10px;border-radius:8px;margin-bottom:14px;text-align:center;}
</style></head><body><div class='box'>
<div class='logo-wrap'><img src='""" + LOGO_B64 + """' alt='Vital Arc Logo'></div>
<h1>Vital Arc</h1>
<div class='subtitle'>HEART HEALTH TRACKER</div>
<p>Monitor your heart health journey</p>
{% if error %}<div class='err'>{{ error }}</div>{% endif %}
<form method='post' action='/login'>
<input name='username' placeholder='Username' required>
<input type='password' name='password' placeholder='Password' required>
<button class='btn'>Login</button></form>
<div class='lnk'><a href='/signup'>Create New Account</a></div>
</div></body></html>"""

SIGNUP_TMPL = """<!DOCTYPE html><html><head><title>Sign Up - Vital Arc</title>
<style>*{margin:0;padding:0;box-sizing:border-box;}
body{font-family:'Segoe UI',sans-serif;height:100vh;display:flex;align-items:center;
justify-content:center;background:linear-gradient(135deg,#11998e,#38ef7d);}
.box{background:#fff;padding:40px;border-radius:20px;width:420px;box-shadow:0 20px 60px rgba(0,0,0,.2);}
.logo-wrap{text-align:center;margin-bottom:14px;}
.logo-wrap img{width:70px;height:70px;border-radius:14px;object-fit:cover;
  box-shadow:0 4px 14px rgba(17,153,142,.4);}
h1{text-align:center;color:#11998e;margin-bottom:20px;}
input{width:100%;padding:13px;margin:8px 0;border:2px solid #e0e0e0;border-radius:9px;font-size:14px;}
input:focus{outline:none;border-color:#11998e;}
.btn{width:100%;padding:13px;background:linear-gradient(135deg,#11998e,#38ef7d);color:#fff;
border:none;border-radius:9px;font-size:15px;font-weight:bold;cursor:pointer;margin-top:10px;}
.lnk{text-align:center;margin-top:18px;} .lnk a{color:#11998e;text-decoration:none;font-weight:bold;}
.err{background:#fee;color:#c00;padding:10px;border-radius:8px;margin-bottom:14px;}
</style></head><body><div class='box'>
<div class='logo-wrap'><img src='""" + LOGO_B64 + """' alt='Vital Arc Logo'></div>
<h1>Create Account</h1>
{% if error %}<div class='err'>{{ error }}</div>{% endif %}
<form method='post'>
<input name='username' placeholder='Username' required>
<input type='password' name='password' placeholder='Password' required>
<input type='email' name='email' placeholder='Email (for reminders)'>
<button class='btn'>Create Account</button></form>
<div class='lnk'><a href='/'>Back to Login</a></div>
</div></body></html>"""


@app.route("/")
def home():
    if "user" in session:
        return redirect("/dashboard")
    return render_template_string(LOGIN_TMPL, error=None)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    error = None
    if request.method == "POST":
        u = request.form["username"]
        p = generate_password_hash(request.form["password"])
        e = request.form.get("email", "")
        try:
            con = get_db()
            con.execute("INSERT INTO users(username,password,email) VALUES(?,?,?)", (u, p, e))
            con.commit()
            con.close()
            return redirect("/")
        except Exception:
            error = "Username already exists."
    return render_template_string(SIGNUP_TMPL, error=error)

@app.route("/login", methods=["POST"])
def login():
    u = request.form["username"]
    p = request.form["password"]
    con = get_db()
    row = con.execute("SELECT password FROM users WHERE username=?", (u,)).fetchone()
    con.close()
    if row and check_password_hash(row["password"], p):
        session["user"] = u
        try:
            # Track user login
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            con2 = get_db()
            con2.execute("INSERT INTO user_logins (username, login_time) VALUES (?, ?)", (u, ts))
            con2.execute("UPDATE users SET last_login=? WHERE username=?", (ts, u))
            con2.commit()
            con2.close()
        except Exception as e:
            print("Login tracking error:", e)
        return redirect("/dashboard")
    return render_template_string(LOGIN_TMPL, error="Invalid username or password.")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/toggle_dark", methods=["POST"])
def toggle_dark():
    if "user" not in session:
        return ("", 403)
    u = session["user"]
    con = get_db()
    row = con.execute("SELECT dark_mode FROM users WHERE username=?", (u,)).fetchone()
    new_val = 0 if (row and row["dark_mode"] == 1) else 1
    con.execute("UPDATE users SET dark_mode=? WHERE username=?", (new_val, u))
    con.commit()
    con.close()
    return ("", 204)


# ================================
# DASHBOARD
# ================================
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")
    u    = session["user"]
    dark = get_dark(u)
    con  = get_db()
    today = datetime.now().strftime("%Y-%m-%d")

    total     = con.execute("SELECT COUNT(*) FROM predictions WHERE username=?", (u,)).fetchone()[0]
    low_risk  = con.execute("SELECT COUNT(*) FROM predictions WHERE username=? AND prediction=0", (u,)).fetchone()[0]
    high_risk = con.execute("SELECT COUNT(*) FROM predictions WHERE username=? AND prediction=1", (u,)).fetchone()[0]
    lr        = con.execute(
        "SELECT prediction,age,chol,trestbps,thalach,fbs,exang,risk_level,timestamp "
        "FROM predictions WHERE username=? ORDER BY id DESC LIMIT 1", (u,)).fetchone()
    wr        = con.execute("SELECT glasses FROM water_intake WHERE username=? AND log_date=?", (u, today)).fetchone()
    water_gl  = wr["glasses"] if wr else 0
    med_cnt   = con.execute("SELECT COUNT(*) FROM medications WHERE username=? AND active=1", (u,)).fetchone()[0]
    rem_cnt   = con.execute("SELECT COUNT(*) FROM reminders WHERE username=? AND email_sent=0 AND remind_date>=?", (u, today)).fetchone()[0]
    con.close()

    latest_score = 0
    latest_risk  = "N/A"
    latest_date  = "No checkups yet"
    if lr:
        latest_score = calc_health_score({
            "prediction": lr["prediction"], "age": lr["age"], "chol": lr["chol"],
            "trestbps": lr["trestbps"], "thalach": lr["thalach"],
            "fbs": lr["fbs"], "exang": lr["exang"]
        })
        latest_risk = lr["risk_level"]
        latest_date = lr["timestamp"]

    sc = "#00b894" if latest_score >= 70 else "#fdcb6e" if latest_score >= 40 else "#d63031"
    risk_cls = "lr" if "LOW" in latest_risk else "hr"
    w_pct    = int(min(water_gl / 8 * 100, 100))

    con2 = get_db()
    urow = con2.execute("SELECT photo,height_cm,weight_kg FROM users WHERE username=?", (u,)).fetchone()
    con2.close()
    photo_html = ""
    if urow and urow["photo"]:
        photo_html = "<img src='" + urow["photo"] + "' style='width:60px;height:60px;border-radius:50%;object-fit:cover;border:3px solid var(--accent);margin-bottom:8px;'>"
    else:
        photo_html = "<div style='width:60px;height:60px;border-radius:50%;background:linear-gradient(135deg,var(--accent),var(--accent2));display:flex;align-items:center;justify-content:center;font-size:26px;color:#fff;margin:0 auto 8px;'>" + u[0].upper() + "</div>"

    bmi_dash = ""
    if urow and urow["height_cm"] and urow["weight_kg"] and float(urow["height_cm"]) > 0 and float(urow["weight_kg"]) > 0:
        bv, bc = calc_bmi(float(urow["weight_kg"]), float(urow["height_cm"]))
        bmi_dash = " &nbsp;|&nbsp; BMI: <b>" + str(bv) + "</b> (" + bc + ")"

    feat_btns = [
        ("/predict",     "🔍", "New Prediction",    "linear-gradient(135deg,#667eea,#764ba2)"),
        ("/history",     "📊", "History",            "linear-gradient(135deg,#a29bfe,#6c5ce7)"),
        ("/bmi",         "⚖️", "BMI Calculator",     "linear-gradient(135deg,#00b894,#00cec9)"),
        ("/water",       "💧", "Water Tracker",      "linear-gradient(135deg,#0984e3,#74b9ff)"),
        ("/medications", "💊", "Medications",        "linear-gradient(135deg,#e17055,#d63031)"),
        ("/goals",       "🎯", "Health Goals",       "linear-gradient(135deg,#fdcb6e,#e17055)"),
        ("/reminders",   "🔔", "Reminders",          "linear-gradient(135deg,#fd79a8,#e84393)"),
        ("/stress",      "🧘", "Stress Check",       "linear-gradient(135deg,#55efc4,#00b894)"),
        ("/bp_zone",     "🩺", "BP Zones",           "linear-gradient(135deg,#fab1a0,#e17055)"),
        ("/hr_zones",    "💓", "HR Zones",           "linear-gradient(135deg,#ff7675,#d63031)"),
        ("/export_csv",  "⬇️", "Export CSV",         "linear-gradient(135deg,#636e72,#2d3436)"),
        ("/profile",     "👤", "My Profile",         "linear-gradient(135deg,#a29bfe,#764ba2)"),
        ("/recommendation", "💡", "Recommendations",  "linear-gradient(135deg,#0984e3,#00cec9)"),
        ("/nearby",      "🏥", "Nearby Hospital",    "linear-gradient(135deg,#e17055,#fab1a0)"),
    ]

    feat_html = ""
    for href, icon, label, grad in feat_btns:
        feat_html += (
            "<a href='" + href + "' style='text-decoration:none;'>"
            "<div style='background:" + grad + ";border-radius:14px;padding:20px;text-align:center;"
            "box-shadow:0 4px 14px rgba(0,0,0,.15);transition:transform .2s;cursor:pointer;color:#fff;"
            "' onmouseover='this.style.transform=\"translateY(-4px)\"' onmouseout='this.style.transform=\"translateY(0)\"'>"
            "<div style='font-size:30px;margin-bottom:8px;'>" + icon + "</div>"
            "<div style='font-weight:bold;font-size:14px;'>" + label + "</div>"
            "</div></a>"
        )

    content = (
        "<div class='card' style='background:linear-gradient(135deg,var(--accent),var(--accent2));"
        "color:#fff;margin-bottom:20px;display:flex;align-items:center;gap:20px;'>"
        "<div style='text-align:center;'>" + photo_html + "</div>"
        "<div>"
        "<h2 style='color:#fff;margin-bottom:4px;'>Welcome back, " + u + "!</h2>"
        "<p style='opacity:.85;font-size:14px;'>Health Score: <b>" + str(latest_score) + "/100</b>" + bmi_dash + "</p>"
        "</div>"
        "<div style='margin-left:auto;text-align:right;'>"
        "<div style='font-size:13px;opacity:.8;'>Last checkup</div>"
        "<div style='font-weight:bold;'>" + str(latest_date)[:10] + "</div>"
        "</div></div>"

        "<div class='g4' style='margin-bottom:20px;'>"
        "<div class='sc'><h4>Total Predictions</h4><div class='val'>" + str(total) + "</div></div>"
        "<div class='sc'><h4>Low Risk</h4><div class='val lr'>" + str(low_risk) + "</div></div>"
        "<div class='sc'><h4>High Risk</h4><div class='val hr'>" + str(high_risk) + "</div></div>"
        "<div class='sc'><h4>Health Score</h4><div class='val' style='color:" + sc + ";'>" + str(latest_score) + "/100</div></div>"
        "</div>"

        "<div class='g2' style='margin-bottom:20px;'>"
        "<div class='card'>"
        "<h3 style='color:var(--accent);margin-bottom:12px;'>Latest Status</h3>"
        "<p><b>Risk Level:</b> <span class='" + risk_cls + "'>" + latest_risk + "</span></p>"
        "<p style='margin-top:8px;'><b>Last Check:</b> " + str(latest_date) + "</p>"
        "<p style='margin-top:8px;'><b>Health Score:</b></p>"
        "<div class='bar'><div class='bar-fill' style='width:" + str(latest_score) + "%;background:" + sc + ";'></div></div>"
        "<p style='text-align:right;font-size:12px;color:var(--sub);'>" + str(latest_score) + "%</p>"
        "</div>"
        "<div class='card'>"
        "<h3 style='color:var(--accent);margin-bottom:12px;'>Today at a Glance</h3>"
        "<p><b>Water:</b> " + str(water_gl) + "/8 glasses</p>"
        "<div class='bar'><div class='bar-fill' style='width:" + str(w_pct) + "%;background:#00cec9;'></div></div>"
        "<p style='margin-top:10px;'><b>Active Medications:</b> " + str(med_cnt) + "</p>"
        "<p style='margin-top:8px;'><b>Pending Reminders:</b> " + str(rem_cnt) + "</p>"
        "</div></div>"

        "<h3 style='color:var(--accent);margin-bottom:14px;'>Quick Access</h3>"
        "<div style='display:grid;grid-template-columns:repeat(4,1fr);gap:14px;'>"
        + feat_html +
        "</div>"
    )
    return base_html("Dashboard", content, u, dark)


# ================================
# PREDICT
# ================================
@app.route("/predict", methods=["GET", "POST"])
def predict():
    if "user" not in session:
        return redirect("/")
    u    = session["user"]
    dark = get_dark(u)
    result = result_class = prediction_id = None

    if request.method == "POST":
        ensure_startup()
        if not MODEL:
            return "Server is still warming up or model failed to load. Please try again in a moment.", 503
        
        import numpy as np
        vals = []
        for c in COL_NAMES:
            v = request.form.get(c)
            vals.append(float(v) if v else float(X[c].median()))
        pred  = int(MODEL.predict(np.array(vals).reshape(1, -1))[0])
        risk  = "HIGH RISK" if pred == 1 else "LOW RISK"
        result       = risk
        result_class = "high" if pred == 1 else "low"
        con  = get_db()
        ts   = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur  = con.cursor()
        cur.execute(
            "INSERT INTO predictions"
            "(username,timestamp,prediction,risk_level,age,sex,cp,trestbps,chol,"
            "fbs,restecg,thalach,exang,oldpeak,slope,ca,thal) VALUES"
            "(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (u, ts, pred, risk, *vals))
        con.commit()
        prediction_id = cur.lastrowid
        con.close()

    def mk_field(name, label, ftype, ph):
        if name == "sex":
            return ("<div><label class='lbl'>" + label + "</label>"
                    "<select name='" + name + "' required>"
                    "<option value=''>Select</option>"
                    "<option value='1'>Male</option>"
                    "<option value='0'>Female</option>"
                    "</select></div>")

        step = ' step="0.1"' if name == "oldpeak" else ""
        return ("<div><label class='lbl'>" + label + "</label>"
                "<input name='" + name + "' type='" + ftype + "' placeholder='" + ph + "'" + step + " required></div>")

    fields_def = [
        ("age","Age","number","e.g. 45"),
        ("sex","Gender","select",""),
        ("cp","Chest Pain Type (0-3)","number","0-3"),
        ("trestbps","Resting BP","number","e.g. 120"),
        ("chol","Cholesterol mg/dl","number","e.g. 200"),
        ("fbs","Fasting Blood Sugar >120","number","1=Yes, 0=No"),
        ("restecg","Resting ECG (0-2)","number","0-2"),
        ("thalach","Max Heart Rate","number","e.g. 150"),
        ("exang","Exercise Angina","number","1=Yes, 0=No"),
        ("oldpeak","ST Depression","number","e.g. 1.5"),
        ("slope","Slope (0-2)","number","0-2"),
        ("ca","Major Vessels (0-4)","number","0-4"),
        ("thal","Thalassemia (0-3)","number","0-3"),
    ]
    fields_html = "".join(mk_field(*f) for f in fields_def)

    res_block = ""
    if result:
        clr = "background:linear-gradient(135deg,#fab1a0,#d63031);color:#fff;" if result_class == "high" \
              else "background:linear-gradient(135deg,#55efc4,#00b894);color:#fff;"
        res_block = (
            "<div style='margin-top:22px;padding:22px;border-radius:14px;text-align:center;"
            "font-size:22px;font-weight:bold;" + clr + "'>" + result + "</div>"
            "<div style='text-align:center;margin-top:12px;'>"
            "<a href='/download_pdf/" + str(prediction_id) + "' "
            "style='padding:10px 26px;background:#667eea;color:#fff;text-decoration:none;"
            "border-radius:8px;font-weight:bold;'>Download PDF Report</a>"
            "</div>"
        )

    content = (
        "<div class='card'>"
        "<h2 style='color:var(--accent);margin-bottom:6px;'>Heart Risk Prediction</h2>"
        "<p style='color:var(--sub);margin-bottom:18px;'>Enter your health metrics below</p>"
        "<form method='post'>"
        "<div class='g3'>" + fields_html + "</div>"
        "<button type='submit' class='btn' style='width:100%;margin-top:16px;'>Predict Risk</button>"
        "</form>"
        + res_block +
        "</div>"
    )
    return base_html("Predict", content, u, dark)

# ================================
# PDF DOWNLOAD
# ================================
@app.route("/download_pdf/<int:pid>")
def download_pdf(pid):
    if "user" not in session:
        return redirect("/")
    u   = session["user"]
    con = get_db()
    row = con.execute("SELECT * FROM predictions WHERE id=? AND username=?", (pid, u)).fetchone()
    con.close()
    if not row:
        return "Prediction not found", 404
    pd_data = dict(row)
    buf = generate_pdf(u, pd_data)
    ts  = str(pd_data["timestamp"]).replace(" ", "_").replace(":", "-")
    return send_file(buf, as_attachment=True,
                     download_name="VitalArc_Report_" + u + "_" + ts + ".pdf",
                     mimetype="application/pdf")

# ================================
# HISTORY
# ================================
@app.route("/history")
def history():
    if "user" not in session:
        return redirect("/")
    u, dark = session["user"], get_dark(session["user"])
    con  = get_db()
    rows = con.execute(
        "SELECT id,timestamp,risk_level,age,sex,chol,trestbps,thalach "
        "FROM predictions WHERE username=? ORDER BY id DESC", (u,)).fetchall()
    con.close()

    table_html = ""
    if rows:
        table_html = "<table><thead><tr><th>Date</th><th>Risk</th><th>Age</th><th>Gender</th><th>Chol</th><th>BP</th><th>Max HR</th><th>PDF</th></tr></thead><tbody>"
        for r in rows:
            bc  = "bl" if "LOW" in str(r["risk_level"]) else "bh"
            gen = "Male" if r["sex"] == 1 else "Female"
            table_html += (
                "<tr>"
                "<td>" + str(r["timestamp"]) + "</td>"
                "<td><span class='badge " + bc + "'>" + str(r["risk_level"]) + "</span></td>"
                "<td>" + str(int(r["age"])) + "</td>"
                "<td>" + gen + "</td>"
                "<td>" + str(int(r["chol"])) + "</td>"
                "<td>" + str(int(r["trestbps"])) + "</td>"
                "<td>" + str(int(r["thalach"])) + "</td>"
                "<td><a href='/download_pdf/" + str(r["id"]) + "' style='color:var(--accent);font-weight:bold;text-decoration:none;'>PDF</a></td>"
                "</tr>"
            )
        table_html += "</tbody></table>"
    else:
        table_html = "<p style='color:var(--sub);padding:20px;'>No predictions yet.</p>"

    content = (
        "<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;'>"
        "<h2 style='color:var(--accent);'>Prediction History</h2>"
        "<a href='/export_csv' class='btn btn-sm btn-outline' style='text-decoration:none;'>Export CSV</a>"
        "</div>"
        "<div class='card' style='overflow-x:auto;'>" + table_html + "</div>"
    )
    return base_html("History", content, u, dark)

# ================================
# CSV EXPORT
# ================================
@app.route("/export_csv")
def export_csv():
    if "user" not in session:
        return redirect("/")
    u   = session["user"]
    con = get_db()
    rows = con.execute("SELECT * FROM predictions WHERE username=? ORDER BY id DESC", (u,)).fetchall()
    con.close()
    out = io.StringIO()
    w   = csv.writer(out)
    w.writerow(["id","username","timestamp","prediction","risk_level",
                "age","sex","cp","trestbps","chol","fbs","restecg",
                "thalach","exang","oldpeak","slope","ca","thal"])
    for r in rows:
        w.writerow(list(r))
    out.seek(0)
    return send_file(io.BytesIO(out.read().encode()),
                     as_attachment=True,
                     download_name="vitalarc_history_" + u + ".csv",
                     mimetype="text/csv")


# ================================
# BMI CALCULATOR
# ================================
@app.route("/bmi", methods=["GET", "POST"])
def bmi_calc():
    if "user" not in session:
        return redirect("/")
    u, dark = session["user"], get_dark(session["user"])
    bmi_val = bmi_cat = weight = height = None
    advice  = ""

    if request.method == "POST":
        weight  = float(request.form["weight"])
        height  = float(request.form["height"])
        bmi_val, bmi_cat = calc_bmi(weight, height)
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        con = get_db()
        con.execute("INSERT INTO bmi_records(username,timestamp,weight_kg,height_cm,bmi,category) VALUES(?,?,?,?,?,?)",
                    (u, ts, weight, height, bmi_val, bmi_cat))
        con.commit()
        con.close()
        advice = {"Underweight": "You may need to gain weight. Consult a nutritionist.",
                  "Normal":      "Great! Maintain a balanced diet and regular exercise.",
                  "Overweight":  "Consider increasing physical activity and dietary changes.",
                  "Obese":       "High health risk. Please consult a healthcare professional."
                 }.get(bmi_cat, "")

    con  = get_db()
    hist = con.execute("SELECT timestamp,weight_kg,height_cm,bmi,category FROM bmi_records "
                       "WHERE username=? ORDER BY id DESC LIMIT 10", (u,)).fetchall()
    con.close()

    bmi_block = ""
    if bmi_val:
        clr = "#00b894" if bmi_cat == "Normal" else "#fdcb6e" if bmi_cat == "Overweight" else "#d63031"
        bmi_block = (
            "<div style='margin-top:18px;padding:18px;border-radius:12px;"
            "background:" + clr + "22;border:2px solid " + clr + ";text-align:center;'>"
            "<div style='font-size:44px;font-weight:bold;color:" + clr + ";'>" + str(bmi_val) + "</div>"
            "<div style='font-size:18px;color:" + clr + ";font-weight:bold;'>" + bmi_cat + "</div>"
            "<p style='margin-top:8px;'>" + advice + "</p>"
            "</div>"
        )

    hist_table = ""
    if hist:
        hist_table = "<table><thead><tr><th>Date</th><th>Weight</th><th>Height</th><th>BMI</th><th>Category</th></tr></thead><tbody>"
        for h in hist:
            clr2 = "#00b894" if h["category"]=="Normal" else "#fdcb6e" if h["category"]=="Overweight" else "#d63031"
            hist_table += (
                "<tr><td>" + str(h["timestamp"]) + "</td>"
                "<td>" + str(h["weight_kg"]) + " kg</td>"
                "<td>" + str(h["height_cm"]) + " cm</td>"
                "<td style='color:" + clr2 + ";font-weight:bold;'>" + str(h["bmi"]) + "</td>"
                "<td>" + str(h["category"]) + "</td></tr>"
            )
        hist_table += "</tbody></table>"
    else:
        hist_table = "<p style='color:var(--sub);'>No records yet.</p>"

    scale = (
        "<div style='margin-top:16px;'>"
        "<p style='color:var(--sub);font-size:13px;margin-bottom:6px;'>BMI Scale:</p>"
        "<div style='display:flex;border-radius:8px;overflow:hidden;height:24px;font-size:11px;'>"
        "<div style='flex:1;background:#636e72;color:#fff;display:flex;align-items:center;justify-content:center;'>&lt;18.5 Underweight</div>"
        "<div style='flex:1.3;background:#00b894;color:#fff;display:flex;align-items:center;justify-content:center;'>18.5-24.9 Normal</div>"
        "<div style='flex:1;background:#fdcb6e;color:#333;display:flex;align-items:center;justify-content:center;'>25-29.9 Overweight</div>"
        "<div style='flex:1;background:#d63031;color:#fff;display:flex;align-items:center;justify-content:center;'>30+ Obese</div>"
        "</div></div>"
    )

    content = (
        "<div class='g2'>"
        "<div class='card'>"
        "<h3 style='color:var(--accent);margin-bottom:14px;'>BMI Calculator</h3>"
        "<form method='post'>"
        "<label class='lbl'>Weight (kg)</label>"
        "<input name='weight' type='number' step='0.1' placeholder='e.g. 70' required>"
        "<label class='lbl' style='margin-top:8px;'>Height (cm)</label>"
        "<input name='height' type='number' step='0.1' placeholder='e.g. 170' required>"
        "<button type='submit' class='btn' style='width:100%;margin-top:12px;'>Calculate BMI</button>"
        "</form>"
        + bmi_block + scale +
        "</div>"
        "<div class='card'>"
        "<h3 style='color:var(--accent);margin-bottom:14px;'>BMI History</h3>"
        + hist_table +
        "</div></div>"
    )
    return base_html("BMI Calculator", content, u, dark)

# ================================
# BP ZONE INDICATOR
# ================================
@app.route("/bp_zone")
def bp_zone():
    if "user" not in session:
        return redirect("/")
    u, dark = session["user"], get_dark(session["user"])
    con  = get_db()
    rows = con.execute("SELECT timestamp,trestbps FROM predictions WHERE username=? ORDER BY id DESC LIMIT 10", (u,)).fetchall()
    con.close()

    def bp_label(v):
        v = float(v)
        if v < 120: return "Normal BP",       "#00b894"
        if v < 130: return "Elevated BP",      "#fdcb6e"
        if v < 140: return "High BP Stage 1",  "#e17055"
        return          "High BP Stage 2",     "#d63031"

    zones_html = (
        "<div class='g4' style='margin-bottom:18px;'>"
        "<div style='padding:13px;border-radius:10px;background:#00b89422;border:2px solid #00b894;text-align:center;'>"
        "<div style='color:#00b894;font-weight:bold;'>Normal</div><div style='font-size:12px;'>&lt;120 mm Hg</div></div>"
        "<div style='padding:13px;border-radius:10px;background:#fdcb6e22;border:2px solid #fdcb6e;text-align:center;'>"
        "<div style='color:#e09700;font-weight:bold;'>Elevated</div><div style='font-size:12px;'>120-129</div></div>"
        "<div style='padding:13px;border-radius:10px;background:#e1705522;border:2px solid #e17055;text-align:center;'>"
        "<div style='color:#e17055;font-weight:bold;'>Stage 1</div><div style='font-size:12px;'>130-139</div></div>"
        "<div style='padding:13px;border-radius:10px;background:#d6303122;border:2px solid #d63031;text-align:center;'>"
        "<div style='color:#d63031;font-weight:bold;'>Stage 2</div><div style='font-size:12px;'>140+</div></div>"
        "</div>"
    )

    bp_table = ""
    if rows:
        bp_table = "<table><thead><tr><th>Date</th><th>Resting BP</th><th>Zone</th></tr></thead><tbody>"
        for r in rows:
            lbl, clr2 = bp_label(r["trestbps"])
            bp_table += (
                "<tr><td>" + str(r["timestamp"]) + "</td>"
                "<td>" + str(int(r["trestbps"])) + " mm Hg</td>"
                "<td style='color:" + clr2 + ";font-weight:bold;'>" + lbl + "</td></tr>"
            )
        bp_table += "</tbody></table>"
    else:
        bp_table = "<p style='color:var(--sub);'>No BP data yet. Run a prediction first.</p>"

    content = (
        "<div class='card'>"
        "<h3 style='color:var(--accent);margin-bottom:14px;'>Blood Pressure Zone Indicator</h3>"
        + zones_html + bp_table +
        "</div>"
    )
    return base_html("BP Zones", content, u, dark)

# ================================
# HEART RATE ZONES
# ================================
@app.route("/hr_zones")
def hr_zones():
    if "user" not in session:
        return redirect("/")
    u, dark = session["user"], get_dark(session["user"])
    con = get_db()
    row = con.execute("SELECT age FROM predictions WHERE username=? ORDER BY id DESC LIMIT 1", (u,)).fetchone()
    con.close()
    age = int(row["age"]) if row else 30
    mhr = 220 - age

    zones = [
        ("Zone 1 Warm Up",   50, 60,  "#74b9ff"),
        ("Zone 2 Fat Burn",  60, 70,  "#00cec9"),
        ("Zone 3 Cardio",    70, 80,  "#fdcb6e"),
        ("Zone 4 Hard",      80, 90,  "#e17055"),
        ("Zone 5 Maximum",   90, 100, "#d63031"),
    ]

    rows_html = ""
    for name, lo, hi, clr2 in zones:
        lo_b = int(mhr * lo / 100)
        hi_b = int(mhr * hi / 100)
        rows_html += (
            "<tr>"
            "<td style='font-weight:bold;color:" + clr2 + ";'>" + name + "</td>"
            "<td>" + str(lo) + "%-" + str(hi) + "%</td>"
            "<td>" + str(lo_b) + "-" + str(hi_b) + " bpm</td>"
            "<td><div style='height:13px;border-radius:7px;background:" + clr2 + ";opacity:.8;'></div></td>"
            "</tr>"
        )

    content = (
        "<div class='card'>"
        "<h3 style='color:var(--accent);margin-bottom:6px;'>Heart Rate Zone Calculator</h3>"
        "<p style='color:var(--sub);margin-bottom:14px;'>Based on your age: <b>" + str(age) + " years</b> - Max HR: <b>" + str(mhr) + " bpm</b></p>"
        "<table><thead><tr><th>Zone</th><th>% Max HR</th><th>BPM Range</th><th>Intensity</th></tr></thead>"
        "<tbody>" + rows_html + "</tbody></table>"
        "<div class='ai' style='margin-top:14px;'>Tip: For heart health, aim for Zone 2-3 (60-80% max HR) for 150 min/week.</div>"
        "</div>"
    )
    return base_html("HR Zones", content, u, dark)


# ================================
# WATER INTAKE
# ================================
@app.route("/water", methods=["GET", "POST"])
def water():
    if "user" not in session:
        return redirect("/")
    u, dark = session["user"], get_dark(session["user"])
    today   = datetime.now().strftime("%Y-%m-%d")
    con     = get_db()

    if request.method == "POST":
        action = request.form.get("action")
        row2   = con.execute("SELECT id,glasses FROM water_intake WHERE username=? AND log_date=?", (u, today)).fetchone()
        if action == "add":
            if row2:
                con.execute("UPDATE water_intake SET glasses=? WHERE id=?", (min(row2["glasses"] + 1, 20), row2["id"]))
            else:
                con.execute("INSERT INTO water_intake(username,log_date,glasses) VALUES(?,?,1)", (u, today))
        elif action == "remove":
            if row2 and row2["glasses"] > 0:
                con.execute("UPDATE water_intake SET glasses=? WHERE id=?", (row2["glasses"] - 1, row2["id"]))
        con.commit()

    wr   = con.execute("SELECT glasses FROM water_intake WHERE username=? AND log_date=?", (u, today)).fetchone()
    gl   = wr["glasses"] if wr else 0
    hist = con.execute("SELECT log_date,glasses FROM water_intake WHERE username=? ORDER BY id DESC LIMIT 7", (u,)).fetchall()
    con.close()

    pct  = int(min(gl / 8 * 100, 100))
    clr2 = "#00b894" if gl >= 8 else "#fdcb6e" if gl >= 4 else "#636e72"
    cups = "".join(
        "<span style='font-size:26px;opacity:" + ("1" if i < gl else "0.2") + ";'>💧</span>"
        for i in range(8)
    )
    goal_msg = "<div class='as' style='margin-top:14px;'>Goal reached! Great hydration!</div>" if gl >= 8 else ""

    hist_table = ""
    if hist:
        hist_table = "<table><thead><tr><th>Date</th><th>Intake</th><th>Progress</th></tr></thead><tbody>"
        for h in hist:
            p2 = int(min(h["glasses"] / 8 * 100, 100))
            hist_table += (
                "<tr><td>" + str(h["log_date"]) + "</td>"
                "<td>" + str(h["glasses"]) + "/8 glasses</td>"
                "<td><div class='bar'><div class='bar-fill' style='width:" + str(p2) + "%;background:#00cec9;'></div></div></td></tr>"
            )
        hist_table += "</tbody></table>"
    else:
        hist_table = "<p style='color:var(--sub);'>No history yet.</p>"

    content = (
        "<div class='g2'>"
        "<div class='card' style='text-align:center;'>"
        "<h3 style='color:var(--accent);margin-bottom:6px;'>Water Intake Tracker</h3>"
        "<p style='color:var(--sub);margin-bottom:14px;'>Today - " + today + "</p>"
        "<div style='font-size:56px;font-weight:bold;color:" + clr2 + ";'>" + str(gl) + "</div>"
        "<div style='color:var(--sub);'>/ 8 glasses</div>"
        "<div style='margin:14px 0;'>" + cups + "</div>"
        "<div class='bar' style='margin-bottom:14px;'>"
        "<div class='bar-fill' style='width:" + str(pct) + "%;background:#00cec9;'></div></div>"
        "<div style='display:flex;gap:12px;justify-content:center;'>"
        "<form method='post' style='display:inline;'>"
        "<input type='hidden' name='action' value='add'>"
        "<button class='btn btn-green'>+ Add Glass</button></form>"
        "<form method='post' style='display:inline;'>"
        "<input type='hidden' name='action' value='remove'>"
        "<button class='btn btn-danger'>- Remove</button></form>"
        "</div>"
        + goal_msg +
        "</div>"
        "<div class='card'>"
        "<h3 style='color:var(--accent);margin-bottom:14px;'>Last 7 Days</h3>"
        + hist_table +
        "</div></div>"
    )
    return base_html("Water Tracker", content, u, dark)

# ================================
# MEDICATIONS
# ================================
@app.route("/medications", methods=["GET", "POST"])
def medications():
    if "user" not in session:
        return redirect("/")
    u, dark = session["user"], get_dark(session["user"])
    con = get_db()
    msg = ""

    if request.method == "POST":
        action = request.form.get("action")
        if action == "add":
            con.execute("INSERT INTO medications(username,med_name,dosage,frequency) VALUES(?,?,?,?)",
                        (u, request.form["med_name"], request.form["dosage"], request.form["frequency"]))
            con.commit()
            msg = "Medication added successfully!"
        elif action == "toggle":
            mid = request.form["mid"]
            row2 = con.execute("SELECT active FROM medications WHERE id=?", (mid,)).fetchone()
            if row2:
                con.execute("UPDATE medications SET active=? WHERE id=?", (0 if row2["active"] else 1, mid))
                con.commit()
        elif action == "delete":
            con.execute("DELETE FROM medications WHERE id=? AND username=?", (request.form["mid"], u))
            con.commit()

    meds = con.execute("SELECT id,med_name,dosage,frequency,active FROM medications WHERE username=? ORDER BY id DESC", (u,)).fetchall()
    con.close()

    med_rows = ""
    for m in meds:
        stc = "#00b894" if m["active"] else "#d63031"
        st  = "Active" if m["active"] else "Inactive"
        med_rows += (
            "<tr>"
            "<td>" + str(m["med_name"]) + "</td>"
            "<td>" + str(m["dosage"]) + "</td>"
            "<td>" + str(m["frequency"]) + "</td>"
            "<td style='color:" + stc + ";font-weight:bold;'>" + st + "</td>"
            "<td style='display:flex;gap:6px;'>"
            "<form method='post' style='display:inline;'>"
            "<input type='hidden' name='action' value='toggle'>"
            "<input type='hidden' name='mid' value='" + str(m["id"]) + "'>"
            "<button class='btn btn-sm btn-outline'>Toggle</button></form>"
            "<form method='post' style='display:inline;'>"
            "<input type='hidden' name='action' value='delete'>"
            "<input type='hidden' name='mid' value='" + str(m["id"]) + "'>"
            "<button class='btn btn-sm btn-danger'>Delete</button></form>"
            "</td></tr>"
        )

    med_table = ""
    if meds:
        med_table = "<div style='overflow-x:auto;'><table><thead><tr><th>Name</th><th>Dosage</th><th>Frequency</th><th>Status</th><th>Actions</th></tr></thead><tbody>" + med_rows + "</tbody></table></div>"
    else:
        med_table = "<p style='color:var(--sub);'>No medications added yet.</p>"

    content = (
        ("<div class='as'>" + msg + "</div>" if msg else "") +
        "<div class='g2'>"
        "<div class='card'>"
        "<h3 style='color:var(--accent);margin-bottom:14px;'>Add Medication</h3>"
        "<form method='post'>"
        "<input type='hidden' name='action' value='add'>"
        "<label class='lbl'>Medication Name</label>"
        "<input name='med_name' placeholder='e.g. Aspirin' required>"
        "<label class='lbl'>Dosage</label>"
        "<input name='dosage' placeholder='e.g. 100mg'>"
        "<label class='lbl'>Frequency</label>"
        "<select name='frequency'>"
        "<option>Once daily</option><option>Twice daily</option>"
        "<option>Three times daily</option><option>As needed</option><option>Weekly</option>"
        "</select>"
        "<button type='submit' class='btn' style='width:100%;margin-top:12px;'>Add Medication</button>"
        "</form></div>"
        "<div class='card'>"
        "<h3 style='color:var(--accent);margin-bottom:14px;'>My Medications</h3>"
        + med_table +
        "</div></div>"
    )
    return base_html("Medications", content, u, dark)


# ================================
# HEALTH GOALS
# ================================
@app.route("/goals", methods=["GET", "POST"])
def goals():
    if "user" not in session:
        return redirect("/")
    u, dark = session["user"], get_dark(session["user"])
    con = get_db()
    msg = ""

    if request.method == "POST":
        action = request.form.get("action")
        if action == "add":
            con.execute("INSERT INTO health_goals(username,goal_type,target,current,unit) VALUES(?,?,?,?,?)",
                        (u, request.form["goal_type"],
                         float(request.form["target"]),
                         float(request.form.get("current", 0) or 0),
                         request.form["unit"]))
            con.commit()
            msg = "Goal added!"
        elif action == "update":
            con.execute("UPDATE health_goals SET current=? WHERE id=? AND username=?",
                        (float(request.form["current"]), request.form["gid"], u))
            con.commit()
        elif action == "delete":
            con.execute("DELETE FROM health_goals WHERE id=? AND username=?", (request.form["gid"], u))
            con.commit()

    goals_list = con.execute("SELECT id,goal_type,target,current,unit FROM health_goals WHERE username=?", (u,)).fetchall()
    con.close()

    goal_cards = ""
    for g in goals_list:
        pct  = int(min(g["current"] / g["target"] * 100, 100)) if g["target"] > 0 else 0
        clr2 = "#00b894" if pct >= 100 else "#667eea" if pct >= 50 else "#fdcb6e"
        done = "Achieved!" if pct >= 100 else str(pct) + "% complete"
        goal_cards += (
            "<div class='card' style='margin-bottom:0;'>"
            "<div style='display:flex;justify-content:space-between;'>"
            "<div><h4 style='color:var(--accent);'>" + str(g["goal_type"]) + "</h4>"
            "<p style='color:var(--sub);font-size:13px;'>Target: " + str(g["target"]) + " " + str(g["unit"]) + "</p></div>"
            "<span style='color:" + clr2 + ";font-weight:bold;font-size:13px;'>" + done + "</span>"
            "</div>"
            "<div style='margin:8px 0;'>"
            "<div style='display:flex;justify-content:space-between;font-size:13px;margin-bottom:4px;'>"
            "<span>Current: " + str(g["current"]) + " " + str(g["unit"]) + "</span>"
            "<span>" + str(pct) + "%</span></div>"
            "<div class='bar'><div class='bar-fill' style='width:" + str(pct) + "%;background:" + clr2 + ";'></div></div>"
            "</div>"
            "<div style='display:flex;gap:8px;'>"
            "<form method='post' style='display:flex;gap:6px;align-items:center;'>"
            "<input type='hidden' name='action' value='update'>"
            "<input type='hidden' name='gid' value='" + str(g["id"]) + "'>"
            "<input name='current' type='number' step='0.1' placeholder='Update value' style='width:130px;padding:7px;margin:0;'>"
            "<button class='btn btn-sm btn-green'>Update</button></form>"
            "<form method='post' style='display:inline;'>"
            "<input type='hidden' name='action' value='delete'>"
            "<input type='hidden' name='gid' value='" + str(g["id"]) + "'>"
            "<button class='btn btn-sm btn-danger'>Delete</button></form>"
            "</div></div>"
        )

    content = (
        ("<div class='as'>" + msg + "</div>" if msg else "") +
        "<div class='g2'>"
        "<div class='card'>"
        "<h3 style='color:var(--accent);margin-bottom:14px;'>Add New Goal</h3>"
        "<form method='post'>"
        "<input type='hidden' name='action' value='add'>"
        "<label class='lbl'>Goal Type</label>"
        "<select name='goal_type'>"
        "<option>Lose Weight (kg)</option><option>Reduce Cholesterol</option>"
        "<option>Lower Blood Pressure</option><option>Increase Max Heart Rate</option>"
        "<option>Daily Steps</option><option>Exercise Minutes/Week</option>"
        "<option>Water Glasses/Day</option><option>Custom Goal</option>"
        "</select>"
        "<label class='lbl'>Target Value</label>"
        "<input name='target' type='number' step='0.1' placeholder='e.g. 70' required>"
        "<label class='lbl'>Current Value</label>"
        "<input name='current' type='number' step='0.1' placeholder='e.g. 80'>"
        "<label class='lbl'>Unit</label>"
        "<input name='unit' placeholder='e.g. kg, bpm, steps'>"
        "<button type='submit' class='btn' style='width:100%;margin-top:12px;'>Add Goal</button>"
        "</form></div>"
        "<div style='display:flex;flex-direction:column;gap:14px;'>"
        + (goal_cards if goals_list else "<div class='card'>No goals yet. Add your first goal!</div>") +
        "</div></div>"
    )
    return base_html("Health Goals", content, u, dark)

# ================================
# REMINDERS
# ================================
@app.route("/reminders", methods=["GET", "POST"])
def reminders():
    if "user" not in session:
        return redirect("/")
    u, dark = session["user"], get_dark(session["user"])
    con = get_db()
    msg = ""
    user_email = ""

    user_row = con.execute("SELECT email FROM users WHERE username=?", (u,)).fetchone()
    if user_row:
        user_email = user_row["email"] or ""

    if request.method == "POST":
        action = request.form.get("action")
        if action == "add":
            rdate = request.form["remind_date"]
            rtime = request.form["remind_time"]
            rmsg  = request.form["message"]
            con.execute("INSERT INTO reminders(username,remind_date,remind_time,message) VALUES(?,?,?,?)",
                        (u, rdate, rtime, rmsg))
            con.commit()
            msg = "Reminder set for " + rdate + " at " + rtime + ". Email will go to: " + (user_email or "no email set")
        elif action == "delete":
            con.execute("DELETE FROM reminders WHERE id=? AND username=?", (request.form["rid"], u))
            con.commit()

    upcoming = con.execute("SELECT id,remind_date,remind_time,message,email_sent FROM reminders "
                           "WHERE username=? ORDER BY remind_date,remind_time", (u,)).fetchall()
    con.close()

    rem_rows = ""
    for r in upcoming:
        sc2 = "#00b894" if r["email_sent"] else "#fdcb6e"
        st  = "Sent" if r["email_sent"] else "Pending"
        rem_rows += (
            "<tr><td>" + str(r["remind_date"]) + "</td>"
            "<td>" + str(r["remind_time"]) + "</td>"
            "<td>" + str(r["message"]) + "</td>"
            "<td style='color:" + sc2 + ";font-weight:bold;'>" + st + "</td>"
            "<td><form method='post' style='display:inline;'>"
            "<input type='hidden' name='action' value='delete'>"
            "<input type='hidden' name='rid' value='" + str(r["id"]) + "'>"
            "<button class='btn btn-sm btn-danger'>Delete</button></form></td></tr>"
        )

    rem_table = ""
    if upcoming:
        rem_table = "<div style='overflow-x:auto;'><table><thead><tr><th>Date</th><th>Time</th><th>Message</th><th>Status</th><th>Action</th></tr></thead><tbody>" + rem_rows + "</tbody></table></div>"
    else:
        rem_table = "<p style='color:var(--sub);'>No reminders set.</p>"

    no_email_warn = "<div class='ai'>No email set on your profile. <a href='/profile'>Update Profile</a></div>" if not user_email else ""

    content = (
        ("<div class='as'>" + msg + "</div>" if msg else "") +
        no_email_warn +
        "<div class='g2'>"
        "<div class='card'>"
        "<h3 style='color:var(--accent);margin-bottom:6px;'>Set a Reminder</h3>"
        "<p style='color:var(--sub);font-size:13px;margin-bottom:14px;'>Receive an email reminder for your checkup</p>"
        "<form method='post'>"
        "<input type='hidden' name='action' value='add'>"
        "<label class='lbl'>Date</label>"
        "<input name='remind_date' type='date' required>"
        "<label class='lbl'>Time</label>"
        "<input name='remind_time' type='time' required>"
        "<label class='lbl'>Reminder Message</label>"
        "<textarea name='message' rows='3' style='width:100%;padding:11px;border:2px solid var(--border);"
        "border-radius:9px;font-size:14px;background:var(--inp);color:var(--text);resize:vertical;'"
        " placeholder='e.g. Time for your weekly heart health checkup!'></textarea>"
        "<button type='submit' class='btn' style='width:100%;margin-top:10px;'>Set Reminder</button>"
        "</form>"
        "</div>"
        "<div class='card'>"
        "<h3 style='color:var(--accent);margin-bottom:14px;'>My Reminders</h3>"
        + rem_table +
        "</div></div>"
    )
    return base_html("Reminders", content, u, dark)


# ================================
# STRESS CHECKER
# ================================
@app.route("/stress", methods=["GET", "POST"])
def stress():
    if "user" not in session:
        return redirect("/")
    u, dark = session["user"], get_dark(session["user"])
    result_html = ""

    questions = [
        ("q1",  "How often have you felt unable to control important things in your life?"),
        ("q2",  "How often have you felt nervous and stressed?"),
        ("q3",  "How often have you been unable to cope with everything you had to do?"),
        ("q4",  "How often have you felt difficulties were piling up so high you could not overcome them?"),
        ("q5",  "How often have you felt confident about your ability to handle personal problems?"),
        ("q6",  "How often have you felt that things were going your way?"),
        ("q7",  "How often have you been able to control irritations in your life?"),
        ("q8",  "How often have you felt on top of things?"),
        ("q9",  "How often have you been angered because of things that happened that were outside your control?"),
        ("q10", "How often have you felt overwhelmed by responsibilities at work or home?"),
        ("q11", "How often have you had trouble sleeping due to worrying thoughts?"),
        ("q12", "How often have you felt a sense of dread or unease without a clear reason?"),
        ("q13", "How often have you felt emotionally drained or burned out?"),
        ("q14", "How often have you found it hard to concentrate because of stress?"),
        ("q15", "How often have you felt isolated or disconnected from people around you?"),
    ]

    if request.method == "POST":
        score = sum(int(request.form.get(q[0], 0)) for q in questions)
        max_score = len(questions) * 4

        if score <= 15:
            level = "Low Stress"; clr2 = "#00b894"; icon = "😌"
            tips = ["Maintain your current healthy routine","Practice daily gratitude journaling",
                    "Stay socially connected with loved ones","Keep up regular physical activity",
                    "Spend time in nature or outdoors"]
        elif score <= 30:
            level = "Moderate Stress"; clr2 = "#fdcb6e"; icon = "😐"
            tips = ["Try 10-15 min of meditation or mindfulness daily","Exercise at least 3 times a week",
                    "Reduce caffeine and sugar intake","Talk openly with a trusted friend or family member",
                    "Set realistic daily goals and prioritise tasks","Take short breaks every 90 minutes during work",
                    "Limit news and social media scrolling"]
        elif score <= 45:
            level = "High Stress"; clr2 = "#e17055"; icon = "😟"
            tips = ["Consider speaking with a therapist or counsellor","Practice deep breathing exercises",
                    "Reduce your workload - delegate where possible","Aim for 7-8 hours of quality sleep each night",
                    "Write down your worries in a journal","Establish clear boundaries between work and personal time",
                    "Engage in a relaxing hobby or creative outlet","Try progressive muscle relaxation before bed"]
        else:
            level = "Severe Stress"; clr2 = "#d63031"; icon = "😰"
            tips = ["Seek professional mental health support as soon as possible",
                    "Reach out to a crisis helpline if you feel overwhelmed",
                    "Talk to your doctor about your stress symptoms","Immediately reduce non-essential commitments",
                    "Prioritise sleep, hydration, and regular meals","Practice grounding techniques (5-4-3-2-1 method)",
                    "Ask for help from family, friends, or colleagues",
                    "Avoid alcohol and substances as coping mechanisms"]

        tips_li = "".join(
            "<li style='padding:7px 0;display:flex;align-items:flex-start;gap:8px;'>"
            "<span style='color:" + clr2 + ";font-size:16px;'>✔</span><span>" + t + "</span></li>"
            for t in tips
        )
        percent = round((score / max_score) * 100)
        result_html = (
            "<div style='margin-top:22px;padding:22px;border-radius:14px;"
            "background:" + clr2 + "18;border:2px solid " + clr2 + ";text-align:center;'>"
            "<div style='font-size:40px;margin-bottom:6px;'>" + icon + "</div>"
            "<div style='font-size:28px;font-weight:bold;color:" + clr2 + ";'>" + level + "</div>"
            "<div style='color:var(--sub);margin-top:6px;font-size:15px;'>Score: <strong>" + str(score) + "</strong> / " + str(max_score) + "</div>"
            "<div style='margin-top:14px;background:var(--alt);border-radius:50px;height:12px;overflow:hidden;'>"
            "<div style='width:" + str(percent) + "%;height:100%;background:" + clr2 + ";border-radius:50px;'></div></div>"
            "<div style='color:var(--sub);font-size:13px;margin-top:6px;'>" + str(percent) + "% of maximum stress score</div>"
            "</div>"
            "<div class='card' style='margin-top:16px;'>"
            "<h4 style='color:var(--accent);margin-bottom:12px;font-size:17px;'>📋 Personalised Recommendations:</h4>"
            "<ul style='list-style:none;padding:0;margin:0;'>" + tips_li + "</ul>"
            "</div>"
            "<div style='margin-top:12px;padding:12px 16px;border-radius:10px;"
            "background:var(--alt);font-size:13px;color:var(--sub);text-align:center;'>"
            "⚠️ This tool is for informational purposes only and does not replace professional medical advice."
            "</div>"
        )

    q_html = ""
    opts = [(0, "Never"), (1, "Almost Never"), (2, "Sometimes"), (3, "Fairly Often"), (4, "Very Often")]
    for i, (name, txt) in enumerate(questions, 1):
        radios = "".join(
            "<label style='display:flex;align-items:center;gap:5px;cursor:pointer;"
            "padding:5px 10px;border-radius:7px;border:1px solid var(--border);"
            "background:var(--bg);font-size:13px;'>"
            "<input type='radio' name='" + name + "' value='" + str(v) + "' required> " + lbl + "</label>"
            for v, lbl in opts
        )
        q_html += (
            "<div style='margin-bottom:18px;padding:16px;background:var(--alt);border-radius:10px;"
            "border-left:4px solid var(--accent);'>"
            "<p style='margin-bottom:10px;font-weight:600;font-size:14px;color:var(--text);'>"
            "<span style='color:var(--accent);margin-right:6px;'>" + str(i) + ".</span>" + txt + "</p>"
            "<div style='display:flex;flex-wrap:wrap;gap:8px;'>" + radios + "</div>"
            "</div>"
        )

    content = (
        "<div class='card'>"
        "<h3 style='color:var(--accent);margin-bottom:6px;'>🧠 Stress Level Checker</h3>"
        "<p style='color:var(--sub);margin-bottom:20px;'>Answer all 15 questions honestly. "
        "Rated from <strong>0 (Never)</strong> to <strong>4 (Very Often)</strong>.</p>"
        "<form method='post'>" + q_html +
        "<button type='submit' class='btn' style='width:100%;padding:14px;font-size:16px;'>"
        "📊 Calculate My Stress Level</button>"
        "</form>"
        + result_html +
        "</div>"
    )
    return base_html("Stress Checker", content, u, dark)

# ================================================================
# DROP-IN REPLACEMENT: paste these two routes into vital_arc.py
# replacing the existing /upload_photo and /profile routes
# ================================================================

@app.route("/upload_photo", methods=["POST"])
def upload_photo():
    if "user" not in session:
        return redirect("/")
    u   = session["user"]
    img = request.files.get("photo")
    if img and img.filename:
        data = img.read()
        b64  = __import__("base64").b64encode(data).decode()
        mime = img.content_type or "image/jpeg"
        data_url = "data:" + mime + ";base64," + b64
        con = get_db()
        con.execute("UPDATE users SET photo=? WHERE username=?", (data_url, u))
        con.commit()
        con.close()
    return redirect("/profile")


@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "user" not in session:
        return redirect("/")
    u    = session["user"]
    dark = get_dark(u)
    con  = get_db()
    msg  = err = ""

    if request.method == "POST":
        action = request.form.get("action")
        if action == "update_info":
            email  = request.form.get("email", "")
            height = float(request.form.get("height_cm") or 0)
            weight = float(request.form.get("weight_kg") or 0)
            dob    = request.form.get("dob", "")
            phone  = request.form.get("phone", "")
            con.execute(
                "UPDATE users SET email=?,height_cm=?,weight_kg=?,dob=?,phone=? WHERE username=?",
                (email, height, weight, dob, phone, u))
            con.commit()
            msg = "profile_saved"
        elif action == "change_pass":
            cur_p = request.form.get("current_pass", "")
            new_p = request.form.get("new_pass", "")
            row2  = con.execute("SELECT password FROM users WHERE username=?", (u,)).fetchone()
            if row2 and check_password_hash(row2["password"], cur_p):
                con.execute("UPDATE users SET password=? WHERE username=?",
                            (generate_password_hash(new_p), u))
                con.commit()
                msg = "pass_saved"
            else:
                err = "wrong_pass"
        elif action == "toggle_dark":
            row2 = con.execute("SELECT dark_mode FROM users WHERE username=?", (u,)).fetchone()
            new_val = 0 if (row2 and row2["dark_mode"] == 1) else 1
            con.execute("UPDATE users SET dark_mode=? WHERE username=?", (new_val, u))
            con.commit()
            dark = new_val

    row = con.execute(
        "SELECT email,height_cm,weight_kg,dob,phone,photo,dark_mode FROM users WHERE username=?",
        (u,)).fetchone()
    total_p = con.execute("SELECT COUNT(*) FROM predictions WHERE username=?", (u,)).fetchone()[0]
    low_p   = con.execute("SELECT COUNT(*) FROM predictions WHERE username=? AND prediction=0", (u,)).fetchone()[0]
    high_p  = con.execute("SELECT COUNT(*) FROM predictions WHERE username=? AND prediction=1", (u,)).fetchone()[0]
    lr2     = con.execute(
        "SELECT risk_level,timestamp FROM predictions WHERE username=? ORDER BY id DESC LIMIT 1", (u,)).fetchone()
    con.close()

    email  = str(row["email"])   if row and row["email"]  else ""
    h      = float(row["height_cm"]) if row and row["height_cm"] else 0
    w      = float(row["weight_kg"]) if row and row["weight_kg"] else 0
    dob    = str(row["dob"])     if row and row["dob"]    else ""
    phone  = str(row["phone"])   if row and row["phone"]  else ""
    photo  = str(row["photo"])   if row and row["photo"]  else ""
    dm_on  = row["dark_mode"]    if row else 0

    bmi_val = bmi_cat = bmi_clr = ""
    if h and w and h > 0 and w > 0:
        bmi_val, bmi_cat = calc_bmi(w, h)
        bmi_clr = ("#00e5a0" if bmi_cat == "Normal"
                   else "#ffd166" if bmi_cat == "Overweight"
                   else "#ff5f7e")

    age_str = age_num = ""
    if dob:
        try:
            bd = datetime.strptime(dob, "%Y-%m-%d")
            age_num = (datetime.now() - bd).days // 365
            age_str = str(age_num)
        except:
            pass

    latest_risk = lr2["risk_level"] if lr2 else "—"
    latest_date = str(lr2["timestamp"])[:10] if lr2 else "—"
    risk_clr    = "#00e5a0" if lr2 and "LOW" in str(lr2["risk_level"]) else "#ff5f7e"

    health_score = 0
    if lr2:
        health_score = calc_health_score({
            "prediction": 0 if "LOW" in str(lr2["risk_level"]) else 1,
            "age": age_num or 40, "chol": 180, "trestbps": 120,
            "thalach": 150, "fbs": 0, "exang": 0
        })

    if photo:
        avatar_img = f"<img src='{photo}' id='avatarImg' style='width:100%;height:100%;object-fit:cover;border-radius:50%;'>"
    else:
        initials = u[0].upper()
        avatar_img = f"<div style='width:100%;height:100%;border-radius:50%;background:linear-gradient(135deg,#667eea,#a855f7);display:flex;align-items:center;justify-content:center;font-size:52px;font-weight:900;color:#fff;letter-spacing:-2px;'>{initials}</div>"

    msg_js = ""
    if msg == "profile_saved":
        msg_js = "showToast('✓ Profile saved successfully','#00e5a0');"
    elif msg == "pass_saved":
        msg_js = "showToast('✓ Password updated','#00e5a0'); closePassModal();"
    elif err == "wrong_pass":
        msg_js = "showToast('✗ Current password is incorrect','#ff5f7e'); openPassModal();"

    dm_label  = "ON" if dm_on else "OFF"
    dm_toggle = "Turn OFF" if dm_on else "Turn ON"

    HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Profile — Vital Arc</title>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
:root{{
  --bg:#07080f;
  --surface:#0d0f1c;
  --card:#111527;
  --border:#1e2340;
  --glow:#667eea;
  --glow2:#a855f7;
  --text:#e8eaf6;
  --sub:#6b7280;
  --green:#00e5a0;
  --red:#ff5f7e;
  --gold:#ffd166;
}}
body{{
  font-family:'DM Sans',sans-serif;
  background:var(--bg);
  color:var(--text);
  min-height:100vh;
  overflow-x:hidden;
}}

/* ── Background mesh ── */
body::before{{
  content:'';
  position:fixed;inset:0;
  background:
    radial-gradient(ellipse 60% 50% at 20% 10%, rgba(102,126,234,.12) 0%, transparent 60%),
    radial-gradient(ellipse 50% 40% at 80% 80%, rgba(168,85,247,.10) 0%, transparent 60%),
    radial-gradient(ellipse 30% 30% at 60% 30%, rgba(0,229,160,.06) 0%, transparent 50%);
  pointer-events:none;z-index:0;
}}

.wrap{{max-width:1100px;margin:0 auto;padding:24px 20px;position:relative;z-index:1;}}

/* ── Top bar ── */
.topbar{{
  display:flex;align-items:center;justify-content:space-between;
  margin-bottom:36px;
}}
.back-btn{{
  display:flex;align-items:center;gap:8px;
  color:var(--sub);font-size:14px;text-decoration:none;
  padding:8px 16px;border:1px solid var(--border);border-radius:40px;
  transition:all .2s;font-family:'Syne',sans-serif;font-weight:600;
}}
.back-btn:hover{{color:var(--text);border-color:var(--glow);box-shadow:0 0 12px rgba(102,126,234,.2);}}
.logout-btn{{
  display:flex;align-items:center;gap:8px;
  color:var(--red);font-size:14px;text-decoration:none;
  padding:8px 20px;border:1px solid rgba(255,95,126,.3);border-radius:40px;
  transition:all .2s;font-family:'Syne',sans-serif;font-weight:700;background:rgba(255,95,126,.06);
}}
.logout-btn:hover{{background:rgba(255,95,126,.15);border-color:var(--red);box-shadow:0 0 14px rgba(255,95,126,.2);}}

/* ── Hero card ── */
.hero{{
  background:var(--card);
  border:1px solid var(--border);
  border-radius:24px;
  padding:36px;
  margin-bottom:24px;
  position:relative;
  overflow:hidden;
}}
.hero::before{{
  content:'';
  position:absolute;top:-1px;left:0;right:0;height:2px;
  background:linear-gradient(90deg,transparent,var(--glow),var(--glow2),transparent);
}}
.hero-inner{{display:flex;align-items:flex-start;gap:32px;flex-wrap:wrap;}}

/* ── Avatar ── */
.avatar-zone{{position:relative;flex-shrink:0;}}
.avatar-ring{{
  width:120px;height:120px;
  border-radius:50%;
  padding:3px;
  background:linear-gradient(135deg,var(--glow),var(--glow2));
  position:relative;
}}
.avatar-ring::before{{
  content:'';
  position:absolute;inset:-4px;
  border-radius:50%;
  background:linear-gradient(135deg,var(--glow),var(--glow2));
  opacity:.3;
  filter:blur(8px);
  z-index:-1;
  animation:pulse-ring 3s ease-in-out infinite;
}}
@keyframes pulse-ring{{0%,100%{{opacity:.3;transform:scale(1)}}50%{{opacity:.6;transform:scale(1.04)}}}}
.avatar-inner{{width:100%;height:100%;border-radius:50%;overflow:hidden;background:var(--surface);}}
.avatar-upload{{
  position:absolute;bottom:2px;right:2px;
  width:34px;height:34px;
  background:linear-gradient(135deg,var(--glow),var(--glow2));
  border-radius:50%;
  display:flex;align-items:center;justify-content:center;
  cursor:pointer;border:2px solid var(--bg);
  font-size:14px;transition:transform .2s;
}}
.avatar-upload:hover{{transform:scale(1.1);}}

/* ── Hero info ── */
.hero-info{{flex:1;min-width:200px;}}
.hero-name{{
  font-family:'Syne',sans-serif;
  font-size:32px;font-weight:800;
  letter-spacing:-1px;
  background:linear-gradient(135deg,#fff 40%,var(--glow));
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  margin-bottom:4px;
}}
.hero-handle{{color:var(--sub);font-size:13px;margin-bottom:16px;letter-spacing:.5px;}}
.hero-tags{{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:20px;}}
.tag{{
  padding:4px 14px;border-radius:30px;font-size:12px;font-weight:500;
  font-family:'Syne',sans-serif;letter-spacing:.3px;
}}
.tag-risk{{background:rgba(0,229,160,.12);color:var(--green);border:1px solid rgba(0,229,160,.25);}}
.tag-risk.high{{background:rgba(255,95,126,.12);color:var(--red);border:1px solid rgba(255,95,126,.25);}}
.tag-neutral{{background:rgba(102,126,234,.12);color:#a29bfe;border:1px solid rgba(102,126,234,.25);}}

/* ── Quick stats row ── */
.qstats{{display:flex;gap:24px;flex-wrap:wrap;}}
.qstat{{text-align:center;}}
.qstat-val{{font-family:'Syne',sans-serif;font-size:22px;font-weight:800;line-height:1;}}
.qstat-lbl{{color:var(--sub);font-size:11px;margin-top:3px;letter-spacing:.5px;text-transform:uppercase;}}

/* ── Hero actions ── */
.hero-actions{{display:flex;flex-direction:column;gap:10px;align-items:flex-end;}}
.btn-edit{{
  padding:10px 24px;
  background:linear-gradient(135deg,var(--glow),var(--glow2));
  color:#fff;border:none;border-radius:40px;font-size:13px;
  font-family:'Syne',sans-serif;font-weight:700;cursor:pointer;
  letter-spacing:.3px;transition:all .2s;box-shadow:0 4px 20px rgba(102,126,234,.3);
}}
.btn-edit:hover{{transform:translateY(-1px);box-shadow:0 6px 24px rgba(102,126,234,.45);}}
.btn-dark{{
  padding:8px 18px;
  background:transparent;
  color:var(--sub);border:1px solid var(--border);border-radius:40px;font-size:12px;
  font-family:'Syne',sans-serif;font-weight:600;cursor:pointer;transition:all .2s;
}}
.btn-dark:hover{{border-color:var(--glow);color:var(--text);}}

/* ── Info grid ── */
.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:24px;}}
.grid3{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;margin-bottom:24px;}}
@media(max-width:700px){{.grid2,.grid3{{grid-template-columns:1fr;}}}}

/* ── Info card ── */
.icard{{
  background:var(--card);border:1px solid var(--border);
  border-radius:18px;padding:20px 24px;
  transition:border-color .2s;
}}
.icard:hover{{border-color:rgba(102,126,234,.3);}}
.icard-label{{
  font-size:10px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;
  color:var(--sub);margin-bottom:8px;font-family:'Syne',sans-serif;
}}
.icard-val{{font-size:20px;font-weight:600;color:var(--text);line-height:1.2;}}
.icard-sub{{font-size:12px;color:var(--sub);margin-top:3px;}}
.icard-empty{{color:var(--sub);font-size:14px;font-style:italic;}}

/* ── Health score ring ── */
.score-card{{
  background:var(--card);border:1px solid var(--border);
  border-radius:18px;padding:24px;
  display:flex;align-items:center;gap:20px;
}}
.score-ring{{position:relative;width:80px;height:80px;flex-shrink:0;}}
.score-ring svg{{transform:rotate(-90deg);}}
.score-ring .score-num{{
  position:absolute;inset:0;display:flex;align-items:center;justify-content:center;
  font-family:'Syne',sans-serif;font-size:18px;font-weight:800;
}}

/* ── Stat bar ── */
.stat-row{{margin-bottom:10px;}}
.stat-meta{{display:flex;justify-content:space-between;font-size:12px;margin-bottom:5px;}}
.stat-meta span:first-child{{color:var(--sub);}}
.stat-meta span:last-child{{font-weight:600;}}
.bar-track{{background:rgba(255,255,255,.06);border-radius:6px;height:6px;overflow:hidden;}}
.bar-fill{{height:100%;border-radius:6px;transition:width .8s cubic-bezier(.4,0,.2,1);}}

/* ── Section header ── */
.sec-header{{
  display:flex;align-items:center;justify-content:space-between;
  margin-bottom:16px;
}}
.sec-title{{
  font-family:'Syne',sans-serif;font-size:13px;font-weight:700;
  letter-spacing:1.5px;text-transform:uppercase;color:var(--sub);
}}

/* ── EDIT PANEL ── */
.edit-panel{{
  background:var(--card);border:1px solid var(--border);
  border-radius:24px;padding:32px;margin-bottom:24px;
  position:relative;overflow:hidden;
  display:none; /* hidden by default */
  animation:slideDown .3s ease;
}}
@keyframes slideDown{{from{{opacity:0;transform:translateY(-12px)}}to{{opacity:1;transform:translateY(0)}}}}
.edit-panel::before{{
  content:'';position:absolute;top:-1px;left:0;right:0;height:2px;
  background:linear-gradient(90deg,transparent,var(--glow2),var(--glow),transparent);
}}
.edit-panel.open{{display:block;}}
.edit-title{{
  font-family:'Syne',sans-serif;font-size:18px;font-weight:800;
  color:var(--text);margin-bottom:24px;
  display:flex;align-items:center;gap:10px;
}}
.edit-title span{{
  width:6px;height:6px;border-radius:50%;
  background:linear-gradient(135deg,var(--glow),var(--glow2));
  display:inline-block;
}}
.form-grid{{display:grid;grid-template-columns:1fr 1fr;gap:16px;}}
@media(max-width:600px){{.form-grid{{grid-template-columns:1fr;}}}}
.field{{display:flex;flex-direction:column;gap:6px;}}
.field label{{font-size:11px;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:var(--sub);}}
.field input{{
  background:var(--surface);border:1px solid var(--border);
  color:var(--text);padding:12px 16px;border-radius:12px;font-size:14px;
  font-family:'DM Sans',sans-serif;transition:border-color .2s,box-shadow .2s;outline:none;
}}
.field input:focus{{border-color:var(--glow);box-shadow:0 0 0 3px rgba(102,126,234,.12);}}
.edit-actions{{display:flex;gap:12px;margin-top:24px;justify-content:flex-end;}}
.btn-save{{
  padding:12px 32px;background:linear-gradient(135deg,var(--glow),var(--glow2));
  color:#fff;border:none;border-radius:40px;font-size:13px;
  font-family:'Syne',sans-serif;font-weight:700;cursor:pointer;
  letter-spacing:.3px;transition:all .2s;box-shadow:0 4px 20px rgba(102,126,234,.3);
}}
.btn-save:hover{{transform:translateY(-1px);box-shadow:0 6px 24px rgba(102,126,234,.45);}}
.btn-cancel{{
  padding:12px 24px;background:transparent;
  color:var(--sub);border:1px solid var(--border);border-radius:40px;font-size:13px;
  font-family:'Syne',sans-serif;font-weight:600;cursor:pointer;transition:all .2s;
}}
.btn-cancel:hover{{border-color:var(--red);color:var(--red);}}

/* ── Password MODAL ── */
.modal-overlay{{
  position:fixed;inset:0;background:rgba(0,0,0,.7);backdrop-filter:blur(8px);
  z-index:1000;display:none;align-items:center;justify-content:center;
  animation:fadeIn .2s ease;
}}
.modal-overlay.open{{display:flex;}}
@keyframes fadeIn{{from{{opacity:0}}to{{opacity:1}}}}
.modal-box{{
  background:var(--card);border:1px solid var(--border);
  border-radius:24px;padding:36px;width:100%;max-width:440px;margin:20px;
  position:relative;animation:scaleIn .25s cubic-bezier(.34,1.56,.64,1);
}}
@keyframes scaleIn{{from{{opacity:0;transform:scale(.92)}}to{{opacity:1;transform:scale(1)}}}}
.modal-box::before{{
  content:'';position:absolute;top:-1px;left:0;right:0;height:2px;border-radius:24px 24px 0 0;
  background:linear-gradient(90deg,transparent,var(--glow),var(--glow2),transparent);
}}
.modal-title{{
  font-family:'Syne',sans-serif;font-size:20px;font-weight:800;margin-bottom:6px;
}}
.modal-sub{{color:var(--sub);font-size:13px;margin-bottom:24px;}}
.modal-close{{
  position:absolute;top:20px;right:20px;
  background:transparent;border:1px solid var(--border);color:var(--sub);
  width:32px;height:32px;border-radius:50%;cursor:pointer;font-size:16px;
  display:flex;align-items:center;justify-content:center;transition:all .2s;
}}
.modal-close:hover{{border-color:var(--red);color:var(--red);}}
.pass-field{{display:flex;flex-direction:column;gap:6px;margin-bottom:14px;}}
.pass-field label{{font-size:11px;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:var(--sub);}}
.pass-field input{{
  background:var(--surface);border:1px solid var(--border);
  color:var(--text);padding:13px 16px;border-radius:12px;font-size:14px;
  font-family:'DM Sans',sans-serif;outline:none;transition:border-color .2s,box-shadow .2s;
}}
.pass-field input:focus{{border-color:var(--glow);box-shadow:0 0 0 3px rgba(102,126,234,.12);}}
.btn-pass-save{{
  width:100%;padding:14px;background:linear-gradient(135deg,var(--glow),var(--glow2));
  color:#fff;border:none;border-radius:12px;font-size:14px;
  font-family:'Syne',sans-serif;font-weight:700;cursor:pointer;margin-top:8px;
  transition:all .2s;letter-spacing:.3px;
}}
.btn-pass-save:hover{{box-shadow:0 6px 24px rgba(102,126,234,.4);}}

/* ── Settings row ── */
.settings-row{{
  background:var(--card);border:1px solid var(--border);
  border-radius:18px;padding:20px 24px;
  display:flex;align-items:center;justify-content:space-between;
  margin-bottom:12px;transition:border-color .2s;
}}
.settings-row:hover{{border-color:rgba(102,126,234,.25);}}
.sr-left{{}}
.sr-title{{font-family:'Syne',sans-serif;font-size:14px;font-weight:700;color:var(--text);}}
.sr-sub{{font-size:12px;color:var(--sub);margin-top:2px;}}
.sr-action{{flex-shrink:0;}}
.btn-sr{{
  padding:8px 20px;border-radius:30px;font-size:12px;
  font-family:'Syne',sans-serif;font-weight:700;cursor:pointer;transition:all .2s;letter-spacing:.3px;
}}
.btn-sr-ghost{{background:transparent;border:1px solid var(--border);color:var(--sub);}}
.btn-sr-ghost:hover{{border-color:var(--glow);color:var(--glow);}}
.btn-sr-accent{{background:rgba(102,126,234,.15);border:1px solid rgba(102,126,234,.3);color:#a29bfe;}}
.btn-sr-accent:hover{{background:rgba(102,126,234,.25);}}
.btn-sr-danger{{background:rgba(255,95,126,.1);border:1px solid rgba(255,95,126,.25);color:var(--red);}}
.btn-sr-danger:hover{{background:rgba(255,95,126,.2);}}

/* ── Toast ── */
.toast{{
  position:fixed;bottom:28px;left:50%;transform:translateX(-50%) translateY(80px);
  padding:14px 28px;border-radius:40px;font-size:14px;font-weight:600;
  font-family:'Syne',sans-serif;letter-spacing:.3px;
  box-shadow:0 8px 32px rgba(0,0,0,.4);z-index:9999;
  transition:transform .4s cubic-bezier(.34,1.56,.64,1);pointer-events:none;
  white-space:nowrap;
}}
.toast.show{{transform:translateX(-50%) translateY(0);}}

/* ── Section divider ── */
.sec-divider{{
  display:flex;align-items:center;gap:12px;margin:28px 0 20px;
}}
.sec-divider-line{{flex:1;height:1px;background:var(--border);}}
.sec-divider-label{{
  font-family:'Syne',sans-serif;font-size:11px;font-weight:700;
  letter-spacing:2px;text-transform:uppercase;color:var(--sub);
}}
</style>
</head>
<body>
<div class="wrap">

  <!-- Top bar -->
  <div class="topbar">
    <a href="/dashboard" class="back-btn">← Dashboard</a>
    <a href="/logout" class="logout-btn">Sign Out →</a>
  </div>

  <!-- ══ HERO ══ -->
  <div class="hero">
    <div class="hero-inner">

      <!-- Avatar -->
      <div class="avatar-zone">
        <div class="avatar-ring">
          <div class="avatar-inner">{avatar_img}</div>
        </div>
        <form method="post" action="/upload_photo" enctype="multipart/form-data">
          <label class="avatar-upload" title="Change photo">
            📷
            <input type="file" name="photo" accept="image/*" style="display:none" onchange="this.form.submit()">
          </label>
        </form>
      </div>

      <!-- Info -->
      <div class="hero-info">
        <div class="hero-name">{u}</div>
        <div class="hero-handle">{'@' + u.lower() + ' · Vital Arc Member'}</div>
        <div class="hero-tags">
          <span class="tag {'tag-risk high' if 'HIGH' in latest_risk else 'tag-risk'}">{latest_risk}</span>
          {'<span class="tag tag-neutral">' + age_str + ' yrs</span>' if age_str else ''}
          {'<span class="tag tag-neutral">BMI ' + str(bmi_val) + '</span>' if bmi_val else ''}
          <span class="tag tag-neutral">{total_p} checks</span>
        </div>
        <div class="qstats">
          <div class="qstat">
            <div class="qstat-val" style="color:var(--green)">{low_p}</div>
            <div class="qstat-lbl">Low Risk</div>
          </div>
          <div class="qstat">
            <div class="qstat-val" style="color:var(--red)">{high_p}</div>
            <div class="qstat-lbl">High Risk</div>
          </div>
          <div class="qstat">
            <div class="qstat-val" style="color:#a29bfe">{total_p}</div>
            <div class="qstat-lbl">Total</div>
          </div>
          {'<div class="qstat"><div class="qstat-val" style="color:var(--gold)">' + str(bmi_val) + '</div><div class="qstat-lbl">BMI</div></div>' if bmi_val else ''}
        </div>
      </div>

      <!-- Actions -->
      <div class="hero-actions">
        <button class="btn-edit" onclick="toggleEdit()">✎ Edit Profile</button>
        <button class="btn-dark" onclick="submitDark()">{'🌕 ' + dm_toggle}</button>
        <form id="darkForm" method="post" style="display:none">
          <input type="hidden" name="action" value="toggle_dark">
        </form>
      </div>
    </div>
  </div>

  <!-- ══ EDIT PANEL (hidden until Edit clicked) ══ -->
  <div class="edit-panel" id="editPanel">
    <div class="edit-title"><span></span> Edit Profile</div>
    <form method="post">
      <input type="hidden" name="action" value="update_info">
      <div class="form-grid">
        <div class="field">
          <label>Email</label>
          <input name="email" type="email" value="{email}" placeholder="your@email.com">
        </div>
        <div class="field">
          <label>Phone</label>
          <input name="phone" type="tel" value="{phone}" placeholder="+91 98765 43210">
        </div>
        <div class="field">
          <label>Height (cm)</label>
          <input name="height_cm" type="number" step="0.1" value="{'%.1f' % h if h else ''}" placeholder="e.g. 170">
        </div>
        <div class="field">
          <label>Weight (kg)</label>
          <input name="weight_kg" type="number" step="0.1" value="{'%.1f' % w if w else ''}" placeholder="e.g. 70">
        </div>
        <div class="field">
          <label>Date of Birth</label>
          <input name="dob" type="date" value="{dob}">
        </div>
      </div>
      <div class="edit-actions">
        <button type="button" class="btn-cancel" onclick="toggleEdit()">Cancel</button>
        <button type="submit" class="btn-save">Save Changes</button>
      </div>
    </form>
  </div>

  <!-- ══ SAVED INFO ══ -->
  <div class="sec-divider">
    <div class="sec-divider-line"></div>
    <div class="sec-divider-label">Health Records</div>
    <div class="sec-divider-line"></div>
  </div>

  <!-- Health score + stats -->
  <div class="grid2" style="margin-bottom:16px;">
    <div class="score-card">
      <div class="score-ring">
        <svg width="80" height="80" viewBox="0 0 80 80">
          <circle cx="40" cy="40" r="34" fill="none" stroke="rgba(255,255,255,.06)" stroke-width="7"/>
          <circle cx="40" cy="40" r="34" fill="none"
            stroke="url(#sg)" stroke-width="7" stroke-linecap="round"
            stroke-dasharray="213.6"
            stroke-dashoffset="{213.6 - (213.6 * health_score / 100):.1f}"/>
          <defs>
            <linearGradient id="sg" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stop-color="#667eea"/>
              <stop offset="100%" stop-color="#a855f7"/>
            </linearGradient>
          </defs>
        </svg>
        <div class="score-num" style="background:linear-gradient(135deg,#fff,var(--glow));-webkit-background-clip:text;-webkit-text-fill-color:transparent;">{health_score}</div>
      </div>
      <div>
        <div style="font-family:'Syne',sans-serif;font-size:15px;font-weight:700;margin-bottom:4px;">Health Score</div>
        <div style="color:var(--sub);font-size:13px;">out of 100</div>
        <div style="font-size:12px;color:{'var(--green)' if health_score >= 70 else 'var(--gold)' if health_score >= 40 else 'var(--red)'};margin-top:6px;font-weight:600;">
          {'Excellent' if health_score >= 70 else 'Moderate' if health_score >= 40 else 'Needs Attention'}
        </div>
      </div>
    </div>
    <div class="icard">
      <div class="icard-label">Prediction Stats</div>
      <div class="stat-row">
        <div class="stat-meta"><span>Low Risk</span><span style="color:var(--green)">{low_p}</span></div>
        <div class="bar-track"><div class="bar-fill" style="width:{'%d' % (low_p/max(total_p,1)*100)}%;background:var(--green);"></div></div>
      </div>
      <div class="stat-row">
        <div class="stat-meta"><span>High Risk</span><span style="color:var(--red)">{high_p}</span></div>
        <div class="bar-track"><div class="bar-fill" style="width:{'%d' % (high_p/max(total_p,1)*100)}%;background:var(--red);"></div></div>
      </div>
      <div style="margin-top:12px;font-size:12px;color:var(--sub);">Last check: <span style="color:var(--text);font-weight:600;">{latest_date}</span></div>
    </div>
  </div>

  <!-- Personal info cards -->
  <div class="grid3">
    <div class="icard">
      <div class="icard-label">Email</div>
      {'<div class="icard-val" style="font-size:15px;word-break:break-all;">' + email + '</div>' if email else '<div class="icard-empty">Not set</div>'}
    </div>
    <div class="icard">
      <div class="icard-label">Phone</div>
      {'<div class="icard-val">' + phone + '</div>' if phone else '<div class="icard-empty">Not set</div>'}
    </div>
    <div class="icard">
      <div class="icard-label">Date of Birth</div>
      {'<div class="icard-val" style="font-size:16px;">' + dob + '</div><div class="icard-sub">' + age_str + ' years old</div>' if dob else '<div class="icard-empty">Not set</div>'}
    </div>
    <div class="icard">
      <div class="icard-label">Height</div>
      {'<div class="icard-val">' + ('%.0f' % h) + ' <span style="font-size:13px;color:var(--sub);">cm</span></div>' if h else '<div class="icard-empty">Not set</div>'}
    </div>
    <div class="icard">
      <div class="icard-label">Weight</div>
      {'<div class="icard-val">' + ('%.1f' % w) + ' <span style="font-size:13px;color:var(--sub);">kg</span></div>' if w else '<div class="icard-empty">Not set</div>'}
    </div>
    <div class="icard">
      <div class="icard-label">BMI</div>
      {'<div class="icard-val" style="color:' + bmi_clr + ';">' + str(bmi_val) + '</div><div class="icard-sub">' + bmi_cat + '</div>' if bmi_val else '<div class="icard-empty">Set height & weight</div>'}
    </div>
  </div>

  <!-- ══ SETTINGS ══ -->
  <div class="sec-divider">
    <div class="sec-divider-line"></div>
    <div class="sec-divider-label">Settings</div>
    <div class="sec-divider-line"></div>
  </div>

  <div class="settings-row">
    <div class="sr-left">
      <div class="sr-title">🔒 Change Password</div>
      <div class="sr-sub">Update your account password</div>
    </div>
    <div class="sr-action">
      <button class="btn-sr btn-sr-accent" onclick="openPassModal()">Change</button>
    </div>
  </div>

  <div class="settings-row">
    <div class="sr-left">
      <div class="sr-title">{'🌙 Dark Mode' if not dm_on else '☀️ Light Mode'}</div>
      <div class="sr-sub">Currently <b style="color:{'#a29bfe' if dm_on else 'var(--sub)'}">{dm_label}</b></div>
    </div>
    <div class="sr-action">
      <button class="btn-sr btn-sr-ghost" onclick="submitDark()">{dm_toggle}</button>
    </div>
  </div>

  <div class="settings-row">
    <div class="sr-left">
      <div class="sr-title">⬇️ Export Data</div>
      <div class="sr-sub">Download your prediction history as CSV</div>
    </div>
    <div class="sr-action">
      <a href="/export_csv" class="btn-sr btn-sr-ghost" style="text-decoration:none;display:inline-block;padding:8px 20px;">Export</a>
    </div>
  </div>

  <div class="settings-row">
    <div class="sr-left">
      <div class="sr-title">🚪 Sign Out</div>
      <div class="sr-sub">Log out of your Vital Arc account</div>
    </div>
    <div class="sr-action">
      <a href="/logout" class="btn-sr btn-sr-danger" style="text-decoration:none;display:inline-block;padding:8px 20px;">Logout</a>
    </div>
  </div>

</div><!-- /wrap -->

<!-- ══ PASSWORD MODAL ══ -->
<div class="modal-overlay" id="passModal">
  <div class="modal-box">
    <button class="modal-close" onclick="closePassModal()">✕</button>
    <div class="modal-title">Change Password</div>
    <div class="modal-sub">Enter your current password to set a new one</div>
    <form method="post">
      <input type="hidden" name="action" value="change_pass">
      <div class="pass-field">
        <label>Current Password</label>
        <input name="current_pass" type="password" placeholder="••••••••" required>
      </div>
      <div class="pass-field">
        <label>New Password</label>
        <input name="new_pass" type="password" placeholder="••••••••" required>
      </div>
      <div class="pass-field">
        <label>Confirm New Password</label>
        <input id="confPass" type="password" placeholder="••••••••">
      </div>
      <button type="submit" class="btn-pass-save">Update Password</button>
    </form>
  </div>
</div>

<!-- ══ TOAST ══ -->
<div class="toast" id="toast"></div>

<script>
// ── Edit panel toggle ──
function toggleEdit() {{
  const p = document.getElementById('editPanel');
  p.classList.toggle('open');
  if (p.classList.contains('open')) {{
    p.scrollIntoView({{behavior:'smooth',block:'nearest'}});
  }}
}}

// ── Password modal ──
function openPassModal()  {{ document.getElementById('passModal').classList.add('open'); }}
function closePassModal() {{ document.getElementById('passModal').classList.remove('open'); }}
document.getElementById('passModal').addEventListener('click', function(e) {{
  if (e.target === this) closePassModal();
}});

// ── Dark mode form ──
function submitDark() {{ document.getElementById('darkForm').submit(); }}

// ── Toast ──
function showToast(msg, color) {{
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.style.background = color;
  t.style.color = color === 'var(--green)' || color === '#00e5a0' ? '#003d2a' : '#fff';
  t.style.color = '#fff';
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 3200);
}}

// ── Run on load ──
window.onload = function() {{
  {msg_js}
}};

// Escape key closes modal
document.addEventListener('keydown', e => {{ if(e.key === 'Escape') closePassModal(); }});
</script>
</body>
</html>"""

    return HTML



















# ================================
# RECOMMENDATION
# ================================
@app.route("/recommendation")
def recommendation():
    if "user" not in session:
        return redirect("/")
    u, dark = session["user"], get_dark(session["user"])
    con = get_db()
    row = con.execute(
        "SELECT prediction, age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal "
        "FROM predictions WHERE username=? ORDER BY id DESC LIMIT 1", (u,)).fetchone()
    con.close()

    if row:
        vals = [row["age"], row["sex"], row["cp"], row["trestbps"], row["chol"], row["fbs"], row["restecg"], row["thalach"], row["exang"], row["oldpeak"], row["slope"], row["ca"], row["thal"]]
        foods, exercises = get_recommendations(vals, row["prediction"])
        risk_str = "HIGH RISK" if row["prediction"] == 1 else "LOW RISK"
        clr = "#d63031" if row["prediction"] == 1 else "#00b894"
        
        foods_html = "".join("<li style='margin-bottom:6px;'>" + f + "</li>" for f in foods)
        exercises_html = "".join("<li style='margin-bottom:6px;'>" + e + "</li>" for e in exercises)
        
        content = (
            "<div class='card'>"
            "<h3 style='color:var(--accent);margin-bottom:14px;'>Personalized Recommendations</h3>"
            "<p style='margin-bottom:14px;'>Based on your latest prediction: <strong style='color:" + clr + ";'>" + risk_str + "</strong></p>"
            "<h4 style='color:var(--accent);margin-top:20px;margin-bottom:10px;'>Recommended Foods:</h4>"
            "<ul style='margin-left:20px;'>" + foods_html + "</ul>"
            "<h4 style='color:var(--accent);margin-top:20px;margin-bottom:10px;'>Recommended Exercises:</h4>"
            "<ul style='margin-left:20px;'>" + exercises_html + "</ul>"
            "</div>"
        )
    else:
        content = "<div class='card'><p>No prediction data found. Please run a prediction first.</p></div>"
        
    return base_html("Recommendations", content, u, dark)


@app.route("/nearby")
def nearby():
    if "user" not in session:
        return redirect("/")
    u, dark = session["user"], get_dark(session["user"])

    content = (
        "<div class='card'>"
        "<h3 style='color:var(--accent);margin-bottom:14px;'>Find Nearby Hospitals</h3>"
        "<p style='color:var(--sub);margin-bottom:14px;'>Click the button to locate hospitals near your current position.</p>"
        "<button onclick='showMap()' class='btn' style='font-size:15px;'>Use My Location</button>"
        "<div id='loc-status' style='margin-top:12px;font-size:13px;color:var(--sub);'></div>"
        "<div id='map-wrap' style='margin-top:16px;display:none;'>"
        "<iframe id='map-frame' width='100%' height='480' style='border:0;border-radius:12px;' loading='lazy' referrerpolicy='no-referrer-when-downgrade' allowfullscreen></iframe>"
        "</div>"
        "</div>"
        "<script>"
        "function showMap() {"
        "  const st = document.getElementById('loc-status');"
        "  const wrap = document.getElementById('map-wrap');"
        "  st.innerText = 'Locating...';"
        "  if (navigator.geolocation) {"
        "    navigator.geolocation.getCurrentPosition(function(pos) {"
        "      const lat = pos.coords.latitude;"
        "      const lon = pos.coords.longitude;"
        "      st.innerText = 'Location found: ' + lat.toFixed(4) + ', ' + lon.toFixed(4);"
        "      const src = 'https://maps.google.com/maps?q=hospitals+near+me&ll=' + lat + ',' + lon + '&z=14&output=embed';"
        "      document.getElementById('map-frame').src = src;"
        "      wrap.style.display = 'block';"
        "    }, function(err) {"
        "      st.innerText = 'Unable to get location: ' + err.message;"
        "    });"
        "  } else {"
        "    st.innerText = 'Geolocation not supported in this browser.';"
        "  }"
        "}"
        "</script>"
    )
    return base_html("Nearby Hospitals", content, u, dark)


# ====================================================
# ADMIN PANEL  (only YOU can access this)
# Credentials:  username = admin   password = adminpassword123
# Login URL  :  /admin_login
# Dashboard  :  /admin_panel
# Export CSV :  /admin_export_csv
# ====================================================

# Hard-coded admin credentials (only you know these)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "adminpassword123"

ADMIN_LOGIN_CSS = """<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{font-family:'Segoe UI',sans-serif;min-height:100vh;display:flex;align-items:center;
justify-content:center;background:linear-gradient(135deg,#1a1a2e,#16213e,#0f3460);}
.box{background:#1e2130;padding:44px;border-radius:20px;
box-shadow:0 20px 60px rgba(0,0,0,.6);width:420px;border:1px solid #2a2d3e;}
.logo-wrap{text-align:center;margin-bottom:20px;font-size:48px;}
h1{text-align:center;color:#e94560;margin-bottom:4px;font-size:26px;}
.sub{text-align:center;color:#888;margin-bottom:26px;font-size:13px;letter-spacing:1px;}
input{width:100%;padding:13px;margin:8px 0;border:2px solid #2a2d3e;border-radius:9px;
font-size:14px;background:#252840;color:#e0e0e0;transition:.2s;}
input:focus{outline:none;border-color:#e94560;}
.btn{width:100%;padding:13px;background:linear-gradient(135deg,#e94560,#c62a47);color:#fff;
border:none;border-radius:9px;font-size:15px;font-weight:bold;cursor:pointer;margin-top:10px;}
.err{background:#3d1a1a;color:#ff6b6b;padding:10px;border-radius:8px;margin-bottom:14px;text-align:center;border:1px solid #c62a47;}
.badge{display:inline-block;background:#e9456022;color:#e94560;border:1px solid #e9456044;
border-radius:20px;padding:3px 12px;font-size:11px;letter-spacing:1px;margin-bottom:20px;}
</style>"""

ADMIN_LOGIN_TMPL = ADMIN_LOGIN_CSS + """<!DOCTYPE html><html><body>
<div class='box'>
<div class='logo-wrap'>🛡️</div>
<div style='text-align:center'><span class='badge'>ADMIN ONLY</span></div>
<h1>Admin Panel</h1>
<div class='sub'>VITAL ARC · RESTRICTED ACCESS</div>
{% if error %}<div class='err'>{{ error }}</div>{% endif %}
<form method='post' action='/admin_login'>
<input name='username' placeholder='Admin Username' required>
<input type='password' name='password' placeholder='Admin Password' required>
<button class='btn' type='submit'>🔐 Enter Admin Panel</button>
</form>
</div>
</body></html>"""

@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        u = request.form.get("username", "")
        p = request.form.get("password", "")
        if u == ADMIN_USERNAME and p == ADMIN_PASSWORD:
            session["admin_user"] = ADMIN_USERNAME
            return redirect("/admin_panel")
        return render_template_string(ADMIN_LOGIN_TMPL, error="❌ Incorrect admin credentials. Access denied.")
    if "admin_user" in session:
        return redirect("/admin_panel")
    return render_template_string(ADMIN_LOGIN_TMPL, error=None)

@app.route("/admin_logout")
def admin_logout():
    session.pop("admin_user", None)
    return redirect("/admin_login")

@app.route("/admin_panel")
def admin_panel():
    if "admin_user" not in session:
        return redirect("/admin_login")

    con = get_db()

    # --- Stats ---
    total_users   = con.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    total_logins  = con.execute("SELECT COUNT(*) FROM user_logins").fetchone()[0]
    total_preds   = con.execute("SELECT COUNT(*) FROM predictions").fetchone()[0]

    # Total visits all time
    row_visits = con.execute("SELECT SUM(visit_count) FROM site_visits").fetchone()
    total_visits  = row_visits[0] if row_visits and row_visits[0] else 0

    # Visits today
    today = datetime.now().strftime("%Y-%m-%d")
    row_today = con.execute("SELECT visit_count FROM site_visits WHERE visit_date=?", (today,)).fetchone()
    today_visits = row_today["visit_count"] if row_today else 0

    # Users list with last login
    users = con.execute(
        "SELECT username, email, last_login FROM users ORDER BY id DESC"
    ).fetchall()

    # Recent logins
    recent_logins = con.execute(
        "SELECT username, login_time FROM user_logins ORDER BY id DESC LIMIT 50"
    ).fetchall()

    # Daily visit chart data (last 14 days)
    visit_data = con.execute(
        "SELECT visit_date, visit_count FROM site_visits ORDER BY visit_date DESC LIMIT 14"
    ).fetchall()
    con.close()

    # Build users table rows
    user_rows = ""
    for u in users:
        last = str(u["last_login"]) if u["last_login"] else "<span style='color:#555;'>Never</span>"
        email = str(u["email"]) if u["email"] else "<span style='color:#555;'>—</span>"
        user_rows += (
            "<tr>"
            "<td style='font-weight:bold;color:#a29bfe;'>" + str(u["username"]) + "</td>"
            "<td>" + email + "</td>"
            "<td>" + last + "</td>"
            "</tr>"
        )

    # Build logins table rows
    login_rows = ""
    for l in recent_logins:
        login_rows += (
            "<tr>"
            "<td style='color:#667eea;font-weight:bold;'>" + str(l["username"]) + "</td>"
            "<td>" + str(l["login_time"]) + "</td>"
            "</tr>"
        )

    # Build visit chart bars
    chart_html = ""
    if visit_data:
        max_v = max((v["visit_count"] for v in visit_data), default=1)
        # Ensure we have a decent height even for small values
        for v in reversed(list(visit_data)):
            # Calculate percentage for height
            h_val = int((v["visit_count"] / max_v) * 120) if max_v > 0 else 0
            # Ensure a minimum visible height
            h_val = max(h_val, 15)
            
            chart_html += (
                "<div style='display:flex;flex-direction:column;align-items:center;gap:4px;flex:1;min-width:40px;'>"
                "<div style='font-size:10px;color:#888;font-weight:bold;'>" + str(v["visit_count"]) + "</div>"
                "<div style='background:linear-gradient(180deg,#667eea,#764ba2);border-radius:6px 6px 0 0;"
                "width:100%;height:" + str(h_val) + "px;transition:height 0.4s ease;box-shadow:0 2px 8px rgba(102,126,234,0.3);'></div>"
                "<div style='font-size:9px;color:#888;writing-mode:vertical-rl;text-orientation:mixed;margin-top:4px;'>"
                + str(v["visit_date"]) + "</div>"
                "</div>"
            )
    else:
        chart_html = "<div style='color:#555;padding:20px;text-align:center;width:100%;'>No visit data collected yet. Start browsing the site!</div>"

    ADMIN_CSS = """<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{font-family:'Segoe UI',Arial,sans-serif;background:#0f1117;color:#e0e0e0;min-height:100vh;}
.wrap{max-width:1200px;margin:0 auto;padding:24px;}
.topbar{display:flex;justify-content:space-between;align-items:center;margin-bottom:28px;
background:#1e2130;padding:16px 24px;border-radius:14px;border:1px solid #2a2d3e;}
.topbar h1{color:#e94560;font-size:22px;display:flex;align-items:center;gap:10px;}
.topbar-right{display:flex;gap:12px;align-items:center;}
.badge-admin{background:#e9456022;color:#e94560;border:1px solid #e9456044;border-radius:20px;padding:4px 14px;font-size:12px;font-weight:bold;}
.btn-lg{padding:10px 20px;background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;border:none;border-radius:9px;font-size:13px;font-weight:bold;cursor:pointer;text-decoration:none;display:inline-block;}
.btn-danger{background:linear-gradient(135deg,#e94560,#c62a47);}
.g4{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:24px;}
.stat-card{background:#1e2130;padding:20px;border-radius:14px;border:1px solid #2a2d3e;text-align:center;}
.stat-card h4{color:#888;font-size:12px;letter-spacing:1px;text-transform:uppercase;margin-bottom:8px;}
.stat-card .val{font-size:36px;font-weight:bold;background:linear-gradient(135deg,#667eea,#a29bfe);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.card{background:#1e2130;padding:24px;border-radius:14px;border:1px solid #2a2d3e;margin-bottom:20px;}
.card h3{color:#a29bfe;margin-bottom:16px;font-size:16px;display:flex;align-items:center;gap:8px;}
table{width:100%;border-collapse:collapse;}
th{background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;padding:12px;text-align:left;font-size:13px;}
td{padding:11px;border-bottom:1px solid #2a2d3e;font-size:13px;}
tr:last-child td{border-bottom:none;}
tr:hover td{background:rgba(102,126,234,.07);}
.chart-wrap{display:flex;align-items:flex-end;gap:6px;height:140px;padding-bottom:8px;overflow-x:auto;}
@media(max-width:800px){.g4{grid-template-columns:1fr 1fr;}}
</style>"""

    HTML = (
        "<!DOCTYPE html><html><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
        "<title>Admin Panel - Vital Arc</title>"
        + ADMIN_CSS +
        "</head><body><div class='wrap'>"
        "<div class='topbar'>"
        "<h1>🛡️ Admin Panel</h1>"
        "<div class='topbar-right'>"
        "<span class='badge-admin'>ADMIN: " + ADMIN_USERNAME + "</span>"
        "<a href='/admin_export_csv' class='btn-lg'>⬇ Export CSV</a>"
        "<a href='/admin_logout' class='btn-lg btn-danger'>Logout</a>"
        "</div></div>"

        "<div class='g4'>"
        "<div class='stat-card'><h4>Total Users</h4><div class='val'>" + str(total_users) + "</div></div>"
        "<div class='stat-card'><h4>Total Logins</h4><div class='val'>" + str(total_logins) + "</div></div>"
        "<div class='stat-card'><h4>Total Visits</h4><div class='val'>" + str(total_visits) + "</div></div>"
        "<div class='stat-card'><h4>Visits Today</h4><div class='val'>" + str(today_visits) + "</div></div>"
        "</div>"

        "<div class='card'>"
        "<h3>📊 Daily Site Visits (Last 14 Days)</h3>"
        "<div class='chart-wrap'>" + (chart_html if chart_html else "<p style='color:#555;'>No visit data yet.</p>") + "</div>"
        "</div>"

        "<div class='card'>"
        "<h3>👥 All Registered Users (" + str(total_users) + ")</h3>"
        "<div style='overflow-x:auto;'><table>"
        "<thead><tr><th>Username</th><th>Email</th><th>Last Login</th></tr></thead>"
        "<tbody>" + (user_rows if user_rows else "<tr><td colspan='3' style='color:#555;text-align:center;'>No users yet.</td></tr>") + "</tbody>"
        "</table></div></div>"

        "<div class='card'>"
        "<h3>🔐 Recent Login Activity (Last 50)</h3>"
        "<div style='overflow-x:auto;'><table>"
        "<thead><tr><th>Username</th><th>Login Time</th></tr></thead>"
        "<tbody>" + (login_rows if login_rows else "<tr><td colspan='2' style='color:#555;text-align:center;'>No logins recorded yet.</td></tr>") + "</tbody>"
        "</table></div></div>"

        "<div style='text-align:center;color:#555;font-size:12px;padding:20px;'>"
        "Vital Arc Admin Panel · Only you can see this page"
        "</div>"

        "</div></body></html>"
    )
    return HTML

@app.route("/admin_export_csv")
def admin_export_csv():
    if "admin_user" not in session:
        return redirect("/admin_login")

    con = get_db()
    users     = con.execute("SELECT username, email, last_login FROM users ORDER BY id").fetchall()
    logins    = con.execute("SELECT username, login_time FROM user_logins ORDER BY id").fetchall()
    visits    = con.execute("SELECT visit_date, visit_count FROM site_visits ORDER BY visit_date").fetchall()
    con.close()

    out = io.StringIO()
    w = csv.writer(out)

    w.writerow(["=== VITAL ARC ADMIN REPORT ===", "", "Generated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
    w.writerow([])

    w.writerow(["--- REGISTERED USERS ---"])
    w.writerow(["Username", "Email", "Last Login"])
    for u in users:
        w.writerow([u["username"], u["email"] or "", u["last_login"] or "Never"])
    w.writerow([])

    w.writerow(["--- LOGIN HISTORY ---"])
    w.writerow(["Username", "Login Time"])
    for l in logins:
        w.writerow([l["username"], l["login_time"]])
    w.writerow([])

    w.writerow(["--- DAILY SITE VISITS ---"])
    w.writerow(["Date", "Visit Count"])
    for v in visits:
        w.writerow([v["visit_date"], v["visit_count"]])

    out.seek(0)
    fname = "vitalarc_admin_report_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".csv"
    return send_file(
        io.BytesIO(out.read().encode()),
        as_attachment=True,
        download_name=fname,
        mimetype="text/csv"
    )


if __name__ == '__main__':
    # When running locally, do startup immediately
    ensure_startup()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)


