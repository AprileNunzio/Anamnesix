import base64
from typing import Dict, Any, Optional
from app.ai.router import ai_router

IMAGING_SYSTEM_PROMPT = """
Sei un medico radiologo e andrologo/ginecologo specializzato in diagnostica per immagini avanzata e medicina della riproduzione umana.
Il tuo compito e analizzare con rigore e accuratezza millimetrica l'immagine radiologica/ecografica fornita (oppure il testo del referto strumentale) ed emettere una perizia diagnostica dettagliata.
La lingua DEVE essere esclusivamente l'ITALIANO.
Devi strutturare il rapporto esattamente nelle seguenti sezioni formattate:
[REFERTO DI VALUTAZIONE DIAGNOSTICA STRUMENTALE & IMAGING ANAMNESIX]

SEZIONE 1. METODICA DI ACQUISIZIONE E DISTRETTO ANATOMICO
Descrizione della tecnologia impiegata (es. Ecocolordoppler Scrotale ad alta frequenza, Ecografia Pelvica Transvaginale 3D, TAC Addome-Pelvi con e senza mdc, Risonanza Magnetica Pelvica multiparametrica, Isterosalpingografia fluoroscopica) e dettagli tecnici identificabili.

SEZIONE 2. ANALISI MORFOLOGICA E REPERTI ANATOMICI
Descrizione sistematica dei dettagli visivi e descrittivi:
- Dimensioni, ecostruttura/intensita di segnale e simmetria degli organi esaminati (didimi, epididimi, utero, ovaie, salpingi, spazio retto-uterino di Douglas).
- Vascolarizzazione, segnale Doppler e comportamento sotto sforzo/Valsalva se pertinente.

SEZIONE 3. ANOMALIE CLINICHE IDENTIFICATE & STRATIFICAZIONE GRAVITA
Elenco dettagliato e rigoroso di qualsiasi alterazione visibile o descritta:
- Presenza di varicocele (grado I-IV, reflusso venoso), cisti epididimarie, formazioni solide o ipoecogene, microlitiasi testicolare.
- Presenza di cisti ovariche funzionali o endometriosiche (cisti cioccolato), quadro policistico PCO/PCOS, polipi endometriali, miomi (sottomucosi, intramurali con classificazione FIGO), adenomiosi (spessore zona giunzionale), idrosalpinge o sinechie.
- Gravita attribuita: NESSUNA ANOMALIA / LIEVE / MODERATA / CRITICA-URGENTE.

SEZIONE 4. IMPATTO SPECIFICO SULLA FERTILITA RIPRODUTTIVA
Spiegazione fisiopatologica di come i reperti riscontrati influenzano:
- Per l'uomo: spermatogenesi, termoregolazione testicolare, transito deferenziale, stress ossidativo e frammentazione del DNA spermatico.
- Per la donna: riserva follicolare, recettivita endometriale, impianto della blastocisti, pervieta tubarica e qualita ovocitaria.

SEZIONE 5. INDICAZIONI CLINICHE & RACCOMANDAZIONI SPECIALISTICHE
Azioni concrete consigliate per l'andrologo o il ginecologo curante (es. embolizzazione/scleroembolizzazione percutanea, laparoscopia, isteroscopia operativa, monitoraggio dell'ovulazione, passaggio a tecniche di PMA di II livello FIVET/ICSI).

SEZIONE 6. AVVISO CLINICO
Dichiarazione di supporto interpretativo basato su intelligenza artificiale conforme alle buone pratiche cliniche.
"""

class ImagingAnalyzer:
    def __init__(self):
        self.ready = True

    async def analyze_imaging(
        self,
        image_bytes: Optional[bytes] = None,
        mime_type: Optional[str] = None,
        report_text: Optional[str] = None,
        tipologia_esame: str = "ECO_TRANSVAGINALE",
        organo_distretto: str = "Pelvi Femminile"
    ) -> Dict[str, Any]:
        testo_fallback = report_text if report_text else "Nessun testo allegato; procedere con ispezione radiologica visiva dell immagine."
        prompt = f"""
DATI DELL'ESAME STRUMENTALE:
Tipologia: {tipologia_esame}
Distretto: {organo_distretto}

Testo del Referto o Note Cliniche Disponibili:
{testo_fallback}

Analizza l'immagine o il referto fornito ed emetti il rapporto strutturato secondo le linee guida.
"""

        if image_bytes and mime_type:
            response = await ai_router.extract_clinical_data(
                document_text=prompt,
                image_bytes=image_bytes,
                mime_type=mime_type
            )
            raw_report = response.get("note_generali") if isinstance(response, dict) else str(response)
            if not raw_report or raw_report == "":
                raw_report = await ai_router.generate_response(
                    system_instruction=IMAGING_SYSTEM_PROMPT,
                    user_prompt=prompt,
                    temperature=0.1
                )
        else:
            raw_report = await ai_router.generate_response(
                system_instruction=IMAGING_SYSTEM_PROMPT,
                user_prompt=prompt,
                temperature=0.1
            )

        criticita = "NORMALE"
        t_low = raw_report.lower()
        if "critica" in t_low or "urgente" in t_low or "severa" in t_low or "idrosalpinge" in t_low or "azoospermia" in t_low:
            criticita = "CRITICA"
        elif "moderata" in t_low or "varicocele" in t_low or "endometriosi" in t_low or "mioma" in t_low or "policistico" in t_low:
            criticita = "MODERATA"
        elif "lieve" in t_low:
            criticita = "LIEVE"

        return {
            "tipologia_esame": tipologia_esame,
            "organo_distretto": organo_distretto,
            "criticita": criticita,
            "referto_dettagliato": raw_report
        }

imaging_analyzer = ImagingAnalyzer()
