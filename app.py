
from flask import Flask,flash,redirect,render_template,url_for,request,jsonify,session,abort
from flask_session import Session
from flask_mysqldb import MySQL
from datetime import date
from datetime import datetime
from sdmail import sendmail
from tokenreset import token
from stoken1 import token1
import os
from datetime import datetime
import datetime

from itsdangerous import URLSafeTimedSerializer
from key import *
import stripe
stripe.api_key='sk_test_51MzcVYSDVehZUuDTkwGUYe8hWu2LGN0krI8iO5QOAEqoRYXx3jgRVgkY7WzXqQmpN62oMWM59ii76NKPrRzg3Gtr005oVpiW82'
app=Flask(__name__)
app.secret_key='hello'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['MYSQL_HOST'] ='localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD']='admin'
app.config['MYSQL_DB']='bidzone'
mysql=MySQL(app)
Session(app)



import random
def genotp():
    u_c=[chr(i) for i in range(ord('A'),ord('Z')+1)]
    l_c=[chr(i) for i in range(ord('a'),ord('z')+1)]
    otp=''
    for i in range(3):
        otp+=random.choice(u_c)
        otp+=str(random.randint(0,9))
        otp+=random.choice(l_c)
    return otp
@app.route('/')
def home():
    return render_template('home.html')

#=========================================Freelancer login and register
@app.route('/ulogin',methods=['GET','POST'])
def ulogin():
    if session.get('user'):
        return redirect(url_for('users_dashboard'))
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        cursor=mysql.connection.cursor()
        cursor.execute('SELECT count(*) from users where username=%s and password=%s',[username,password])
        count=cursor.fetchone()[0]
        if count==1:
            session['user']=username
            if not session.get(username):
                session[username]={}
            return redirect(url_for("userviewitems"))
        else:
            flash('Invalid username or password')
            return render_template('ulogin.html')
    return render_template('ulogin.html')

@app.route('/uregistration',methods=['GET','POST'])
def uregistration():
    if request.method=='POST':
        username = request.form['username']
        
        email = request.form['email']
        phone_number = request.form['phone']
        address = request.form['address']
        password = request.form['password']
        
        
        cursor=mysql.connection.cursor()
        cursor.execute('select count(*) from users where username=%s',[username])
        count=cursor.fetchone()[0]
        cursor.execute('select count(*) from users where email=%s',[email])
        count1=cursor.fetchone()[0]
        cursor.close()
        if count==1:
            flash('username already in use')
            return render_template('uregistration.html')
        elif count1==1:
            flash('Email already in use')
            return render_template('uregistration.html')
        
        data={'username':username,'email':email,'phone_number':phone_number,'address':address,'password':password}
        subject='Email Confirmation'
        body=f"Thanks for signing up\n\nfollow this link for further steps-{url_for('uconfirm',token=token(data,salt),_external=True)}"
        sendmail(to=email,subject=subject,body=body)
        flash('Confirmation link sent to mail')
        return redirect(url_for('uregistration'))
    
    return render_template('uregistration.html')
@app.route('/uconfirm/<token>')
def uconfirm(token):
    try:
        serializer=URLSafeTimedSerializer(secret_key)
        data=serializer.loads(token,salt=salt,max_age=180)
    except Exception as e:
      
        return 'Link Expired register again'
    else:
        cursor=mysql.connection.cursor()
        id1=data['username']
        cursor.execute('select count(*) from users where username=%s',[id1])
        count=cursor.fetchone()[0]
        if count==1:
            cursor.close()
            flash('You are already registerterd!')
            return redirect(url_for('ulogin'))
        else:
            cursor.execute('INSERT INTO users (username,email,phone_number,address,password) VALUES (%s,%s,%s,%s,%s)',[data['username'],data['email'],data['phone_number'],data['address'], data['password']])

            mysql.connection.commit()
            cursor.close()
            flash('Details registered!')
            return redirect(url_for('ulogin'))
@app.route('/forget',methods=['GET','POST'])
def uforgot():
    if request.method=='POST':
        id1=request.form['id1']
        cursor=mysql.connection.cursor()
        cursor.execute('select count(*) from users where username=%s',[id1])
        count=cursor.fetchone()[0]
        cursor.close()
        if count==1:
            cursor=mysql.connection.cursor()

            cursor.execute('SELECT email  from users where username=%s',[id1])
            email=cursor.fetchone()[0]
            cursor.close()
            subject='Forget Password'
            confirm_link=url_for('ureset',token=token(id1,salt=salt2),_external=True)
            body=f"Use this link to reset your password-\n\n{confirm_link}"
            sendmail(to=email,body=body,subject=subject)
            flash('Reset link sent check your email')
            return redirect(url_for('ulogin'))
        else:
            flash('Invalid email id')
            return render_template('forgot.html')
    return render_template('forgot.html')


