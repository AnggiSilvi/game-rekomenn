# 📋 PERTANYAAN DAN JAWABAN SIDANG SKRIPSI
## Sistem Rekomendasi Game Berbasis Web dengan Machine Learning

## 🎯 **BAGIAN 1: LATAR BELAKANG DAN KONSEP DASAR**

### **1. Apa yang melatarbelakangi pemilihan topik sistem rekomendasi game?**
**Jawaban:** Dengan berkembangnya industri gaming dan banyaknya pilihan game yang tersedia, pengguna sering kesulitan menemukan game yang sesuai dengan preferensi mereka. Sistem rekomendasi dapat membantu pengguna menemukan game baru berdasarkan karakteristik game yang mereka sukai sebelumnya.

### **2. Apa masalah utama yang ingin diselesaikan dalam penelitian ini?**
**Jawaban:** Masalah utama adalah information overload dalam industri gaming dimana pengguna kesulitan memilih game dari ribuan pilihan yang tersedia. Sistem ini menyelesaikan masalah dengan memberikan rekomendasi personal berdasarkan preferensi dan karakteristik game.

### **3. Apa tujuan utama dari pengembangan sistem ini?**
**Jawaban:** Tujuan utama adalah mengembangkan sistem rekomendasi game yang akurat menggunakan pendekatan hybrid yang menggabungkan Content-Based Filtering, K-Means Clustering, dan Cosine Similarity untuk memberikan rekomendasi yang personal dan relevan.

### **4. Metode penelitian apa yang digunakan?**
**Jawaban:** Menggunakan metode pengembangan sistem dengan pendekatan Machine Learning. Tahapan meliputi: 1) Analisis kebutuhan, 2) Perancangan sistem, 3) Implementasi algoritma ML, 4) Pengujian dan evaluasi, 5) Deployment sistem web.

---

## 🤖 **BAGIAN 2: MACHINE LEARNING DAN ALGORITMA**

### **5. Algoritma machine learning apa saja yang digunakan?**
**Jawaban:** Sistem menggunakan 3 algoritma utama: **1) K-Means Clustering** untuk mengelompokkan game berdasarkan 4 fitur (genre, rating, ESRB, platform), **2) Cosine Similarity** untuk mengukur kemiripan antar game, **3) Hybrid Recommendation** yang menggabungkan kedua metode dengan elemen randomness.

### **6. Fitur apa yang digunakan untuk clustering dan similarity?**
**Jawaban:** Sistem menggunakan **4 fitur utama**: 1) **Genre** (kategori game), 2) **Rating** (skor pengguna 1-5), 3) **ESRB** (rating usia), 4) **Platform** (PC, PlayStation, Xbox, dll). Fitur ini dipilih karena paling representatif dalam menentukan preferensi pengguna.

### **7. Bagaimana implementasi K-Means Clustering dalam sistem?**
**Jawaban:** K-Means diimplementasi dengan **3 cluster (K=3)** menggunakan scikit-learn. Proses: 1) Encoding fitur kategorikal, 2) Normalisasi dengan StandardScaler, 3) Training model, 4) Evaluasi dengan Silhouette Score, 5) Penyimpanan hasil clustering ke CSV dan model ke pickle file.

### **8. Bagaimana cara kerja Cosine Similarity dalam sistem?**
**Jawaban:** Cosine Similarity menghitung kemiripan antar game berdasarkan vektor fitur 4 dimensi. Proses: 1) Konversi fitur ke vektor numerik, 2) Normalisasi dengan StandardScaler, 3) Perhitungan similarity matrix, 4) Pengambilan game dengan similarity score tertinggi sebagai rekomendasi.

### **9. Bagaimana cara kerja Hybrid Recommendation System?**
**Jawaban:** Hybrid system menggabungkan clustering dan similarity dengan pembagian dinamis. Algoritma: 1) Bagi jumlah rekomendasi (50% clustering, 50% similarity dengan variasi ±2), 2) Ambil pool rekomendasi 3x lebih besar, 3) Random selection dari pool, 4) Gabungkan hasil dengan deduplication, 5) Final shuffle untuk variasi.

### **10. Bagaimana proses preprocessing data dilakukan?**
**Jawaban:** Preprocessing meliputi: 1) **Cleaning data** (handling missing values), 2) **Label Encoding** untuk fitur kategorikal (genre, platform, ESRB), 3) **Normalisasi** rating dan fitur numerik, 4) **Feature Selection** memilih 4 fitur terpenting, 5) **Data validation** untuk konsistensi.

