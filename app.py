from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'ganti-rahasia-ini-pake-string-random-panjang-bro'  # WAJIB ganti!
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'     # atau db.sqlite3 kalau mau ganti
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'png', 'jpg', 'jpeg', 'docx'}

db = SQLAlchemy(app)

# Model Pesanan (paste ini kalau belum ada class model)
class Pesanan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    kontak = db.Column(db.String(100))  # email atau no HP
    jenis_print = db.Column(db.String(50))
    ukuran = db.Column(db.String(20))
    jumlah = db.Column(db.Integer)
    file_path = db.Column(db.String(255))
    status = db.Column(db.String(20), default='pending')  # pending, selesai, batal
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Buat tabel kalau belum ada (paste ini di bawah model)
with app.app_context():
    db.create_all()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/', methods=['GET', 'POST'])
def index():
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

            flash('Pesanan berhasil dikirim! Tunggu ya, admin lagi cek.', 'success')
        else:
            flash('File ga valid atau kosong bro.', 'danger')

        return redirect(url_for('index'))

    return render_template('user/index.html')

@app.route('/admin')
def admin():
    pesanan_list = Pesanan.query.order_by(Pesanan.created_at.desc()).all()
    return render_template('admin/dashboard.html', pesanan=pesanan_list)

@app.route('/update/<int:id>', methods=['POST'])
def update(id):
    pesanan = Pesanan.query.get_or_404(id)
    pesanan.status = request.form['status']
    db.session.commit()
    flash('Status updated!', 'info')
    return redirect(url_for('admin'))

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)