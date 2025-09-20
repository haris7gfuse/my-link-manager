# 🔗 Link Manager - Streamlit Web Application

A modern, user-friendly web application for managing your links and bookmarks. Built with Python, Streamlit, and SQLite, this application transforms a command-line link manager into a beautiful web interface with user authentication and comprehensive link management features.

## 📋 Table of Contents

- [Features](#-features)
- [Screenshots](#-screenshots)
- [Installation](#-installation)
- [Usage](#-usage)
- [Database Schema](#-database-schema)
- [Project Structure](#-project-structure)
- [Technology Stack](#-technology-stack)
- [Contributing](#-contributing)
- [License](#-license)

## ✨ Features

### 🔐 **Authentication System**
- **User Registration**: Create new accounts with email validation
- **Secure Login**: SHA-256 password hashing for security
- **Session Management**: Persistent login state across sessions
- **Email Validation**: Proper email format validation

### 📊 **Dashboard & Analytics**
- **Overview Statistics**: View total links, recent additions, and account status
- **Recent Links Display**: Quick access to your 5 most recent links
- **Visual Cards**: Modern card-based UI with gradient backgrounds
- **User-specific Data**: Each user sees only their own links

### 🔗 **Link Management**
- **Add Links**: Simple form with automatic URL formatting
- **Edit Links**: Update existing links with pre-filled current values
- **Delete Links**: Safe deletion with confirmation warnings
- **View All Links**: Comprehensive table view of all your links
- **Link Validation**: Automatic HTTPS prefix addition

### 🔍 **Search & Discovery**
- **Smart Search**: Search across link names and descriptions
- **Real-time Results**: Instant search results as you type
- **Organized Display**: Clean, card-based search results

### 📱 **User Experience**
- **Responsive Design**: Works seamlessly on desktop and mobile
- **Modern UI**: Custom CSS with contemporary design elements
- **Intuitive Navigation**: Sidebar navigation for easy access
- **Visual Feedback**: Success/error messages and loading states

### 🛠 **Technical Features**
- **Database Migration**: Automatic upgrade of existing databases
- **Backward Compatibility**: Works with legacy database schemas
- **Error Handling**: Comprehensive error handling and user feedback
- **Data Security**: User isolation and secure password storage

## 📸 Screenshots

### Login & Registration
- Clean authentication interface with tabbed login/registration
- Form validation and error handling
- Modern card-based design

### Dashboard
- Statistics overview with visual cards
- Recent links display
- User profile information in sidebar

### Link Management
- Add new links with description support
- Edit existing links with current values
- Delete links with confirmation
- Search functionality across all links

## 🚀 Installation

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Step-by-Step Installation

1. **Clone the repository** (or download the files):
```bash
git clone git@git.7gfuselab.com:haris.khan/link-manager.git
cd link-manager
```

2. **Create a virtual environment** (recommended):
```bash
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

3. **Install required packages**:
```bash
pip install streamlit pandas
```

4. **Run the application**:
```bash
streamlit run app.py
```

5. **Open your browser** and navigate to:
```
http://localhost:8501
```

## 💻 Usage

### Getting Started

1. **First Launch**: The application will automatically create the SQLite database
2. **Register**: Create a new account with your name, email, and password
3. **Login**: Use your credentials to access the dashboard

### Managing Links

#### Adding Links
1. Navigate to **"Add Link"** from the sidebar
2. Fill in the link name (required)
3. Enter the URL (required) - HTTPS will be added automatically if missing
4. Add an optional description
5. Click **"Add Link"**

#### Viewing Links
- **Dashboard**: See your 5 most recent links
- **Search Links**: Use the search function to find specific links
- **Manage Links**: View all links in a comprehensive table

#### Editing Links
1. Go to **"Manage Links"**
2. Select the link you want to edit from the dropdown
3. Update the fields as needed
4. Click **"Update Link"**

#### Deleting Links
1. Go to **"Manage Links"**
2. Select the link you want to delete
3. Confirm the deletion (this action cannot be undone)

### Search Functionality
- Use the search bar to find links by name or description
- Search is case-insensitive and matches partial text
- Results are displayed in real-time

## 🗄️ Database Schema

The application uses SQLite with two main tables:

### USER Table
```sql
CREATE TABLE USER (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### LINK Table
```sql
CREATE TABLE LINK (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    link TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES USER(id) ON DELETE CASCADE
);
```

## 📁 Project Structure

```
link-manager/
├── app.py                 # Main Streamlit application
├── link_manager.db        # SQLite database (created automatically)
├── README.md              # Project documentation
└── requirements.txt       # Python dependencies
```

### Core Functions

- **Authentication**: `register_user()`, `login_user()`, `hash_password()`
- **Database**: `init_database()`, `migrate_database()`
- **Link Operations**: `add_link()`, `update_link()`, `delete_link()`, `get_user_links()`
- **Search**: `search_links()`
- **UI Components**: `show_dashboard()`, `show_auth_page()`, etc.

## 🛠️ Technology Stack

- **Backend**: Python 3.7+
- **Web Framework**: Streamlit
- **Database**: SQLite3
- **UI Components**: Streamlit native components
- **Styling**: Custom CSS with modern design elements
- **Security**: SHA-256 password hashing
- **Data Handling**: Pandas for data display


## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Getting Started
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Make your changes
4. Run tests to ensure everything works
5. Commit your changes (`git commit -m 'Add AmazingFeature'`)
6. Push to the branch (`git push origin feature/AmazingFeature`)
7. Open a Pull Request

### Contribution Ideas
- [ ] Export links to CSV/JSON
- [ ] Import links from browser bookmarks
- [ ] Categories/tags for links
- [ ] Link validation and health checking
- [ ] Dark mode toggle
- [ ] Advanced search filters
- [ ] Link sharing between users
- [ ] REST API for mobile integration

### Code Style
- Follow PEP 8 for Python code
- Use descriptive variable names
- Add comments for complex logic
- Include docstrings for functions

## 🐛 Troubleshooting

### Common Issues

#### Database Errors
**Error**: `sqlite3.OperationalError: no such column: created_at`
**Solution**: The app includes automatic migration. Restart the application to trigger migration.

#### Login Issues
**Error**: Can't login after registration
**Solution**: Ensure you're using the exact email and password. Check for typos and case sensitivity.

#### Port Already in Use
**Error**: `OSError: [Errno 48] Address already in use`
**Solution**: Use a different port: `streamlit run app.py --server.port 8502`

#### Import Errors
**Error**: `ModuleNotFoundError: No module named 'streamlit'`
**Solution**: Install requirements: `pip install streamlit pandas`

### Getting Help
- Check the [Issues](https://github.com/yourusername/link-manager/issues) page
- Create a new issue with detailed error information
- Include your Python version and operating system

## 📈 Future Enhancements

### Planned Features
- **Categories & Tags**: Organize links with custom categories
- **Link Health Check**: Automatic validation of link availability
- **Export/Import**: CSV and JSON support for data portability
- **Advanced Search**: Filters by date, category, and link status
- **API Integration**: REST API for mobile app integration
- **Collaboration**: Share links between users
- **Link Analytics**: Track click counts and access patterns

### Performance Improvements
- Database indexing for faster searches
- Caching for frequently accessed data
- Pagination for large link collections
- Async database operations

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### MIT License Summary
- ✅ Commercial use
- ✅ Modification
- ✅ Distribution
- ✅ Private use
- ❌ Liability
- ❌ Warranty

## 👨‍💻 Author

**Haris Khan**
- GitHub: [@hariskhann1](https://github.com/hariskhann1)
- Email: haris.khan@7gFuse.com

## 🙏 Acknowledgments

- **Streamlit Team** for the amazing framework
- **SQLite** for the reliable database engine
- **Python Community** for excellent libraries and resources
- **Contributors** who help improve this project

## 📊 Project Stats

- **Language**: Python
- **Framework**: Streamlit
- **Database**: SQLite
- **Lines of Code**: ~500+
- **Features**: 15+
- **Supported Python**: 3.7+

---

## 🚀 Quick Start Commands

```bash
# Clone and setup
git clone git@git.7gfuselab.com:haris.khan/link-manager.git
cd link-manager
python -m venv env
source env/bin/activate  # Windows: env\Scripts\activate

# Install and run
pip install streamlit pandas
streamlit run app.py

# Access application
# Open browser to http://localhost:8501
```

---

**⭐ If you find this project useful, please consider giving it a star!**

**🤝 Want to contribute? Check out our [Contributing Guidelines](#-contributing)**