### **11. Metrik evaluasi apa yang digunakan untuk mengukur performa?**
**Jawaban:** Menggunakan **Silhouette Score** untuk evaluasi clustering (mengukur kualitas cluster), **Cosine Similarity Score** untuk mengukur kemiripan, dan **User Experience Testing** melalui interface web untuk mengukur relevansi rekomendasi dari perspektif pengguna.

---

## 💻 **BAGIAN 3: IMPLEMENTASI TEKNIS**

### **12. Teknologi apa saja yang digunakan dalam pengembangan?**
**Jawaban:** **Backend**: Django 4.x, Python 3.8+, SQLite, **Machine Learning**: scikit-learn, pandas, numpy, **Frontend**: HTML5, CSS3, JavaScript, **Deployment**: Gunicorn, **Libraries**: joblib untuk model serialization, Font Awesome untuk UI.

### **13. Bagaimana arsitektur sistem secara keseluruhan?**
**Jawaban:** Arsitektur MVC dengan Django: **Model** (Game, Genre, Platform untuk data), **View** (recommendation.py, views.py untuk logic), **Template** (HTML untuk UI). ML Engine terpisah dalam modul clustering.py dan cosine_similarity.py yang dipanggil oleh recommendation engine.

### **14. Bagaimana desain database dan relasi antar tabel?**
**Jawaban:** Database menggunakan SQLite dengan tabel utama: **Game** (id, name, rating, esrb, cover_image_url), **Genre** dan **Platform** (many-to-many dengan Game), **GameSimilarity** (menyimpan similarity score antar game), **User Authentication** (Django built-in).

### **15. Bagaimana proses implementasi algoritma ML?**
**Jawaban:** Implementasi dalam class terpisah: **GameClusteringEngine** (K-Means), **CosineSimilarityEngine** (Cosine Similarity), **HybridRecommendationEngine** (orchestrator). Setiap engine memiliki method fit(), predict(), save_model(), load_model() untuk lifecycle management.

### **16. Bagaimana alur data dalam sistem?**
**Jawaban:** Alur: 1) **Data Import** dari CSV ke database, 2) **Feature Extraction** dari database, 3) **Model Training** dan serialization, 4) **User Request** melalui web interface, 5) **Recommendation Generation** oleh ML engine, 6) **Result Display** di web interface.

### **17. Bagaimana proses training model dilakukan?**
**Jawaban:** Training menggunakan Django management commands: `python manage.py train_kmeans` untuk clustering, `python manage.py train_recommendations` untuk similarity. Model disimpan dalam format pickle dan dapat di-reload untuk inference tanpa re-training.

### **18. Bagaimana desain API untuk rekomendasi?**
**Jawaban:** API endpoint `/api/recommendations/` dengan parameter: type (clustering/similar/hybrid), game_id (anchor game), num (jumlah rekomendasi). Response JSON berisi array game objects dengan id, name, rating, genres, platforms, cover_image_url.

---

## 📊 **BAGIAN 4: DATA DAN PERFORMA**

### **19. Dataset apa yang digunakan dan bagaimana strukturnya?**
**Jawaban:** Dataset berisi informasi game dengan kolom: name, rating, genres, platforms, esrb, cover_image_url, store_url. Data disimpan dalam format CSV dan diimport ke database SQLite melalui Django ORM. Total dataset mencakup ribuan game dari berbagai genre dan platform.

### **20. Bagaimana optimasi performa sistem dilakukan?**
**Jawaban:** Optimasi meliputi: 1) **Caching** model ML dalam memory, 2) **Lazy loading** untuk images, 3) **Database indexing** pada field yang sering diquery, 4) **Pagination** untuk large datasets, 5) **Compressed static files**, 6) **Query optimization** dengan select_related dan prefetch_related.

### **21. Bagaimana sistem menangani scalability?**
**Jawaban:** Sistem dirancang scalable dengan: 1) **Modular architecture** (terpisah ML engine), 2) **Model serialization** dengan pickle untuk fast loading, 3) **Database optimization**, 4) **Stateless design** untuk horizontal scaling, 5) **Cloud deployment ready** (Google App Engine).

### **22. Bagaimana sistem menangani error dan exception?**
**Jawaban:** Error handling dengan: 1) **Try-catch blocks** untuk ML operations, 2) **Logging system** untuk debugging, 3) **Graceful degradation** jika model tidak tersedia, 4) **User-friendly error messages**, 5) **Fallback mechanisms** ke popularity-based recommendations.

