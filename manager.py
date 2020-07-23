import sqlite3
from hashlib import sha256
import secrets
import string
from cryptography.fernet import Fernet
import os

ADMIN_PASSWORD = '789'

login = input('Enter the password:\n')

while ADMIN_PASSWORD != login:
    print('Wrong password.')
    login = input('Enter the password:\n')
    if login == 'quit':
        break


# Connect to database
connection = sqlite3.connect('safe.db')
cursor = connection.cursor()


# Encrypts the password to be stored
def encrypt_password(password):
    key = Fernet.generate_key()
    f = Fernet(key)
    encrypted_pass = f.encrypt(password.encode())
    return encrypted_pass, key
    

# Decrypts the password that was stored
def decrypt_password(key, encrypted_pass):
    f = Fernet(key)
    decrypted_pass = f.decrypt(encrypted_pass)
    return decrypted_pass


# Store service, username, password given by the user in the database
def store_password(service, username, password):
    if not service or not username or not password:
        print('Error, please try again')
    else:
        password, pass_key = encrypt_password(password)
        cursor.execute('''
            INSERT INTO Passwords (service, username, password, pass_key) VALUES (?, ?, ?, ?)
        ''', (service, username, password, pass_key))
        connection.commit()
        print(f'Your password for "{service}" is now safely stored')
        print('')

# Create random password for the user
def create_random_password():
    alphabet = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(alphabet) for i in range(16))
    print('')
    print("Here's the password generate for you: "  + password)
    print('')
    question = input('Do you want to store it? (Y/N)\n')
    if question == 'Y':
        service = input('What is the name of the service?\n')
        username = input('What is the username you want to user?\n')
        store_password(service, username, password)
    else:
        return 'continue'

# Retrives password based on the service
def get_password(service):
    result = cursor.execute('''
        SELECT * FROM Passwords WHERE service=?
    ''', (service, )).fetchone()

    if result is None:
        print('')
        print(f'No password is stored for "{service}""')
    else:  
        password = decrypt_password(result[4], result[3])
        print('-' * 50)
        print('   Service: ' + result[1])
        print('   Username: ' + result[2])
        print('   Password: ' + password.decode())
        print('-' * 50)

# Retrives all passwords from database
def get_all_passwords():
    results = cursor.execute('SELECT * FROM Passwords ORDER BY Service DESC').fetchall()

    if not len(results) > 0:
        print('')
        print('You have no passwords stored.')
    else:
        for row in results:
            password = decrypt_password(row[4], row[3])
            print('-' * 50)
            print('   Service: ' + row[1])
            print('   Username: ' + row[2])
            print('   Password: ' + password.decode())
            print('-' * 50)

# Deletes multiple passwords from database based on the user choice
def delete_password():
    nums = '1234567890'
    print('')
    n_delets = input('How many passwords do you want to delete?\nInput a number or if you want to delete all just write "all".\n')
    if n_delets == 'all':
        cursor.execute(f'''
                DELETE FROM Passwords
            ''')
        connection.commit()
        print('')
        print('All passwords have been deleted')
    elif n_delets in nums and n_delets != '':
        n_delets = int(n_delets)
        for _ in range(n_delets):
            service = input('What is the service for which you want to delete the password?\n')
            cursor.execute(f'''
                DELETE FROM Passwords WHERE service=?
            ''', (service, ))
            connection.commit()
            print(f'Password for "{service}" deleted')
    else:
        print('Invalid input. Please try again')
    


# Ask if the user wants to keep using the program
def question_continue():
    question = input('Do you want to keep using the program? (Y/N) ')
    if question == 'Y':
        return 'continue'
    elif question == 'N':
        return 'break'
    else:
        print('Unexpected input, please try again with Y or N')
        question_continue()



# Main program
if ADMIN_PASSWORD == login:
    # Create new table in database
    try:
        cursor.execute('''
            CREATE TABLE Passwords (id INTEGER PRIMARY KEY, service TEXT, username TEXT, password TEXT, pass_key TEXT)
        ''')
    except:
        print('Your safe database is ready. What do you want to do?\n')

    while True:
        print('')
        print('     ' + '-' * 68)
        print('')
        print('Actions:')
        print('''
            1. Store a password
            2. Let the program create a password for you and then store it
            3. Get the password you need
            4. Get all the passwords
            5. Delete one or more passwords
            6. Create/update file with all passwords (not crypted)
            7. Delete file with all passwords
            8. Exit
        ''')
        print('     ' + '-' * 68)
        print('')
        inp = input('What do you want to do: ')

        if inp == '1':
            # Get all user inputs
            service = input('What is the name of the service?\n')
            username = input('What is the username you used to signup?\n')
            password = input('What is the password for that account?\n')

            store_password(service, username, password)
            
            if question_continue() == 'break':
                break
        elif inp == '2':
            create_random_password()
            print('')
            if question_continue() == 'break':
                break
        elif inp == '3':
            service = input('What is the service for which you need the password?\n')
            get_password(service)
            print('')
            if question_continue() == 'break':
                break
        elif inp == '4':
            get_all_passwords()
            print('')
            if question_continue() == 'break':
                break
        elif inp == '5':
            delete_password()
            print('')
            if question_continue() == 'break':
                break
        elif inp == '6':
            data = cursor.execute('SELECT * FROM Passwords ORDER BY Service DESC').fetchall()

            if not len(data) > 0:
                print('')
                print('You have no passwords stored.\n')
                continue
            
            with open('passwords.txt', 'w', encoding='utf-8') as f:
                f.write('These are the passwords you stored:\n\n\n')
                for row in data:
                    password = decrypt_password(row[4], row[3])
                    f.write('   Service: ' + row[1] + '\n')
                    f.write('   Username: ' + row[2] + '\n')
                    f.write('   Password: ' + password.decode() + '\n')
                    f.write('-' * 50 + '\n')
            print('')
            print('File with name "passwords.txt" was just created/updated in this script directory')
            print('')

            if question_continue() == 'break':
                break
        elif inp == '7':
            if os.path.exists("passwords.txt"):
                os.remove("passwords.txt")
                print('')
                print('"passwords.txt" file has been deleted\n')
            else:
                print('')
                print("The file does not exist\n")
                
            if question_continue() == 'break':
                break
        elif inp == '8':
            break
        else:
            continue
