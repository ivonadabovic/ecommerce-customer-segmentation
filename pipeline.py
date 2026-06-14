# pipeline.py
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.mixture import GaussianMixture
import streamlit as st

def izracunaj_rfm(df):
    """Računa RFM metrike"""
    
    if len(df) == 0:
        return pd.DataFrame()
    
    zadnji_datum = df['InvoiceDate'].max()
    
    # Grupisanje
    rfm = df.groupby('Customer ID').agg(
        Recency=('InvoiceDate', lambda x: (zadnji_datum - x.max()).days),
        Prvi_datum=('InvoiceDate', 'min'),
        Frequency=('InvoiceNo', 'nunique'),
        Monetary=('TotalPrice', 'sum')
    )
    
    rfm = rfm[rfm.index.notna()]
    rfm['Recency'] = rfm['Recency'].clip(lower=0).fillna(999)
    
    return rfm

def napravi_segmente(rfm):
    """Automatski pravi segmente kupaca"""
    
    if len(rfm) < 3:
        rfm['Segment'] = 0
        opis_segmenata = {0: "Nedovoljno podataka"}
        return rfm, opis_segmenata
    
    # Standardizacija
    scaler = StandardScaler()
    rfm_scaled = scaler.fit_transform(rfm[['Recency', 'Frequency', 'Monetary']])
    
    # Odredi broj klastera (2 do 4)
    broj_klastera = min(4, max(2, len(rfm) // 100))
    
    # GMM klasterovanje
    gmm = GaussianMixture(n_components=broj_klastera, random_state=42)
    segmenti = gmm.fit_predict(rfm_scaled)
    rfm['Segment'] = segmenti
    
    # Opisi segmenata na osnovu prosječne potrošnje
    opis_segmenata = {}
    prosjeci = rfm.groupby('Segment')['Monetary'].mean().sort_values(ascending=False)
    
    for i, (seg, prosjek) in enumerate(prosjeci.items()):
        if i == 0:
            opis = "VIP kupci - najveća potrošnja"
        elif i == 1:
            opis = "Loyalni kupci - dobra potrošnja"
        elif i == 2:
            opis = "Prosječni kupci"
        else:
            opis = "Povremeni/Uspavani kupci"
        
        opis_segmenata[int(seg)] = opis
    
    return rfm, opis_segmenata

def predvidi_clv(rfm):
    """Predviđa Lifetime Value"""
    
    if len(rfm) == 0:
        return rfm
    
    rfm['CLV'] = rfm['Monetary'] * 1.2
    rfm['CLV'] = rfm['CLV'].fillna(rfm['Monetary'])
    
    return rfm

def pokreni_pipeline(uploaded_file):
    """Glavna funkcija"""
    
    # Učitaj podatke
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    
    st.write("📋 **Pronađene kolone:**", list(df.columns))
    
    # Mapiranje kolona
    if 'Invoice' in df.columns and 'InvoiceNo' not in df.columns:
        df['InvoiceNo'] = df['Invoice']
    if 'Price' in df.columns and 'UnitPrice' not in df.columns:
        df['UnitPrice'] = df['Price']
    
    # Provjera kolona
    potrebne = ['InvoiceNo', 'Quantity', 'InvoiceDate', 'UnitPrice', 'Customer ID']
    fale = [k for k in potrebne if k not in df.columns]
    if fale:
        raise Exception(f"Fale kolone: {fale}")
    
    # Čišćenje
    df = df.dropna(subset=['Customer ID'])
    df = df[df['Quantity'] > 0]
    df = df[df['UnitPrice'] > 0]
    df['Customer ID'] = df['Customer ID'].astype(str)
    df['TotalPrice'] = df['Quantity'] * df['UnitPrice']
    
    # Datum
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'], errors='coerce', dayfirst=True)
    df = df.dropna(subset=['InvoiceDate'])
    
    st.write(f"📊 Učitano {len(df)} redova")
    
    # RFM
    rfm = izracunaj_rfm(df)
    st.write(f"👥 Pronađeno {len(rfm)} kupaca")
    
    # Segmenti
    rfm, opis_segmenata = napravi_segmente(rfm)
    
    # CLV
    rfm = predvidi_clv(rfm)
    
    st.write(f"🎯 Kreirano {len(rfm['Segment'].unique())} segmenata")
    
    return rfm, opis_segmenata