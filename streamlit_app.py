import streamlit as st

st.set_page_config(
    page_title="Kalkulator MPKK | BCP LAW",
    page_icon="logo_bcp.png",
    layout="centered"
)

# Logo i nagłówek
st.image("logo_bcp.png", width=180)
st.markdown(
    "<h1 style='margin-bottom:0.2em;'>Kalkulator MPKK</h1>"
    "<div style='color:#333; font-size:1.1rem; margin-bottom:1em;'>"
    "Oblicz maksymalne pozaodsetkowe koszty kredytu konsumenckiego według aktualnych przepisów."
    "</div>",
    unsafe_allow_html=True
)

st.divider()

# Termin zawarcia umowy
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

st.divider()

# Kwota kredytu
st.header("Podaj kwotę kredytu", divider="gray")
st.markdown(
    """
    Kwota kredytu musi mieścić się w przedziale **od 0 do 255&nbsp;550 złotych**.
    <br>Możesz wpisać w formacie: <code>100000</code>, <code>100.000</code>, <code>240000,12</code>, <code>240.000,12</code> itp.
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

K = parse_amount(kwota_str) if kwota_str else None

def format_pln(amount):
    return f"{amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

if kwota_str:
    if K is None or K < 0 or K > 255550:
        st.error("Podaj poprawną kwotę kredytu z zakresu od 0 do 255 550 zł.")
    else:
        st.divider()
        # Okres spłaty
        st.header("Podaj okres spłaty", divider="gray")
        st.info(
            "Rekomendacja: dla największej precyzji zalecamy wpisywanie okresu spłaty w dniach. "
            "Liczba dni w poszczególnych miesiącach różni się, dlatego podanie okresu w miesiącach może powodować niewielkie rozbieżności w wyniku."
        )

        input_type = st.radio("Wybierz sposób podania okresu spłaty:", ("W miesiącach", "W dniach"), key="okres")
        if input_type == "W miesiącach":
            months = st.number_input("Okres spłaty (miesiące):", min_value=1, step=1, key="miesiace")
            n = months * 30.42
        else:
            n = st.number_input("Okres spłaty (dni):", min_value=1, step=1, key="dni")

        R = 365

        st.divider()
        st.header("Wynik i wzór MPKK", divider="gray")

        # Opisy wzorów
        if choice == "1":
            st.info("**Wybrano wzór:**\n"
                    "MPKK = (K × 25%) + (K × n/R × 30%)\n"
                    "Maksymalna wysokość MPKK = całkowita kwota kredytu")
            limit_info = "maksymalna wysokość MPKK = całkowita kwota kredytu"
        elif choice == "2":
            st.info("""**Wybrano wzór:**  
- Dla okresu **krótszego niż 30 dni**: MPKK = K × 5%  
- Dla okresu **równego lub dłuższego niż 30 dni**: MPKK = (K × 15%) + (K × n/R × 6%)  
Maksymalna wysokość MPKK = 45% całkowitej kwoty kredytu""")
            limit_info = "maksymalna wysokość MPKK = 45% całkowitej kwoty kredytu"
        elif choice == "3":
            st.info("**Wybrano wzór:**\n"
                    "MPKK = (K × 25%) + (K × n/R × 30%)\n"
                    "Maksymalna wysokość MPKK = całkowita kwota kredytu")
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
        <span style='font-size:0.85rem;'>Designed by Hubert Domański BCP LAW ® 2025</span>
    </div>
    """, unsafe_allow_html=True
)
