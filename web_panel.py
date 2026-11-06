import os
from flask import Flask, request, render_template_string, redirect, url_for, session
# render template string: allows you to put your html code inside the python file as a string
# session: the server remembers who you are
# Get the folder where this script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Combine it with the filename
FOOTER_FILE = os.path.join(BASE_DIR, 'footer.txt')

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_session'  # Needed for logging in
# Flask uses "Sessions" to log people in. These sessions are stored in Cookies in the browser.

# To prevent hackers from faking a cookie (and logging in as Admin without a password),
# Flask cryptographically signs the cookie using this secret key.

# Professor Question: "What happens if you delete this line?"

# Answer: The login system will break completely because Flask cannot create secure
# sessions without a key.

# --- CONFIGURATION ---
# The file where we store the footer
FOOTER_FILE = 'footer.txt'

# Hardcoded Admins (Username: Password)
ADMINS = {
    'admin1': '1234',
    'john': 'pass2',
    'sara': 'usc_2025'
}

# --- HTML TEMPLATES (Simple UI) ---
LOGIN_HTML = """
<!DOCTYPE html>
<html>
<head><title>Admin Login</title></head>
<body style="font-family: sans-serif; text-align: center; padding-top: 50px;">
    <h2>🔐 Bot Panel Login</h2>
    <form method="post" action="/login">
        <input type="text" name="username" placeholder="Username" required><br><br>
        <input type="password" name="password" placeholder="Password" required><br><br>
        <button type="submit">Login</button>
    </form>
    {% if error %}
        <p style="color: red;">{{ error }}</p>
    {% endif %}
</body>
</html>
"""

PANEL_HTML = """
<!DOCTYPE html>
<html>
<head><title>Footer Editor</title></head>
<body style="font-family: sans-serif; padding: 20px;">
    <h2>📝 Edit Telegram Bot Footer</h2>
    <p>Logged in as: <b>{{ username }}</b> | <a href="/logout">Logout</a></p>
    
    <form method="post" action="/save">
        <label>Edit the HTML code below:</label><br>
        <!-- This box shows the current content -->
        <textarea name="footer_content" rows="10" cols="80">{{ current_content }}</textarea>
        <br><br>
        <button type="submit">💾 Save Changes</button>
    </form>
    
    {% if message %}
        <p style="color: green;"><b>{{ message }}</b></p>
    {% endif %}
</body>
</html>
"""

# --- ROUTES (The logic) ---

@app.route('/') # when someone visits the home page , run this function
def index():
    """If not logged in, go to login. If logged in, go to panel."""
    if 'username' in session: # if already logged in
        return redirect(url_for('panel'))
    return render_template_string(LOGIN_HTML) # if not return to login page

@app.route('/login', methods=['POST'])
def login():
    """Checks username and password."""
    username = request.form.get('username')
    password = request.form.get('password')

    # Check if user exists and password matches
    if username in ADMINS and ADMINS[username] == password:
        session['username'] = username
        return redirect(url_for('panel'))
    else:
        return render_template_string(LOGIN_HTML, error="❌ Wrong username or password.")

@app.route('/panel')
def panel():
    """The dashboard to edit the footer."""
    if 'username' not in session:
        return redirect(url_for('index'))
    
    # Read the current footer from the file to show it in the box
    try:
        with open(FOOTER_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        content = "Footer file not found!"

    return render_template_string(PANEL_HTML, username=session['username'], current_content=content)

@app.route('/save', methods=['POST'])
def save_footer():
    """Saves the new footer to the file."""
    if 'username' not in session:
        return redirect(url_for('index'))
    
    new_content = request.form.get('footer_content')
    
    # Write the new content to the file
    with open(FOOTER_FILE, 'w', encoding='utf-8') as f:
        f.write(new_content)
        
    # Show the panel again with a success message
    return render_template_string(PANEL_HTML, username=session['username'], current_content=new_content, message="✅ Footer updated successfully!")

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Run the web server on port 5000
    app.run(debug=True, port=5000)
