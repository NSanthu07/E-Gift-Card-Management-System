from flask import Flask, render_template, request, redirect, url_for, session
from flaskext.mysql import MySQL
from pymysql.cursors import DictCursor
from datetime import datetime

app = Flask(__name__, static_url_path='/static')

# Set a secret key for session management
app.secret_key = 'Hello123$'

# Configure MySQL
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'santhU123$'
app.config['MYSQL_DATABASE_DB'] = 'egiftcards'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql = MySQL(app)

# Routes

@app.route('/')
def index():
    return render_template('signup.html')

def authenticate_user(table, email, password):
    cursor = mysql.get_db().cursor()
    cursor.execute(f"SELECT * FROM {table} WHERE {table[:-1]}_email = %s AND {table[:-1]}_password = %s", (email, password))
    user = cursor.fetchone()
    return user

def is_username_exists(table, username):
    cursor = mysql.get_db().cursor()
    cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE {table[:-1]}_name = %s", (username,))
    result = cursor.fetchone()
    return result[0] > 0

def is_email_exists(table, email):
    cursor = mysql.get_db().cursor()
    cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE {table[:-1]}_email = %s", (email,))
    result = cursor.fetchone()
    return result[0] > 0

def check_existing_credentials(table, name, email):
    if is_username_exists(table, name):
        return f"{table[:-1].title()} name already exists"
    elif is_email_exists(table, email):
        return f"{table[:-1].title()} email already exists"
    return None

def get_selected_card_id(request_form):
    return request_form.get('selected-card', None)

@app.route('/signup', methods=['POST'])
def signup():
    try:
        if 'user-signup' in request.form:
            # User signup form submission
            user_id = request.form['user-id']
            user_name = request.form['user-name']
            user_email = request.form['user-email']

            # Check if username or email already exists
            error_message = check_existing_credentials('users', user_name, user_email)
            if error_message:
                #error_message = "Username or email already exists."
                return render_template('signup.html', error=error_message)
            
            user_password = request.form['user-password']
            first_name = request.form['first-name']
            last_name = request.form['last-name']
            user_phone = request.form['user-phone']
            user_address = request.form['user-address']

            print(f"Received User Signup Data: {user_id}, {user_name}, {user_email}, {first_name}, {last_name}, {user_phone}, {user_address}")

            # Save user data to MySQL
            cursor = mysql.get_db().cursor()
            cursor.execute(
                'INSERT INTO users (user_id, user_name, user_email, user_password, first_name, last_name, user_phone, user_address) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
                (user_id, user_name, user_email, user_password, first_name, last_name, user_phone, user_address)
            )
            mysql.get_db().commit()
            print("User data successfully inserted into the database")

        elif 'merchant-signup' in request.form:
            # Merchant signup form submission
            merchant_id = request.form['merchant-id']
            merchant_name = request.form['merchant-name']
            merchant_email = request.form['merchant-email']

            # Check if merchant name or email already exists
            error_message = check_existing_credentials('merchants', merchant_name, merchant_email)
            if error_message:
                return render_template('signup.html', error=error_message)
            
            merchant_password = request.form['merchant-password']
            merchant_phone = request.form['merchant-phone']
            merchant_address = request.form['merchant-address']

            print(f"Received Merchant Signup Data: {merchant_id}, {merchant_name}, {merchant_email}, {merchant_phone}, {merchant_address}")

            # Save merchant data to MySQL
            cursor = mysql.get_db().cursor()
            cursor.execute(
                'INSERT INTO merchants (merchant_id, merchant_name, merchant_email, merchant_password, merchant_phone, merchant_address) VALUES (%s, %s, %s, %s, %s, %s)',
                (merchant_id, merchant_name, merchant_email, merchant_password, merchant_phone, merchant_address)
            )
            mysql.get_db().commit()
            print("Merchant data successfully inserted into the database")

        return redirect(url_for('signin'))

    except Exception as e:
        # Handle errors appropriately
        print(str(e))
        return redirect(url_for('index'))

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'GET':
        return render_template('signin.html')
    
    try:
        if 'user-signin' in request.form:
            # User sign-in form submission
            user_email = request.form['user-email']
            user_password = request.form['user-password']

            # Authenticate user
            user = authenticate_user('users', user_email, user_password)
            if user:
                # Successful sign-in, you can store user information in the session if needed
                print("Successful user signin")
                user_id, user_name, user_email, user_password, first_name, last_name, user_phone, user_address = user
                
                # Store merchant information in the session
                session['user_id'] = user_id
                session['user_name'] = user_name

                # Redirect to the user dashboard
                return redirect(url_for('user_dashboard'))

            else:
                error_message = "Invalid email or password. Please try again."
                return render_template('signin.html', user_error=error_message)

        elif 'merchant-signin' in request.form:
            # Merchant sign-in form submission
            merchant_email = request.form['merchant-email']
            merchant_password = request.form['merchant-password']

            # Authenticate merchant
            merchant = authenticate_user('merchants', merchant_email, merchant_password)
            if merchant:
                # Successful sign-in, store merchant information in the session
                print("Successful merchant signin")
                merchant_id, merchant_name, merchant_email, merchant_password, merchant_phone, merchant_address = merchant

                # Store merchant information in the session
                session['merchant_id'] = merchant_id
                session['merchant_name'] = merchant_name

                # Redirect to the merchant dashboard
                return redirect(url_for('merchant_dashboard'))

            else:
                error_message = "Invalid email or password. Please try again."
                return render_template('signin.html', merchant_error=error_message)

        return redirect(url_for('signin'))

    except Exception as e:
        # Handle errors appropriately
        print(str(e))
        return redirect(url_for('signin'))

