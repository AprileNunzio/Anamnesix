# Anamnesix - Cartella Clinica Intelligente & Suite Diagnostica Desktop

Anamnesix e una piattaforma software desktop avanzata per Windows 10 e Windows 11 (x64) dedicata all'acquisizione, cifratura Zero-Knowledge, estrazione OCR ultra-avanzata, normalizzazione clinica, correlazione multi-parametro e interrogazione conversazionale RAG di referti ed esami medici per l'intero nucleo familiare.

---

## Indice dei Contenuti
1. Architettura di Sistema e Sicurezza Zero-Knowledge
2. Struttura Modulare: Directory Indipendenti per Ogni Pagina e Analita
3. Gestione Multi-Profilo Familiare con Database Dedicati
4. Pipeline di Ingestion & Motore OCR Ultra-Avanzato
5. Router AI Ibrido: Ollama Locale & Google Gemini con Privacy Guard
6. Motori Analitici e Correlazioni Cliniche Incrociate
7. Chat Clinica Conversazionale con RAG e Citazioni Verificate
8. Integrazione Nativa Server Model Context Protocol (MCP)
9. Interfaccia Grafica Clinica Responsive fino ad 8K
10. Guida all'Installazione, Build Standalone e Auto-Aggiornamento

---

## 1. Architettura di Sistema e Sicurezza Zero-Knowledge

Anamnesix adotta un'architettura crittografica di sicurezza estrema a conoscenza zero:
* **Derivazione della Chiave:** Funzione di derivazione crittografica **Argon2id** (memory_cost = 64MB, iterations = 3, parallelism = 4) calcolata a partire dalla Master Password e da un sale crittografico univoco a 128 bit salvato in `salt.bin`.
* **Cifratura Dati e File:** Cifratura autenticata **AES-256-GCM** per ogni record del database e per ogni file referto originale (PDF, immagini) salvato su disco. I file rimangono sempre cifrati (`.enc`) e vengono decrittati esclusivamente in RAM nel momento della visualizzazione.
* **Integrazione Windows DPAPI:** Possibilita opzionale di memorizzare la chiave derivata protetta tramite le API native Windows Data Protection (`CryptProtectData`), vincolando lo sblocco rapido alle credenziali dell'utente Windows locale.
* **Auto-Lock:** Timer di inattivita configurabile che azzera immediatamente i buffer di memoria RAM tramite sovrascrittura di byte (`zeroize_bytes`).
* **Percorso Assoluto su Windows:** `%USERPROFILE%\Documents\Anamnesix`
  * `/vault/profiles/{profile_id}/anamnesix.db`: Database SQLite cifrato del membro familiare.
  * `/vault/profiles/{profile_id}/vectors.bin`: Indice vettoriale cifrato locale per il RAG.
  * `/vault/profiles_metadata.enc`: Metadati cifrati del nucleo familiare.
  * `/documents/{profile_id}/`: File referti originali archiviati esclusivamente come blob cifrati `.enc`.
  * `/backups/{profile_id}/`: Snapshot e backup automatici.
  * `/config/`: Configurazioni di sistema cifrate e chiavi protette.

---

## 2. Struttura Modulare: Directory Indipendenti per Ogni Pagina e Analita

Il software e interamente modulare. Ogni singola schermata e ogni singolo biomarcatore clinico possiedono una directory e file di logica dedicati.

### Albero Modulare dei Biomarcatori Clinici
Ciascun biomarcatore possiede il proprio algoritmo in una cartella dedicata con logica di conversione unita, calcolo del rischio clinico e interpretazione fisiopatologica:
* `app/biomarkers/metabolico/glicemia/algorithm.py`
* `app/biomarkers/metabolico/emoglobina_glicata/algorithm.py`
* `app/biomarkers/lipidico/colesterolo_totale/algorithm.py`
* `app/biomarkers/lipidico/colesterolo_ldl/algorithm.py`
* `app/biomarkers/lipidico/colesterolo_hdl/algorithm.py`
* `app/biomarkers/lipidico/trigliceridi/algorithm.py`
* `app/biomarkers/epatico/alt/algorithm.py`
* `app/biomarkers/epatico/ast/algorithm.py`
* `app/biomarkers/epatico/ggt/algorithm.py`
* `app/biomarkers/renale/creatinina/algorithm.py`
* `app/biomarkers/tiroide/tsh/algorithm.py`
* `app/biomarkers/marziale/ferritina/algorithm.py`
* `app/biomarkers/emocromo/emoglobina/algorithm.py`
* `app/biomarkers/infiammatorio/pcr/algorithm.py`
* `app/biomarkers/vitamine/vitamina_d/algorithm.py`

