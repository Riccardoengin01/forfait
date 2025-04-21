import streamlit as st


st.title("📊 Calcolo tasse regime forfettario")

st.markdown("""
Questa app ti aiuta a calcolare quante **tasse hai maturato finora** in regime forfettario, 
in base al tuo **fatturato attuale** e alla tua situazione fiscale.
""")

# === INPUT ===

st.header("📥 Inserisci i tuoi dati")

fatturato = st.number_input("Inserisci il tuo fatturato attuale (€)", min_value=0.0, format="%.2f")

# Codici ATECO → Coefficiente di redditività
ateco_dict = {
    "Grafico (74.10.29) – 78%": 0.78,
    "Commerciante – 40%": 0.40,
    "Artigiano generico – 67%": 0.67,
    "Consulente informatico – 78%": 0.78,
    "Altre attività – 86%": 0.86
}

scelta_ateco = st.selectbox("Seleziona la tua attività (codice ATECO)", list(ateco_dict.keys()))
coefficiente = ateco_dict[scelta_ateco]
st.info(f"📌 Coefficiente di redditività applicato: **{coefficiente*100:.0f}%**")

# Checkbox iscrizione CCIAA
iscritto_cciaa = st.checkbox("✅ Sei iscritto alla Camera di Commercio (artigiano o commerciante)?")

st.markdown("""
> ℹ️ **Se spunti questa opzione**, pagherai i **contributi fissi INPS artigiani/commercianti** + una quota variabile + diritto camerale (~50€).
>
> **Se NON la spunti**, pagherai i contributi tramite **Gestione Separata INPS (libero professionista senza albo)**.
""")

riduzione_35 = st.checkbox("✅ Hai la riduzione INPS del 35%?")
aliquota = st.radio("Aliquota imposta sostitutiva", ["5%", "15%"])

# === CALCOLI ===

st.header("📊 Calcolo in corso...")

reddito_imponibile = fatturato * coefficiente

if iscritto_cciaa:
    # INPS Artigiani/Commercianti
    soglia_eccedenza = 18415
    quota_fissa = 4208  # aggiornato 2024
    eccedenza = max(0, reddito_imponibile - soglia_eccedenza)
    quota_variabile = eccedenza * 0.24

    if riduzione_35:
        quota_fissa *= 0.65
        quota_variabile *= 0.65

    contributi_inps = quota_fissa + quota_variabile
    diritto_cciaa = 50
else:
    # Gestione separata INPS
    contributi_inps = reddito_imponibile * 0.2607
    if riduzione_35:
        contributi_inps *= 0.65
    quota_fissa = None
    quota_variabile = None
    diritto_cciaa = 0

# Imposta sostitutiva
aliquota_percento = 0.05 if aliquota == "5%" else 0.15
imponibile_fiscale = reddito_imponibile - (contributi_inps * 0.50)
imposta = imponibile_fiscale * aliquota_percento

# Totali
tasse_totali = contributi_inps + imposta + diritto_cciaa
reddito_netto = fatturato - tasse_totali

# === OUTPUT ===

st.header("📤 Risultati")

st.write(f"**Reddito imponibile**: € {reddito_imponibile:,.2f}")

if iscritto_cciaa:
    st.subheader("🧱 Contributi INPS (artigiani/commercianti)")
    st.write(f"Quota fissa INPS: € {quota_fissa:,.2f}")
    st.write(f"Quota variabile INPS (24% oltre €18.415): € {quota_variabile:,.2f}")
else:
    st.subheader("📌 Contributi INPS gestione separata")
    st.write(f"Totale contributi gestione separata: € {contributi_inps:,.2f}")

st.write(f"**Imposta sostitutiva ({aliquota})**: € {imposta:,.2f}")
if iscritto_cciaa:
    st.write(f"**Diritto camerale (stimato)**: € {diritto_cciaa:.2f}")

st.markdown("---")
st.success(f"💸 **Tasse totali maturate finora**: € {tasse_totali:,.2f}")
st.info(f"💼 **Reddito netto stimato**: € {reddito_netto:,.2f}")