@app.route('/reset/<token>',methods=['GET','POST'])
def ureset(token):
    try:
        serializer=URLSafeTimedSerializer(secret_key)
        id1=serializer.loads(token,salt=salt2,max_age=180)
    except:
        abort(404,'Link Expired')
    else:
        if request.method=='POST':
            newpassword=request.form['npassword']
            confirmpassword=request.form['cpassword']
            if newpassword==confirmpassword:
                cursor=mysql.connection.cursor()
                cursor.execute('update  users set password=%s where username=%s',[newpassword,id1])
                mysql.connection.commit()
                flash('Reset Successful')
                return redirect(url_for('ulogin'))
            else:
                flash('Passwords mismatched')
                return render_template('newpassword.html')
        return render_template('newpassword.html')
@app.route('/ulogout')
def ulogout():
    if session.get('user'):
        session.pop('user')
        flash('Successfully loged out')
        return redirect(url_for('ulogin'))
    else:
        return redirect(url_for('ulogin'))
@app.route('/users_dashboard')
def users_dashboard():
    if session.get('user'):
        return render_template('users_dashboard.html')
    return redirect(url_for('ulogin'))
#========================user can bid to the items
@app.route('/biditems/<item_id>',methods=['GET','POST'])
def biditems(item_id):
    #print('================================',item_id)
    if session.get('user'):
        cursor=mysql.connection.cursor()
        cursor.execute('SELECT winning_bid_amount FROM auction_data WHERE item_id = %s', [item_id])
        winning_bid_amount = cursor.fetchone()

        if winning_bid_amount is not None:
            flash('This item already has a winning bid. You cannot bid on it.')
            return redirect(url_for('userviewitems'))
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM  items where item_id=%s',[item_id])
        items = cursor.fetchall()
        cursor.execute('select * from placed_bids where item_id=%s',[item_id])
        bids=cursor.fetchall()
        return render_template('userbiding.html', items=items,bids=bids)

    else:
        return redirect(url_for('ulogin'))
#============================================= Place bid route
'''@app.route('/place_bid/<item_id>', methods=['POST'])
def place_bid(item_id):
   
    

    if request.method == 'POST':
        bid_amount = request.form['bid_amount']
        item_id = item_id
        bidder_username = session.get('user')  # Assuming you store the logged-in user's username in the session
        bid_time = datetime.datetime.now()

        # Validate bid amount (you can add more validation logic here)
        if int(bid_amount) <= 0:
            return 'Invalid bid amount'

        # Connect to MySQL and execute the query to store bid data
        
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO auction_data (item_id, bidder_username, bid_amount, bid_time) VALUES (%s, %s, %s, %s)', (item_id, bidder_username, bid_amount, bid_time))
        mysql.connection.commit()
        cursor.execute('SELECT * FROM  items where item_id=%s',[item_id])
        items = cursor.fetchall()
        cursor.close()
        flash('the bid is displayed')
        return render_template('userbiding.html', items=items)
# Place bid route
@app.route('/place_bid/<item_id>', methods=['POST'])
def place_bid(item_id):
    if session.get('user'):
        if request.method == 'POST':
            bid_amount = int(request.form['bid_amount'])
            bidder_username = session.get('user')  # Assuming you store the logged-in user's username in the session
            bid_time = datetime.datetime.now()
            
            cursor = mysql.connection.cursor()
            cursor.execute('SELECT seller_username, starting_price FROM items WHERE item_id = %s', [item_id])
            item_data = cursor.fetchone()
            cursor.close()

            seller_username = item_data[0]
            starting_price = item_data[1]
            cursor = mysql.connection.cursor()
            cursor.execute('SELECT current_bid FROM auction_data WHERE item_id = %s ORDER BY bid_time DESC LIMIT 1', [item_id])
            current_bid_data = cursor.fetchone()
            cursor.close()

            # Calculate bid increment
            current_bid = current_bid_data[0] if current_bid_data else starting_price  # Set current bid to starting price if no bids yet
            bid_increment = bid_amount - current_bid  # Calculate bid increment from current bid

            # Validate bid amount and bid increment
            if bid_amount <= 0 or bid_increment <= 0:
                flash('Invalid bid amount or bid increment')
                return redirect(url_for('userviewitems'))
            # Check if bid amount is valid and within bid increment
            if bid_amount > starting_price and (bid_amount - starting_price) % bid_increment == 0:
                # Connect to MySQL and execute the query to store bid data
                cursor = mysql.connection.cursor()
                cursor.execute('INSERT INTO auction_data (item_id, bidder_username, bid_amount, bid_time, seller_username, starting_price, bid_increment, auction_end) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', (item_id, bidder_username, bid_amount, bid_time, seller_username, starting_price, bid_increment, bid_time + datetime.timedelta(days=1)))  # Assuming auction lasts for 1 day
                mysql.connection.commit()
                cursor.close()
                flash('Bid placed successfully')
                return redirect(url_for('userviewitems'))
            else:
                return 'Bid amount must be higher than starting price and within bid increment'
        return redirect(url_for('userviewitems'))  # Redirect to the items view page after placing the bid
    else:
        return redirect(url_for('ulogin'))'''


