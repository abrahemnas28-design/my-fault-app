import streamlit as st
import sqlite3
import os
import uuid

# תיקיית תמונות
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# סיסמת מנהל
ADMIN_PASSWORD = "1997"

# בסיס נתונים
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
        os.remove(img_path)

def get_all_faults():
    conn = sqlite3.connect('factory_faults.db')
    c = conn.cursor()
    c.execute("SELECT * FROM faults")
    data = c.fetchall()
    conn.close()
    return data

init_db()

# עיצוב המערכת והחלפת מסכים
st.set_page_config(layout="wide")
st.sidebar.title("🛠️ תפריט מערכת")
role = st.sidebar.radio("בחר אזור:", ["👷 אזור עובדים", "🔑 אזור מנהל"])

if role == "👷 אזור עובדים":
    st.title("👷 מסך עובדים - עדכון תקלות")
    faults = get_all_faults()
    if not faults:
        st.info("אין תקלות פעילות במערכת.")
    
    for fault in faults:
        fid, loc, desc, note, status, img_path = fault
        emoji = "🔴" if status == "לא בוצע" else "🟡" if status == "בתיקון" else "🟢"
        
        with st.expander(f"{emoji} מיקום: {loc} | סטטוס: {status}"):
            col1, col2 = st.columns([1, 1])
            with col1:
                st.write(f"**מה התקלה:** {desc}")
                st.write(f"**הערה נוכחית:** {note}")
                st.markdown("---")
                new_status = st.selectbox("עדכן סטטוס", ["לא בוצע", "בתיקון", "טופל"], index=["לא בוצע", "בתיקון", "טופל"].index(status), key=f"s_{fid}")
                new_note = st.text_area("הוסף הערה חדשה", value=note, key=f"n_{fid}")
                if st.button("💾 שמור עדכון", key=f"b_{fid}"):
                    update_fault(fid, new_status, new_note)
                    st.success("העדכון נשמר!")
                    st.rerun()
            with col2:
                if img_path and os.path.exists(img_path):
                    st.image(img_path, caption="תמונת התקלה", use_container_width=True)

elif role == "🔑 אזור מנהל":
    st.title("🔑 מסך מנהל - הגדרות והוספת תקלות")
    password = st.text_input("הכנס סיסמה:", type="password")
    
    if password == ADMIN_PASSWORD:
        tab1, tab2 = st.tabs(["➕ הוספת תקלה חדשה", "❌ מחיקת תקלות"])
        
        with tab1:
            with st.form("add_form"):
                loc = st.text_input("מיקום התקלה (למשל: מסוע נוזלים, מפריד 2)")
                desc = st.text_area("מה התקלה?")
                initial_note = st.text_area("הערה מנהלתית (אופציונלי)")
                uploaded_file = st.file_uploader("צרף תמונה", type=['png', 'jpg', 'jpeg'])
                if st.form_submit_button("🚀 פרסם לעובדים"):
                    if loc and desc:
                        file_path = ""
                        if uploaded_file:
                            file_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}.jpg")
                            with open(file_path, "wb") as f:
                                f.write(uploaded_file.getbuffer())
                        add_fault(loc, desc, initial_note, "לא בוצע", file_path)
                        st.success("התקלה פורסמה!")
                        st.rerun()
                    else:
                        st.error("חובה למלא מיקום ותיאור!")
                        
        with tab2:
            st.header("מחיקת תקלות ישנות")
            for fault in get_all_faults():
                fid, loc, desc, note, status, img_path = fault
                with st.expander(f"🗑️ {loc} - {status}"):
                    st.write(f"**תיאור:** {desc}")
                    if st.button("❌ מחק לצמיתות", key=f"del_{fid}"):
                        delete_fault(fid, img_path)
                        st.warning("נמחק!")
                        st.rerun()
