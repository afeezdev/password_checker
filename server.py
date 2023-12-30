from flask import Flask, render_template, url_for, request, redirect
import requests
import hashlib
# import sys


app = Flask(__name__)

@app.route("/")
def my_home():
    return render_template('index.html')

@app.route('/<string:page_name>')
def html_page(page_name):
    return render_template(page_name)

def request_api_data(query_char):
    url = 'https://api.pwnedpasswords.com/range/' + query_char
    res = requests.get(url)
    if res.status_code != 200:
        raise RuntimeError(f'Error fetching: {res.status_code}, check the api and try again')
    return res

def get_password_leaks_count(hashes, hash_to_check):
    hashes = (line.split(':') for line in hashes.text.splitlines())
    for h, count in hashes:
        if h == hash_to_check:
            return count
    return 0

def pwned_api_check(password):
    sha1password = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    first5_char, tail = sha1password[:5], sha1password[5:]
    response = request_api_data(first5_char)  
    return get_password_leaks_count(response, tail )
    
@app.route('/submit_form', methods=['POST', 'GET'])
def submit_form():
    if request.method == 'POST':
        try:
            data = request.form.to_dict()
            count = pwned_api_check(data["password"])
            password_length = len(data['password'])
            displayed_password = '*' * password_length 
            if (data["password"]) != '':
                if int(count) > 0 :
                    return render_template(
                        '/contact.html', 
                        counts= f'Your password "{displayed_password}" was found {count} times....you should probably change your password',
                        color = "red")
                else:
                    return render_template(
                        '/contact.html', 
                        counts= f'Your pasword "{displayed_password}" was NOT found. carry on!',
                        color= "green")
            else:
                return render_template('/contact.html', counts= f'Ooop! you can not check for empty password', color="#d6e020")
        except:
            return 'something is wrong, try again'
    else:
        return 'something went wrong, try again'
    
    