''''@app.route('/place_bid/<item_id>', methods=['POST'])
def place_bid(item_id):
    if session.get('user'):
        if request.method == 'POST':
            bid_amount = int(request.form['bid_amount'])
            bidder_username = session.get('user')  # Assuming you store the logged-in user's username in the session
            bid_time = datetime.datetime.now()

            # Check if initial auction details already exist for the item
            cursor = mysql.connection.cursor()
            cursor.execute('SELECT auction_id FROM auction_data WHERE item_id = %s', [item_id])
            existing_auction = cursor.fetchone()
            cursor.close()

            if existing_auction:
                auction_id = existing_auction[0]
            else:
                # Insert initial auction details
                cursor = mysql.connection.cursor()
                cursor.execute('SELECT seller_username, starting_price FROM items WHERE item_id = %s', [item_id])
                item_data = cursor.fetchone()
               

                seller_username = item_data[0]
                starting_price = item_data[1]
               
                cursor.execute('INSERT INTO auction_data (item_id, seller_username, starting_price, auction_start, auction_end, status) VALUES (%s, %s, %s, %s, %s, %s)', (item_id, seller_username, starting_price, bid_time, bid_time + datetime.timedelta(days=1), 'Active'))  # Assuming auction lasts for 1 day
                mysql.connection.commit()
                cursor.close()

                # Fetch the newly inserted auction ID
                cursor = mysql.connection.cursor()
                cursor.execute('SELECT LAST_INSERT_ID()')
                auction_id = cursor.fetchone()[0]
                cursor.close()

            # Store the bid details in placed_bids table
            cursor = mysql.connection.cursor()
            cursor.execute('INSERT INTO placed_bids (auction_id, item_id, bidder_username, bid_amount, bid_time) VALUES (%s, %s, %s, %s, %s)', (auction_id, item_id, bidder_username, bid_amount, bid_time))
            mysql.connection.commit()
            cursor.close()

            flash('Bid placed successfully')
            return redirect(url_for('userviewitems'))

        return redirect(url_for('userviewitems'))  # Redirect to the items view page after placing the bid
    else:
        return redirect(url_for('ulogin'))'''
#===============================================================================
'''@app.route('/place_bid/<item_id>', methods=['POST'])
def place_bid(item_id):
    if session.get('user'):
        if request.method == 'POST':
            bid_amount = int(request.form['bid_amount'])
            bidder_username = session.get('user')  # Assuming you store the logged-in user's username in the session
            bid_time = datetime.datetime.now()
            print("================================",item_id)
            # Fetch the current bid
            cursor = mysql.connection.cursor()
            cursor.execute('SELECT bid_amount FROM placed_bids WHERE item_id = %s ORDER BY bid_time DESC LIMIT 1', [item_id])
            current_bid_data = cursor.fetchone()
            cursor.close()

            current_bid = current_bid_data[0] if current_bid_data else None  # Set current bid to None if no bids yet

            # Check if initial auction details already exist for the item
            cursor = mysql.connection.cursor()
            cursor.execute('SELECT auction_id, starting_price FROM auction_data WHERE item_id = %s', [item_id])
            existing_auction = cursor.fetchone()
            print("==============================================",existing_auction)
            cursor.close()
            # auction_id, starting_price = existing_auction
            # if existing_auction!= None:
            #     auction_id, starting_price = existing_auction
            # else:
            #     flash('Auction details not found for the item')
            #     return redirect(url_for('userviewitems'))

            bid_increment = bid_amount - current_bid if current_bid is not None else bid_amount - existing_auction[1]   # Calculate bid increment

            if bid_amount <= 0 or bid_increment <= 0:
                flash('Invalid bid amount or bid increment')
                return redirect(url_for('userviewitems'))

            # Store the bid details in placed_bids table
            cursor = mysql.connection.cursor()
            cursor.execute('INSERT INTO placed_bids (auction_id, item_id, bidder_username, bid_amount, bid_time, current_bid, bid_increment) VALUES (%s, %s, %s, %s, %s, %s, %s)', (auction_id, item_id, bidder_username, bid_amount, bid_time, current_bid, bid_increment))
            mysql.connection.commit()
            cursor.close()

            flash('Bid placed successfully')
            return redirect(url_for('userviewitems'))

        return redirect(url_for('userviewitems'))  # Redirect to the items view page after placing the bid
    else:
        return redirect(url_for('ulogin')) 

@app.route('/place_bid/<item_id>', methods=['POST'])
def place_bid(item_id):
    if session.get('user'):
        if request.method == 'POST':
            bid_amount = int(request.form['bid_amount'])
            bidder_username = session.get('user')  # Assuming you store the logged-in user's username in the session
            bid_time = datetime.datetime.now()

            # Fetch the current bid
            cursor = mysql.connection.cursor()
            cursor.execute('SELECT bid_amount FROM placed_bids WHERE item_id = %s ORDER BY bid_time DESC LIMIT 1', [item_id])
            current_bid_data = cursor.fetchone()
            cursor.close()

            current_bid = current_bid_data[0] if current_bid_data else None  # Set current bid to None if no bids yet

            # Check if initial auction details already exist for the item
            cursor = mysql.connection.cursor()
            cursor.execute('SELECT auction_id, starting_price FROM auction_data WHERE item_id = %s', [item_id])
            existing_auction = cursor.fetchone()
            cursor.close()

            if existing_auction is None:
                # Insert initial auction data
                cursor = mysql.connection.cursor()
                cursor.execute('select seller_username from items where item_id=%s',item_id)
                seller_username=cursor.fetchone()
                cursor.execute('select starting_price from items where item_id=%s',item_id)
                starting_price=cursor.fetchone()
                cursor.execute('INSERT INTO auction_data (item_id, seller_username, starting_price, auction_start, status) VALUES (%s, %s, %s, %s, %s)', (item_id, seller_username, starting_price, bid_time, 'Active'))
                mysql.connection.commit()
                cursor.close()
                
                # Fetch the inserted auction data
                cursor = mysql.connection.cursor()
                cursor.execute('SELECT auction_id, starting_price FROM auction_data WHERE item_id = %s', [item_id])
                existing_auction = cursor.fetchone()
                cursor.close()

            auction_id, starting_price = existing_auction
            bid_increment = bid_amount - current_bid if current_bid is not None else bid_amount - starting_price  # Calculate bid increment

            if bid_amount <= 0 or bid_increment <= 0:
                flash('Invalid bid amount or bid increment')
                return redirect(url_for('userviewitems'))

            # Store the bid details in placed_bids table
            cursor = mysql.connection.cursor()
            cursor.execute('INSERT INTO placed_bids (auction_id, item_id, bidder_username, bid_amount, bid_time, current_bid, bid_increment) VALUES (%s, %s, %s, %s, %s, %s, %s)', (auction_id, item_id, bidder_username, bid_amount, bid_time, current_bid, bid_increment))
            mysql.connection.commit()
            cursor.close()

            flash('Bid placed successfully')
            return redirect(url_for('userviewitems'))

        return redirect(url_for('userviewitems'))  # Redirect to the items view page after placing the bid
    else:
        return redirect(url_for('ulogin'))'''
 