# Add a new route for the user dashboard
@app.route('/user_dashboard')
def user_dashboard():
    # Check if the user is logged in as a user
    # (you may need to modify this based on how you manage user sessions)
    if 'user_id' in session:
        # Fetch user information from the session
        user_id = session['user_id']
        user_name = session['user_name']

        # Render the user dashboard template
        return render_template('user_dashboard.html', user_name=user_name)

    # If not logged in as a user, redirect to the sign-in page
    return redirect(url_for('signin'))

# Add a new route for the merchant dashboard
@app.route('/merchant_dashboard')
def merchant_dashboard():
    # Check if the user is logged in as a merchant
    if 'merchant_id' in session:
        # Fetch merchant information from the session
        merchant_id = session['merchant_id']
        merchant_name = session['merchant_name']

        # Render the merchant dashboard template
        return render_template('merchant_dashboard.html', merchant_name=merchant_name)

    # If not logged in as a merchant, redirect to the sign-in page
    return redirect(url_for('signin'))

# Create the gift_cards table
@app.route('/create_gift_cards', methods=['GET', 'POST'])
def create_gift_cards():
    if request.method == 'GET':
        return render_template('create_gift_cards.html')
    
    try:
        # Extract gift card data from the form
        card_id = request.form['card-id']
        card_price = request.form['card-price']
        discount_amount = request.form['discount-amount']
        expiry_date = request.form['expiry-date']
        activation_date = request.form['activation-date']

        # Save gift card data to MySQL
        cursor = mysql.get_db().cursor()
        cursor.execute(
            'INSERT INTO gift_cards (card_id, card_price, discount_amount, expiry_date, activation_date) VALUES (%s, %s, %s, %s, %s)',
            (card_id, card_price, discount_amount, expiry_date, activation_date)
        )

        cursor.execute(
            'INSERT INTO done_gift_cards (c_id) VALUES (%s)', 
            (card_id)
        )
        
        print("OK!!")

        mysql.get_db().commit()
        print("Gift card data successfully inserted into the database")

        # TODO: Add any additional logic or redirects as needed after creating gift cards.

        return redirect(url_for('merchant_dashboard'))

    except Exception as e:
        # Handle errors appropriately
        print(str(e))
        return redirect(url_for('merchant_dashboard'))


# Add a new route for promoting gift cards
@app.route('/promote_gift_cards', methods=['GET', 'POST'])
def promote_gift_cards():
    if request.method == 'GET':
        return render_template('promote_gift_cards.html')
    
    try:
        if request.method == 'POST':
            # Extract data from the form
            card_id = request.form['card-id']
            promotion_id = request.form['promotion-id']
            description = request.form['description']
            discount_amount = request.form['discount-amount']
            validity_period = request.form['validity-period']

            # Check if the card ID exists in the gift_cards table
            cursor = mysql.get_db().cursor()
            cursor.execute('SELECT * FROM gift_cards WHERE card_id = %s', (card_id,))
            card_exists = cursor.fetchone()

            if not card_exists:
                error_message = "Invalid Card ID. Please enter a valid Card ID."
                return render_template('promote_gift_cards.html', error=error_message)

            # Save promotion data to MySQL
            cursor.execute(
                'INSERT INTO promotions (promotion_id, card_id, description, discount_amount, validity_period) VALUES (%s, %s, %s, %s, %s)',
                (promotion_id, card_id, description, discount_amount, validity_period)
            )
            mysql.get_db().commit()
            print("Promotion data successfully inserted into the database")

            # TODO: Add any additional logic or redirects as needed after promoting gift cards.

            return redirect(url_for('merchant_dashboard'))

    except Exception as e:
        # Handle errors appropriately
        print(str(e))
        return redirect(url_for('merchant_dashboard'))    
    
