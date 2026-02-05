from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'rahasia-super-panjang-ubah-ini-pake-os-urandom-bro'  
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'png', 'jpg', 'jpeg', 'docx'}

db = SQLAlchemy(app)

class Pesanan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    kontak = db.Column(db.String(100))
    jenis_print = db.Column(db.String(50))
    ukuran = db.Column(db.String(20))
    jumlah = db.Column(db.Integer)
    file_path = db.Column(db.String(255))
    status = db.Column(db.String(20), default='pending')  
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def home():
    return redirect(url_for('produk'))

@app.route('/produk')
def produk():
    return render_template('produk.html')

@app.route('/pesan', methods=['GET', 'POST'])
def pesan():
    if request.method == 'POST':
        nama = request.form.get('nama')
        kontak = request.form.get('kontak')
        jenis = request.form.get('jenis_print')
        ukuran = request.form.get('ukuran')
        jumlah = request.form.get('jumlah', type=int)

        file = request.files.get('file')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            pesanan = Pesanan(nama=nama, kontak=kontak, jenis_print=jenis,
                              ukuran=ukuran, jumlah=jumlah, file_path=file_path)
            db.session.add(pesanan)
            db.session.commit()

            flash('Pesanan berhasil dikirim! Tunggu admin cek ya.', 'success')
        else:
            flash('File tidak valid atau kosong.', 'danger')

        return redirect(url_for('pesan'))  

    return render_template('user/index.html')  

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == 'admin' and password == 'unitproduksi123':
            session['admin_logged_in'] = True
            session['admin_user'] = username
            flash('Login berhasil! Selamat datang Admin.', 'success')
            return redirect(url_for('admin'))
        else:
            flash('Username atau password salah.', 'danger')

    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_user', None)
    flash('Anda telah logout.', 'info')
    return redirect(url_for('admin_login'))

@app.before_request
def require_admin_login():
    if request.path.startswith('/admin') and request.path != '/admin/login':
        if not session.get('admin_logged_in'):
            flash('Silakan login terlebih dahulu sebagai admin.', 'warning')
            return redirect(url_for('admin_login'))

@app.route('/admin')
def admin():
    pesanan_list = Pesanan.query.order_by(Pesanan.created_at.desc()).all()
    return render_template('admin/dashboard.html', pesanan=pesanan_list)

@app.route('/update/<int:id>', methods=['POST'])
def update(id):
    pesanan = Pesanan.query.get_or_404(id)
    pesanan.status = request.form['status']
    db.session.commit()
    flash('Status berhasil diupdate!', 'info')
    return redirect(url_for('admin'))

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)