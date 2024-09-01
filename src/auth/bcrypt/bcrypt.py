import bcrypt

def create_hash_password(password : str) -> str :
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt() 
    hash_password = bcrypt.hashpw(pwd_bytes,salt)
    return hash_password.decode('utf-8')

def verify_hash_password(password : str,hashPassowrd : str) -> bool :
    plain_password_byte = password.encode('utf-8')
    hash_password_byte = hashPassowrd.encode('utf-8')
    print(plain_password_byte,hash_password_byte)
    isPassword = bcrypt.checkpw(plain_password_byte,hash_password_byte)
    return isPassword