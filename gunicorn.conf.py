# Gunicorn bu dosyayı kendiliğinden okur (Render'daki "gunicorn app:app" komutu).

# GIF üretimi Render'ın ücretsiz planında kare başına ~1 saniye sürüyor.
# Varsayılan 30 saniyelik sınır uzun GIF'leri yarıda kesiyordu.
timeout = 120

# Ücretsiz plan 512 MB bellek veriyor; tek işçi yeterli ve güvenli.
workers = 1
