import streamlit as st
import time

# Konfiguracja strony
st.set_page_config(
    page_title="Kalkulator MPKK | Salutaris Polska",
    page_icon="logo_bcp.png",
    layout="centered"
)

# Logo i nagłówek
with open("logo_bcp.png", "rb") as f:
    logo_data = f.read()
import base64
encoded_logo = base64.b64encode(logo_data).decode()

st.markdown(
    f"""
    <div style='text-align: center;'>
        <img src='data:image/png;base64,{encoded_logo}' style='width:300px;' />
    </div>
    """,
    unsafe_allow_html=True
)
st.markdown(
    "<h1 style='margin-bottom:0.2em;'>Kwalifikacja do SKD wraz z kalkulatorem MPKK</h1>"
    "<div style='color:#333; font-size:1.1rem; margin-bottom:1em;'>"
    "Sprawdź czy Twój kredyt się kwalifikuję oraz oblicz maksymalne pozaodsetkowe koszty kredytu konsumenckiego według aktualnych przepisów."
    "</div>",
    unsafe_allow_html=True
)
st.divider()

# --- 1. Termin zawarcia umowy
st.header("Wybierz termin zawarcia umowy kredytu", divider="gray")
terminy = [
    "11.03.2016 - 30.03.2020",
    "31.03.2020 - 30.06.2021",
    "01.07.2021 - 17.12.2022",
    "Od 18.12.2022"
]
choice_idx = st.radio(
    label="",
    options=list(range(len(terminy))),
    format_func=lambda i: terminy[i],
    index=0,
    key="termin"
)
choice = str(choice_idx + 1)

# Informacja o starszych umowach
st.warning(
    "Jeśli umowa została zawarta **przed 11 marca 2016 roku**, "
    "ale **po 18 grudnia 2011 roku**, "
    "możliwe jest zastosowanie SKD. Skontaktuj się z nami w celu indywidualnej analizy."
)

st.divider()

# --- 2. Rodzaj kredytu
st.header("Wybierz rodzaj kredytu", divider="gray")

# Lista wszystkich możliwych rodzajów
rodzaje_kredytu_all = [
    "🧾 Kredyt konsumencki",
    "💸 Umowa pożyczki",
    "💳 Kredyt odnawialny",
    "🏦 Kredyt w rozumieniu prawa bankowego",
    "🛠️ Kredyt niezabezpieczony hipoteką przeznaczony na remont nieruchomości",
    "🤝 Kredyt polegający na zaciągnięciu zobowiązania wobec osoby trzeciej z obowiązkiem zwrotu kredytodawcy określonego świadczenia",
    "⏳ Umowa o odroczeniu terminu spełnienia świadczenia pieniężnego",
    "🏡 Kredyt hipoteczny",
    "🚗 Leasing bez obowiązku nabycia przedmiotu przez konsumenta",
]

# Dynamiczna modyfikacja dostępnych opcji w zależności od wyboru terminu
rodzaje_kredytu = rodzaje_kredytu_all.copy()

if choice == "1":
    # Usuń "kredyt na remont" jeśli termin to 11.03.2016 - 30.03.2020
    rodzaje_kredytu = [r for r in rodzaje_kredytu if r != "🛠️ Kredyt niezabezpieczony hipoteką przeznaczony na remont nieruchomości"]

kredyt = st.selectbox(
    label="Rodzaj kredytu:",
    options=rodzaje_kredytu,
    key="rodzaj"
)

# Obsługa typów kredytów niekwalifikujących się + Tryb konsultacyjny
if kredyt in ["🏡 Kredyt hipoteczny", "🚗 Leasing bez obowiązku nabycia przedmiotu przez konsumenta"]:
    st.warning(
        "**Twoja sprawa może wymagać indywidualnej analizy.** "
        "Wybrany rodzaj kredytu nie kwalifikuje się do standardowego wyliczenia MPKK. "
        "Skontaktuj się z prawnikiem lub doradcą finansowym."
    )
    st.stop()

# --- 3. Kwota kredytu
st.header("Podaj kwotę kredytu", divider="gray")
st.markdown(
    """
    Kwota kredytu musi mieścić się w przedziale **od 0 do 255&nbsp;550 złotych**,
    chyba że wybrałeś kredyt na remont nieruchomości **(wtedy limit nie obowiązuje)**.
    <br>Możesz wpisać w formacie: <code>100000</code>, <code>100.000</code>, <code>240000,12</code> itp.
    """, unsafe_allow_html=True
)
kwota_str = st.text_input("Kwota kredytu:", value="", key="kwota")

def parse_amount(amount_str):
    amount_str = amount_str.replace(" ", "")
    if "," in amount_str and "." in amount_str:
        amount_str = amount_str.replace(".", "").replace(",", ".")
    elif "," in amount_str:
        amount_str = amount_str.replace(",", ".")
    else:
        amount_str = amount_str.replace(".", "")
    try:
        value = float(amount_str)
        return value
    except ValueError:
        return None

def format_pln(amount):
    return f"{amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

K = parse_amount(kwota_str) if kwota_str else None

if kwota_str:
    if K is None or K < 0 or (K > 255550 and kredyt != "🛠️ Kredyt niezabezpieczony hipoteką przeznaczony na remont nieruchomości"):
        st.error("Podaj poprawną kwotę kredytu zgodną z limitem.")
        st.stop()

st.divider()

# --- 4. Okres spłaty
st.header("Podaj okres spłaty", divider="gray")
st.info(
    "Rekomendacja: dla największej precyzji zalecamy wpisywanie okresu spłaty w dniach. "
    "Liczba dni w poszczególnych miesiącach różni się, dlatego podanie okresu w miesiącach może powodować niewielkie rozbieżności w wyniku."
)

