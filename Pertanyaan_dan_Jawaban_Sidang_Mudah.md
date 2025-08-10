# 📋 PERTANYAAN DAN JAWABAN SIDANG SKRIPSI
## Sistem Rekomendasi Game Berbasis Web dengan Machine Learning

## 🎯 **BAGIAN 1: LATAR BELAKANG**

### **1. Kenapa pilih topik sistem rekomendasi game?**
**Jawaban:** Game sekarang banyak banget, orang jadi bingung mau main yang mana. Makanya saya buat sistem yang bisa kasih saran game yang cocok.

### **2. Masalah apa yang mau diselesaikan?**
**Jawaban:** Orang susah pilih game karena terlalu banyak pilihan. Sistem saya bantu kasih rekomendasi yang sesuai selera.

### **3. Tujuan utama penelitian ini apa?**
**Jawaban:** Bikin website yang bisa nyaranin game pakai kecerdasan buatan, jadi user gampang nemuin game yang dia suka.

### **4. Metode penelitiannya gimana?**
**Jawaban:** Saya analisis kebutuhan dulu, terus desain sistem, bikin programnya, tes, dan deploy ke internet.

---

## 🤖 **BAGIAN 2: TEKNOLOGI KECERDASAN BUATAN**

### **5. Algoritma AI apa yang dipakai?**
**Jawaban:** Pakai 3 cara: 
- K-Means (kelompokin game yang mirip)
- Cosine Similarity (ukur seberapa mirip game)
- Hybrid (gabungin kedua cara di atas)

### **6. Data apa yang dipakai buat analisis?**
**Jawaban:** 4 hal: Genre game (action, RPG, dll), Rating (1-5 bintang), ESRB (rating umur), Platform (PC, PlayStation, Xbox).

### **7. K-Means itu apa dan gimana kerjanya?**
**Jawaban:** K-Means itu cara buat kelompokin game. Game yang mirip dimasukin ke grup yang sama. Saya bagi jadi 3 grup.

### **8. Cosine Similarity itu apa?**
**Jawaban:** Cara ngitung seberapa mirip 2 game. Kalau mirip banget, skornya tinggi. Kalau beda banget, skornya rendah.

### **9. Hybrid System itu gimana?**
**Jawaban:** Gabungin hasil dari K-Means sama Cosine Similarity. Jadi rekomendasi lebih akurat dan bervariasi.

### **10. Gimana cara bersihin data?**
**Jawaban:** Hapus data yang kosong, ubah kata jadi angka (misal: "Action" jadi 1), dan pastikan semua data konsisten.

### **11. Gimana cara ukur bagus tidaknya sistem?**
**Jawaban:** Pakai Silhouette Score buat ukur clustering, similarity score buat ukur kemiripan, dan tes langsung sama user.

---

## 💻 **BAGIAN 3: PEMROGRAMAN**

### **12. Teknologi apa yang dipakai?**
**Jawaban:** Django (bikin website), Python (bahasa program), SQLite (database), HTML/CSS/JS (tampilan).

### **13. Arsitektur sistemnya gimana?**
**Jawaban:** Pakai pola MVC: Model (data), View (logika), Template (tampilan). AI-nya dipisah di modul khusus.

### **14. Database-nya gimana?**
**Jawaban:** Pakai SQLite. Ada tabel Game (data utama), Genre, Platform, dan tabel buat nyimpen skor kemiripan.

### **15. Gimana implementasi AI-nya?**
**Jawaban:** Bikin 3 class: satu buat K-Means, satu buat Cosine Similarity, satu lagi buat gabungin keduanya.

### **16. Alur datanya gimana?**
**Jawaban:** Import data → Proses data → Latih AI → User minta rekomendasi → AI kasih saran → Tampilkan di website.

### **17. Gimana cara latih AI-nya?**
**Jawaban:** Jalanin command: `python manage.py train_kmeans` dan `python manage.py train_recommendations`.

### **18. API-nya gimana?**
**Jawaban:** Ada endpoint `/api/recommendations/` yang nerima parameter game dan kasih balik daftar rekomendasi dalam format JSON.

---