#========================stop the auction by seller
'''@app.route('/stop_auction/<item_id>', methods=['POST'])
def stop_auction(item_id):
    if session.get('seller'):
        seller_username = session.get('seller')  # Assuming you store the logged-in user's username in the session

        # Check if the user is the seller of the item
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT seller_username FROM auction_data WHERE item_id = %s', [item_id])
        seller_data = cursor.fetchone()
        cursor.close()

        if seller_data and seller_data[0] == seller_username:
            # Update the auction status to 'Completed' and determine the winner
            cursor = mysql.connection.cursor()
            cursor.execute('UPDATE auction_data SET status = "Completed" WHERE item_id = %s', [item_id])
            cursor.execute('UPDATE items SET status = "Completed" WHERE item_id = %s', [item_id])
            # Fetch the highest bid for this item
            cursor.execute('SELECT bidder_username, bid_amount FROM placed_bids WHERE item_id = %s ORDER BY bid_amount DESC LIMIT 1', [item_id])
            winning_bid_data = cursor.fetchone()
            cursor.close()

            if winning_bid_data:
                winning_bidder_username, winning_bid_amount = winning_bid_data
                cursor = mysql.connection.cursor()
                cursor.execute('UPDATE auction_data SET winning_bidder_username = %s, winning_bid_amount = %s WHERE item_id = %s', (winning_bidder_username, winning_bid_amount, item_id))
                mysql.connection.commit()
                cursor.close()

                flash(f'Auction for item {item_id} stopped successfully. Winner: {winning_bidder_username}, Winning Bid: {winning_bid_amount}')
            else:
                flash('No bids placed for this item yet.')

            return redirect(url_for('userviewitems'))
        else:
            flash('You are not authorized to stop this auction.')
            return redirect(url_for('userviewitems'))
    else:
        return redirect(url_for('slogin')) '''