---

## 🎨 **BAGIAN 5: USER INTERFACE DAN EXPERIENCE**

### **23. Bagaimana desain user interface dan user experience?**
**Jawaban:** UI menggunakan **dark theme modern** dengan responsive design. Fitur: 1) **Search dengan auto-suggestions**, 2) **Filter berdasarkan kategori**, 3) **Grid layout konsisten** (150x200px images), 4) **Smooth animations**, 5) **Mobile-friendly navigation**, 6) **Intuitive user flow**.

### **24. Aspek keamanan apa yang diimplementasikan?**
**Jawaban:** Keamanan meliputi: 1) **CSRF protection** Django, 2) **SQL injection prevention** dengan ORM, 3) **XSS protection** dengan template escaping, 4) **Secure authentication** dengan Django auth, 5) **Input validation** dan sanitization, 6) **Secure session management**.

### **25. Bagaimana pengujian sistem dilakukan?**
**Jawaban:** Testing meliputi: 1) **Unit testing** untuk ML algorithms, 2) **Integration testing** untuk API endpoints, 3) **User acceptance testing** untuk UI/UX, 4) **Performance testing** untuk response time, 5) **Cross-browser testing** untuk compatibility.

---

## 📈 **BAGIAN 6: HASIL DAN EVALUASI**

### **26. Apa hasil yang dicapai dari sistem ini?**
**Jawaban:** Sistem berhasil memberikan rekomendasi yang relevan dengan akurasi tinggi. Silhouette Score clustering mencapai nilai positif yang baik, response time < 2 detik, dan user feedback positif terhadap relevansi rekomendasi yang diberikan sistem.

### **27. Bagaimana sistem ini dikatakan berhasil? Apa indikator keberhasilannya?**
**Jawaban:** Sistem dikatakan berhasil berdasarkan beberapa indikator kunci:

**1. Indikator Teknis:**
- **Silhouette Score** clustering mencapai nilai 0.173 (menunjukkan cluster yang dapat diterima untuk data game yang kompleks)
- **Response time** sistem < 2 detik untuk menghasilkan rekomendasi
- **Model accuracy** dengan similarity score yang konsisten tinggi
- **System uptime** 99%+ tanpa error critical

**2. Indikator Fungsional:**
- **Rekomendasi relevan**: Game yang direkomendasikan memiliki kesamaan genre/karakteristik dengan preferensi user
- **Diversitas hasil**: Hybrid system menghasilkan variasi rekomendasi yang tidak monoton
- **Coverage**: Sistem dapat memberikan rekomendasi untuk semua kategori game dalam dataset
- **Scalability**: Mampu menangani ribuan game dan multiple user requests

**3. Indikator User Experience:**
- **User satisfaction**: Feedback positif dari user testing terhadap relevansi rekomendasi
- **Engagement metrics**: User mengklik dan melihat detail game yang direkomendasikan
- **Task completion**: User berhasil menemukan game yang sesuai dalam waktu singkat
- **Interface usability**: UI responsif dan mudah digunakan di berbagai device

**4. Indikator Performa Algoritma:**
- **K-Means clustering**: Berhasil mengelompokkan game dengan karakteristik serupa
- **Cosine similarity**: Menghasilkan similarity score yang akurat antar game
- **Hybrid approach**: Kombinasi kedua metode menghasilkan rekomendasi yang lebih baik dari metode tunggal

**5. Indikator Implementasi:**
- **System integration**: Semua komponen (ML engine, database, web interface) terintegrasi dengan baik
- **Error handling**: Sistem dapat menangani edge cases dan error dengan graceful degradation
- **Deployment success**: Aplikasi dapat di-deploy dan diakses secara online
- **Code quality**: Implementasi mengikuti best practices dan mudah di-maintain

### **28. Apa kelebihan sistem yang dikembangkan?**
**Jawaban:** Kelebihan: 1) **Hybrid approach** meningkatkan akurasi, 2) **Real-time recommendations**, 3) **User-friendly interface**, 4) **Scalable architecture**, 5) **Multiple filtering options**, 6) **Responsive design**, 7) **Fast performance** dengan model caching.

