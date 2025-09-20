import streamlit as st
import sqlite3
import hashlib
import pandas as pd
from datetime import datetime
import re

# Database setup
def init_database():
    """Initialize the database with required tables"""
    conn = sqlite3.connect('link_manager.db')
    cur = conn.cursor()
    
    # User table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS USER (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Link table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS LINK (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            link TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES USER(id) ON DELETE CASCADE
        )
    """)
    
    # Migrate existing database if needed
    migrate_database()
    
    conn.commit()
    conn.close()

def migrate_database():
    """Add missing columns to existing database"""
    conn = sqlite3.connect('link_manager.db')
    cur = conn.cursor()
    
    try:
        # Check if created_at column exists in USER table
        cur.execute("PRAGMA table_info(USER)")
        user_columns = [column[1] for column in cur.fetchall()]
        if 'created_at' not in user_columns:
            cur.execute("ALTER TABLE USER ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            
        # Check if created_at column exists in LINK table
        cur.execute("PRAGMA table_info(LINK)")
        link_columns = [column[1] for column in cur.fetchall()]
        if 'created_at' not in link_columns:
            cur.execute("ALTER TABLE LINK ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            
        # Check if user_id column exists in LINK table (for old databases)
        if 'user_id' not in link_columns:
            cur.execute("ALTER TABLE LINK ADD COLUMN user_id INTEGER DEFAULT 1")
            
        conn.commit()
    except Exception as e:
        st.error(f"Database migration error: {e}")
    finally:
        conn.close()

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def register_user(name, email, password):
    """Register a new user"""
    conn = sqlite3.connect('link_manager.db')
    cur = conn.cursor()
    
    try:
        hashed_password = hash_password(password)
        cur.execute(
            "INSERT INTO USER (name, email, password) VALUES (?, ?, ?)",
            (name, email, hashed_password)
        )
        conn.commit()
        return True, "Registration successful!"
    except sqlite3.IntegrityError:
        return False, "Email already exists!"
    except Exception as e:
        return False, f"Registration failed: {str(e)}"
    finally:
        conn.close()

def login_user(email, password):
    """Login user and return user info"""
    conn = sqlite3.connect('link_manager.db')
    cur = conn.cursor()
    
    hashed_password = hash_password(password)
    cur.execute(
        "SELECT id, name, email FROM USER WHERE email = ? AND password = ?",
        (email, hashed_password)
    )
    user = cur.fetchone()
    conn.close()
    
    return user

def get_user_links(user_id):
    """Get all links for a specific user"""
    conn = sqlite3.connect('link_manager.db')
    cur = conn.cursor()
    
    # Check if user_id column exists, if not get all links (for backward compatibility)
    try:
        cur.execute(
            "SELECT id, name, link, description, created_at FROM LINK WHERE user_id = ? ORDER BY id DESC",
            (user_id,)
        )
        links = cur.fetchall()
    except sqlite3.OperationalError:
        # Fallback for old database without user_id column
        cur.execute("SELECT id, name, link, description, NULL FROM LINK ORDER BY id DESC")
        links = cur.fetchall()
    
    conn.close()
    return links

def add_link(user_id, name, link, description):
    """Add a new link for user"""
    conn = sqlite3.connect('link_manager.db')
    cur = conn.cursor()
    
    try:
        # Try with user_id first
        cur.execute(
            "INSERT INTO LINK (user_id, name, link, description) VALUES (?, ?, ?, ?)",
            (user_id, name, link, description)
        )
        conn.commit()
        return True, "Link added successfully!"
    except sqlite3.OperationalError:
        # Fallback for old database without user_id column
        try:
            cur.execute(
                "INSERT INTO LINK (name, link, description) VALUES (?, ?, ?)",
                (name, link, description)
            )
            conn.commit()
            return True, "Link added successfully!"
        except Exception as e:
            return False, f"Failed to add link: {str(e)}"
    except Exception as e:
        return False, f"Failed to add link: {str(e)}"
    finally:
        conn.close()

def update_link(link_id, user_id, name, link, description):
    """Update an existing link"""
    conn = sqlite3.connect('link_manager.db')
    cur = conn.cursor()
    
    try:
        # Try with user_id first
        cur.execute(
            "UPDATE LINK SET name = ?, link = ?, description = ? WHERE id = ? AND user_id = ?",
            (name, link, description, link_id, user_id)
        )
        conn.commit()
        if cur.rowcount > 0:
            return True, "Link updated successfully!"
        else:
            # Try without user_id for backward compatibility
            cur.execute(
                "UPDATE LINK SET name = ?, link = ?, description = ? WHERE id = ?",
                (name, link, description, link_id)
            )
            conn.commit()
            if cur.rowcount > 0:
                return True, "Link updated successfully!"
            else:
                return False, "Link not found."
    except Exception as e:
        return False, f"Failed to update link: {str(e)}"
    finally:
        conn.close()

def delete_link(link_id, user_id):
    """Delete a link"""
    conn = sqlite3.connect('link_manager.db')
    cur = conn.cursor()
    
    try:
        # Try with user_id first
        cur.execute("DELETE FROM LINK WHERE id = ? AND user_id = ?", (link_id, user_id))
        conn.commit()
        if cur.rowcount > 0:
            return True, "Link deleted successfully!"
        else:
            # Try without user_id for backward compatibility
            cur.execute("DELETE FROM LINK WHERE id = ?", (link_id,))
            conn.commit()
            if cur.rowcount > 0:
                return True, "Link deleted successfully!"
            else:
                return False, "Link not found."
    except Exception as e:
        return False, f"Failed to delete link: {str(e)}"
    finally:
        conn.close()

def search_links(user_id, query):
    """Search links by name or description"""
    conn = sqlite3.connect('link_manager.db')
    cur = conn.cursor()
    
    try:
        cur.execute(
            """SELECT id, name, link, description, created_at FROM LINK 
               WHERE user_id = ? AND (name LIKE ? OR description LIKE ?) 
               ORDER BY id DESC""",
            (user_id, f"%{query}%", f"%{query}%")
        )
        links = cur.fetchall()
    except sqlite3.OperationalError:
        # Fallback for old database without user_id column
        cur.execute(
            """SELECT id, name, link, description, NULL FROM LINK 
               WHERE (name LIKE ? OR description LIKE ?) 
               ORDER BY id DESC""",
            (f"%{query}%", f"%{query}%")
        )
        links = cur.fetchall()
    
    conn.close()
    return links

# Initialize session state
def init_session_state():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_info' not in st.session_state:
        st.session_state.user_info = None
    if 'page' not in st.session_state:
        st.session_state.page = 'login'

# Main application
def main():
    st.set_page_config(
        page_title="Link Manager",
        page_icon="🔗",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize database and session state
    init_database()
    init_session_state()
    
    # Custom CSS
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .link-card {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        background-color: #f9f9f9;
    }
    .link-title {
        font-size: 1.2rem;
        font-weight: bold;
        color: #333;
    }
    .link-url {
        color: #1f77b4;
        text-decoration: none;
    }
    .stats-card {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)
    
    if not st.session_state.logged_in:
        show_auth_page()
    else:
        show_dashboard()

def show_auth_page():
    """Show login/register page"""
    st.markdown('<div class="main-header">🔗 Link Manager</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Login to Your Account")
        
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="Enter your email")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submit_login = st.form_submit_button("Login", use_container_width=True)
            
            if submit_login:
                if email and password:
                    user = login_user(email, password)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user_info = {
                            'id': user[0],
                            'name': user[1],
                            'email': user[2]
                        }
                        st.success(f"Welcome back, {user[1]}!")
                        st.rerun()
                    else:
                        st.error("Invalid email or password!")
                else:
                    st.error("Please fill in all fields!")
    
    with tab2:
        st.subheader("Create New Account")
        
        with st.form("register_form"):
            name = st.text_input("Full Name", placeholder="Enter your full name")
            email = st.text_input("Email", placeholder="Enter your email")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
            submit_register = st.form_submit_button("Register", use_container_width=True)
            
            if submit_register:
                if name and email and password and confirm_password:
                    if not validate_email(email):
                        st.error("Please enter a valid email address!")
                    elif len(password) < 6:
                        st.error("Password must be at least 6 characters long!")
                    elif password != confirm_password:
                        st.error("Passwords do not match!")
                    else:
                        success, message = register_user(name, email, password)
                        if success:
                            st.success(message)
                            st.info("Please go to the Login tab to sign in.")
                        else:
                            st.error(message)
                else:
                    st.error("Please fill in all fields!")

def show_dashboard():
    """Show main dashboard"""
    # Sidebar
    with st.sidebar:
        st.markdown(f"### Welcome, {st.session_state.user_info['name']}!")
        st.markdown(f"**Email:** {st.session_state.user_info['email']}")
        
        st.markdown("---")
        
        # Navigation
        page = st.selectbox(
            "Navigate",
            ["Dashboard", "Add Link", "Search Links", "Manage Links"],
            key="navigation"
        )
        
        st.markdown("---")
        
        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_info = None
            st.rerun()
    
    # Main content
    if page == "Dashboard":
        show_dashboard_page()
    elif page == "Add Link":
        show_add_link_page()
    elif page == "Search Links":
        show_search_page()
    elif page == "Manage Links":
        show_manage_links_page()

def show_dashboard_page():
    """Show dashboard overview"""
    st.title("📊 Dashboard")
    
    user_id = st.session_state.user_info['id']
    links = get_user_links(user_id)
    
    # Statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="stats-card">
            <h2>📊</h2>
            <h3>{}</h3>
            <p>Total Links</p>
        </div>
        """.format(len(links)), unsafe_allow_html=True)
    
    with col2:
        recent_links = [link for link in links if link[4]][:7]  # Last 7 days
        st.markdown("""
        <div class="stats-card">
            <h2>🆕</h2>
            <h3>{}</h3>
            <p>Recent Links</p>
        </div>
        """.format(len(recent_links)), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="stats-card">
            <h2>👤</h2>
            <h3>Active</h3>
            <p>Account Status</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Recent links
    st.subheader("🔗 Recent Links")
    
    if links:
        recent_links = links[:5]  # Show last 5 links
        for link in recent_links:
            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{link[1]}**")
                    st.markdown(f"[🔗 {link[2]}]({link[2]})")
                    if link[3]:
                        st.caption(link[3])
                with col2:
                    if link[4]:  # created_at exists
                        try:
                            date = datetime.fromisoformat(link[4]).strftime("%Y-%m-%d")
                            st.caption(f"Added: {date}")
                        except (ValueError, TypeError):
                            st.caption("Added: Unknown")
                    else:
                        st.caption("Added: Unknown")
                st.markdown("---")
    else:
        st.info("No links found. Add your first link!")

def show_add_link_page():
    """Show add link page"""
    st.title("➕ Add New Link")
    
    with st.form("add_link_form"):
        name = st.text_input("Link Name*", placeholder="Enter a name for your link")
        url = st.text_input("URL*", placeholder="https://example.com")
        description = st.text_area("Description", placeholder="Optional description")
        
        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("Add Link", use_container_width=True)
        with col2:
            clear = st.form_submit_button("Clear Form", use_container_width=True)
        
        if submit:
            if name and url:
                # Basic URL validation
                if not (url.startswith('http://') or url.startswith('https://')):
                    url = 'https://' + url
                
                user_id = st.session_state.user_info['id']
                success, message = add_link(user_id, name, url, description)
                
                if success:
                    st.success(message)
                    st.balloons()
                else:
                    st.error(message)
            else:
                st.error("Please fill in the required fields (Name and URL)!")
        
        if clear:
            st.rerun()

def show_search_page():
    """Show search links page"""
    st.title("🔍 Search Links")
    
    search_query = st.text_input("Search by name or description", placeholder="Enter search terms...")
    
    if search_query:
        user_id = st.session_state.user_info['id']
        results = search_links(user_id, search_query)
        
        st.subheader(f"Search Results ({len(results)} found)")
        
        if results:
            for link in results:
                with st.container():
                    col1, col2, col3 = st.columns([2, 2, 1])
                    with col1:
                        st.markdown(f"**{link[1]}**")
                        st.markdown(f"[🔗 Open Link]({link[2]})")
                    with col2:
                        if link[3]:
                            st.caption(link[3])
                    with col3:
                        if link[4]:  # created_at exists
                            try:
                                date = datetime.fromisoformat(link[4]).strftime("%Y-%m-%d")
                                st.caption(f"Added: {date}")
                            except (ValueError, TypeError):
                                st.caption("Added: Unknown")
                        else:
                            st.caption("Added: Unknown")
                    st.markdown("---")
        else:
            st.info("No links found matching your search.")

def show_manage_links_page():
    """Show manage links page"""
    st.title("⚙️ Manage Links")
    
    user_id = st.session_state.user_info['id']
    links = get_user_links(user_id)
    
    if not links:
        st.info("No links to manage. Add some links first!")
        return
    
    # Convert to DataFrame for better display
    df_data = []
    for link in links:
        created_date = 'Unknown'
        if link[4]:  # created_at exists
            try:
                created_date = datetime.fromisoformat(link[4]).strftime("%Y-%m-%d")
            except (ValueError, TypeError):
                created_date = 'Unknown'
        
        df_data.append({
            'ID': link[0],
            'Name': link[1],
            'URL': link[2],
            'Description': link[3] if link[3] else 'No description',
            'Created': created_date
        })
    
    df = pd.DataFrame(df_data)
    
    # Display table
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Edit/Delete section
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Edit Link")
        link_ids = [link[0] for link in links]
        link_names = [f"{link[0]} - {link[1]}" for link in links]
        
        selected_link = st.selectbox("Select link to edit", 
                                   options=link_ids, 
                                   format_func=lambda x: next(name for id_, name in zip(link_ids, link_names) if id_ == x))
        
        if selected_link:
            # Get current link data
            current_link = next(link for link in links if link[0] == selected_link)
            
            with st.form("edit_form"):
                new_name = st.text_input("Name", value=current_link[1])
                new_url = st.text_input("URL", value=current_link[2])
                new_description = st.text_area("Description", value=current_link[3] if current_link[3] else "")
                
                if st.form_submit_button("Update Link"):
                    if new_name and new_url:
                        success, message = update_link(selected_link, user_id, new_name, new_url, new_description)
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
                    else:
                        st.error("Name and URL are required!")
    
    with col2:
        st.subheader("Delete Link")
        delete_link_id = st.selectbox("Select link to delete", 
                                    options=link_ids, 
                                    format_func=lambda x: next(name for id_, name in zip(link_ids, link_names) if id_ == x),
                                    key="delete_select")
        
        if delete_link_id:
            current_link = next(link for link in links if link[0] == delete_link_id)
            st.warning(f"You are about to delete: **{current_link[1]}**")
            
            if st.button("🗑️ Delete Link", type="secondary"):
                success, message = delete_link(delete_link_id, user_id)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

if __name__ == "__main__":
    main()