# === ANALISI ANNO PRECEDENTE ===
st.markdown("---")
st.header("📘 Analisi anno precedente")

st.markdown("Questa sezione ti aiuta a capire se hai già coperto tutto ciò che dovevi per l'anno fiscale precedente (es. 2024), oppure se nel 2025 dovrai ancora pagare qualcosa.")

with st.expander("➕ Inserisci i dati dell'anno precedente per analizzare i saldi"):
    fatturato_anno_prec = st.number_input("Fatturato anno precedente (€)", min_value=0.0, format="%.2f", key="fatt_prec")
    coeff_prec = st.slider("Coefficiente di redditività (%)", 40, 86, 78, key="coeff_prec") / 100
    aliquota_prec = st.radio("Aliquota imposta sostitutiva anno precedente", [5, 15], key="aliq_prec") / 100
    sconto_inps_prec = st.checkbox("Riduzione INPS 35% per l'anno precedente?", value=True, key="sconto_prec")

    inps_versata_prec = st.number_input("INPS versata nel 2024 (prime 3 rate) (€)", min_value=0.0, format="%.2f", key="inps_prec")
    quarta_rata_versata = st.checkbox("Hai già pagato la 4ª rata INPS (febbraio 2025)?", value=False)

    imposta_versata_prec = st.number_input("Totale imposta versata (€)", min_value=0.0, format="%.2f", key="imp_prec")

    # Calcoli base
    reddito_imp_prec = fatturato_anno_prec * coeff_prec
    inps_fissa_lorda = 4208
    inps_fissa_prec = inps_fissa_lorda * (0.65 if sconto_inps_prec else 1.0)
    eccedenza_prec = max(0, reddito_imp_prec - 18415)
    inps_var_prec = eccedenza_prec * 0.24 * (0.65 if sconto_inps_prec else 1.0)
    inps_totale_prec = inps_fissa_prec + inps_var_prec

    # Calcolo automatico 4ª rata
    quarta_rata_importo = inps_fissa_prec / 4 if quarta_rata_versata else 0.0
    inps_totale_versata = inps_versata_prec + quarta_rata_importo

    deducibile = inps_totale_prec * 0.50
    base_imposta = reddito_imp_prec - deducibile
    imposta_prec = base_imposta * aliquota_prec

    saldo_inps_prec = inps_totale_prec - inps_totale_versata
    saldo_imposta_prec = imposta_prec - imposta_versata_prec

    st.subheader("📊 Riepilogo anno precedente")
    st.write(f"Reddito imponibile: € {reddito_imp_prec:,.2f}")
    st.write(f"INPS stimata (fissa + variabile): € {inps_totale_prec:,.2f}")
    st.write(f"Imposta sostitutiva stimata: € {imposta_prec:,.2f}")

    st.markdown(f"💡 La 4ª rata INPS, se pagata a febbraio 2025, è considerata parte del 2024. Calcolata automaticamente come 1/4 della quota fissa: **€ {quarta_rata_importo:,.2f}**")

    st.markdown("---")
    st.subheader("💰 Versamenti conteggiati")
    st.write(f"INPS versata (incl. eventuale 4ª rata): € {inps_totale_versata:,.2f}")
    st.write(f"Tasse versate: € {imposta_versata_prec:,.2f}")

    st.markdown("---")
    st.subheader("📌 Saldi previsti da pagare nel 2025")

    if saldo_inps_prec <= 0:
        st.success(f"✅ Nessun saldo INPS dovuto. Hai versato {abs(saldo_inps_prec):,.2f} € in più.")
    else:
        st.warning(f"⚠️ Saldo INPS da pagare: € {saldo_inps_prec:,.2f}")

    if saldo_imposta_prec <= 0:
        st.success(f"✅ Nessun saldo imposta sostitutiva. Hai versato {abs(saldo_imposta_prec):,.2f} € in più.")
    else:
        st.warning(f"⚠️ Saldo imposta sostitutiva da pagare: € {saldo_imposta_prec:,.2f}")
