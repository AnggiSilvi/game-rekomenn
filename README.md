
# 🎮 Game Recommender System

Sistem rekomendasi game berbasis web yang dibangun dengan Django, menggunakan machine learning untuk memberikan rekomendasi game yang dipersonalisasi berdasarkan preferensi pengguna.

## ✨ Fitur Utama

### 🔍 **Pencarian & Eksplorasi**
- Pencarian game dengan auto-suggestions
- Filter berdasarkan genre, platform, rating ESRB, dan rating pengguna
- Tampilan grid yang responsif dengan gambar konsisten

### 🤖 **Sistem Rekomendasi**
- **Hybrid Recommendation System** dengan 3 metode:
  - **Content-Based Filtering** - Berdasarkan genre dan karakteristik game
  - **K-Means Clustering** - Pengelompokan game berdasarkan kesamaan fitur
  - **Popularity-Based** - Berdasarkan rating dan popularitas
- Machine learning untuk rekomendasi personal yang akurat

### 📱 **User Interface**
- Dark theme yang modern dan elegan
- Responsive design untuk mobile, tablet, dan desktop
- Navigasi yang intuitif dan user-friendly
- Gambar game dengan ukuran konsisten (150px × 200px)

### 👤 **Manajemen Pengguna**
- Sistem autentikasi (login/register)
- Bookmark game favorit
- Rating dan review game
- Profil pengguna personal

## 🛠️ Teknologi yang Digunakan

### Backend
- **Django 4.x** - Web framework
- **Python 3.8+** - Programming language
- **SQLite** - Database
- **Pandas** - Data manipulation
- **Scikit-learn** - Machine learning
- **Pickle** - Model serialization

### Frontend
- **HTML5** - Markup
- **CSS3** - Styling dengan CSS Variables
- **JavaScript** - Interaktivitas
- **Font Awesome** - Icons
- **Google Fonts** - Typography (Inter)

### Machine Learning
- **Content-Based Filtering** - Rekomendasi berdasarkan konten
- **K-Means Clustering** - Pengelompokan game berdasarkan fitur
- **Cosine Similarity** - Perhitungan kemiripan
- **TF-IDF Vectorization** - Text processing

## 📦 Instalasi

### Prerequisites
- Python 3.8 atau lebih tinggi
- pip (Python package manager)
- Git

### Langkah Instalasi

1. **Clone repository**
```bash
git clone https://github.com/AnggiSilvi/game-rekomenn.git
cd game-rekomenn
```

2. **Buat virtual environment**
```bash
python -m venv venv
```

3. **Aktivasi virtual environment**
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

4. **Install dependencies**
```bash
pip install -r requirements.txt
```

5. **Setup database**
```bash
python manage.py migrate
```

6. **Import data games**
```bash
python manage.py import_csv
```

7. **Buat superuser (opsional)**
```bash
python manage.py createsuperuser
```

8. **Jalankan server**
```bash
python manage.py runserver
```

9. **Akses aplikasi**
Buka browser dan kunjungi: `http://localhost:8000`

## 📁 Struktur Proyek

```
game-rekomenn/
├── config/                 # Django settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── games/                  # Main Django app
│   ├── models.py          # Database models
│   ├── views.py           # View controllers
│   ├── urls.py            # URL routing
│   ├── recommendation.py   # ML recommendation engine
│   ├── templates/         # HTML templates
│   ├── static/           # CSS, JS, images
│   └── management/       # Custom commands
├── data/
│   ├── games.csv         # Game dataset
│   ├── games_with_images.csv
│   └── df_clustering.csv  # K-Means clustering data
├── models/
│   ├── rekomendasi_sistem.pkl  # Content-based model
│   └── model_kmeans.pkl       # K-Means clustering model
├── requirements.txt      # Python dependencies
├── manage.py            # Django management script
└── README.md           # Project documentation
```

## 🎯 Cara Penggunaan

### 1. **Eksplorasi Game**
- Kunjungi halaman utama untuk melihat game populer
- Gunakan menu navigasi untuk browse berdasarkan kategori
- Cari game spesifik menggunakan search bar

### 2. **Mendapatkan Rekomendasi**
- Daftar/login ke akun Anda
- Rate beberapa game yang sudah Anda mainkan
- Sistem akan memberikan rekomendasi personal di dashboard