### Albero Modulare dell'Interfaccia Grafica
Ciascuna pagina possiede la propria directory contenente il template HTML, lo stile CSS e la logica JavaScript:
* `frontend/pages/auth/`: Sblocco con Master Password e DPAPI.
* `frontend/pages/dashboard/`: Health Score, radar anomalie e statistiche generali.
* `frontend/pages/profiles/`: Gestione del nucleo familiare.
* `frontend/pages/referti/`: Area drag-and-drop per documenti e lista referti.
* `frontend/pages/human_in_loop/`: Revisione comparativa fianco a fianco.
* `frontend/pages/trends/`: Grafici longitudinali interattivi su Canvas ad alta risoluzione.
* `frontend/pages/correlations/`: Pannelli di correlazione clinica e Second Opinion AI.
* `frontend/pages/chat_rag/`: Chat clinica con citazione fonti.
* `frontend/pages/dossier/`: Generazione ed esportazione dossier PDF protetto da password.
* `frontend/pages/settings/`: Configurazione AI Router, Ollama, Gemini e aggiornamenti.

---

## 3. Gestione Multi-Profilo Familiare con Database Dedicati

Anamnesix permette di gestire tutti i componenti della famiglia (es. Intestatario, Coniuge, Figli, Genitori, Nonni):
* Appena effettuato lo sblocco con Master Password, l'utente puo selezionare istantaneamente il membro attivo tramite il selettore nella barra superiore.
* Ciascun profilo dispone di un proprio database relazionale isolato (`anamnesix.db`), un archivio documentale separato e un indice semantico dedicato.
* I dati e le anamnesi di ciascun familiare rimangono separati e protetti da chiavi crittografiche.

---

## 4. Pipeline di Ingestion & Motore OCR Ultra-Avanzato

La pipeline di ingestione supporta documenti PDF digitali, scansioni cartacee e fotografie ad alta risoluzione (JPG, PNG, WEBP):
1. **Analisi PDF Nativi:** Estrazione testuale tramite PyMuPDF preservando formattazione tabellare e layout originale.
2. **Pre-Processing Immagini con OpenCV:**
   * Conversione in scala di grigi.
   * Equalizzazione adattiva dell'istogramma con contrasto limitato (CLAHE) per evidenziare testi sbiaditi o referti fotografati con luce non uniforme.
   * Filtraggio bilaterale per rimozione del rumore conservando i bordi dei caratteri.
   * Calcolo dell'angolo di inclinazione tramite `minAreaRect` e correzione rotazionale automatica (deskew).
   * Binarizzazione adattiva con soglia di Otsu e operatori morfologici di apertura.
3. **Riconoscimento Ottico dei Caratteri (OCR):** Esecuzione Tesseract multilingua (`ita+eng`) configurato per layout tabellari clinici.
4. **Human-in-the-Loop:** Prima del commit definitivo nel database cifrato, all'utente viene mostrata la schermata di revisione fianco a fianco: a sinistra l'anteprima del documento scansionato, a destra la tabella interattiva con tutti i parametri estratti, i valori di riferimento e le unita di misura correggibili.

---

## 5. Router AI Ibrido: Ollama Locale & Google Gemini con Privacy Guard

Il router AI seleziona dinamicamente il fornitore di intelligenza artificiale preferito:
* **Provider 1: Ollama (100% Locale, Privato & Offline)**
  * Comunicazione via socket HTTP locale (`127.0.0.1:11434`).
  * Rilevamento automatico dei modelli installati via `/api/tags` (es. `llama3.1`, `qwen2.5`, `mistral`, `meditron`).
  * Supporto a modelli vision (es. `llama3.2-vision`, `llava`) per l'analisi visiva diretta di tabelle complesse.
  * Garanzia assoluta: nessun dato esce dalla workstation.
* **Provider 2: Google Gemini API (Cloud ad Alte Prestazioni)**
  * Supporto per `gemini-2.5-flash` per estrazione ad altissima velocita e `gemini-2.5-pro` per ragionamento clinico complesso.
  * Chiave API memorizzata cifrata nel vault con AES-256-GCM.
  * **Privacy Guard (PII Scrubbing Attivo di Default):** Prima di inviare qualsiasi stringa o testo ai server cloud, il modulo `pii_scrubber.py` rileva e maschera tramite token pseudonimizzati codice fiscale, nomi, cognomi, numeri telefonici, email e indirizzi fisici del paziente, reinserendoli localmente solo al momento del rendering finale.

---

## 6. Motori Analitici e Correlazioni Cliniche Incrociate