@app.route('/placed_bids/<itemid>',methods=['GET','POST'])
def placed_bids(itemid):
    if session.get('user'):
        if request.method=="POST":
            bid_amount = int(request.form['bid_amount'])
            bidder_username = session.get('user')  # Assuming you store the logged-in user's username in the session
            bid_time = datetime.datetime.now()
            cursor=mysql.connection.cursor()
            #checking to the particular itemid is found in auction data if not found insert
            cursor.execute('select count(*) from auction_data where item_id=%s',[itemid])
            count=cursor.fetchone()[0]
            if count==1:
                # Fetch the current bid
                cursor = mysql.connection.cursor()
                cursor.execute('select auction_id from auction_data where item_id=%s',[itemid])
                auction_id=cursor.fetchone()
                cursor.execute('SELECT bid_amount FROM placed_bids WHERE item_id = %s ORDER BY bid_time DESC LIMIT 1', [itemid])
                current_bid_data = cursor.fetchone()
                cursor.execute('select starting_price from items where item_id=%s',[itemid])
                starting_price=cursor.fetchone()[0]
                
                cursor.close()

                current_bid = current_bid_data[0] if current_bid_data else None  # Set current bid to None if no bids yet
                bid_increment = bid_amount - current_bid if current_bid is not None else bid_amount - starting_price  # Calculate bid increment

                if bid_amount <= 0 or bid_increment <= 0:
                    flash('Invalid bid amount or bid increment')
                    return redirect(url_for('userviewitems'))

                # Store the bid details in placed_bids table
                cursor = mysql.connection.cursor()
                cursor.execute('INSERT INTO placed_bids (auction_id, item_id, bidder_username, bid_amount, bid_time, current_bid, bid_increment) VALUES (%s, %s, %s, %s, %s, %s, %s)', (auction_id, itemid, bidder_username, bid_amount, bid_time, current_bid, bid_increment))
                mysql.connection.commit()
                cursor.close()

                flash('Bid placed successfully')
                return redirect(url_for('userviewitems'))

            else:
                cursor=mysql.connection.cursor()
                cursor.execute('select seller_username from items where item_id=%s',[itemid])
                seller_username=cursor.fetchone()[0]
                cursor.execute('select starting_price from items where item_id=%s',[itemid])
                starting_price=cursor.fetchone()[0]
                cursor.execute('INSERT INTO auction_data (item_id, seller_username, starting_price, auction_start, status) VALUES (%s, %s, %s, %s, %s)', (itemid, seller_username, starting_price, bid_time, 'Active'))
                mysql.connection.commit()
                #now insert into placed bids
                cursor = mysql.connection.cursor()
                cursor.execute('select auction_id from auction_data where item_id=%s',[itemid])
                auction_id=cursor.fetchone()
                cursor.execute('SELECT bid_amount FROM placed_bids WHERE item_id = %s ORDER BY bid_time DESC LIMIT 1', [itemid])
                current_bid_data = cursor.fetchone()
                cursor.close()

                current_bid = current_bid_data[0] if current_bid_data else None  # Set current bid to None if no bids yet
                bid_increment = bid_amount - current_bid if current_bid is not None else bid_amount - starting_price  # Calculate bid increment

                if bid_amount <= 0 or bid_increment <= 0:
                    flash('Invalid bid amount or bid increment')
                    return redirect(url_for('userviewitems'))

                # Store the bid details in placed_bids table
                cursor = mysql.connection.cursor()
                cursor.execute('INSERT INTO placed_bids (auction_id, item_id, bidder_username, bid_amount, bid_time, current_bid, bid_increment) VALUES (%s, %s, %s, %s, %s, %s, %s)', (auction_id, itemid, bidder_username, bid_amount, bid_time, current_bid, bid_increment))
                mysql.connection.commit()
                cursor.close()

                flash('Bid placed successfully')
                return redirect(url_for('userviewitems'))



    return redirect(url_for('ulogin'))
@app.route('/stop_auction/<item_id>', methods=['POST'])
def stop_auction(item_id):
    if session.get('seller'):
        seller_username = session.get('seller')  # Assuming you store the logged-in seller's username in the session

        # Check if the user is the seller of the item
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT seller_username FROM auction_data WHERE item_id = %s', [item_id])
        seller_data = cursor.fetchone()
        cursor.close()

        if seller_data and seller_data[0] == seller_username:
            # Update the auction status to 'Completed'
            cursor = mysql.connection.cursor()
            cursor.execute('UPDATE auction_data SET status = "Completed" WHERE item_id = %s', [item_id])
            cursor.execute('UPDATE items SET status = "Completed" WHERE item_id = %s', [item_id])

            # Fetch all bids for this item
            cursor.execute('SELECT bidder_username, bid_amount FROM placed_bids WHERE item_id = %s ORDER BY bid_amount DESC', [item_id])
            all_bids_data = cursor.fetchall()
            cursor.close()

            if all_bids_data:
                winning_bidder_username, winning_bid_amount = all_bids_data[0]  # First row has the highest bid
                cursor = mysql.connection.cursor()
                cursor.execute('UPDATE auction_data SET winning_bidder_username = %s, winning_bid_amount = %s WHERE item_id = %s', (winning_bidder_username, winning_bid_amount, item_id))
                mysql.connection.commit()
                cursor.close()

                flash(f'Auction for item {item_id} stopped successfully. Winner: {winning_bidder_username}, Winning Bid: {winning_bid_amount}')
            else:
                flash('No bids placed for this item yet.')

            return redirect(url_for('userviewitems'))
        else:
            flash('You are not authorized to stop this auction.')
            return redirect(url_for('userviewitems'))
    else:
        return redirect(url_for('slogin'))

#===================user view the items
@app.route('/userviewitems', methods=['GET', 'POST'])
def userviewitems():
   
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM items ')
    items = cursor.fetchall()
    return render_template('userviewitems.html', items=items)
