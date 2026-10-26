import base64

from flask import Flask, render_template, request, Response
import pandas as pd
from cozucu import coz, CozumHatasi
from grafik import animasyonlu_grafik

app = Flask(__name__)

YONTEM_ADLARI = [
    ("euler", "Euler"),
    ("mod_euler", "Modified Euler"),
    ("heun", "Heun"),
    ("midpoint", "Midpoint"),
    ("ralston", "Ralston"),
    ("rk4", "RK4"),
]

# Tarayıcıdaki grafiğe en fazla bu kadar nokta gönderilir (n çok büyükse seyreltilir)
GRAFIK_EN_FAZLA_NOKTA = 500

# İndirilen GIF'in kare sayısı (Render'da kare başına ~1 sn sürüyor)
GIF_KARE_SAYISI = 30


def formu_oku():
    ifade = request.form["ifade"]
    derece = int(request.form["derece"])
    x0 = float(request.form["x0"])
    baslangiclar = [
        float(request.form["y0"]),
        float(request.form["yp0"]),
        float(request.form["ypp0"]),
    ]
    xmax = float(request.form["xmax"])
    yontem = request.form["yontem"]
    n = int(request.form["n"])
    return ifade, derece, x0, baslangiclar, xmax, yontem, n


def grafik_basligi(derece, ifade, yontem, n):
    return "y" + "'" * derece + " = " + ifade + f"   ({yontem}, n = {n})"


def seyrelt(tablo, en_fazla):
    # Tablodan eşit aralıklı en fazla `en_fazla` satır seç, son satırı her zaman dahil et
    atla = max(1, (len(tablo) - 1) // en_fazla)
    secilen = tablo.iloc[::atla]
    if secilen.index[-1] != tablo.index[-1]:
        secilen = pd.concat([secilen, tablo.iloc[[-1]]])
    return secilen


@app.route("/", methods=["GET", "POST"])
def ana_sayfa():
    mesaj = ""
    ifade = "3*exp(-x) - 0.4*y"
    derece = 1
    x0 = 0.0
    baslangiclar = [5.0, 0.0, 0.0]
    xmax = 3.0
    yontem = "euler"
    n = 30
    sutunlar = []
    satirlar = []
    hata_var = False
    son_degerler = []
    grafik_verisi = None

    if request.method == "POST":
        ifade, derece, x0, baslangiclar, xmax, yontem, n = formu_oku()

        try:
            tablo = coz(ifade, x0, baslangiclar[:derece], xmax, yontem, n)
        except CozumHatasi as hata:
            mesaj = str(hata)
            hata_var = True
        else:
            son = tablo.iloc[-1]
            yontem_adi = dict(YONTEM_ADLARI)[yontem]
            mesaj = f"{yontem_adi} · {n} adım · x = {son['x']:.6g} noktasında"
            for sutun in tablo.columns[1:]:
                son_degerler.append((sutun, f"{son[sutun]:.6g}"))

            secilen = seyrelt(tablo, 15)
            sutunlar = list(tablo.columns)
            for i, satir in secilen.iterrows():
                hucreler = [i]
                for sutun in sutunlar:
                    hucreler.append(f"{satir[sutun]:.6g}")
                satirlar.append(hucreler)

            # Animasyonu tarayıcı çizecek: ona sadece sayıları gönderiyoruz
            noktalar = seyrelt(tablo, GRAFIK_EN_FAZLA_NOKTA)
            grafik_verisi = {
                "baslik": grafik_basligi(derece, ifade, yontem, n),
                "x": noktalar["x"].tolist(),
                "seriler": [
                    {"ad": sutun, "degerler": noktalar[sutun].tolist()}
                    for sutun in tablo.columns[1:]
                ],
                # GIF indirilirken aynı çözüm yeniden hesaplanır
                "parametreler": {
                    "ifade": ifade,
                    "derece": derece,
                    "x0": x0,
                    "xmax": xmax,
                    "y0": baslangiclar[0],
                    "yp0": baslangiclar[1],
                    "ypp0": baslangiclar[2],
                    "yontem": yontem,
                    "n": n,
                },
            }

    return render_template(
        "index.html",
        mesaj=mesaj,
        ifade=ifade,
        derece=derece,
        etiket="y" + "'" * derece,
        x0=x0,
        baslangiclar=baslangiclar,
        xmax=xmax,
        yontem_adlari=YONTEM_ADLARI,
        secili_yontem=yontem,
        n=n,
        sutunlar=sutunlar,
        satirlar=satirlar,
        hata=hata_var,
        son_degerler=son_degerler,
        grafik_verisi=grafik_verisi,
    )


@app.route("/indir", methods=["POST"])
def indir():
    ifade, derece, x0, baslangiclar, xmax, yontem, n = formu_oku()

    try:
        tablo = coz(ifade, x0, baslangiclar[:derece], xmax, yontem, n)
    except CozumHatasi as hata:
        return str(hata)

    csv_yazi = tablo.to_csv(index=False, sep=";", decimal=",")
    return Response(
        csv_yazi,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=cozum.csv"},
    )


@app.route("/gif", methods=["POST"])
def gif_indir():
    ifade, derece, x0, baslangiclar, xmax, yontem, n = formu_oku()

    try:
        tablo = coz(ifade, x0, baslangiclar[:derece], xmax, yontem, n)
    except CozumHatasi as hata:
        return str(hata), 400

    baslik = grafik_basligi(derece, ifade, yontem, n)
    gif = animasyonlu_grafik(tablo, baslik, en_fazla_kare=GIF_KARE_SAYISI)
    return Response(
        base64.b64decode(gif),
        mimetype="image/gif",
        headers={"Content-Disposition": "attachment; filename=cozum.gif"},
    )


if __name__ == "__main__":
    app.run(debug=True)