## 📊 **BAGIAN 4: DATA DAN PERFORMA**

### **19. Data game-nya dari mana?**
**Jawaban:** Dari file CSV yang berisi ribuan data game dengan info nama, rating, genre, platform, dan gambar.

### **20. Gimana biar sistemnya cepat?**
**Jawaban:** Simpen AI di memory, lazy loading gambar, indexing database, dan optimasi query.

### **21. Bisa handle user banyak ga?**
**Jawaban:** Bisa, karena pakai arsitektur modular, AI disimpen di file, dan siap deploy ke cloud.

### **22. Kalau error gimana?**
**Jawaban:** Ada try-catch, logging error, fallback mechanism, dan pesan error yang user-friendly.

---

## 🎨 **BAGIAN 5: TAMPILAN WEBSITE**

### **23. Tampilannya gimana?**
**Jawaban:** Dark theme, responsive (bisa di HP/laptop), ada search dengan saran otomatis, filter kategori, dan navigasi mudah.

### **24. Keamanannya gimana?**
**Jawaban:** Ada proteksi CSRF, SQL injection, XSS, autentikasi aman, dan validasi input.

### **25. Gimana cara tesnya?**
**Jawaban:** Tes unit (AI), tes integrasi (API), tes user (tampilan), tes performa, dan tes di berbagai browser.

---

## 📈 **BAGIAN 6: HASIL**

### **26. Hasilnya gimana?**
**Jawaban:** Sistem berhasil kasih rekomendasi yang relevan, cepat (< 2 detik), dan user puas dengan hasilnya.

### **27. Gimana tau sistemnya berhasil?**
**Jawaban:** 
- **Teknis**: Silhouette Score 0.173, response cepat, sistem stabil
- **User**: Rekomendasi cocok, hasil beragam, mudah dipakai
- **AI**: Clustering berhasil, similarity akurat, hybrid lebih baik

### **28. Kelebihan sistem ini apa?**
**Jawaban:** Akurat karena hybrid, real-time, user-friendly, bisa handle banyak user, dan tampilannya bagus.

### **29. Kekurangannya apa?**
**Jawaban:** User baru susah dapat rekomendasi, data game terbatas, belum ada fitur collaborative filtering.

### **30. Gimana validasi hasilnya?**
**Jawaban:** Cross-validation, A/B testing, evaluasi manual, feedback user, dan bandingkan dengan metode lain.

---

## 🚀 **BAGIAN 7: DEPLOYMENT**

### **31. Gimana cara deploy sistemnya?**
**Jawaban:** Development pakai Django runserver, production pakai Gunicorn, deploy ke Google App Engine.

### **32. Maintenance-nya gimana?**
**Jawaban:** Retrain AI berkala, backup database, monitoring performa, update security, dan tambah fitur baru.

### **33. Nilai bisnisnya apa?**
**Jawaban:** User lebih engage, hemat waktu cari game, pengalaman personal, insight buat developer game.

---

## 🔬 **BAGIAN 8: KONTRIBUSI**

### **34. Kebaruannya apa?**
**Jawaban:** Gabungin K-Means + Cosine Similarity dengan randomness, optimasi 4 fitur, implementasi web modern.

### **35. Tantangan teknisnya apa?**
**Jawaban:** Kompatibilitas model (solved: version control), performa (solved: caching), kualitas data (solved: preprocessing).

### **36. Pengembangan ke depannya?**
**Jawaban:** Tambah collaborative filtering, deep learning, real-time learning, social features, dan mobile app.

---

## 📊 **RINGKASAN SINGKAT**

### **Teknologi AI:**
- K-Means: 3 grup, 4 fitur, skor 0.173
- Cosine Similarity: ukur kemiripan 4 dimensi
- Hybrid: gabungin keduanya dengan random

### **Teknologi Web:**
- Django + Python + SQLite
- HTML/CSS/JS + Font Awesome
- Response < 2 detik

---

**💡 Tips Sidang:**
1. Pahami 3 algoritma AI
2. Siapkan demo website
3. Buat diagram sederhana
4. Tunjukkan contoh rekomendasi
5. Jelaskan kenapa pilih teknologi ini