@app.route('/userbiditems')
def userbiditems():
    if session.get('user'):
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT item_id FROM placed_bids WHERE bidder_username = %s', [session['user']])
        item_id = cursor.fetchone()

        cursor.execute('SELECT * FROM items WHERE item_id = %s', [item_id])
        items = cursor.fetchall()

        cursor.execute('''
            SELECT ad.item_id, ad.seller_username, ad.starting_price, ad.auction_start, ad.auction_end, ad.status,
                   ad.winning_bidder_username, ad.winning_bid_amount, pb.bid_amount, pb.bid_time
            FROM auction_data ad
            JOIN placed_bids pb ON ad.auction_id = pb.auction_id
            WHERE pb.bidder_username = %s
            ''', [session['user']])
        userbids = cursor.fetchall()

        #print("==================================", userbids)
        return render_template('userbiditems.html', userbids=userbids, items=items)

    else:
        return redirect(url_for('ulogin'))
#==========================user payements
'''@app.route('/pay/<itemid>',methods=['GET','POST'])
def pay(itemid):
    if session.get('user'):
        cursor=mysql.connection.cursor()
        cursor=cursor.execute('select count(*) from auction_data where winning_bidder_username=%s',[session['user']])
        count=cursor.fetchone()[0]
        if count==1:
            cursor.execute('select winning_bid_amount from auction_data where winning_bidder_username=%s',[session['user']])
            total=cursor.fetchone()
            cursor.execute('select item_name from items where item_id=%s',[itemid])
            iname=cursor.fetchone()
            checkout_session=stripe.checkout.Session.create(
                success_url=url_for('success',itemid=itemid,name=iname,total=total,_external=True),
                line_items=[
                    {
                        'price_data': {
                            'product_data': {
                                'name': iname,
                            },
                            'unit_amount': total*100,
                            'currency': 'inr',
                        },
                       
                    },
                    ],
                mode="payment",)
            return redirect(checkout_session.url)
    
                     
        else:
            flash('oops you are not the bid winner, so you can not  purchase the item')
            return redirect(url_for('/userviewitems'))
    else:
        return redirect(url_for('ulogin')) '''
@app.route('/pay/<itemid>', methods=['GET', 'POST'])
def pay(itemid):
    if session.get('user'):
        cursor = mysql.connection.cursor()
        cursor.execute('select count(*) from auction_data where winning_bidder_username=%s', [session['user']])
        count = cursor.fetchone()[0]  # Fetch the count value correctly

        if count == 1:
            cursor.execute('select winning_bid_amount from auction_data where winning_bidder_username=%s', [session['user']])
            total = cursor.fetchone()[0]  # Fetch the total value correctly

            cursor.execute('select item_name from items where item_id=%s', [itemid])
            iname = cursor.fetchone()[0]  # Fetch the item name correctly

            checkout_session = stripe.checkout.Session.create(
                success_url=url_for('success', itemid=itemid, name=iname, total=total, _external=True),
                line_items=[
                    {
                        'price_data': {
                            'product_data': {
                                'name': iname,
                            },
                            'unit_amount': total * 100,  # Multiply by 100 to convert to cents
                            'currency': 'inr',
                        },
                        'quantity': 1,
                    },
                ],
                mode="payment",
            )
            return redirect(checkout_session.url)

        else:
            flash('Oops! You are not the bid winner, so you cannot purchase the item.')
            return redirect(url_for('userviewitems'))
    else:
        return redirect(url_for('ulogin'))
    
@app.route('/orders')
def orders():
    if session.get('user'):
        cursor=mysql.connection.cursor()
        cursor.execute('select * from orders where user_name=%s',[session['user']])
       
        orders=cursor.fetchall()
        print('========================================',orders)
        cursor.execute('select item_id from orders where  user_name=%s',[session['user']])
        itemid=cursor.fetchone()
        cursor.execute('select * from items where item_id=%s',[itemid])
       
        items=cursor.fetchall()
        print('========================================',items)

        
        return render_template('orders.html',orders=orders,items=items)
    return redirect(url_for('ulogin'))
@app.route('/success/<itemid>/<name>/<total>')
def success(itemid,name,total):
    if session.get('user'):
        cursor=mysql.connection.cursor()
        cursor.execute('SELECT item_id from auction_data where winning_bidder_username=%s',[session['user']])
        item_id=cursor.fetchone()
        cursor.execute('SELECT winning_bid_amount from auction_data where winning_bidder_username=%s',[session['user']])
        winning_bid_amount=cursor.fetchone()
        cursor.execute('select item_name from items where item_id=%s',[item_id])
        item_name=cursor.fetchone()
        cursor.execute('select dis from items where item_id=%s',[item_id])
        dis=cursor.fetchone()
        cursor.execute('insert into orders(item_id,item_name,amount,user_name,item_description) values(%s,%s,%s,%s,%s)',[item_id,item_name,winning_bid_amount,session.get('user'),dis])
        mysql.connection.commit()
        return redirect(url_for('orders'))
    return redirect(url_for('login'))
      