* **Health Score Globale (0-100):** Algoritmo di sintesi dello stato di salute suddiviso in 7 apparati fisiologici: Cardiovascolare, Metabolico, Epatico, Renale, Ematologico, Ormonale, Infiammatorio.
* **Radar delle Anomalie:** Tabella prioritizzata degli esami fuori norma, ordinati matematicamente in base alla percentuale di scostamento dai limiti di riferimento e alla persistenza temporale (ripetizione dell'anomalia nei controlli consecutivi).
* **Grafici Longitudinali:** Monitoraggio dell'andamento nel tempo di ciascun biomarcatore con tracciamento della banda verde di normalita ottimale e calcolo della percentuale di variazione e della direzione del trend (Crescente, Decrescente, Stabile).
* **Correlazioni Fisiopatologiche:**
  * *Pannello Anemia:* Analisi combinata di Ferritina, Sideremia, Emoglobina e MCV per identificare deficit marziali latenti o anemie microcitiche.
  * *Pannello Sindrome Metabolica:* Valutazione congiunta di Glucosio Basale, HbA1c, Trigliceridi e Colesterolo HDL per la stima dell'insulino-resistenza.
  * *Pannello Tiroide:* Analisi incrociata di TSH, FT3 e FT4 per la distinzione tra ipotiroidismo subclinico e franco.
  * *Pannello Epatico:* Rapporto tra transaminasi ALT/AST e GGT per pattern di citolisi o sofferenza epatocitaria.
  * *Pannello Renale:* Correlazione tra Creatinina Sierica, eGFR e Azotemia per stimare la riserva funzionale del nefrone.
  * *Pannello Flogistico:* Integrazione tra PCR e VES per il rilevamento di stati infiammatori sistemici acuti o cronici.
* **Second Opinion AI:** Generazione di un referto strutturato per il medico curante contenente sintesi esecutiva, esame per apparati, trend evolutivi, ipotesi cliniche e 4-6 domande mirate da porre durante la visita specialistica.

---

## 7. Chat Clinica Conversazionale con RAG e Citazioni Verificate

La sezione di chat clinica permette all'utente di porre domande in linguaggio naturale sul proprio storico medico:
* **Retrieval Ibrido:** Il motore analizza l'intento clinico, estrae dal database SQLite le misurazioni pertinenti e interroga l'indice semantico locale.
* **Prompt di Sistema Certificato:** Il modello di linguaggio (Ollama o Gemini) riceve come contesto unicamente i dati estratti dal database cifrato.
* **Citazione Obbligatoria delle Fonti:** Ogni risposta fornisce badge cliccabili contenenti la data esatta del prelievo, il valore registrato, l'unita di misura, il laboratorio di analisi e i range di riferimento.

---

## 8. Integrazione Nativa Server Model Context Protocol (MCP)

Anamnesix integra un server conforme alle specifiche **Model Context Protocol (MCP)**, accessibile tramite endpoint JSON-RPC su `/api/mcp/rpc`:
* `list_family_profiles`: Elenca tutti i membri della famiglia registrati nel software.
* `get_patient_clinical_summary`: Restituisce Health Score e stato sintetico del familiare.
* `get_out_of_range_anomalies`: Ottiene tutti gli analiti fuori range con scostamento percentuale e persistenza temporale.
* `get_biomarker_history`: Restituisce l'andamento cronologico completo di un parametro specifico.
* `evaluate_health_correlations`: Esegue la valutazione incrociata dei pannelli clinici complessi.
* `query_clinical_rag`: Interroga la cartella clinica in linguaggio naturale con citazioni puntuali.

---

## 9. Interfaccia Grafica Clinica Responsive fino ad 8K

L'interfaccia utente desktop e sviluppata con standard visivi moderni:
* **Risoluzione Adattiva fino a 8K (7680x4320):** Utilizzo estensivo di `clamp()`, variabili dimensionali `rem` e griglie fluide CSS che garantiscono nitidezza impeccabile da laptop 1080p a monitor medicali 4K e display 8K.
* **Clinical Dark & Light Mode:** Tema scuro ad alto contrasto antiriflesso e tema clinico chiaro con commutazione istantanea.
* **Canvas Vettoriale ad Alta Densita:** Grafici disegnati con correzione automatica per il fattore `devicePixelRatio`.

---

## 10. Guida all'Installazione, Build Standalone e Auto-Aggiornamento

### Prerequisiti
* Windows 10 o Windows 11 (x64)
* Python 3.11+
* Tesseract OCR (con pacchetto lingua italiano `tesseract-ocr-ita`) per scansioni cartacee
* Istanza locale di Ollama (opzionale per modalita 100% offline)

### Installazione delle Dipendenze in Ambiente Locale
```bash
pip install -r requirements.txt
```

### Avvio dell'Applicazione in Modalita Sviluppo
```bash
python -m app.main
```

### Compilazione dell'Eseguibile Standalone con PyInstaller
```bash
python scripts/build_windows.py
```

### Compilazione dell'Installer Unico con Inno Setup
```bash
ISCC.exe scripts/installer.iss
```
Questo comando generera il file `Anamnesix_Setup.exe` all'interno della cartella `Output/`.

### Auto-Aggiornamento Continuo da Commit GitHub
Anamnesix include un sistema di aggiornamento che verifica automaticamente la presenza di nuovi commit sul branch `main` del repository GitHub `AprileNunzio/Anamnesix`:
* L'installer `Anamnesix_Setup.exe` viene eseguito solo per la prima installazione.
* Gli aggiornamenti successivi vengono rilevati e applicati a caldo direttamente dal menu impostazioni, scaricando ed estraendo le modifiche senza richiedere una nuova installazione.
