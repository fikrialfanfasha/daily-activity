from flask import Flask, render_template, request, redirect, url_for, session
import csv
import os
from datetime import datetime
import locale

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Ganti dengan kunci rahasia Anda

# Mengatur locale ke bahasa Indonesia
locale.setlocale(locale.LC_TIME, 'id_ID.UTF-8')

# Nama siswa
siswa = ["kenryu", "dery", "malik", "akas", "hamim", 
          "melani", "silvi", "nisa", "naila", "kheisya", 
          "nova", "ade"]

# Memastikan direktori data ada
os.makedirs('data', exist_ok=True)

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Validasi username dan password
        with open('users.csv', 'r') as user_file:
            reader = csv.DictReader(user_file)
            for row in reader:
                if row['username'] == username and row['password'] == password:
                    session['username'] = username
                    return redirect(url_for('index'))
            return render_template('login.html', error='Nama pengguna atau kata sandi salah')
    return render_template('login.html')

@app.route('/index')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    siswa_file = f'data/{session["username"]}.csv'
    daily_work = []
    today_filled = False  # Status apakah pekerjaan sudah diisi untuk hari ini
    
    today = datetime.now().strftime('%Y-%m-%d')
    formatted_today = datetime.now().strftime('%A,  %d  %B  %Y')  # Format tanggal untuk ditampilkan
    
    if os.path.exists(siswa_file):
        with open(siswa_file, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    # Mengubah format tanggal
                    row_date = datetime.strptime(row['Tanggal'], '%Y-%m-%d').strftime('%A - %d - %B - %Y')
                    daily_work.append((row_date, row['Pekerjaan']))
                    
                    # Cek apakah pekerjaan sudah diisi untuk hari ini
                    if row['Tanggal'] == today:
                        today_filled = True
                except ValueError:
                    # Jika format tanggal tidak valid, skip
                    print(f"Tanggal tidak valid ditemukan: {row['Tanggal']}")
                    continue
    
    return render_template('index.html', daily_work=daily_work, today_filled=today_filled, formatted_today=formatted_today)


@app.route('/submit', methods=['POST'])
def submit():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    pekerjaan = request.form['pekerjaan']
    tanggal = datetime.now().strftime('%Y-%m-%d')  # Format tanggal

    # Menyimpan pekerjaan ke CSV siswa yang sesuai
    siswa_file = f'data/{session["username"]}.csv'
    
    with open(siswa_file, 'a', newline='') as csvfile:
        fieldnames = ['Tanggal', 'Pekerjaan']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if os.stat(siswa_file).st_size == 0:  # Cek jika file kosong
            writer.writeheader()
        writer.writerow({'Tanggal': tanggal, 'Pekerjaan': pekerjaan})

    # Menambahkan pesan ke sesi
    session['status_message'] = 'Hari ini kamu sudah mengisi kegiatan!'
    return redirect(url_for('index'))

@app.route('/view')
def view_work():
    if 'username' not in session:
        return redirect(url_for('login'))

    # Nama file CSV siswa yang sesuai
    siswa_file = f'data/{session["username"]}.csv'
    
    # Membaca data pekerjaan dari file CSV
    daily_work = []
    if os.path.exists(siswa_file):
        with open(siswa_file, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    # Mengubah format tanggal
                    formatted_date = datetime.strptime(row['Tanggal'], '%Y-%m-%d').strftime('%A , %d  %B  %Y')
                    daily_work.append((formatted_date, row['Pekerjaan']))
                except ValueError:
                    # Jika format tanggal tidak valid, skip
                    print(f"Tanggal tidak valid ditemukan: {row['Tanggal']}")
                    continue

    return render_template('view.html', daily_work=daily_work)


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
