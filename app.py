# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pipeline import pokreni_pipeline

st.set_page_config(page_title="Segmentacija Kupaca", layout="wide")

st.title("🛍️ Alat za segmentaciju kupaca")

st.markdown("""
### Kako radi?
1. Uploadujte Excel ili CSV fajl sa podacima o kupovinama
2. Sistem će **automatski** podijeliti kupce u grupe
3. Dobićete preporuke šta kojoj grupi da pošaljete
""")

uploaded_file = st.file_uploader("Uploaduj Excel ili CSV fajl", type=["xlsx", "xls", "csv"])

if uploaded_file is not None:
    with st.spinner("Analiziram kupce... (ovo traje 10-20 sekundi)"):
        try:
            rfm, opis_segmenata = pokreni_pipeline(uploaded_file)
            
            rfm['Segment_prikaz'] = rfm['Segment'] + 1
            
            st.success("✅ Segmentacija završena!")
            
            # ========== OSNOVNA STATISTIKA ==========
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Broj kupaca", len(rfm))
            with col2:
                st.metric("Broj segmenata", len(rfm['Segment'].unique()))
            with col3:
                ukupna_vrijednost = rfm['Monetary'].sum()
                st.metric("Ukupna vrijednost", f"{ukupna_vrijednost:,.0f}€")
            with col4:
                prosjecan_clv = rfm['CLV'].mean()
                st.metric("Prosječan CLV", f"{prosjecan_clv:,.0f}€")
            
            # ========== MARKETINŠKI METRIČKI POKAZATELJI ==========
            st.subheader("📊 Ključni marketinški metrički pokazatelji")
            
            arpu = rfm['Monetary'].sum() / len(rfm)
            customer_equity = rfm['CLV'].sum()
            avg_frequency = rfm['Frequency'].mean()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("💰 ARPU (Avg Revenue per User)", f"{arpu:.2f}€")
            with col2:
                st.metric("🏦 Customer Equity (Ukupna CLV)", f"{customer_equity:,.0f}€")
            with col3:
                st.metric("🔄 Prosječna frekvencija kupovine", f"{avg_frequency:.1f}")
            
            # ========== COHORT ANALYSIS ==========
            st.subheader("📅 Cohort Analysis - Novi kupci po godinama")
            
            if 'Prvi_datum' in rfm.columns:
                rfm['Godina_prve'] = pd.to_datetime(rfm['Prvi_datum']).dt.year
                rfm['Godina_prve'] = rfm['Godina_prve'].fillna(0).astype(int)
                rfm_valid = rfm[(rfm['Godina_prve'] >= 2000) & (rfm['Godina_prve'] <= 2025)]
                
                if len(rfm_valid) > 0:
                    cohort_data = rfm_valid['Godina_prve'].value_counts().reset_index()
                    cohort_data.columns = ['Godina prve kupovine', 'Broj novih kupaca']
                    cohort_data = cohort_data.sort_values('Godina prve kupovine')
                    cohort_data['Godina prve kupovine'] = cohort_data['Godina prve kupovine'].astype(int)
                    
                    fig_cohort = px.bar(cohort_data, 
                                        x='Godina prve kupovine', 
                                        y='Broj novih kupaca', 
                                        title='📊 Broj novih kupaca po godinama',
                                        color='Broj novih kupaca',
                                        color_continuous_scale='Viridis',
                                        text='Broj novih kupaca')
                    fig_cohort.update_traces(textposition='outside')
                    st.plotly_chart(fig_cohort, use_container_width=True)
                else:
                    st.info("📊 Nema dovoljno podataka za cohort analizu.")
            else:
                st.info("📊 Podaci ne sadrže informaciju o prvom datumu kupovine.")
            
            # ========== RASPODJELA SEGMENATA ==========
            st.subheader("📊 Raspodjela segmenata")
            
            segment_counts = rfm['Segment_prikaz'].value_counts().reset_index()
            segment_counts.columns = ['Segment', 'Broj kupaca']
            
            fig1 = px.pie(segment_counts, 
                         values='Broj kupaca', 
                         names='Segment',
                         title='Raspodjela kupaca po segmentima',
                         color_discrete_sequence=px.colors.qualitative.Set2)
            fig1.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig1, use_container_width=True)
            
            # ========== RFM ANALIZA ==========
            st.subheader("📈 RFM analiza po segmentima")
            
            rfm_avg = rfm.groupby('Segment_prikaz').agg({
                'Recency': 'mean',
                'Frequency': 'mean',
                'Monetary': 'mean'
            }).reset_index()
            rfm_avg.columns = ['Segment', 'Recency', 'Frequency', 'Monetary']
            
            fig2a = go.Figure()
            fig2a.add_trace(go.Bar(name='📅 Recency (dana)', x=rfm_avg['Segment'], y=rfm_avg['Recency'], marker_color='red'))
            fig2a.add_trace(go.Bar(name='🔄 Frequency (broj kupovina)', x=rfm_avg['Segment'], y=rfm_avg['Frequency'], marker_color='blue'))
            fig2a.update_layout(
                title="Recency i Frequency po segmentima",
                barmode='group',
                yaxis_title="Vrijednost"
            )
            st.plotly_chart(fig2a, use_container_width=True)
            
            fig2b = go.Figure()
            fig2b.add_trace(go.Bar(name='💰 Monetary (€)', x=rfm_avg['Segment'], y=rfm_avg['Monetary'], marker_color='green'))
            fig2b.update_layout(
                title="Potrošnja (Monetary) po segmentima",
                yaxis_title="Iznos u €"
            )
            st.plotly_chart(fig2b, use_container_width=True)
            
            # Normalizovani prikaz
            st.subheader("📊 Poređenje segmenata (normalizovano)")
            
            rfm_norm = rfm_avg.copy()
            for col in ['Recency', 'Frequency', 'Monetary']:
                max_val = rfm_norm[col].max()
                if max_val > 0:
                    rfm_norm[col] = (rfm_norm[col] / max_val) * 100
            
            fig2c = go.Figure()
            fig2c.add_trace(go.Bar(name='📅 Recency', x=rfm_norm['Segment'], y=rfm_norm['Recency'], marker_color='red'))
            fig2c.add_trace(go.Bar(name='🔄 Frequency', x=rfm_norm['Segment'], y=rfm_norm['Frequency'], marker_color='blue'))
            fig2c.add_trace(go.Bar(name='💰 Monetary', x=rfm_norm['Segment'], y=rfm_norm['Monetary'], marker_color='green'))
            fig2c.update_layout(
                title="Sve metrike na istoj skali (normalizovano 0-100)",
                barmode='group',
                yaxis_title="Normalizovana vrijednost (100 = najbolje)"
            )
            st.plotly_chart(fig2c, use_container_width=True)
            
            # ========== TABELA SA KUPCIMA ==========
            st.subheader("📋 Detalji svih kupaca")
            
            show_top = st.selectbox("Prikaži:", ["Sve kupce", "Top 50 po potrošnji", "Top 100 po potrošnji"])
            if show_top == "Top 50 po potrošnji":
                prikaz_rfm = rfm.sort_values('Monetary', ascending=False).head(50)
            elif show_top == "Top 100 po potrošnji":
                prikaz_rfm = rfm.sort_values('Monetary', ascending=False).head(100)
            else:
                prikaz_rfm = rfm.sort_values('Monetary', ascending=False)
            
            tabela = pd.DataFrame({
                'Recency (dana)': prikaz_rfm['Recency'],
                'Frequency (broj)': prikaz_rfm['Frequency'],
                'Monetary (€)': prikaz_rfm['Monetary'],
                'Segment': prikaz_rfm['Segment_prikaz'],
                'CLV (€)': prikaz_rfm['CLV']
            })
            st.dataframe(tabela, use_container_width=True)
            
            # ========== MARKETING PLAYBOOK ==========
            st.subheader("🎯 Marketing Playbook - Šta raditi?")
            
            for segment, opis in opis_segmenata.items():
                prikaz_segmenta = int(segment) + 1
                podaci = rfm[rfm['Segment'] == segment]
                
                with st.expander(f"📌 Segment {prikaz_segmenta}: {opis}"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Broj kupaca", len(podaci))
                    with col2:
                        st.metric("Prosječna potrošnja", f"{podaci['Monetary'].mean():.2f}€")
                    with col3:
                        st.metric("Prosječna CLV", f"{podaci['CLV'].mean():.2f}€")
                    
                    if "VIP" in opis:
                        st.success("""
                        **💎 VIP strategija:**
                        - 💌 Personalizovani email sa ekskluzivnim proizvodima
                        - 🎁 Rani pristup novim kolekcijama
                        - 🔥 Poseban popust 25% na sve
                        - 👥 Program preporuke prijatelja
                        """)
                    elif "Loyalni" in opis:
                        st.info("""
                        **🤝 Loyalni kupci strategija:**
                        - 💳 Program lojalnosti (sakupi bodove)
                        - 🎯 Preporuka sličnih proizvoda
                        - 💰 Popust 15% na sljedeću kupovinu
                        - 🎂 Birthday popust 20%
                        """)
                    elif "Uspavani" in opis:
                        st.warning("""
                        **😴 Buđenje uspavanih:**
                        - 📧 Email "Nedostaješ nam" + 30% popusta
                        - 🔔 Podsjetnik na omiljene kategorije
                        - ⏰ Limited-time offer (48h)
                        - 🚚 Besplatna dostava
                        """)
                    elif "Štedljivi" in opis:
                        st.info("""
                        **💰 Štedljivi kupci strategija:**
                        - 📦 Bundle ponude (kupi 2, plati 1.5)
                        - 🏷️ Jeftiniji proizvodi u fokusu
                        - 🚚 Besplatna dostava iznad 30€
                        - 🛒 Outlet sekcija
                        """)
                    else:
                        st.info("""
                        **📈 Aktivacija prosječnih:**
                        - 👋 Welcome back popust 20%
                        - 🔥 Top prodavani proizvodi
                        - 📧 Email newsletter 2x sedmično
                        - ⚡ Flash sale notifikacije
                        """)
            
            # ========== ROI SIMULACIJA ==========
            st.subheader("💰 Šta ako? - Simulacija ROI")
            
            col1, col2 = st.columns(2)
            with col1:
                popust = st.slider("Popust (%)", 0, 50, 20)
                stopa_reakcije = st.slider("Očekivana stopa reakcije (%)", 0, 100, 10)
                marza = st.slider("Marža proizvoda (%)", 0, 100, 30)
            with col2:
                troskovi_kampanje = st.number_input("Troškovi kampanje (€)", 0, 50000, 5000)
                prosjecna_narudzba = st.number_input("Prosječna vrijednost narudžbe (€)", 0, 500, 75)
                broj_kupaca_u_kampanji = st.number_input("Broj kupaca u kampanji", 0, 100000, 10000)
            
            prihod_prije_popusta = broj_kupaca_u_kampanji * (stopa_reakcije / 100) * prosjecna_narudzba
            prihod_poslije_popusta = prihod_prije_popusta * (1 - popust/100)
            zarada = prihod_poslije_popusta * (marza / 100)
            neto_profit = zarada - troskovi_kampanje
            
            if troskovi_kampanje > 0:
                roi = (neto_profit / troskovi_kampanje) * 100
            else:
                roi = 0
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📊 ROI", f"{roi:.0f}%")
            with col2:
                st.metric("💰 Prihod (nakon popusta)", f"{prihod_poslije_popusta:,.0f}€")
            with col3:
                st.metric("💵 Zarada (nakon marže)", f"{zarada:,.0f}€")
            with col4:
                st.metric("📈 Neto profit", f"{neto_profit:,.0f}€")
            
            # ========== DOWNLOAD ==========
            rfm_download = rfm.copy()
            rfm_download['Segment'] = rfm_download['Segment'] + 1
            csv = rfm_download.to_csv().encode('utf-8')
            st.download_button("📥 Preuzmi segmentaciju (CSV)", csv, "segmenti_kupaca.csv", "text/csv")
            
        except Exception as e:
            st.error(f"Greška: {e}")
            st.write("Provjeri da li fajl ima kolone: InvoiceNo, Quantity, InvoiceDate, UnitPrice, Customer ID")
else:
    st.info("👈 Uploaduj Excel ili CSV fajl sa lijeve strane da počneš")
    
    with st.expander("📖 Kako treba da izgleda fajl?"):
        st.write("""
        **Potrebne kolone:**
        - **InvoiceNo** (broj računa)
        - **StockCode** (šifra proizvoda)
        - **Description** (opis)
        - **Quantity** (količina)
        - **InvoiceDate** (datum)
        - **UnitPrice** (cijena)
        - **Customer ID** (ID kupca)
        - **Country** (država)
        """)