# Add a new route for displaying created gift cards
@app.route('/created_gift_cards')
def created_gift_cards():
    try:
        # Fetch gift card data from the database using DictCursor
        cursor = mysql.get_db().cursor(cursor=DictCursor)
        cursor.execute('SELECT * FROM gift_cards')
        gift_cards = cursor.fetchall()

        print("Displayed the created e-gift cards.")
        return render_template('created_gift_cards.html', gift_cards=gift_cards)

    except Exception as e:
        # Handle errors appropriately
        print(str(e))
        return render_template('created_gift_cards.html', gift_cards=[])
    
# Add a new route for deleting gift cards
@app.route('/delete_gift_cards', methods=['GET', 'POST'])
def delete_gift_cards():
    if request.method == 'GET':
        return render_template('delete_gift_cards.html')

    try:
        if request.method == 'POST':
            # Extract data from the form
            card_id = request.form['card-id']

            # Check if the card ID exists in the gift_cards table
            cursor = mysql.get_db().cursor()
            cursor.execute('SELECT * FROM gift_cards WHERE card_id = %s', (card_id,))
            card_exists = cursor.fetchone()

            if not card_exists:
                error_message = "Invalid Card ID. Please enter a valid Card ID."
                return render_template('delete_gift_cards.html', error=error_message)

            # Delete the gift card from the database
            cursor.execute('DELETE FROM gift_cards WHERE card_id = %s', (card_id,))
            mysql.get_db().commit()
            print("Gift card successfully deleted from the database")

            # TODO: Add any additional logic or redirects as needed after deleting gift cards.

            return redirect(url_for('merchant_dashboard'))

    except Exception as e:
        # Handle errors appropriately
        print(str(e))
        return redirect(url_for('merchant_dashboard'))
    
# Add a new route for purchasing gift cards
@app.route('/purchase_gift_cards', methods=['GET', 'POST'])
def purchase_gift_cards():
    if request.method == 'GET':
        try:
            # Fetch gift card data from the database using DictCursor
            cursor = mysql.get_db().cursor(cursor=DictCursor)
            cursor.execute('SELECT * FROM gift_cards')
            gift_cards = cursor.fetchall()

            return render_template('purchase_gift_cards.html', gift_cards=gift_cards)

        except Exception as e:
            # Handle errors appropriately
            print(str(e))
            return render_template('purchase_gift_cards.html', gift_cards=[])

    elif request.method == 'POST':
        try:
            print("Hiiii")
            selected_card_id = request.form['selected-card']

            # TODO: Add logic for processing the gift card purchase,
            # update the database, and perform any necessary redirects.

            print(f"Selected Gift Card ID: {selected_card_id}")

            return render_template('transaction.html', selected_card_id=selected_card_id)

        except Exception as e:
            # Handle errors appropriately
            print(str(e))
            return redirect(url_for('user_dashboard'))

        
    
# Add a new route for processing transactions
@app.route('/process_transaction', methods=['GET', 'POST'])
def process_transaction():
    if request.method == 'GET':
        # Handle GET requests separately, e.g., show a confirmation page or handle redirects
        return render_template('transaction.html')

    elif request.method == 'POST':
        try:
            # Extract data from the form
            transaction_id = request.form['transaction-id']
            transaction_date = request.form['transaction-date']
            transaction_type = request.form['transaction-type']
            transaction_amount = request.form['transaction-amount']

            # Fetch user ID from the session
            user_id = session.get('user_id')

            if user_id is None:
                # Handle the case where the user is not logged in
                return redirect(url_for('signin'))

            # Save transaction data to MySQL
            cursor = mysql.get_db().cursor()
            cursor.execute(
                'INSERT INTO transactions (transaction_id, user_id, transaction_date, transaction_type, transaction_amount) VALUES (%s, %s, %s, %s, %s)',
                (transaction_id, user_id, transaction_date, transaction_type, transaction_amount)
            )
            mysql.get_db().commit()
            print("Transaction data successfully inserted into the database")

            # Remove the purchased gift card from the gift_cards table
            selected_card_id = request.form['selected-card']
            print(f"Selected Card ID for Deletion: {selected_card_id}")

            if selected_card_id is None:
                # Handle the case where 'selected-card' is not present in the form data
                print("No selected card ID received.")
                return redirect(url_for('user_dashboard'))
            
            try:
                cursor.execute('DELETE FROM gift_cards WHERE card_id = %s', (selected_card_id,))
                mysql.get_db().commit()
                print("Gift card successfully removed from available gift cards")

            except Exception as e:
                print(f"Error deleting gift card: {str(e)}")

            # TODO: Add any additional logic or redirects as needed after processing the transaction.

            return redirect(url_for('user_dashboard'))

        except Exception as e:
            # Handle errors appropriately
            print(str(e))
            return redirect(url_for('user_dashboard'))

        
