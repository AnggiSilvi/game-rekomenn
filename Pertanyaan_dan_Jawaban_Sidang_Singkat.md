# 📋 PERTANYAAN DAN JAWABAN SIDANG SKRIPSI
## Sistem Rekomendasi Game Berbasis Web dengan Machine Learning

## 🎯 **BAGIAN 1: LATAR BELAKANG DAN KONSEP DASAR**

### **1. Apa yang melatarbelakangi pemilihan topik sistem rekomendasi game?**
**Jawaban:** Banyaknya pilihan game membuat pengguna bingung memilih. Sistem rekomendasi membantu pengguna menemukan game yang sesuai dengan selera mereka.

### **2. Apa masalah utama yang ingin diselesaikan dalam penelitian ini?**
**Jawaban:** Mengatasi kebingungan pengguna dalam memilih game dari ribuan pilihan yang tersedia dengan memberikan rekomendasi yang personal.

### **3. Apa tujuan utama dari pengembangan sistem ini?**
**Jawaban:** Membuat sistem rekomendasi game yang akurat menggunakan machine learning untuk memberikan saran game yang sesuai dengan preferensi pengguna.

### **4. Metode penelitian apa yang digunakan?**
**Jawaban:** Metode pengembangan sistem dengan machine learning: analisis kebutuhan → desain sistem → implementasi → testing → deployment.

---

## 🤖 **BAGIAN 2: MACHINE LEARNING DAN ALGORITMA**

### **5. Algoritma machine learning apa saja yang digunakan?**
**Jawaban:** 3 algoritma: K-Means Clustering (mengelompokkan game), Cosine Similarity (mengukur kemiripan), dan Hybrid System (gabungan keduanya).

### **6. Fitur apa yang digunakan untuk clustering dan similarity?**
**Jawaban:** 4 fitur utama: Genre (jenis game), Rating (skor 1-5), ESRB (rating usia), Platform (PC, PlayStation, Xbox).

### **7. Bagaimana implementasi K-Means Clustering dalam sistem?**
**Jawaban:** Mengelompokkan game menjadi 3 cluster berdasarkan kesamaan fitur menggunakan scikit-learn, lalu menyimpan hasilnya ke file CSV.

### **8. Bagaimana cara kerja Cosine Similarity dalam sistem?**
**Jawaban:** Menghitung seberapa mirip antar game berdasarkan 4 fitur, kemudian merekomendasikan game dengan similarity score tertinggi.

### **9. Bagaimana cara kerja Hybrid Recommendation System?**
**Jawaban:** Menggabungkan hasil clustering dan similarity (50%-50%), lalu memilih secara acak dari pool rekomendasi untuk variasi hasil.

### **10. Bagaimana proses preprocessing data dilakukan?**
**Jawaban:** Membersihkan data kosong, mengubah data kategori menjadi angka, normalisasi rating, dan validasi konsistensi data.

### **11. Metrik evaluasi apa yang digunakan untuk mengukur performa?**
**Jawaban:** Silhouette Score untuk clustering, Cosine Similarity Score untuk kemiripan, dan user testing untuk relevansi rekomendasi.

---

## 💻 **BAGIAN 3: IMPLEMENTASI TEKNIS**

### **12. Teknologi apa saja yang digunakan dalam pengembangan?**
**Jawaban:** Django (web framework), Python (programming), SQLite (database), scikit-learn (machine learning), HTML/CSS/JS (frontend).

### **13. Bagaimana arsitektur sistem secara keseluruhan?**
**Jawaban:** Menggunakan pola MVC Django: Model (data), View (logika), Template (tampilan). ML engine terpisah dalam modul khusus.

### **14. Bagaimana desain database dan relasi antar tabel?**
**Jawaban:** Database SQLite dengan tabel Game (utama), Genre dan Platform (many-to-many), GameSimilarity (skor kemiripan), User (autentikasi).

### **15. Bagaimana proses implementasi algoritma ML?**
**Jawaban:** Dibuat dalam class terpisah: GameClusteringEngine, CosineSimilarityEngine, HybridRecommendationEngine dengan method standar ML.

### **16. Bagaimana alur data dalam sistem?**
**Jawaban:** Import CSV → Extract fitur → Training model → User request → Generate rekomendasi → Tampilkan hasil.

### **17. Bagaimana proses training model dilakukan?**
**Jawaban:** Menggunakan Django command: `python manage.py train_kmeans` dan `python manage.py train_recommendations`. Model disimpan dalam file pickle.

### **18. Bagaimana desain API untuk rekomendasi?**
**Jawaban:** Endpoint `/api/recommendations/` dengan parameter: type (jenis), game_id (game acuan), num (jumlah). Response berupa JSON array game.

---

## 📊 **BAGIAN 4: DATA DAN PERFORMA**

### **19. Dataset apa yang digunakan dan bagaimana strukturnya?**
**Jawaban:** Dataset game dalam CSV dengan kolom: name, rating, genres, platforms, esrb, cover_image_url. Diimport ke database SQLite.

