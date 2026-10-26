import numpy as np
import pandas as pd

# Kullanıcının denkleminde yazabileceği isimler
IZINLI = {
    "exp": np.exp,
    "sin": np.sin,
    "cos": np.cos,
    "tan": np.tan,
    "sqrt": np.sqrt,
    "log": np.log,
    "pi": np.pi,
    "e": np.e,
}

TUREV_UYARILARI = {
    "y1": "y' ancak 2. ve 3. dereceden denklemlerde kullanılabilir",
    "y2": "y'' ancak 3. dereceden denklemlerde kullanılabilir",
}

class CozumHatasi(Exception):
    pass

# ---------- DENKLEMLER: y' = f(x, y) ----------

def metinden_fonksiyon(ifade):
    ifade = ifade.replace("^", "**")
    ifade = ifade.replace("y''", "y2")
    ifade = ifade.replace("y'", "y1")
    kod = compile(ifade, "<denklem>", "eval")

    def g(x, Y):
        degiskenler = dict(IZINLI)
        degiskenler["x"] = x
        degiskenler["y"] = Y[0]
        for k in range(1, len(Y)):
            degiskenler["y" + str(k)] = Y[k]
        return eval(kod, {"__builtins__": {}}, degiskenler)

    return g

# ---------- YÖNTEMLER: bir adım at, yf'yi döndür ----------

def euler1d(f, xi, yi, xf):
    yf = yi + f(xi, yi) * (xf - xi)
    return yf

def euler1m(f, xi, yi, xf):
    yf = yi + f(xi, yi) * (xf - xi)
    yf = yi + (f(xi, yi) + f(xf, yf)) * 0.5 * (xf - xi)
    return yf

def rk2_1st_heun(f, xi, yi, xf):
    k1 = f(xi, yi)
    k2 = f(xf, yi + k1 * (xf - xi))
    yf = yi + 0.5 * (f(xi, yi) + k2) * (xf - xi)
    return yf

def rk2_1st_midpoint(f, xi, yi, xf):
    k1 = f(xi, yi)
    k2 = f(xi + 0.5 * (xf - xi), yi + 0.5 * k1 * (xf - xi))
    yf = yi + k2 * (xf - xi)
    return yf

def rk2_1st_ralston(f, xi, yi, xf):
    h = xf - xi
    k1 = f(xi, yi)
    k2 = f(xi + 0.75 * h, yi + 0.75 * k1 * h)
    yf = yi + ((1. / 3) * k1 + (2. / 3) * k2) * h
    return yf

def rk4_1st(f, xi, yi, xf):
    h = xf - xi
    k1 = f(xi, yi)
    k2 = f(xi + h / 2.0, yi + (k1 * h) / 2.0)
    k3 = f(xi + h / 2.0, yi + (k2 * h) / 2.0)
    k4 = f(xi + h, yi + k3 * h)
    yf = yi + ((k1 + 2.0 * (k2 + k3) + k4) * h) / 6.0
    return yf

def sisteme_cevir(g, derece):
    def F(x, Y):
        turevler = np.zeros(derece)
        for k in range(derece - 1):
            turevler[k] = Y[k + 1]
        turevler[derece - 1] = g(x, Y)
        return turevler
    return F
# ---------- SEÇİM TABLOLARI ----------

# yöntem kodu -> adım fonksiyonu
YONTEMLER = {
    "euler": euler1d,
    "mod_euler": euler1m,
    "heun": rk2_1st_heun,
    "midpoint": rk2_1st_midpoint,
    "ralston": rk2_1st_ralston,
    "rk4": rk4_1st,
}

# ---------- ÇÖZÜCÜ ----------
def coz_sistem(g, derece, x0, Y0, xmax, yontem, n):
    F = sisteme_cevir(g, derece)
    adim = YONTEMLER[yontem]

    h = (xmax - x0) / n
    xi = x0
    Yi = np.array(Y0, dtype=float)
    xler = [xi]
    Yler = [Yi]

    for i in range(n):
        xf = xi + h
        Yf = adim(F, xi, Yi, xf)
        xler.append(xf)
        Yler.append(Yf)
        xi = xf
        Yi = Yf

    Yler = np.array(Yler)
    tablo = pd.DataFrame({"x": xler})
    isimler = ["y", "y'", "y''"]
    for k in range(derece):
        tablo[isimler[k]] = Yler[:, k]
    return tablo

def coz(ifade, x0, Y0, xmax, yontem, n):
    if xmax <= x0:
        raise CozumHatasi("xmax, x0'dan büyük olmalı")
    if n < 1:
        raise CozumHatasi("Adım sayısı en az 1 olmalı")
    if len(Y0) < 1 or len(Y0) > 3:
        raise CozumHatasi("Derece 1, 2 ya da 3 olmalı")
    if yontem not in YONTEMLER:
        raise CozumHatasi(f"Bilinmeyen yöntem: {yontem}")

    try:
        g = metinden_fonksiyon(ifade)
        with np.errstate(all="raise"):# Program patlamıyor son fonksiyonda durup kaynağa hata bildirimi gönderiyor.
            tablo = coz_sistem(g, len(Y0), x0, Y0, xmax, yontem, n)
    except SyntaxError:
        raise CozumHatasi("Denklemde yazım hatası var, parantezleri kontrol et")
    except NameError as hata:
        if hata.name in TUREV_UYARILARI:
            raise CozumHatasi(TUREV_UYARILARI[hata.name])
        raise CozumHatasi(f"Tanımsız isim: {hata.name} (sadece x, y, y', y'' ve izinli fonksiyonları kullan)")
    except ZeroDivisionError:
        raise CozumHatasi("Sıfıra bölme oluştu")
    except FloatingPointError:
        raise CozumHatasi("Hesaplama tanımsız ya da sonsuz bir değere ulaştı (çözüm patlamış olabilir)")
    except Exception as hata:
        raise CozumHatasi(f"Hesaplama hatası: {hata}")

    return tablo

# ---------- TEST (sadece bu dosya doğrudan çalışınca) ----------

if __name__ == "__main__":
    # Hocanın 2. örneği: y'' + 2y' + y = e^(-t), Euler h=0.25
    print(coz("exp(-x) - 2*y' - y", 0.0, [1, 2], 0.75, "euler", 3))

    # Sarkaç
    print(coz("-9.8*sin(y)", 0.0, [0.2, 0], 3.0, "rk4", 30).tail(1))

    # 3. derece: y''' = 6 → y = x³
    print(coz("6", 0.0, [0, 0, 0], 1.0, "rk4", 10).tail(1))

    # Hocanın 1. örneği: 3y'' + 2y' + 5y = e^(-x)
    print(coz("(exp(-x) - 2*y' - 5*y)/3", 0.0, [5, 7], 1.0, "rk4", 10).tail(1))

    # 1. derece hâlâ çalışıyor mu?
    print(coz("3*exp(-x) - 0.4*y", 0.0, [5.0], 3.0, "euler", 30).tail(1))

    # Yanlış derecede türev kullanmak
    for ifade, Y0 in [("y' + y", [1.0]), ("y'' + y", [1.0, 0.0]), ("3*z", [1.0, 0.0])]:
        try:
            coz(ifade, 0.0, Y0, 1.0, "euler", 10)
        except CozumHatasi as hata:
            print(ifade, "->", hata)
