from quick_add_user import add_user

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

for line in data.strip().split('\n'):
    line = line.strip()
    if not line:
        continue
    email, password = line.split(' - ')
    email = email.strip()
    password = password.strip()
    # Using the name portion of the email capitalized
    name = email.split('@')[0].capitalize()
    add_user(name=name, email=email, password=password, role='student')