input_type = st.radio("Wybierz sposób podania okresu spłaty:", ("W miesiącach", "W dniach"), key="okres")

with st.expander("⚙️ Opcjonalnie: Ustawienia liczby dni w roku i miesiącu"):
    st.markdown(
        """
        Domyślnie rok przyjmowany jest jako **365 dni**, a miesiąc jako **30,42 dnia**.  
        Jeśli Twoja umowa wskazuje inne wartości (np. rok = 360 dni, miesiąc = 30 dni), możesz je zmienić tutaj.
        """
    )
    col1, col2 = st.columns(2)
    with col1:
        days_in_year = st.number_input("Liczba dni w roku:", min_value=1, max_value=400, value=365, step=1, key="dni_rok")
    with col2:
        days_in_month = st.number_input("Liczba dni w miesiącu:", min_value=1.0, max_value=31.0, value=30.42, step=0.01, key="dni_miesiac")

# Walidacja wartości roku i miesiąca
if days_in_year < 300 or days_in_year > 400:
    st.warning(f"⚠️ Wybrałeś nietypową liczbę dni w roku: {days_in_year} dni. Standardowo przyjmuje się 365.")

if days_in_month < 25 or days_in_month > 31:
    st.warning(f"⚠️ Wybrałeś nietypową liczbę dni w miesiącu: {days_in_month:.2f} dni. Standardowo przyjmuje się 30,42.")

# Wyliczanie okresu n
if input_type == "W miesiącach":
    months = st.number_input("Okres spłaty (w miesiącach):", min_value=1, step=1, key="miesiace")
    n = months * days_in_month
else:
    n = st.number_input("Okres spłaty (w dniach):", min_value=1, step=1, key="dni")

# Rok do wzoru
R = days_in_year

st.divider()

# --- 5. Wzór i wyliczenia
st.header("Wzór MPKK", divider="gray")
if choice == "1":
    st.info("**Wybrano wzór:**\nMPKK = (K × 25%) + (K × n/R × 30%)\nMaksymalna wysokość MPKK = całkowita kwota kredytu")
    limit_info = "maksymalna wysokość MPKK = całkowita kwota kredytu"
elif choice == "2":
    st.info("""**Wybrano wzór:**  
- Dla okresu **krótszego niż 30 dni**: MPKK = K × 5%  
- Dla okresu **równego lub dłuższego niż 30 dni**: MPKK = (K × 15%) + (K × n/R × 6%)  
Maksymalna wysokość MPKK = 45% całkowitej kwoty kredytu""")
    limit_info = "maksymalna wysokość MPKK = 45% całkowitej kwoty kredytu"
elif choice == "3":
    st.info("**Wybrano wzór:**\nMPKK = (K × 25%) + (K × n/R × 30%)\nMaksymalna wysokość MPKK = całkowita kwota kredytu")
    limit_info = "maksymalna wysokość MPKK = całkowita kwota kredytu"
elif choice == "4":
    st.info("""**Wybrano wzór:**  
- Dla okresu **krótszego niż 30 dni**: MPKK = K × 5%  
- Dla okresu **równego lub dłuższego niż 30 dni**: MPKK = (K × 10%) + (K × n/R × 10%)  
Maksymalna wysokość MPKK = 45% całkowitej kwoty kredytu""")
    limit_info = "maksymalna wysokość MPKK = 45% całkowitej kwoty kredytu"

if st.button("Oblicz MPKK"):
    is_short_term = n < 30

    if choice in ["1", "3"]:
        mpkk_wzor = (K * 0.25) + (K * n / R * 0.30)
        formula = "MPKK = (K × 25%) + (K × n/R × 30%)"
        limit = K
    elif choice == "2":
        if is_short_term:
            mpkk_wzor = K * 0.05
            formula = "MPKK = K × 5% (dla okresu krótszego niż 30 dni)"
        else:
            mpkk_wzor = (K * 0.15) + (K * n / R * 0.06)
            formula = "MPKK = (K × 15%) + (K × n/R × 6%) (dla okresu równego lub dłuższego niż 30 dni)"
        limit = K * 0.45
    elif choice == "4":
        if is_short_term:
            mpkk_wzor = K * 0.05
            formula = "MPKK = K × 5% (dla okresu krótszego niż 30 dni)"
        else:
            mpkk_wzor = (K * 0.10) + (K * n / R * 0.10)
            formula = "MPKK = (K × 10%) + (K × n/R × 10%) (dla okresu równego lub dłuższego niż 30 dni)"
        limit = K * 0.45

    MPKK = min(mpkk_wzor, limit)

    st.success(f"**Obliczona maksymalna wysokość pozaodsetkowych kosztów kredytu:** {format_pln(MPKK)} zł")
    st.write(f"**Użyty wzór:** {formula}")
    st.write(f"**Wynik MPKK według wzoru:** {format_pln(mpkk_wzor)} zł")

    if mpkk_wzor > limit:
        st.warning(
            f"MPKK według wzoru przekracza limit, {limit_info}. Limit wynosi: {format_pln(limit)} zł"
        )
    else:
        st.info("MPKK według wzoru mieści się w ustawowym limicie.")

st.divider()
st.markdown(
    """
    <div style="text-align:center; color:#888; font-size:0.95rem;">
        Kalkulator nie stanowi porady prawnej.<br>
        W razie wątpliwości skonsultuj się z prawnikiem lub doradcą finansowym.<br>
        <br>
        <span style='font-size:0.85rem;'>Designed by Hubert Domański Salutaris Polska ® 2025</span>
    </div>
    """, unsafe_allow_html=True
)
