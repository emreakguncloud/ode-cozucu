from flask import Flask, render_template, request, Response
import pandas as pd
from cozucu import coz, CozumHatasi
from grafik import statik_grafik, animasyonlu_grafik

app = Flask(__name__)

YONTEM_ADLARI = [
    ("euler", "Euler"),
    ("mod_euler", "Modified Euler"),
    ("heun", "Heun"),
    ("midpoint", "Midpoint"),
    ("ralston", "Ralston"),
    ("rk4", "RK4"),
]


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
    grafik = ""
    gif = ""
    hata_var = False
    son_degerler = []

    if request.method == "POST":
        ifade, derece, x0, baslangiclar, xmax, yontem, n = formu_oku()

        try:
            tablo = coz(ifade, x0, baslangiclar[:derece], xmax, yontem, n)
        except CozumHatasi as hata:
            mesaj = str(hata)
            hata_var = True
        else:
            baslik = "y" + "'" * derece + " = " + ifade + f"   ({yontem}, n = {n})"
            grafik = statik_grafik(tablo, baslik)
            gif = animasyonlu_grafik(tablo, baslik)
            son = tablo.iloc[-1]
            yontem_adi = dict(YONTEM_ADLARI)[yontem]
            mesaj = f"{yontem_adi} · {n} adım · x = {son['x']:.6g} noktasında"
            for sutun in tablo.columns[1:]:
                son_degerler.append((sutun, f"{son[sutun]:.6g}"))

            atla = max(1, n // 15)
            secilen = tablo.iloc[::atla]
            if secilen.index[-1] != tablo.index[-1]:
                secilen = pd.concat([secilen, tablo.iloc[[-1]]])

            sutunlar = list(tablo.columns)
            for i, satir in secilen.iterrows():
                hucreler = [i]
                for sutun in sutunlar:
                    hucreler.append(f"{satir[sutun]:.6g}")
                satirlar.append(hucreler)

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
        grafik=grafik,
        gif=gif,
        hata=hata_var,
        son_degerler=son_degerler,
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


if __name__ == "__main__":
    app.run(debug=True)