### 3. **Manajemen Favorit**
- Bookmark game yang menarik
- Beri rating dan review
- Lihat history aktivitas Anda

## 🔧 Konfigurasi

### Environment Variables
Buat file `.env` di root directory:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Database Configuration
Default menggunakan SQLite. Untuk production, ubah di `config/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_db_name',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## 🚀 Deployment

### Local Development
```bash
python manage.py runserver
```

### Production (contoh dengan Gunicorn)
```bash
pip install gunicorn
gunicorn config.wsgi:application
```

### Google Cloud Platform
File `app.yaml` sudah disediakan untuk deployment ke Google App Engine:
```bash
gcloud app deploy
```

## 📊 Dataset

Proyek ini menggunakan dataset game yang mencakup:
- **Nama game** dan deskripsi
- **Genre** (Action, RPG, Strategy, dll.)
- **Platform** (PC, PlayStation, Xbox, dll.)
- **Rating ESRB** (E, T, M, dll.)
- **Rating pengguna** (1-5 bintang)
- **Cover image** URL
- **Release date**

## 🤖 Machine Learning Model

### Algoritma yang Digunakan
1. **Content-Based Filtering**
   - TF-IDF untuk genre dan deskripsi
   - Cosine similarity untuk mencari game serupa

2. **K-Means Clustering**
   - Pengelompokan game berdasarkan fitur-fitur seperti genre, rating, platform
   - Model: `model_kmeans.pkl`
   - Data clustering: `df_clustering.csv`
   - Rekomendasi berdasarkan game dalam cluster yang sama

3. **Popularity-Based Filtering**
   - Fallback system berdasarkan rating dan popularitas
   - Digunakan ketika metode lain tidak tersedia

### Hybrid Recommendation System
Sistem menggunakan pendekatan hybrid yang menggabungkan ketiga metode:
- **Primary**: Content-based similarity
- **Secondary**: K-Means clustering
- **Fallback**: Popularity-based

### Model Training
```bash
python manage.py train_recommendations
```

### File Model yang Digunakan
- `rekomendasi_sistem.pkl` - Content-based similarity model
- `model_kmeans.pkl` - K-Means clustering model
- `df_clustering.csv` - Data hasil clustering dengan kolom 'Cluster'

## 🧪 Testing

Jalankan test suite:
```bash
python manage.py test
```

Test coverage:
```bash
coverage run --source='.' manage.py test
coverage report
```

## 📱 Responsive Design

Aplikasi ini fully responsive dengan breakpoints:
- **Mobile**: < 768px
- **Tablet**: 768px - 1023px  
- **Desktop**: 1024px+

## 🎨 UI/UX Features

- **Dark Theme** dengan color scheme yang konsisten
- **Smooth animations** dan transitions
- **Consistent image sizing** (150px × 200px) di semua device
- **Intuitive navigation** dengan breadcrumbs
- **Search suggestions** dengan real-time filtering

## 🔒 Security Features

- CSRF protection
- SQL injection prevention
- XSS protection
- Secure authentication system
- Input validation dan sanitization

## 📈 Performance

- **Lazy loading** untuk images
- **Database query optimization**
- **Caching** untuk rekomendasi
- **Compressed static files**
- **Efficient pagination**

## 🤝 Contributing

1. Fork repository
2. Buat feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push ke branch (`git push origin feature/AmazingFeature`)
5. Buat Pull Request

## 📝 License

Distributed under the MIT License. See `LICENSE` for more information.

## 👨‍💻 Author

**Anggi** - *Full Stack Developer*

- GitHub: [@AnggiSilvi](https://github.com/AnggiSilvi)
- Email: your.email@example.com

## 🙏 Acknowledgments

- Dataset game dari berbagai sumber publik
- Django community untuk framework yang luar biasa
- Scikit-learn untuk machine learning tools
- Font Awesome untuk icons
- Google Fonts untuk typography

## 📞 Support

Jika Anda mengalami masalah atau memiliki pertanyaan:

1. Cek [Issues](https://github.com/AnggiSilvi/game-rekomenn/issues) yang sudah ada
2. Buat issue baru jika diperlukan
3. Hubungi developer melalui email

---

⭐ **Jika proyek ini membantu Anda, jangan lupa berikan star!** ⭐
#   g a m e - r e k o m e n n 
 
 