@app.route('/add_to_favourites/<item_id>/<username>/<item_name>/<description>/<category>/<starting_price>/<status>/<iid>')
def add_to_favourites(item_id,username,item_name,description,category,starting_price,status,iid):
    #print(session)
    #print('==========================',item_id)
    if session.get('user'):
        #print(song_id,name,pic,audio,album)
        #print('-------------------',session[session['user']])
        if item_id not in session.get(session['user'], {}): 
            session.get(session['user'], {})[item_id] = [username,item_name,description, category,starting_price,status,iid]
            session.modified = True
            #print(session[session.get('user')])
            flash(f'{item_name} added to favourites')
            return redirect(url_for('viewcart'))
        else:
            flash(f'{item_name} is already in favorites')
        return redirect(url_for('viewcart'))
    return redirect(url_for('ulogin'))
@app.route('/viewcart')
def viewcart():
    if 'user' not in session:
        return redirect(url_for('ulogin'))
   
    items = session.get(session['user'], {})
    #print('===================================',items)
    if not items:
        return 'No added favourite songs'
    return render_template('favourites.html', items=items)
@app.route('/remove_cart/<item_id>')
def remove_cart(item_id):
    if session.get('user'):
        session[session.get('user')].pop(item_id)
        return redirect(url_for('viewcart'))
    return redirect(url_for('ulogin'))

#============================== Seller registration
@app.route('/slogin',methods=['GET','POST'])
def slogin():
    if session.get('seller'):
        return redirect(url_for('seller_dashboard'))
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        cursor=mysql.connection.cursor()
        cursor.execute('SELECT count(*) from sellers where seller_username=%s and password=%s',[username,password])
        count=cursor.fetchone()[0]
        if count==1:
            session['seller']=username
            return redirect(url_for('seller_dashboard'))
        else:
            flash('Invalid username or password')
            return render_template('slogin.html')
    return render_template('slogin.html')

@app.route('/sregistration',methods=['GET','POST'])
def sregistration():
    if request.method=='POST':
        name=request.form['seller_name']
        email=request.form['email']
        phone=request.form['phone_number']
        location=request.form['location']
        password=request.form['password']
        
        
        
        cursor=mysql.connection.cursor()
        cursor.execute('select count(*) from sellers where seller_username=%s',[name])
        count=cursor.fetchone()[0]
        cursor.execute('select count(*) from sellers where email=%s',[email])
        count1=cursor.fetchone()[0]
        cursor.close()
        if count==1:
            flash('username already in use')
            return render_template('sregister.html')
        elif count1==1:
            flash('Email already in use')
            return render_template('sregister.html')
        
        data1={'name':name,'email':email,'phone':phone,'location':location,'password':password}
        subject='Email Confirmation'
        body=f"Thanks for signing up\n\nfollow this link for further steps-{url_for('sconfirm',token=token1(data1,salt),_external=True)}"
        sendmail(to=email,subject=subject,body=body)
        flash('Confirmation link sent to mail')
        return redirect(url_for('sregistration'))
    
    return render_template('sregister.html')
@app.route('/sconfirm/<token>')
def sconfirm(token):
    try:
        serializer=URLSafeTimedSerializer(secret_key)
        data=serializer.loads(token,salt=salt,max_age=180)
    except Exception as e:
      
        return 'Link Expired register again'
    else:
        cursor=mysql.connection.cursor()
        id1=data['name']
        cursor.execute('select count(*) from sellers where seller_username=%s',[id1])
        count=cursor.fetchone()[0]
        if count==1:
            cursor.close()
            flash('You are already registerterd!')
            return redirect(url_for('seller_dashboard'))
        else:
            cursor.execute('INSERT INTO sellers (seller_username, email, phone_number,location,password) VALUES (%s, %s, %s, %s, %s)', [data['name'], data['email'], data['phone'], data['location'],data['password']])

            mysql.connection.commit()
            cursor.close()
            flash('Details registered!')
            return redirect(url_for('slogin'))
@app.route('/sforget',methods=['GET','POST'])
def sforgot():
    if request.method=='POST':
        id1=request.form['id1']
        cursor=mysql.connection.cursor()
        cursor.execute('select count(*) from sellers where seller_username=%s',[id1])
        count=cursor.fetchone()[0]
        cursor.close()
        if count==1:
            cursor=mysql.connection.cursor()

            cursor.execute('SELECT email from sellers where email=%s',[id1])
            email=cursor.fetchone()[0]
            cursor.close()
            subject='Forget Password'
            confirm_link=url_for('sreset',token=token1(id1,salt=salt2),_external=True)
            body=f"Use this link to reset your password-\n\n{confirm_link}"
            sendmail(to=email,body=body,subject=subject)
            flash('Reset link sent check your email')
            return redirect(url_for('blogin'))
        else:
            flash('Invalid email id')
            return render_template('forgot.html')
    return render_template('forgot.html')


