# Groupchat & DM Yıllık Özet

Groupchat'leriniz için yıllık özet oluşturan basit bir web aracı.

Groupchat'leriniz cihazınızdan asla dışarı çıkmaz (**Local & Privacy First**). Tüm işlemler tarayıcınızın içinde, JavaScript ile yapılır. Sayfadaki Content-Security-Policy, tarayıcının dışarıya herhangi bir veri isteği (fetch/XHR/beacon) göndermesini tamamen engeller.

## Özellikler
- 📊 En çok konuşanlar
- 🦉 Gece kuşları ve Sabahçılar
- 💬 Kelime ve emoji analizi
- 🖥️ Tam ekran, interaktif slayt sunumu
- 📥 Sunumu PDF olarak indirme
- ✨ "Örnek sunum oluştur" ile kendi sohbetinizi yüklemeden, hayali bir grup sohbetiyle deneme

## Nasıl Çalıştırırım? (Local)

Bilgisayarınızda Python yüklüyse, proje klasöründe şu komutu çalıştırıp tarayıcıdan girebilirsiniz:

```bash
python -m http.server
```

Tarayıcınızda `http://localhost:8000` adresine gidin.

## Kullanım
1. Groupchat'lerinizin medyasız olarak dışarı aktarın (`.txt` veya `.zip`).
2. Siteye yükleyin.
3. Sunum otomatik olarak tam ekranda açılır; yön tuşlarıyla gezinin, dilerseniz "📥 Slayt PDF" ile indirin.