# Add a new route for displaying available gift cards
@app.route('/available_gift_cards')
def available_gift_cards():
    try:
        # Fetch gift card data from the database using DictCursor
        cursor = mysql.get_db().cursor(cursor=DictCursor)
        cursor.execute('SELECT * FROM gift_cards')
        gift_cards = cursor.fetchall()

        print("Displayed the available e-gift cards.")
        return render_template('available_gift_cards.html', gift_cards=gift_cards)

    except Exception as e:
        # Handle errors appropriately
        print(str(e))
        return render_template('available_gift_cards.html', gift_cards=[])

# Add a new route for displaying transaction history
@app.route('/transaction_history')
def transaction_history():
    try:
        # Fetch transaction data from the database using DictCursor
        cursor = mysql.get_db().cursor(cursor=DictCursor)
        cursor.execute('SELECT * FROM transactions WHERE user_id = %s', (session['user_id'],))
        transactions = cursor.fetchall()

        print("Displayed the transaction history.")
        return render_template('transaction_history.html', transactions=transactions)

    except Exception as e:
        # Handle errors appropriately
        print(str(e))
        return render_template('transaction_history.html', transactions=[])

# Create the feedback table
@app.route('/give_feedback', methods=['GET', 'POST'])
def give_feedback():
    if request.method == 'GET':
        return render_template('feedback.html')
    
    try:
        if request.method == 'POST':
            # Extract data from the form
            feedback_id = request.form['feedback-id']
            card_id = request.form['card-id']
            rating = request.form['rating']
            comments = request.form['comments']
            feedback_date = request.form['feedback-date']

            # Check if the card ID exists in the gift_cards table
            cursor = mysql.get_db().cursor()
            cursor.execute('SELECT * FROM done_gift_cards WHERE c_id = %s', (card_id,))
            card_exists = cursor.fetchone()

            if not card_exists:
                error_message = "Invalid Card ID. Please enter a valid Card ID."
                return render_template('feedback.html', error=error_message)

            # Save feedback data to MySQL
            cursor.execute(
                'INSERT INTO feedback (feedback_id, card_id, rating, comments, feedback_date) VALUES (%s, %s, %s, %s, %s)',
                (feedback_id, card_id, rating, comments, feedback_date)
            )
            mysql.get_db().commit()
            print("Feedback data successfully inserted into the database")

            # TODO: Add any additional logic or redirects as needed after giving feedback.

            return redirect(url_for('user_dashboard'))

    except Exception as e:
        # Handle errors appropriately
        print(str(e))
        return redirect(url_for('user_dashboard'))  
    
# Add this route in your Flask application
@app.route('/get_promotions/<int:card_id>')
def get_promotions(card_id):
    try:
        # Fetch promotions details for the specified card_id from the database
        # You can customize this query based on your database schema
        cursor = mysql.get_db().cursor(cursor=DictCursor)
        cursor.execute('SELECT * FROM promotions WHERE card_id = %s', (card_id,))
        promotions = cursor.fetchall()

        # Render a template with the promotions details
        return render_template('promotions_details.html', promotions=promotions)

    except Exception as e:
        # Handle errors appropriately
        print(str(e))
        return 'Error fetching promotions details.'
    

# Add a new route for displaying feedbacks with user information
@app.route('/feedbacks')
def feedbacks():
    try:
        # Fetch feedback data with user information from the database using JOIN
        cursor = mysql.get_db().cursor(cursor=DictCursor)
        sql_statement = '''
            SELECT f.feedback_id, f.card_id, f.rating, f.comments, f.feedback_date, u.user_name
            FROM feedback f
            JOIN done_gift_cards dgc ON f.card_id = dgc.c_id
            JOIN users u ON f.card_id = dgc.c_id
        '''
        cursor.execute(sql_statement)
        feedbacks = cursor.fetchall()

        #print("Query:", sql_statement)
        #print("Fetched Data:", feedbacks)

        return render_template('merchant_feedbacks.html', feedbacks=feedbacks)

    except Exception as e:
        # Handle errors appropriately
        print("Error:", str(e))
        return render_template('merchant_feedbacks.html', feedbacks=[])




if __name__ == '__main__':
    app.run(debug=True)