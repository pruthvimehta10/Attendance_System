import pg8000.dbapi
from werkzeug.security import generate_password_hash

data = """meet@somaiya.edu - Meet33
jeet@somaiya.edu - Jeet34
pruthvi@somaiya.edu - Pruthvi35
nileshkumar@somaiya.edu - Nileshkumar36
yash@somaiya.edu - Yash37
dev@somaiya.edu - Dev38
soham@somaiya.edu - Soham39
atharva@somaiya.edu - Atharva40
isha@somaiya.edu - Isha41
kushal@somaiya.edu - Kushal42
siddhant@somaiya.edu - Siddhant43
daksh@somaiya.edu - Daksh44
krish@somaiya.edu - Krish45
yashodhan@somaiya.edu - Yashodhan46
darshan@somaiya.edu - Darshan47"""

try:
    print("Connecting to Railway database...")
    conn = pg8000.dbapi.connect(
        user="postgres", 
        password="JuCwuCcxVNTrqnHCcRfEryJvlCIHwsJr", 
        host="crossover.proxy.rlwy.net", 
        port=32181, 
        database="railway"
    )
    cursor = conn.cursor()
    
    for line in data.strip().split('\n'):
        line = line.strip()
        if not line: continue
        email, password = line.split(' - ')
        email = email.strip()
        password = password.strip()
        name = email.split('@')[0].capitalize()
        role = 'student'
        password_hash = generate_password_hash(password)
        
        cursor.execute("SELECT id FROM public.\"user\" WHERE email = %s", (email,))
        if cursor.fetchone():
            print(f"User {email} already exists!")
        else:
            print(f"Inserting new user {email}...")
            cursor.execute(
                'INSERT INTO public."user" (name, email, password_hash, role) VALUES (%s, %s, %s, %s)', 
                (name, email, password_hash, role)
            )
            conn.commit()
            print(f"Added {email} successfully!")
            
    conn.close()
    print("Done!")
except Exception as e:
    print(f"Error: {e}")