### **20. Bagaimana optimasi performa sistem dilakukan?**
**Jawaban:** Caching model di memory, lazy loading gambar, database indexing, pagination, dan optimasi query database.

### **21. Bagaimana sistem menangani scalability?**
**Jawaban:** Arsitektur modular, model serialization, database optimization, stateless design, dan siap deploy ke cloud.

### **22. Bagaimana sistem menangani error dan exception?**
**Jawaban:** Try-catch blocks, logging system, graceful degradation, user-friendly error messages, dan fallback mechanism.

---

## 🎨 **BAGIAN 5: USER INTERFACE DAN EXPERIENCE**

### **23. Bagaimana desain user interface dan user experience?**
**Jawaban:** Dark theme modern, responsive design, search dengan auto-suggestions, filter kategori, grid layout konsisten, dan navigasi mobile-friendly.

### **24. Aspek keamanan apa yang diimplementasikan?**
**Jawaban:** CSRF protection, SQL injection prevention, XSS protection, secure authentication, input validation, dan secure session management.

### **25. Bagaimana pengujian sistem dilakukan?**
**Jawaban:** Unit testing (algoritma ML), integration testing (API), user acceptance testing (UI/UX), performance testing, dan cross-browser testing.

---

## 📈 **BAGIAN 6: HASIL DAN EVALUASI**

### **26. Apa hasil yang dicapai dari sistem ini?**
**Jawaban:** Sistem berhasil memberikan rekomendasi relevan dengan response time < 2 detik dan feedback positif dari user testing.

### **27. Bagaimana sistem ini dikatakan berhasil? Apa indikator keberhasilannya?**
**Jawaban:** 
- **Teknis**: Silhouette Score 0.173, response time < 2 detik, system uptime 99%+
- **Fungsional**: Rekomendasi relevan, hasil beragam, coverage lengkap, scalable
- **User Experience**: User puas, engagement tinggi, task completion cepat, UI responsif
- **Algoritma**: Clustering berhasil, similarity akurat, hybrid lebih baik
- **Implementasi**: Integrasi baik, error handling, deployment sukses, code quality

### **28. Apa kelebihan sistem yang dikembangkan?**
**Jawaban:** Hybrid approach akurat, real-time, user-friendly, scalable, multiple filtering, responsive design, dan performa cepat.

### **29. Apa keterbatasan sistem saat ini?**
**Jawaban:** Cold start problem untuk user baru, dataset terbatas, belum ada collaborative filtering, manual feature selection.

### **30. Bagaimana validasi hasil rekomendasi dilakukan?**
**Jawaban:** Cross-validation, A/B testing, manual evaluation, user feedback, dan comparison dengan baseline methods.

---

## 🚀 **BAGIAN 7: DEPLOYMENT DAN MAINTENANCE**

### **31. Bagaimana proses deployment sistem?**
**Jawaban:** Local development dengan Django runserver, production dengan Gunicorn, cloud deployment ke Google App Engine, dan database migration otomatis.

### **32. Bagaimana maintenance dan update sistem?**
**Jawaban:** Regular model retraining, database backup, performance monitoring, security updates, dan feature updates berdasarkan feedback.

### **33. Apa nilai bisnis dari sistem ini?**
**Jawaban:** Meningkatkan user engagement, mengurangi waktu pencarian, personalized experience, insights untuk developer, dan solusi scalable.

---

## 🔬 **BAGIAN 8: KONTRIBUSI DAN PENGEMBANGAN**

### **34. Apa kebaruan/kontribusi dari penelitian ini?**
**Jawaban:** Kombinasi K-Means + Cosine Similarity dengan randomness, optimasi 4-fitur, hybrid dynamic allocation, web implementation modern.

### **35. Apa tantangan teknis yang dihadapi dan solusinya?**
**Jawaban:** Model compatibility (version control), performance (caching), data quality (preprocessing), scalability (modular design), UI (responsive).

### **36. Apa pengembangan yang dapat dilakukan di masa depan?**
**Jawaban:** Collaborative filtering, deep learning, real-time learning, multi-criteria recommendation, social features, dan mobile app.

---

## 📊 **RINGKASAN TEKNIS SISTEM**

### **Arsitektur ML:**
- K-Means: 3 clusters, 4 features, Silhouette Score 0.173
- Cosine Similarity: 4D vectors, StandardScaler normalization
- Hybrid: Dynamic allocation dengan randomness

### **Tech Stack:**
- Backend: Django 4.x, Python 3.8+, SQLite
- ML: scikit-learn, pandas, numpy, joblib
- Frontend: HTML5, CSS3, JavaScript, Font Awesome

### **Performance:**
- Response time: < 2 seconds
- Model loading: Cached in memory
- UI: Mobile-responsive, cross-browser

---

**💡 Tips Sidang:**
1. Pahami algoritma step-by-step
2. Siapkan demo live sistem
3. Buat diagram arsitektur
4. Siapkan contoh hasil rekomendasi
5. Pahami trade-offs design decisions