@app.route('/sreset/<token>',methods=['GET','POST'])
def sreset(token):
    try:
        serializer=URLSafeTimedSerializer(secret_key)
        id1=serializer.loads(token,salt=salt2,max_age=180)
    except:
        abort(404,'Link Expired')
    else:
        if request.method=='POST':
            newpassword=request.form['npassword']
            confirmpassword=request.form['cpassword']
            if newpassword==confirmpassword:
                cursor=mysql.connection.cursor()
                cursor.execute('update sellers set password=%s seller_username=%s',[newpassword,id1])
                mysql.connection.commit()
                flash('Reset Successful')
                return redirect(url_for('slogin'))
            else:
                flash('Passwords mismatched')
                return render_template('newpassword.html')
        return render_template('newpassword.html')
@app.route('/slogout')
def slogout():
    if session.get('seller'):
        session.pop('seller')
        flash('Successfully loged out')
        return redirect(url_for('slogin'))
    else:
        return redirect(url_for('slogin'))
@app.route('/sellers_dashboard')
def seller_dashboard():
    if session.get('seller'):
        return render_template('sellersdashboard.html')
    else:
        return redirect(url_for('slogin'))

#================================sellers can add the items
@app.route('/additems',methods=['GET','POST'])
def additems():
    if session.get('seller'):
        id1_pic=genotp()
        if request.method=="POST":
            itemname=request.form['item_name']
            dis=request.form['dis']
            category=request.form['category']
            starting_price=request.form['starting_price']
            image = request.files['image']
            filename=id1_pic+'.jpg'
            cursor=mysql.connection.cursor()
            cursor.execute('INSERT INTO  items (seller_username,item_name,dis,category,starting_price,img_id) VALUES (%s, %s, %s, %s, %s, %s)',[session['seller'],itemname,dis,category,starting_price,id1_pic] )
            mysql.connection.commit()
            cursor.close()
            path = os.path.join(app.root_path,'static')
            image.save(os.path.join(path, filename))
            mysql.connection.commit()
            flash('items added successfully')
            return redirect(url_for('seller_dashboard'))
        return render_template('additems.html')
    else:
        return redirect(url_for('slogin'))
#===========================view items
@app.route('/viewitems', methods=['GET', 'POST'])
def viewitems():
    if session.get('seller'):
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM items WHERE seller_username=%s', [session['seller']])
        items = cursor.fetchall()
        return render_template('viewitems.html', items=items)
    else:
        return redirect(url_for('slogin'))
#=====================update item
@app.route('/update_item/<itemid>',methods=['GET','POST'])
def update_item(itemid):
    if session.get('seller'):
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM items WHERE seller_username=%s', [session['seller']])
        items = cursor.fetchall()

        if request.method=="POST":
            name=request.form['item_name']
            dis=request.form['dis']
            category=request.form['category']
            price=request.form['starting_price']
            cursor=mysql.connection.cursor()
            cursor.execute(' UPDATE items SET item_name = %s, dis = %s, category = %s, starting_price = %s WHERE item_id = %s',[name,dis,category,price,itemid])
            mysql.connection.commit()
            flash('Item updated successfully')
            return redirect(url_for('viewitems'))
            
        return render_template('updateitems.html',items=items)
        
    
    else:
        return redirect(url_for('slogin'))
@app.route('/deleteitem/<itemid>',methods=['GET','POST'])
def deleteitem(itemid):
    if session.get('seller'):
        if request.method=="POST":
            cursor=mysql.connection.cursor()
            cursor.execute('delte from items where item_id=%s',[itemid])
            mysql.connection.commit()
            cursor.close()
            flash('item deletd sucessfully')
            return redirect(url_for('viewitems'))
    return redirect(url_for('slogin'))
#===============================view bid items
@app.route('/viewbiditems')
def viewbiditems():
    if session.get('seller'):
        cursor=mysql.connection.cursor()
        cursor.execute('select * from auction_data where seller_username=%s',[session['seller'],])
        details=cursor.fetchall()
        cursor.execute('select item_id from auction_data where seller_username=%s',[session['seller']])
        itemid=cursor.fetchone()
        print("================================",itemid)
        cursor.execute('select * from items where item_id=%s',[itemid,])
        items=cursor.fetchall()
        print("==============================",items)
        return render_template('adminviewauction.html',details=details,items=items)
    return redirect(url_for('slogin'))

@app.route('/ordersdetails')
def ordersdetails():
    if session.get('seller'):
        cursor=mysql.connection.cursor()
        cursor.execute('select item_id from items where seller_username=%s',[session['seller']])
        itemid=cursor.fetchone()
        cursor.execute('select * from orders where item_id=%s',[itemid])
        data=cursor.fetchall()
        cursor.execute('select * from items where item_id=%s',[itemid])
        items=cursor.fetchall()
        return render_template('vieworders.html',orders=data,items=items)
    return redirect(url_for('slogin'))
app.run(use_reloader=True,debug=True)
