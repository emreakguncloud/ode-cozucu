import base64 #fotoğraf değil de metin olarak çıktıyı dönüştürmek için
import io #fotoğrafları kaydetmeden çerezlemek için
from PIL import Image # GIF üretmek için
from matplotlib.figure import Figure


def statik_grafik(tablo, baslik):
    fig = Figure(figsize=(7, 4))
    ax = fig.subplots()

    for sutun in tablo.columns[1:]:
        ax.plot(tablo["x"], tablo[sutun], "o-", markersize=3, label=sutun)

    ax.set_xlabel("x")
    ax.set_title(baslik)
    ax.grid(True)
    ax.legend()

    tampon = io.BytesIO()
    fig.savefig(tampon, format="png", dpi=100, bbox_inches="tight")
    return base64.b64encode(tampon.getvalue()).decode("ascii")

def animasyonlu_grafik(tablo, baslik, en_fazla_kare=60):
    fig = Figure(figsize=(7, 4), layout="tight")
    ax = fig.subplots()
    sutunlar = list(tablo.columns[1:])

    # statik grafikten farklı olarak eksenler sabitlenmeli veriler güncellenmeli
    alt = tablo[sutunlar].min().min()
    ust = tablo[sutunlar].max().max()
    pay = (ust - alt) * 0.05
    if pay == 0:
        pay = 1.0
    ax.set_xlim(tablo["x"].min(), tablo["x"].max())
    ax.set_ylim(alt - pay, ust + pay)
    ax.set_xlabel("x")
    ax.set_title(baslik)
    ax.grid(True)

    # Boş çizgiler oluştur, her karede verilerini güncelleyeceğiz 
    cizgiler = []
    for sutun in sutunlar:
        cizgi, = ax.plot([], [], "o-", markersize=3, label=sutun)
        cizgiler.append(cizgi)
    ax.legend(loc="upper right")

    son_satir = len(tablo) - 1
    kare_sayisi = min(en_fazla_kare, son_satir)
    kareler = []

    for kare in range(1, kare_sayisi + 1):
        son = round(kare * son_satir / kare_sayisi)
        parca = tablo.iloc[: son + 1]

        for cizgi, sutun in zip(cizgiler, sutunlar):
            cizgi.set_data(parca["x"], parca[sutun])

        tampon = io.BytesIO()
        fig.savefig(tampon, format="png", dpi=80)
        tampon.seek(0)
        kareler.append(Image.open(tampon).convert("RGB"))

    sureler = [80] * len(kareler)
    sureler[-1] = 1500

    gif_tampon = io.BytesIO()
    kareler[0].save(
        gif_tampon,
        format="GIF",
        save_all=True,
        append_images=kareler[1:],
        duration=sureler,
        loop=0,
    )
    return base64.b64encode(gif_tampon.getvalue()).decode("ascii")