# ODE Çözücü — Hesaplamalı Fizik Notları

Bu belge, programın **sayısal yöntem tarafını** anlatır: adi diferansiyel denklemlerin (ODE) nasıl
temsil edildiğini, yüksek dereceli denklemlerin nasıl birinci dereceye indirgendiğini ve tüm
yöntemlerin tek bir ortak çözücüde nasıl çalıştığını. Kodun tamamı `cozucu.py` dosyasındadır.

---

## 1. Çözülen problem

Program, aşağıdaki biçimdeki **başlangıç değer problemlerini** çözer:

$$
y^{(n)} = g\left(x,\; y,\; y',\; \dots,\; y^{(n-1)}\right), \qquad n = 1, 2, 3
$$

Kullanıcı sadece **en yüksek türevin neye eşit olduğunu** (`g`'yi), aralığı (`x₀`, `xmax`), başlangıç
değerlerini ve adım sayısını (`n`) verir. Program `[x₀, xmax]` aralığını `n` eşit parçaya böler ve
çözümü her adımda sayısal olarak ilerletir:

$$
h = \frac{x_{max} - x_0}{n}
$$

---

## 2. Dereceyi indirgeme: her şey birinci dereceye döner

Euler ve Runge-Kutta yöntemleri yalnızca **birinci dereceden** denklemler için tanımlıdır: bir noktadaki
eğime (y') bakıp bir adım atarlar. Daha yüksek dereceli denklemler bu yüzden yeni değişkenler
tanımlanarak **birinci dereceden bir sisteme** çevrilir.

### Örnek (2. derece)

$$
3y'' + 2y' + 5y = e^{-x}, \qquad y(0) = 5,\; y'(0) = 7
$$

Yeni değişken $z = y'$ tanımlanır. O zaman $y'' = z'$ olur ve denklem iki birinci dereceden denkleme ayrılır:

$$
\begin{aligned}
y' &= z, & y(0) &= 5 \\
z' &= \tfrac{1}{3}\left(e^{-x} - 2z - 5y\right), & z(0) &= 7
\end{aligned}
$$

### Genel kural (n. derece)

$y_0 = y,\; y_1 = y',\; \dots,\; y_{n-1} = y^{(n-1)}$ tanımlanırsa:

$$
\begin{aligned}
y_0' &= y_1 \\
y_1' &= y_2 \\
&\;\;\vdots \\
y_{n-1}' &= g(x, y_0, y_1, \dots, y_{n-1})
\end{aligned}
$$

İlk $n-1$ denklem her zaman "bir değişkenin türevi bir sonrakidir" şeklindedir. Fiziksel içerik
yalnızca son denklemde, yani kullanıcının yazdığı $g$'dedir.

---

## 3. Durum vektörü ve `sisteme_cevir`

Sistemin o anki durumu tek bir **durum vektörü** ile tutulur:

$$
\mathbf{Y} = \left[\, y,\; y',\; y'' \,\right]
$$

(1. derecede tek elemanlı, 2. derecede iki elemanlı, 3. derecede üç elemanlı.)

Bu vektörün türevini üreten fonksiyon `sisteme_cevir` ile kurulur:

```python
def sisteme_cevir(g, derece):
    def F(x, Y):
        turevler = np.zeros(derece)
        for k in range(derece - 1):
            turevler[k] = Y[k + 1]        # y_k' = y_{k+1}
        turevler[derece - 1] = g(x, Y)    # en yüksek türev: kullanıcının denklemi
        return turevler
    return F
```

Sonuçta problem her derecede aynı biçime gelir:

$$
\mathbf{Y}' = \mathbf{F}(x, \mathbf{Y})
$$

Derece ayrıca bir parametre olarak sorulmaz. **Verilen başlangıç değeri sayısı dereceyi belirler**
(`len(Y0)`). Böylece "derece 2 ama 3 başlangıç değeri" gibi tutarsız bir durum oluşamaz.

---

## 4. Yöntemler

Her yöntem aynı işi yapar: $(x_i, \mathbf{Y}_i)$ noktasından $x_{i+1} = x_i + h$ noktasına **tek bir adım**
atar ve $\mathbf{Y}_{i+1}$'i döndürür.

| Yöntem | Formül | Yerel hata | Toplam hata |
|---|---|---|---|
| **Euler** | $\mathbf{Y}_{i+1} = \mathbf{Y}_i + h\,\mathbf{F}(x_i, \mathbf{Y}_i)$ | $O(h^2)$ | $O(h)$ |
| **Heun** (= Modified Euler) | $\mathbf{k}_1 = \mathbf{F}(x_i, \mathbf{Y}_i)$, $\;\mathbf{k}_2 = \mathbf{F}(x_i + h, \mathbf{Y}_i + h\mathbf{k}_1)$, $\;\mathbf{Y}_{i+1} = \mathbf{Y}_i + \tfrac{h}{2}(\mathbf{k}_1 + \mathbf{k}_2)$ | $O(h^3)$ | $O(h^2)$ |
| **Midpoint** | $\mathbf{k}_2 = \mathbf{F}(x_i + \tfrac{h}{2}, \mathbf{Y}_i + \tfrac{h}{2}\mathbf{k}_1)$, $\;\mathbf{Y}_{i+1} = \mathbf{Y}_i + h\,\mathbf{k}_2$ | $O(h^3)$ | $O(h^2)$ |
| **Ralston** | $\mathbf{k}_2 = \mathbf{F}(x_i + \tfrac{3}{4}h, \mathbf{Y}_i + \tfrac{3}{4}h\mathbf{k}_1)$, $\;\mathbf{Y}_{i+1} = \mathbf{Y}_i + h\left(\tfrac{1}{3}\mathbf{k}_1 + \tfrac{2}{3}\mathbf{k}_2\right)$ | $O(h^3)$ | $O(h^2)$ |
| **RK4** | $\mathbf{Y}_{i+1} = \mathbf{Y}_i + \tfrac{h}{6}(\mathbf{k}_1 + 2\mathbf{k}_2 + 2\mathbf{k}_3 + \mathbf{k}_4)$ | $O(h^5)$ | $O(h^4)$ |

**Not:** Modified Euler ve Heun **aynı yöntemdir**. İkisi de önce Euler ile bir tahmin adımı atar, sonra
başlangıçtaki eğimle tahmin noktasındaki eğimin ortalamasıyla asıl adımı atar. Kodda iki farklı
yazımla duruyorlar ve her zaman birebir aynı sonucu verirler. Midpoint, Ralston ve Heun, ikinci
dereceden Runge-Kutta ailesinin üyeleridir: hepsinde iki eğim (k₁, k₂) hesaplanır, ama k₂'nin alındığı
nokta ve ağırlıklar farklıdır.

### Aynı fonksiyonlar neden her derecede çalışıyor?

Yöntem fonksiyonları yalnızca toplama ve sayıyla çarpma işlemleri kullanır. `numpy` dizileri bu
işlemleri **eleman eleman** yaptığı için, aynı satır skaler bir $y$ için de, $[y, z]$ gibi bir vektör
için de doğru çalışır. Örneğin Euler satırı 2. derecede:

$$
[y,\, z] + h\,[z,\, f_2] = [\,y + h z,\;\; z + h f_2\,]
$$

Bu, hocanın notlarındaki iki ayrı Euler denkleminin ($y_{i+1} = y_i + f_1 h$, $z_{i+1} = z_i + f_2 h$)
ta kendisidir. Bu sayede 2. ve 3. derece için ayrı ayrı `euler_2nd`, `rk4_2nd` gibi fonksiyonlar
yazmaya gerek kalmaz.

---

## 5. Ortak çözücü: `coz_sistem`

Bütün dereceler ve bütün yöntemler **tek bir döngüden** geçer:

```python
def coz_sistem(g, derece, x0, Y0, xmax, yontem, n):
    F = sisteme_cevir(g, derece)          # n. derece → birinci dereceden sistem
    adim = YONTEMLER[yontem]              # seçilen yöntemin tek-adım fonksiyonu

    h = (xmax - x0) / n
    xi = x0
    Yi = np.array(Y0, dtype=float)
    ...
    for i in range(n):                    # tam n adım, tam xmax'ta biter
        xf = xi + h
        Yf = adim(F, xi, Yi, xf)
        ...
        xi, Yi = xf, Yf
```

- **Yöntem seçimi:** Bir sözlükten (`YONTEMLER`) yapılır. Yeni bir yöntem eklemek için tek-adım
  fonksiyonunu yazıp sözlüğe bir satır eklemek yeterlidir.
- **Döngü:** `while x < xmax` yerine `for i in range(n)` ile kurulmuştur. Kayan nokta toplamalarındaki
  yuvarlama yüzünden `while` döngüsü bazen fazladan bir adım atıp `xmax`'ı geçebiliyordu. `for`
  döngüsü her zaman tam `n` adım atar.
- **Çıktı:** Bir `pandas.DataFrame`'dir. Sütunları `x, y, y', y''` (dereceye göre), satırları adımlardır.
  Türevler de durum vektörünün parçası olduğu için ek bir hesap yapılmadan tabloya girer.

---

## 6. Metinden fonksiyona: `metinden_fonksiyon`

Kullanıcı denklemi yazı olarak girer, örneğin `(exp(-x) - 2*y' - 5*y)/3`. Bu yazı bir kez
derlenir, sonra her adımda bir Python fonksiyonu gibi çağrılır.

```python
def metinden_fonksiyon(ifade):
    ifade = ifade.replace("^", "**")    # x^2 → x**2
    ifade = ifade.replace("y''", "y2")  # önce uzun olan!
    ifade = ifade.replace("y'", "y1")
    kod = compile(ifade, "<denklem>", "eval")

    def g(x, Y):
        degiskenler = dict(IZINLI)       # exp, sin, cos, tan, sqrt, log, pi, e
        degiskenler["x"] = x
        degiskenler["y"] = Y[0]
        for k in range(1, len(Y)):
            degiskenler["y" + str(k)] = Y[k]   # y1 = y', y2 = y''
        return eval(kod, {"__builtins__": {}}, degiskenler)

    return g
```

1. **Türev gösterimi:** Python değişken adında `'` karakterine izin vermez. Bu yüzden `y''` → `y2` ve
   `y'` → `y1` çevirisi yapılır. Sıra önemlidir: `y'` önce çevrilirse `y''` yazısı `y1'` haline gelip bozulur.
2. **`compile`:** Yazı bir kez derlenir. Böylece yazım hataları çözüm başlamadan yakalanır, ve her
   adımda yazının yeniden ayrıştırılması gerekmez.
3. **Değişkenleri bağlamak:** Her çağrıda durum vektörünün elemanları isimlere bağlanır:
   `y = Y[0]`, `y1 = Y[1]`, `y2 = Y[2]`. Vektörde olmayan bir türev (örneğin 1. dereceden bir
   denklemde `y'`) tanımsız kalır, ve bu bir `NameError` olarak yakalanıp anlaşılır bir mesaja çevrilir.
4. **Sınırlı isim alanı:** `eval` yalnızca `IZINLI` sözlüğündeki matematik fonksiyonlarını ve
   `x, y, y1, y2` değişkenlerini görür. Bütün fonksiyonlar `numpy` sürümleridir (`np.exp`, `np.sin`, …).

Ortaya çıkan `g(x, Y)`, 3. bölümdeki `sisteme_cevir`'in beklediği biçimdedir. Yani metin → fonksiyon →
sistem → ortak çözücü zinciri hiçbir dereceye özel kod içermez.

---

## 7. Sayısal hata denetimi

Dışarıya açılan tek fonksiyon `coz(...)`'dur. Girdileri kontrol eder, çözümü çalıştırır ve olası
bütün hataları tek bir `CozumHatasi` türüne çevirir.

- **Kayan nokta hataları:** Çözüm `np.errstate(all="raise")` bloğu içinde çalışır. `numpy` normalde
  $\sqrt{-1}$, $\log 0$ ya da taşma (overflow) gibi durumlarda hata vermez, sessizce `nan` veya `inf`
  üretip devam eder. Bu blok bu durumları `FloatingPointError`'a dönüştürür. Ayar sadece blok
  süresince geçerlidir, programın geri kalanını etkilemez.
- **Patlayan çözümler:** Örneğin $y' = y^2,\; y(0) = 1$ denkleminin gerçek çözümü $y = 1/(1-x)$'tir ve
  $x = 1$'de sonsuza gider. Bu yüzden $x = 2$'ye kadar bir çözüm yoktur. Program bu durumda anlamsız
  bir tablo üretmek yerine "çözüm patlamış olabilir" uyarısı verir.
- **Diğer kontroller:** $x_{max} > x_0$, $n \geq 1$, derecenin 1–3 aralığında olması ve yöntemin bilinmesi.

---

## 8. Doğrulama

| Test | Yöntem / adım | Beklenen | Program |
|---|---|---|---|
| $y'' + 2y' + y = e^{-t}$, $y(0)=1$, $y'(0)=2$, $y(0.75)$ = ? | Euler, $h = 0.25$ | elle hesap: 1.829925 | **1.829925** |
| $y''' = 6$, $y(0)=y'(0)=y''(0)=0$ → $y = x^3$ | RK4, 10 adım | $y(1)=1,\; y'(1)=3,\; y''(1)=6$ | **1, 3, 6** |
| $y' = 3e^{-x} - 0.4y$, $y(0)=5$, $y(3)$ = ? | Euler, $h = 0.1$ | hocanın `simpleEuler-0.1000.dat` dosyası: 2.796659 | **2.796659** |
| Basit sarkaç $\theta'' = -9.8\sin\theta$, $\theta_0 = 0.2$ | RK4, 30 adım | genlik korunur (±0.2 rad) | $\theta(3) = -0.199632$ |

### Yakınsama

$y' = 3e^{-x} - 0.4y$, $y(0) = 5$ için gerçek çözüm $y = 10e^{-0.4x} - 5e^{-x}$, yani $y(3) = 2.763007$:

| $h$ | Euler hatası | Heun hatası |
|---|---|---|
| 0.1 | $3.4 \times 10^{-2}$ | $6.0 \times 10^{-4}$ |
| 0.01 | $3.3 \times 10^{-3}$ | $6.1 \times 10^{-6}$ |
| 0.001 | $3.3 \times 10^{-4}$ | $6.2 \times 10^{-8}$ |

$h$ 10 kat küçülünce Euler'in hatası **10 kat**, Heun'un hatası **100 kat** azalır. Bu, sırasıyla
1. ve 2. dereceden yöntem olmalarının doğrudan sonucudur.

### Enerji korunumu

Sürtünmesiz sarkaçta enerji korunmalıdır, yani salınımın genliği sabit kalmalıdır.
$\theta_0 = 0.2$ rad, $h = 0.1$ (30 adım) ile $t = 3$ s'de:

- **RK4:** $\theta = -0.1996$. Genlik korunuyor.
- **Euler:** $\theta = -0.727$. Genlik 0.2 rad'dan 0.73 rad'a çıkıyor.

Euler sisteme **yapay enerji ekler**. Adım sayısı 3000'e çıkarılsa bile ($\theta = -0.2026$) RK4'ün
30 adımdaki doğruluğuna ulaşamaz. Salınım problemlerinde yüksek mertebeli yöntemlerin tercih
edilmesinin sebebi budur.

---

## 9. Sınırlamalar

- **Sabit adım:** Tüm yöntemler sabit adım büyüklüğüyle çalışır. Uyarlamalı adım (adaptive step) yoktur.
- **Açık yöntemler:** Kullanılan yöntemlerin hepsi açık (explicit) yöntemlerdir. Katı (stiff)
  denklemlerde küçük $h$ gerektirebilir ya da kararsızlaşabilir.
- **En fazla 3. derece:** Bu sınır yalnızca arayüzden ve tablo sütun adlarından gelir. Matematik
  (`sisteme_cevir` ve `coz_sistem`) herhangi bir derecede çalışır.
- **Tek denklem:** Birbirine bağlı sistemler (örneğin av-avcı modeli) şimdilik doğrudan girilemez,
  ancak durum vektörü yapısı buna hazırdır.
- **Güvenlik:** `eval` sınırlı bir isim alanıyla kullanılır, ama bu bir güvenlik garantisi değildir.
  Herkese açık bir sunucu için ifadenin `ast` modülüyle ayrıştırılıp yalnızca izin verilen işlemlerin
  kabul edilmesi gerekir.
