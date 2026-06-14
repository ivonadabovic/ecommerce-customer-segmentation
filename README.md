# E-commerce Customer Segmentation Tool

## Opis projekta
Ovaj alat rjesava problem e-commerce kompanije koja svim kupcima salje iste emailove, iste popuste i isti pristup.
Cilj je automatski identifikovati razlicite tipove kupaca i dati konkretne preporuke za marketinske akcije prilagodjene svakom segmentu.

## Funkcionalnosti
- Upload fajla: Podrzava Excel (.xlsx, .xls) i CSV format
- Automatska segmentacija: GMM klasterovanje + BIC za automatski odabir broja segmenata
- RFM analiza: Recency, Frequency, Monetary metrike
- CLV predikcija: Customer Lifetime Value izracun
- Interaktivni grafikoni: Plotly dashboard sa 3 razlicita prikaza
- Cohort analysis: Broj novih kupaca po godinama
- Marketing playbook: Specificne preporuke za svaki segment
- ROI simulacija: Sta ako analiza za marketinske kampanje
- Download rezultata: Export segmentacije kao CSV fajl

## Tehnologije
- Python 3.11
- VS Code (razvojno okruzenje)
- Streamlit (Web aplikacija)
- Pandas / NumPy (Obrada podataka)
- Scikit-learn (GMM klasterovanje)
- Plotly (Interaktivni grafikoni)
- HDBSCAN (Opciona metoda klasterovanja)

## Instalacija i pokretanje
### Preduslovi
- Instaliran Python 3.11 ili noviji (https://python.org)
- Instaliran VS Code (opciono, ali preporuceno)
### Korak 1: Kloniraj repozitorijum
git clone https://github.com/ivonadabovic/ecommerce-customer-segmentation.git
cd ecommerce-customer-segmentation
### Korak 2: Instaliraj potrebne biblioteke
pip install -r requirements.txt
### Korak 3: Pokreni aplikaciju
python -m streamlit run app.py
### Korak 4: Otvori browser
Aplikacija ce se automatski otvoriti na adresi: http://localhost:8501

## Kako koristiti alat
### 1. Pripremi podatke
Fajl mora sadrzavati sljedece kolone:
- InvoiceNo (broj racuna)
- StockCode (sifra proizvoda)
- Description (opis proizvoda)
- Quantity (kolicina)
- InvoiceDate (datum i vrijeme)
- UnitPrice (cijena sa tackom)
- Customer ID (ID kupca)
- Country (drzava)

### 2. Preuzmi testni dataset
Preporuceni dataset: Online Retail II
- Link: https://archive.ics.uci.edu/dataset/502/online+retail+ii


### 3. Uploaduj fajl
- Klikni "Browse files" u aplikaciji
- Odaberi svoj Excel ili CSV fajl
- Sacekaj 10-20 sekundi dok sistem analizira

### 4. Pregledaj rezultate
Aplikacija ce prikazati:
- Broj kupaca i segmenata
- Ukupnu vrijednost i prosjecan CLV
- ARPU i Customer Equity
- Cohort analysis (grafikon)
- Raspodjelu segmenata (pie chart)
- RFM analizu (3 grafikona)
- Detaljnu tabelu kupaca
- Marketing playbook
- ROI simulaciju

## Struktura projekta
ecommerce-customer-segmentation/
├── app.py                 (Streamlit aplikacija - dashboard)
├── pipeline.py            (ML logika - RFM, segmentacija, CLV)
├── requirements.txt       (Python biblioteke)
├── README.md              (Dokumentacija)
└── data/                  (opcioni folder za dataset)
    └── online_retail_II.xlsx

## Rjesavanje problema
Problem: streamlit not recognized
Rjesenje: Koristi python -m streamlit run app.py

Problem: Module not found
Rjesenje: Instaliraj biblioteku: pip ime_biblioteke

Problem: Greska sa datumima
Rjesenje: Provjeri da je InvoiceDate ispravan format

Problem: Upload ne radi
Rjesenje: Provjeri da li fajl ima sve potrebne kolone

## requirements.txt
streamlit==1.58.0
pandas==3.0.3
numpy==2.3.5
scikit-learn==1.9.0
plotly==6.8.0
hdbscan==0.8.44
openpyxl==3.1.5

## Deploy
Aplikacija je dostupna online na:
https://ivonadabovic-ecommerce-customer-segmentation.streamlit.app

## Autor
Ivana Dabovic
GitHub: ivonadabovic
Projektni zadatak: E-commerce Customer Segmentation

## Zakljucak

Ovaj alat omogucava e-commerce kompaniji da:
- Razumije razlicite tipove svojih kupaca
- Personalizuje marketinske akcije
- Predvidi ROI prije pokretanja kampanje
- Poveca prihod kroz ciljane ponude

Umjesto istog emaila za sve - svaki segment dobija ono sto mu najbolje odgovara.