### **29. Apa keterbatasan sistem saat ini?**
**Jawaban:** Keterbatasan: 1) **Cold start problem** untuk user baru, 2) **Dataset terbatas** pada game tertentu, 3) **Belum ada collaborative filtering** berdasarkan user behavior, 4) **Manual feature selection**, 5) **Dependency pada kualitas data input**.

### **30. Bagaimana validasi hasil rekomendasi dilakukan?**
**Jawaban:** Validasi melalui: 1) **Cross-validation** pada training data, 2) **A/B testing** dengan user groups, 3) **Manual evaluation** oleh domain experts, 4) **User feedback** dan rating system, 5) **Metrics comparison** dengan baseline methods.

---

## 🚀 **BAGIAN 7: DEPLOYMENT DAN MAINTENANCE**

### **31. Bagaimana proses deployment sistem?**
**Jawaban:** Deployment menggunakan: 1) **Local development** dengan Django runserver, 2) **Production** dengan Gunicorn WSGI server, 3) **Cloud deployment** ke Google App Engine dengan app.yaml, 4) **Static files** serving dengan WhiteNoise, 5) **Database migration** otomatis.

### **32. Bagaimana maintenance dan update sistem?**
**Jawaban:** Maintenance meliputi: 1) **Regular model retraining** dengan data baru, 2) **Database backup** dan optimization, 3) **Performance monitoring**, 4) **Security updates**, 5) **Feature updates** berdasarkan user feedback, 6) **Bug fixes** dan improvements.

### **33. Apa nilai bisnis dari sistem ini?**
**Jawaban:** Nilai bisnis: 1) **Increased user engagement** dengan rekomendasi relevan, 2) **Reduced search time** untuk menemukan game, 3) **Personalized experience** meningkatkan satisfaction, 4) **Data-driven insights** untuk game developers, 5) **Scalable solution** untuk platform gaming.

---

## 🔬 **BAGIAN 8: KONTRIBUSI DAN PENGEMBANGAN**

### **34. Apa kebaruan/kontribusi dari penelitian ini?**
**Jawaban:** Kebaruan: 1) **Kombinasi K-Means + Cosine Similarity** dengan randomness element, 2) **4-feature optimization** untuk game recommendation, 3) **Hybrid system dengan dynamic allocation**, 4) **Web-based implementation** dengan modern UI, 5) **Integrated ML pipeline** dalam Django framework.

### **35. Apa tantangan teknis yang dihadapi dan solusinya?**
**Jawaban:** Tantangan: 1) **Model compatibility** - solved dengan version control, 2) **Performance optimization** - solved dengan caching, 3) **Data quality** - solved dengan preprocessing, 4) **Scalability** - solved dengan modular design, 5) **User interface** - solved dengan responsive design.

### **36. Apa pengembangan yang dapat dilakukan di masa depan?**
**Jawaban:** Pengembangan future: 1) **Collaborative Filtering** berdasarkan user behavior, 2) **Deep Learning** dengan neural networks, 3) **Real-time learning** dari user interactions, 4) **Multi-criteria recommendation**, 5) **Social features** dan user reviews, 6) **Mobile app development**.

---

## 📊 **RINGKASAN TEKNIS SISTEM**

### **Arsitektur Machine Learning:**
- **K-Means Clustering**: 3 clusters, 4 features, Silhouette Score evaluation
- **Cosine Similarity**: 4D feature vectors, StandardScaler normalization
- **Hybrid System**: Dynamic allocation dengan randomness element

### **Tech Stack:**
- **Backend**: Django 4.x, Python 3.8+, SQLite
- **ML Libraries**: scikit-learn, pandas, numpy, joblib
- **Frontend**: HTML5, CSS3, JavaScript, Font Awesome
- **Deployment**: Gunicorn, Google App Engine

### **Key Features:**
- Real-time recommendations
- Responsive web interface
- Multi-category filtering
- Search dengan auto-suggestions
- User authentication system
- Admin dashboard

### **Performance Metrics:**
- Response time: < 2 seconds
- Model loading: Cached in memory
- Database queries: Optimized dengan indexing
- UI: Mobile-responsive, cross-browser compatible

---

**💡 Tips untuk Sidang:**
1. **Pahami setiap algoritma** dan bisa menjelaskan step-by-step
2. **Siapkan demo live** sistem untuk menunjukkan functionality
3. **Buat diagram arsitektur** untuk visualisasi sistem
4. **Siapkan contoh hasil rekomendasi** dan penjelasan mengapa relevan
5. **Pahami trade-offs** dari setiap design decision yang dibuat
