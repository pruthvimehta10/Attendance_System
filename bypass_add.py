import pg8000.dbapi
from werkzeug.security import generate_password_hash

try:
    print("Connecting directly to Railway database...")
    conn = pg8000.dbapi.connect(
        user="postgres", 
        password="JuCwuCcxVNTrqnHCcRfEryJvlCIHwsJr", 
        host="crossover.proxy.rlwy.net", 
        port=32181, 
        database="railway"
    )
    cursor = conn.cursor()
    
    # Pruthvi's requested credentials
    name = "Pruthvi Mehta"
    email = "pruthvi.mehta@somaiya.edu"
    password_hash = generate_password_hash("Password10")
    role = "student"
    
    # Check if user already exists
    cursor.execute("SELECT id FROM public.user WHERE email = %s", (email,))
    if cursor.fetchone():
        print(f"User {email} already exists!")
    else:
        print(f"Inserting new user {email}...")
        cursor.execute(
            "INSERT INTO public.user (name, email, password_hash, role) VALUES (%s, %s, %s, %s)", 
            (name, email, password_hash, role)
        )
        conn.commit()
        print("🎉 Success! Pruthvi Mehta added directly to the database!")
    
    conn.close()
except Exception as e:
    print(f"Error: {e}")
