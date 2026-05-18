# 🎬 Netflix Klonu - İçerik Yönetim ve İzleme Platformu

Bu proje, **PyQt6** ile geliştirilmiş masaüstü arayüzüne ve **SQL Server (T-SQL)** veritabanı altyapısına sahip, katmanlı mimari (*Repository Pattern*) mimarisine uygun olarak tasarlanmış gelişmiş bir İçerik Yönetim Platformudur. Kullanıcılar içerikleri arayabilir, puanlayabilir, favorilerine ekleyebilir ve izleme geçmişlerini takip edebilirken; yöneticiler ise içerik, tür, kullanıcı yönetimi yapabilir ve detaylı istatistiksel raporlara erişebilir.

---

## 🚀 Öne Çıkan Özellikler

### 👤 Kullanıcı Paneli
* **Akıllı Kayıt ve Giriş:** E-mail formatı doğrulama, minimum 6 karakter şifre güvenliği ve hesap durum (aktif/pasif) kontrolü.
* **İlgi Alanına Göre Öneri Sistemi:** Kullanıcının kayıt olurken seçtiği 3 favori türe, daha önce izlediği içeriklerin türlerine ve yüksek puan ($\ge 7$) verdiği içeriklerin türlerine göre dinamik içerik önerisi.
* **Gelişmiş Arama & Filtreleme:** İçerik adı, tür, tip (Film/Dizi), yayın yılı ve minimum puana göre anlık listeleme.
* **İzleme & Kaldığı Yerden Devam Etme:** Videoların izleme sürelerini kaydetme, diziler için bölüm seçimi ve kapatıp açıldığında tam kaldığı dakikadan devam edebilme mekanizması.
* **Profil & Favori Yönetimi:** Kişisel bilgileri ve favori 3 türü güncelleyebilme, içerikleri favorilere ekleme/çıkarma ve türe göre favori filtreleme.

### 👑 Yönetici (Admin) Paneli
* **İçerik (Program) Yönetimi:** Sisteme yeni Film/Dizi ekleme, mevcut içerikleri düzenleme, silme ve dizilere özel dinamik **yeni bölüm tanımlama** pop-up'ı.
* **Tür Yönetimi:** Manuel olarak yeni film/dizi türleri ekleme, güncelleme ve bağımlılık kontrolü yaparak güvenli silme (*İçeriğe bağlı türlerin silinmesi engellenir*).
* **Kullanıcı Yönetimi:** Kayıtlı tüm kullanıcıları listeleme, detaylı izleme geçmişlerini modal penceresinde inceleme ve kullanıcı hesaplarını tek tıkla **Aktif/Pasif** duruma getirme.
* **Gelişmiş Raporlama Sitemi:**
    * Toplam kullanıcı, izlenme ve puanlama özet istatistikleri.
    * En çok izlenen ve en yüksek puanlı "Top 10" içerik analizi.
    * En çok izlenen türler ve en aktif kullanıcıların listesi.
    * Son 7 günde popüler olan içeriklerin trend analizi.

---

## 🛠️ Kullanılan Teknolojiler

* **Arayüz (GUI):** Python `PyQt6` (Sinyal-slot mekanizması, `QStackedWidget` sayfa yönetimi ve özel Netflix temalı karanlık mod CSS tasarımı)
* **Veritabanı:** Microsoft SQL Server
* **Bağlantı Katmanı:** `pyodbc`
* **Test Altyapısı:** `unittest` & `unittest.mock` (Veritabanına zarar vermeden taklit verilerle iş mantığı testi)

---

## 📂 Proje Yapısı

* ├── database_connection.py  # SQL Server Windows Authentication bağlantı yönetimi
* ├── table_creator.py        # İlişkisel veritabanı tablolarını ve indeksleri otomatik oluşturan katman
* ├── repositories.py         # SQL sorgularını ve veri tabanı işlemlerini soyutlayan Repository sınıfları
* ├── programController.py    # Uygulamanın tüm iş mantğını (Business Logic) yöneten kontrolör
* ├── main.py                 # PyQt6 ile yazılmış modern, CSS giydirmeli kullanıcı arayüzü katmanı
* └── test_controller.py      # İş mantığı kurallarını doğrulayan Mock tabanlı birim testleri

## ⚙️ Kurulum ve Çalıştırma

1. Ön Gereksinimler
Sisteminizde Python 3.8+ ve Microsoft SQL Server kurulu olmalıdır.

2. Gerekli Kütüphanelerin Yüklenmesi
Terminal veya komut satırını açarak aşağıdaki kütüphaneleri yükleyin
'pip install PyQt6 pyodbc'

3. Veritabanı Yapılandırması
database_connection.py dosyasını açarak SQL Server bağlantı bilgilerinizi doğrulayın. Varsayılan olarak lokalinizdeki FilmDB isimli veritabanına Windows Authentication (Trusted_Connection=yes) kullanarak bağlanacak şekilde ayarlanmıştır:

"DRIVER={SQL Server};"
"SERVER=localhost;"
"DATABASE=FilmDB;"
"Trusted_Connection=yes;"

  Not: Veritabanı tabloları, indeksler ve kısıtlamalar (Constraints) uygulama ilk kez çalıştırıldığında table_creator.py tarafından otomatik olarak oluşturulacaktır. Sizin manuel bir SQL scripti yürütmenize gerek yoktur.

4. Uygulamayı Başlatma
Projenin ana dizinindeyken aşağıdaki komutla uygulamayı ayağa kaldırabilirsiniz:
'python main.py'


## 🧪 Birim Testlerinin Çalıştırılması
'python -m unittest test_controller.py' kodunu terminalden çalıştırın.


## 🏛️ Mimari Tasarım Notları
Katmanlı Mimari (N-Tier Layout): GUI katmanı (main.py) veritabanına asla doğrudan SQL sorgusu göndermez. Tüm istekler ProgramController üzerinden geçerek iş mantığı süzgecinden geçirilir ve ilgili Repository sınıfına iletilir. Bu sayede kodun bakımı kolaylaşır ve test edilebilirliği maksimum seviyeye çıkar.
Veri Güvenliği ve Tutarlılık: Veritabanı tablosu seviyesinde şifre uzunlukları (CHECK constraint) ve benzersiz e-mailler (UNIQUE constraint) kontrol edilir. Kritik ekleme, silme ve güncelleme işlemlerinde try-except blokları ve ilişkisel bütünlük kısıtlamaları kullanılarak olası veri kayıpları veya sistem çökmeleri tamamen engellenmiştir.





