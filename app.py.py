import streamlit as st
import sqlite3
import os
import uuid

# הגדרת דף מורחב ותפריט מודרני
st.set_page_config(page_title="מערכת תקלות", layout="wide", initial_sidebar_state="expanded")

# הזרקת עיצוב CSS מותאם אישית (Custom Styling)
st.markdown("""
    <style>
    /* עיצוב כללי וצבע רקע */
    .stApp {
        background-color: #f4f6f9;
    }
    
    /* עיצוב כרטיסיית תקלה (Card) */
    .fault-card {
        background-color: white;
        padding: 24px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        border-right: 6px solid #6c757d;
    }
    .status-red { border-right-color: #dc3545 !important; }
    .status-yellow { border-right-color: #ffc107 !important; }
    .status-green { border-right-color: #28a745 !important; }
    
    /* כותרות בתוך הכרטיסייה */
    .card-title {
        color: #1e293b;
        font-size: 20px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    
    /* תגיות סטטוס מודרניות */
    .badge {
        padding: 6px 12px;
        border-radius: 50px;
        font-size: 13px;
        font-weight: bold;
        display: inline-block;
    }
    .badge-red { background-color: #ffe5e5; color: #cc0000; }
    .badge-yellow { background-color: #fff9db; color: #9e7000; }
    .badge-green { background-color: #e6fcf5; color: #0ca678; }
    
    /* עיצוב הטפסים והכפתורים */
    div.stButton > button:first-child {
        background-color: #4f46e5;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 8px 20px;
        font-weight: bold;
        transition: all 0.3s;
    }
    div.stButton > button:first-child:hover {
        background-color: #4338ca;
        transform: translateY(-1px);
    }
    </style>
""", unsafe_allow_html=True)

UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

ADMIN_PASSWORD = "1234"

