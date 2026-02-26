import streamlit as st
import sqlite3
from datetime import datetime

# ---------------- PAGE CONFIG ----------------
st.set_page_config("Smart Farmer", "🌱", layout="wide")

# ---------------- UI STYLE ----------------
st.markdown("""
<style>
/* BACKGROUND */
.main { background: linear-gradient(to right, #e8f5e9, #f1f8e9); }
/* HEADINGS */
h1, h2, h3 { color: #1b5e20; font-weight: 700; }
/* BUTTONS */
.stButton>button {
    background: linear-gradient(to right, #2e7d32, #43a047);
    color: white; border-radius: 10px; height: 3em; width: 100%;
    border: none; font-size: 16px; font-weight: 600; transition: 0.3s ease;
}
.stButton>button:hover { background: linear-gradient(to right, #1b5e20, #2e7d32); transform: scale(1.02); }
/* CARD */
.card { padding:16px; border-radius:12px; background-color:white; border-left:6px solid #66bb6a; box-shadow:0 6px 12px rgba(0,0,0,0.08); margin-bottom:15px; }
/* BADGES */
.badge { display:inline-block; padding:4px 10px; border-radius:20px; font-size:12px; font-weight:700; color:white; margin-left:6px; }
.badge-new { background: #ff9800; }
.badge-featured { background: #1e88e5; }
.badge-trending { background: #e53935; }
footer { visibility:hidden; }
</style>
""", unsafe_allow_html=True)

# ---------------- LANGUAGE ----------------
LANG = {
    "English": {
        "login":"Login","username":"Username","password":"Password","role":"Login as",
        "farmer":"Farmer","customer":"Customer","logout":"Logout",
        "add_veg":"Add Vegetable","veg_name":"Vegetable Name",
        "price":"Price (₹/Kg)","qty":"Quantity (Kg)",
        "buy":"Buy","order_success":"Order placed successfully!",
        "order_history":"Order History","no_orders":"No orders yet"
    },
    "தமிழ்": {
        "login":"உள்நுழைவு","username":"பயனர் பெயர்","password":"கடவுச்சொல்",
        "role":"உள்நுழைவு வகை","farmer":"விவசாயி","customer":"வாடிக்கையாளர்",
        "logout":"வெளியேறு","add_veg":"காய்கறி சேர்க்க",
        "veg_name":"காய்கறி பெயர்","price":"விலை (₹/கிலோ)",
        "qty":"அளவு (கிலோ)","buy":"வாங்க",
        "order_history":"ஆர்டர் வரலாறு","no_orders":"இன்னும் எந்த ஆர்டரும் இல்லை"
    }
}

