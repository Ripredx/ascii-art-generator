<div align="center">

# 🎨 ASCII Art Studio

**Görüntüleri, metinleri ve çizimleri ASCII sanatına dönüştüren modern masaüstü uygulaması.**

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![PyQt6](https://img.shields.io/badge/PyQt6-GUI-41CD52?style=for-the-badge&logo=qt&logoColor=white)](https://www.riverbankcomputing.com/software/pyqt/)
[![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20|%20macOS%20|%20Linux-lightgrey?style=for-the-badge)]()

<br/>

```
    _   ____   ____ ___ ___      _    ____ _____
   / \ / ___| / ___|_ _|_ _|   / \  |  _ \_   _|
  / _ \\___ \| |    | | | |   / _ \ | |_) || |
 / ___ \___) | |___ | | | |  / ___ \|  _ < | |
/_/   \_\____/ \____|___|___/_/   \_\_| \_\|_|
              ____  _             _ _
             / ___|| |_ _   _  __| (_) ___
             \___ \| __| | | |/ _` | |/ _ \
              ___) | |_| |_| | (_| | | (_) |
             |____/ \__|\__,_|\__,_|_|\___/
```

</div>

---

## ✨ Özellikler

### 🖼️ Görüntüden ASCII'ye Dönüştürme
- **Görüntü yükleme** — PNG, JPG, BMP, GIF ve daha fazlasını destekler
- **Gerçek zamanlı webcam** — Kameranızdan canlı ASCII art akışı
- **GIF animasyonu** — Animasyonlu GIF'leri kare kare ASCII'ye dönüştürme
- **30+ karakter seti** — Klasik, Braille, Unicode blokları, Emoji, Japon Katakana ve daha fazlası
- **Özel karakter seti** — Kendi karakter setinizi tanımlayın
- **Ayarlanabilir parametreler** — Genişlik, kontrast, parlaklık ve renk ters çevirme

### ✏️ Metin → ASCII Art (Figlet Font Galerisi)
- **35+ figlet fontu** — Standard, Big, Banner, Graffiti, Starwars ve daha fazlası
- **Anlık galeri önizlemesi** — Yazdığınız metin tüm fontlarda aynı anda görüntülenir
- **Tek tıkla uygulama** — Beğendiğiniz fontu seçip canvas'a gönderin
- **Arka planda render** — Font oluşturma işlemi ayrı thread'de çalışır, UI donmaz

### 🎨 ASCII Çizim Tuvali
- **Çizim araçları** — Kalem, Silgi, Kova (flood fill), Çizgi ve Dikdörtgen
- **25+ fırça karakteri** — `@`, `#`, `█`, `▓`, `░` ve daha fazlası (özel karakter girişi destekli)
- **Ayarlanabilir tuval boyutu** — 20×10'dan 200×100'e kadar
- **Geri alma (Undo)** — 50 adıma kadar geri alma desteği
- **Kutu çerçeveli tuval** — Box-drawing karakterleriyle çizilmiş profesyonel görünüm

### 📤 Dışa Aktarma
| Format | Açıklama |
|--------|----------|
| 📋 **Clipboard** | ASCII art'ı panoya kopyalar |
| 💾 **TXT** | Düz metin dosyası olarak kaydeder |
| 🌐 **HTML** | Özel arka plan rengiyle HTML sayfası oluşturur |
| 🖼️ **PNG** | Monospace fontla render edilmiş görüntü oluşturur |

### 🎛️ Ek Özellikler
- **9 arka plan teması** — Pitch Black, Hacker Green, Matrix, Midnight Blue vb.
- **Zoom kontrolü** — `Ctrl+Scroll` veya `+`/`-` butonları
- **Modern koyu tema UI** — Glassmorphism ve gradient efektleri

---

## � Ekran Görüntüleri

> Uygulamanın ekran görüntülerini buraya ekleyebilirsiniz.

---

## 🚀 Kurulum

### Gereksinimler
- Python 3.8+
- pip

### Adımlar

```bash
# 1. Repoyu klonlayın
git clone https://github.com/KULLANICI_ADINIZ/ascii-art-generator.git
cd ascii-art-generator

# 2. Sanal ortam oluşturun (önerilir)
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# 3. Bağımlılıkları yükleyin
pip install PyQt6 Pillow opencv-python pyfiglet

# 4. Uygulamayı çalıştırın
python main.py
```

---

## 📁 Proje Yapısı

```
ascii-art-generator/
├── main.py                 # Ana uygulama — PyQt6 UI, event handling, tab yönetimi
├── requirements.txt        # Python bağımlılıkları
├── core/                   # Çekirdek motorlar
│   ├── __init__.py
│   ├── ascii_engine.py     # Görüntü → ASCII ve metin → figlet dönüştürme motoru
│   └── draw_engine.py      # Çizim tuvali motoru (paint, flood fill, line, rect)
├── utils/                  # Yardımcı modüller
│   ├── __init__.py
│   ├── constants.py        # Karakter setleri ve arka plan renk tanımları
│   └── exports.py          # Clipboard, TXT, HTML ve PNG dışa aktarma fonksiyonları
├── .gitignore
└── README.md
```

---

## 🧰 Kullanılan Teknolojiler

| Teknoloji | Kullanım Alanı |
|-----------|---------------|
| [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) | GUI framework |
| [Pillow (PIL)](https://pillow.readthedocs.io/) | Görüntü işleme, kontrast/parlaklık ayarları |
| [OpenCV](https://opencv.org/) | Webcam erişimi ve video yakalama |
| [pyfiglet](https://github.com/pwaller/pyfiglet) | Metin → ASCII art dönüştürme (figlet fontları) |

---

## 🎮 Kullanım Rehberi

### Görüntüden ASCII Art
1. **🖼️ Image** sekmesine gidin
2. `📁 Load Image` butonuyla bir görüntü yükleyin
3. Karakter setini, genişliği, kontrastı ve parlaklığı ayarlayın
4. Sonucu dışa aktarın (Copy / TXT / HTML / PNG)

### Webcam ile Canlı ASCII
1. **🖼️ Image** sekmesinde `📷 Webcam` butonuna tıklayın
2. Canlı ASCII art akışını izleyin
3. `🛑 Stop` ile durdurun

### Metin → ASCII Art
1. **✏️ Text** sekmesine gidin
2. Üst kısımdaki metin kutusuna yazın
3. 35+ fontta önizleme otomatik olarak oluşturulur
4. Beğendiğiniz kartın `⬆ Use` butonuna tıklayın

### ASCII Çizim
1. **🎨 Draw** sekmesine gidin
2. Sol panelden araç ve fırça karakteri seçin
3. Tuval üzerinde fare ile çizin
4. `↩ Undo` ile geri alın, sonucu dışa aktarın

---

## 🤝 Katkıda Bulunma

Katkılarınızı memnuniyetle karşılıyoruz! Lütfen aşağıdaki adımları izleyin:

1. Bu repoyu **fork** edin
2. Yeni bir **branch** oluşturun (`git checkout -b feature/yeni-ozellik`)
3. Değişikliklerinizi **commit** edin (`git commit -m 'feat: yeni özellik eklendi'`)
4. Branch'inizi **push** edin (`git push origin feature/yeni-ozellik`)
5. Bir **Pull Request** açın

---

## � Lisans

Bu proje [MIT Lisansı](LICENSE) ile lisanslanmıştır.

---

<div align="center">

**⭐ Projeyi beğendiyseniz yıldız vermeyi unutmayın!**

</div>