def init_db():
    conn = sqlite3.connect('factory_faults.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS faults 
                 (id TEXT PRIMARY KEY, location TEXT, description TEXT, note TEXT, status TEXT, image_path TEXT)''')
    conn.commit()
    conn.close()

def add_fault(location, description, note, status, image_path):
    conn = sqlite3.connect('factory_faults.db')
    c = conn.cursor()
    c.execute("INSERT INTO faults VALUES (?, ?, ?, ?, ?, ?)", (str(uuid.uuid4()), location, description, note, status, image_path))
    conn.commit()
    conn.close()

def update_fault(fault_id, new_status, new_note):
    conn = sqlite3.connect('factory_faults.db')
    c = conn.cursor()
    c.execute("UPDATE faults SET status = ?, note = ? WHERE id = ?", (new_status, new_note, fault_id))
    conn.commit()
    conn.close()

def delete_fault(fault_id, img_path):
    conn = sqlite3.connect('factory_faults.db')
    c = conn.cursor()
    c.execute("DELETE FROM faults WHERE id = ?", (fault_id,))
    conn.commit()
    conn.close()
    if img_path and os.path.exists(img_path):
        try: os.remove(img_path)
        except: pass

def get_all_faults():
    conn = sqlite3.connect('factory_faults.db')
    c = conn.cursor()
    c.execute("SELECT * FROM faults")
    data = c.fetchall()
    conn.close()
    return data

init_db()

# תפריט ניווט בצד - מעוצב ונקי
st.sidebar.markdown("<h2 style='text-align: center; color: #4f46e5;'>🖥️ ניווט</h2>", unsafe_allow_html=True)
role = st.sidebar.radio("", ["👷 אזור עובדים", "🔑 אזור מנהל"])

# --- אזור עובדים ---
if role == "👷 אזור עובדים":
    st.markdown("<h1 style='color: #1e293b;'>👷 לוח תקלות ומשימות</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b;'>צפו בתקלות הפתוחות ועדכנו סטטוס לאחר טיפול</p>", unsafe_allow_html=True)
    
    faults = get_all_faults()
    if not faults:
        st.info("מעולה! אין תקלות פעילות במערכת כרגע.")
    
    for fault in faults:
        fid, loc, desc, note, status, img_path = fault
        
        # התאמת קלאס עיצובי לפי סטטוס
        card_class = "status-red" if status == "לא בוצע" else "status-yellow" if status == "בתיקון" else "status-green"
        badge_class = "badge-red" if status == "לא בוצע" else "badge-yellow" if status == "בתיקון" else "badge-green"
        
        # יצירת כרטיסיה מעוצבת ב-HTML
        st.markdown(f"""
            <div class="fault-card {card_class}">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div class="card-title">📍 מיקום: {loc}</div>
                    <div class="badge {badge_class}">{status}</div>
                </div>
                <p style="color: #334155; margin-top: 8px;"><strong>מה התקלה:</strong> {desc}</p>
                <p style="color: #64748b; font-style: italic;"><strong>הערת מערכת:</strong> {note if note else 'אין הערות'}</p>
            </div>
        """, unsafe_allow_html=True)
        
        # פתיחת אזור עדכון נתונים מתחת לכרטיסיה
        with st.expander(f"⚙️ לחץ כאן לעדכון או צפייה בתמונה של {loc}"):
            col1, col2 = st.columns([1, 1])
            with col1:
                new_status = st.selectbox("שנה סטטוס ל:", ["לא בוצע", "בתיקון", "טופל"], index=["לא בוצע", "בתיקון", "טופל"].index(status), key=f"s_{fid}")
                new_note = st.text_area("עדכן הערה / דיווח מהשטח:", value=note, key=f"n_{fid}")
                if st.button("💾 שמור שינויים", key=f"b_{fid}"):
                    update_fault(fid, new_status, new_note)
                    st.success("הסטטוס עודכן בהצלחה!")
                    st.rerun()
            with col2:
                if img_path and os.path.exists(img_path):
                    st.image(img_path, caption="תמונת המצב מהשטח", use_container_width=True)
        st.markdown("<br>", unsafe_allow_html=True)

# --- אזור מנהל ---
elif role == "🔑 אזור מנהל":
    st.markdown("<h1 style='color: #1e293b;'>🔑 פאנל ניהול ומעקב</h1>", unsafe_allow_html=True)
    password = st.text_input("הכנס סיסמת מנהל לגישה מלאה:", type="password")
    
    if password == ADMIN_PASSWORD:
        tab1, tab2 = st.tabs(["➕ דיווח על תקלה/פרויקט חדש", "❌ הסרת תקלות מהרשימה"])
        
        with tab1:
            st.markdown("<h3 style='color: #1e293b;'>הזנת משימה חדשה לעובדים</h3>", unsafe_allow_html=True)
            with st.form("add_form", clear_on_submit=True):
                loc = st.text_input("מיקום מדויק במפעל")
                desc = st.text_area("תיאור מלא של הבעיה או המשימה")
                initial_note = st.text_area("הערות מיוחדות או דגשים (אופציונלי)")
                uploaded_file = st.file_uploader("העלה צילום של התקלה", type=['png', 'jpg', 'jpeg'])
                
                if st.form_submit_button("🚀 שלח והפץ לעובדים"):
                    if loc and desc:
                        file_path = ""
                        if uploaded_file:
                            file_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}.jpg")
                            with open(file_path, "wb") as f:
                                f.write(uploaded_file.getbuffer())
                        add_fault(loc, desc, initial_note, "לא בוצע", file_path)
                        st.success("התקלה נרשמה בהצלחה ומופיעה כעת בלוח העובדים!")
                        st.rerun()
                    else:
                        st.error("אנא מלא את השדות חובה: מיקום ותיאור התקלה.")
                        
        with tab2:
            st.markdown("<h3 style='color: #1e293b;'>מחיקת תקלות מהמערכת</h3>", unsafe_allow_html=True)
            faults = get_all_faults()
            if not faults:
                st.info("אין מה למחוק, המערכת ריקה.")
            for fault in faults:
                fid, loc, desc, note, status, img_path = fault
                with st.expander(f"🗑️ סגור ומחק: {loc} ({status})"):
                    st.write(f"**תיאור:** {desc}")
                    if st.button("❌ מחק לצמיתות", key=f"del_{fid}"):
                        delete_fault(fid, img_path)
                        st.warning(f"התקלה ב{loc} נמחקה.")
                        st.rerun()