# ---------------- DATABASE ----------------
conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT,
    role TEXT,
    UNIQUE(username, role)
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS vegetables(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    farmer_name TEXT,
    vegetable_name TEXT,
    price REAL,
    quantity INTEGER
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS orders(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer TEXT,
    vegetable TEXT,
    quantity INTEGER,
    order_date TEXT
)
""")
conn.commit()

# ---------------- SESSION ----------------
st.session_state.setdefault("user", None)
st.session_state.setdefault("role", None)
st.session_state.setdefault("show_payment", False)
st.session_state.setdefault("edit_item_id", None)
st.session_state.setdefault("delete_item_id", None)
st.session_state.setdefault("selected_item", None)
st.session_state.setdefault("selected_qty", 0)

# ---------------- LANGUAGE SELECT ----------------
language = st.sidebar.selectbox("🌐 Language / மொழி", ["English", "தமிழ்"])
T = LANG[language]

# ---------------- LOGIN ----------------
def login():
    st.title(f"🔐 {T['login']}")
    username_input = st.text_input(T["username"]).strip().lower()
    password_input = st.text_input(T["password"], type="password")
    role_ui = st.selectbox(T["role"], [T["farmer"], T["customer"]])
    role = "Farmer" if role_ui == T["farmer"] else "Customer"

    if st.button(T["login"]):
        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=? AND role=?",
            (username_input, password_input, role)
        )
        user = cursor.fetchone()
        if user:
            st.session_state.user = username_input
            st.session_state.role = role
            st.success(f"✅ Logged in as {role}")
            st.rerun()
        else:
            st.error("❌ Invalid credentials. Check username, password, and role.")

    if st.button("Register"):
        cursor.execute("SELECT * FROM users WHERE username=? AND role=?", (username_input, role))
        exists = cursor.fetchone()
        if exists:
            st.warning("⚠️ Username already exists for this role. Try a different name.")
        else:
            cursor.execute(
                "INSERT INTO users(username,password,role) VALUES(?,?,?)",
                (username_input, password_input, role)
            )
            conn.commit()
            st.success("✅ Registered successfully! Now login.")

# ---------------- FEATURES ----------------
st.markdown("### 🌟 Key Features")
st.markdown("🔐 Smart Role-Based Login <span class='badge badge-new'>NEW</span>", unsafe_allow_html=True)
st.markdown("🌐 Tamil & English Support <span class='badge badge-featured'>FEATURED</span>", unsafe_allow_html=True)
st.markdown("📦 Order History <span class='badge badge-trending'>TRENDING</span>", unsafe_allow_html=True)

# ---------------- MAIN APP ----------------
if not st.session_state.user:
    login()
else:
    st.sidebar.success(f"Logged in as {st.session_state.user}")
    if st.sidebar.button(T["logout"]):
        st.session_state.user = None
        st.session_state.role = None
        st.rerun()

    # ---------------- FARMER DASHBOARD ----------------
    if st.session_state.role == "Farmer":
        st.title(f"👨‍🌾 {T['farmer']} Dashboard")
        veg = st.text_input(T["veg_name"])
        price = st.number_input(T["price"], min_value=1)
        qty = st.number_input(T["qty"], min_value=1)

        if st.button(T["add_veg"]):
            cursor.execute(
                "INSERT INTO vegetables(farmer_name,vegetable_name,price,quantity) VALUES(?,?,?,?)",
                (st.session_state.user, veg, price, qty)
            )
            conn.commit()
            st.success("✅ Vegetable listed successfully")

        st.markdown("### 🧺 Your Listed Vegetables")
        cursor.execute("SELECT * FROM vegetables WHERE farmer_name=?", (st.session_state.user,))
        my_items = cursor.fetchall()

        if not my_items:
            st.info("No vegetables added yet.")

        for item in my_items:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown(f"<h3>🥕 {item[2]} <span class='badge badge-featured'>MY PRODUCT</span></h3>", unsafe_allow_html=True)

            if st.session_state.edit_item_id != item[0]:
                st.write(f"💰 Price: ₹{item[3]} / Kg")
                st.write(f"⚖️ Quantity: {item[4]} Kg")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✏️ Edit", key=f"edit{item[0]}"):
                        st.session_state.edit_item_id = item[0]
                        st.rerun()
                with col2:
                    if st.button("🗑️ Delete", key=f"del{item[0]}"):
                        cursor.execute("DELETE FROM vegetables WHERE id=? AND farmer_name=?", 
                                       (item[0], st.session_state.user))
                        conn.commit()
                        st.success("🗑️ Deleted successfully")
                        st.rerun()
            else:
                new_price = st.number_input("Update Price (₹/Kg)", value=float(item[3]), min_value=1.0, key=f"price{item[0]}")
                new_qty = st.number_input("Update Quantity (Kg)", value=int(item[4]), min_value=1, key=f"qty{item[0]}")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 Save", key=f"save{item[0]}"):
                        cursor.execute("UPDATE vegetables SET price=?, quantity=? WHERE id=? AND farmer_name=?", 
                                       (new_price, new_qty, item[0], st.session_state.user))
                        conn.commit()
                        st.success("✅ Updated successfully")
                        st.session_state.edit_item_id = None
                        st.rerun()
                with col2:
                    if st.button("❌ Cancel", key=f"cancel{item[0]}"):
                        st.session_state.edit_item_id = None
                        st.info("Edit cancelled")
            st.markdown("</div>", unsafe_allow_html=True)

        # ---------------- SALES HISTORY ----------------
        st.markdown("---")
        st.subheader("📊 Sales History")
        cursor.execute("""
        SELECT o.vegetable, o.quantity, o.order_date 
        FROM orders o
        JOIN vegetables v ON o.vegetable = v.vegetable_name
        WHERE v.farmer_name=? ORDER BY o.order_date DESC
        """, (st.session_state.user,))
        sales = cursor.fetchall()
        if not sales:
            st.info("No sales yet")
        else:
            for s in sales:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.write(f"🥬 **{s[0]}**")
                st.write(f"📦 Sold Quantity: {s[1]} Kg")
                st.write(f"📅 Date: {s[2]}")
                st.markdown("</div>", unsafe_allow_html=True)

        # ---------------- TOTAL EARNINGS ----------------
        st.markdown("### 💰 Total Earnings")
        cursor.execute("""
        SELECT SUM(o.quantity*v.price) FROM orders o
        JOIN vegetables v ON o.vegetable=v.vegetable_name
        WHERE v.farmer_name=?
        """, (st.session_state.user,))
        total_earnings = cursor.fetchone()[0]
        if total_earnings:
            st.success(f"💵 Total Income Earned: ₹ {total_earnings}")
        else:
            st.info("No earnings yet")

    # ---------------- CUSTOMER DASHBOARD ----------------
    else:
        st.title(f"🛒 {T['customer']} Dashboard")
        cursor.execute("SELECT * FROM vegetables")
        items = cursor.fetchall()
        for i in items:
            st.markdown("<div class='card'>", unsafe_allow_html=True)

            # -------- SMART BADGES --------
            badges = ""
            if i[4] == 0:
                badges += '<span class="badge badge-trending">OUT OF STOCK</span>'
            if i[3] <= 50 and i[4] > 0:
                badges += '<span class="badge badge-featured">LOW PRICE</span>'
            # Check trending: sold more than 10 units
            cursor.execute("SELECT SUM(quantity) FROM orders WHERE vegetable=?", (i[2],))
            sold_qty = cursor.fetchone()[0] or 0
            if sold_qty >= 10:
                badges += '<span class="badge badge-new">TRENDING</span>'

            st.markdown(f"<h3>🥬 {i[2]} {badges}</h3>", unsafe_allow_html=True)
            st.write(f"💰 ₹{i[3]} / Kg")
            st.write(f"👨‍🌾 {i[1]}")

            # BUY BUTTON LOGIC
            if i[4] > 0:
                qty = st.number_input(T["qty"], min_value=1, max_value=i[4], key=i[0])
                if st.button(f"{T['buy']} {i[2]}", key=f"buy{i[0]}"):
                    st.session_state.selected_item = i
                    st.session_state.selected_qty = qty
                    st.session_state.show_payment = True
            else:
                st.warning("🚫 This item is currently unavailable")

            st.markdown("</div>", unsafe_allow_html=True)

        # PAYMENT LOGIC
        if st.session_state.show_payment:
            st.subheader("💳 Payment Gateway (Demo)")
            item = st.session_state.selected_item
            qty = st.session_state.selected_qty

            cursor.execute("SELECT quantity FROM vegetables WHERE id=?", (item[0],))
            available_qty = cursor.fetchone()[0]

            if qty > available_qty:
                st.error("❌ Not enough stock available")
            else:
                cursor.execute(
                    "INSERT INTO orders(customer,vegetable,quantity,order_date) VALUES(?,?,?,?)",
                    (st.session_state.user, item[2], qty, datetime.now())
                )
                cursor.execute(
                    "UPDATE vegetables SET quantity=quantity-? WHERE id=?",
                    (qty, item[0])
                )
                conn.commit()
                st.success("✅ Order placed & stock updated!")
                st.session_state.show_payment = False
                st.balloons()
                
        # ORDER HISTORY
        st.subheader(f"📦 {T['order_history']}")
        cursor.execute("SELECT vegetable, quantity, order_date FROM orders WHERE customer=?", 
                       (st.session_state.user,))
        orders = cursor.fetchall()
        if not orders:
            st.info(T["no_orders"])
        else:
            for o in orders:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.write(f"🥬 {o[0]}")
                st.write(f"⚖️ {o[1]} Kg")
                st.write(f"📅 {o[2]}")
                st.markdown("</div>", unsafe_allow_html=True)