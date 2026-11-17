from typing import List, Dict, Any
from app.database.connection import get_db_connection

class CorrelationEngine:
    def __init__(self):
        self.ready = True

    def evaluate_correlations(self, profile_id: str | None = None) -> List[Dict[str, Any]]:
        conn = get_db_connection(profile_id=profile_id)
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT a.*
                FROM analiti a
                INNER JOIN (
                    SELECT nome_standardizzato, MAX(data_prelievo) as max_data
                    FROM analiti
                    GROUP BY nome_standardizzato
                ) latest ON a.nome_standardizzato = latest.nome_standardizzato AND a.data_prelievo = latest.max_data
                """
            )
            latest = {r["nome_standardizzato"]: dict(r) for r in cur.fetchall()}
        finally:
            conn.close()

        findings: List[Dict[str, Any]] = []

        ferritina = latest.get("Ferritina")
        sideremia = latest.get("Sideremia (Ferro)")
        hb = latest.get("Emoglobina (Hb)")
        mcv = latest.get("Volume Corpuscolare Medio (MCV)")

        if ferritina or sideremia or hb:
            f_val = ferritina.get("valore_numerico") if ferritina else None
            s_val = sideremia.get("valore_numerico") if sideremia else None
            h_val = hb.get("valore_numerico") if hb else None
            m_val = mcv.get("valore_numerico") if mcv else None

            if (f_val and f_val < 30) or (s_val and s_val < 50):
                if h_val and h_val < 12.0:
                    findings.append({
                        "titolo": "Quadro di Anemia Sideropenica Microcitica",
                        "sistema": "Ematologico",
                        "criticita": "ALTA",
                        "descrizione": "Bassi livelli di ferritina e sideremia associati a emoglobina ridotta e MCV basso orientano verso una carenza marziale attiva.",
                        "biomarcatori": ["Ferritina", "Sideremia (Ferro)", "Emoglobina (Hb)", "Volume Corpuscolare Medio (MCV)"]
                    })
                else:
                    findings.append({
                        "titolo": "Deplezione dei Depositi Marziali (Sideropenia Latente)",
                        "sistema": "Ematologico",
                        "criticita": "MEDIA",
                        "descrizione": "Ferritina o sideremia basse con emoglobina ancora nei limiti: riserve di ferro esaurite in fase pre-anemica.",
                        "biomarcatori": ["Ferritina", "Sideremia (Ferro)"]
                    })

        glicemia = latest.get("Glucosio Basale")
        hba1c = latest.get("Emoglobina Glicata (HbA1c)")
        trigliceridi = latest.get("Trigliceridi")
        hdl = latest.get("Colesterolo HDL")

        if glicemia or hba1c or trigliceridi:
            g_val = glicemia.get("valore_numerico") if glicemia else None
            a_val = hba1c.get("valore_numerico") if hba1c else None
            t_val = trigliceridi.get("valore_numerico") if trigliceridi else None
            h_val = hdl.get("valore_numerico") if hdl else None

            if (g_val and g_val >= 100) or (a_val and a_val >= 5.7):
                if t_val and t_val >= 150:
                    findings.append({
                        "titolo": "Rischio Sindrome Metabolica e Disglicemia",
                        "sistema": "Metabolico",
                        "criticita": "ALTA" if (g_val and g_val >= 126) or (a_val and a_val >= 6.5) else "MEDIA",
                        "descrizione": "Co-presenza di iperglicemia/HbA1c alterata e ipertrigliceridemia indicativa di insulino-resistenza sistemica.",
                        "biomarcatori": ["Glucosio Basale", "Emoglobina Glicata (HbA1c)", "Trigliceridi"]
                    })

        tsh = latest.get("Tireotropina (TSH)")
        ft3 = latest.get("Triiodotironina Libera (FT3)")
        ft4 = latest.get("Tiroxina Libera (FT4)")

        if tsh:
            tsh_val = tsh.get("valore_numerico")
            ft4_val = ft4.get("valore_numerico") if ft4 else None

            if tsh_val and tsh_val > 4.2:
                if ft4_val and ft4_val < 0.8:
                    findings.append({
                        "titolo": "Ipotiroidismo Primario Conclamato",
                        "sistema": "Ormonale",
                        "criticita": "ALTA",
                        "descrizione": "TSH elevato in associazione a FT4 ridotto evidenzia una ridotta funzionalita tiroidea periferica.",
                        "biomarcatori": ["Tireotropina (TSH)", "Tiroxina Libera (FT4)"]
                    })
                else:
                    findings.append({
                        "titolo": "Ipotiroidismo Subclinico",
                        "sistema": "Ormonale",
                        "criticita": "MODERATA",
                        "descrizione": "TSH elevato con ormoni tiroidei liberi (FT4/FT3) ancora nel range di normalita.",
                        "biomarcatori": ["Tireotropina (TSH)"]
                    })
            elif tsh_val and tsh_val < 0.3:
                findings.append({
                    "titolo": "Sospetta Iperattivita Tiroidea",
                    "sistema": "Ormonale",
                    "criticita": "MEDIA",
                    "descrizione": "TSH soppresso: monitorare frazioni libere FT3 e FT4 per escludere tireotossicosi.",
                    "biomarcatori": ["Tireotropina (TSH)"]
                })

        alt = latest.get("Alanina Aminotransferasi (ALT)")
        ast = latest.get("Aspartato Aminotransferasi (AST)")
        ggt = latest.get("Gamma Glutamil Transferasi (GGT)")

        if alt or ast:
            alt_val = alt.get("valore_numerico") if alt else None
            ast_val = ast.get("valore_numerico") if ast else None
            ggt_val = ggt.get("valore_numerico") if ggt else None

            if (alt_val and alt_val > 45) or (ast_val and ast_val > 40):
                findings.append({
                    "titolo": "Pattern di Citolisi Epatica",
                    "sistema": "Epatico",
                    "criticita": "MEDIA" if (alt_val and alt_val < 100) else "ALTA",
                    "descrizione": "Innalzamento delle transaminasi epatiche ALT/AST, suggestivo di sofferenza o flogosi epatocitaria.",
                    "biomarcatori": ["Alanina Aminotransferasi (ALT)", "Aspartato Aminotransferasi (AST)", "Gamma Glutamil Transferasi (GGT)"]
                })

        creat = latest.get("Creatinina Sierica")
        egfr = latest.get("Velocita di Filtrazione Glomerulare (eGFR)")
        azot = latest.get("Azotemia (Urea)")

        if creat or egfr:
            c_val = creat.get("valore_numerico") if creat else None
            e_val = egfr.get("valore_numerico") if egfr else None

            if (c_val and c_val > 1.25) or (e_val and e_val < 60.0):
                findings.append({
                    "titolo": "Riduzione della Riserva Funzionale Renale",
                    "sistema": "Renale",
                    "criticita": "ALTA" if (e_val and e_val < 45.0) else "MEDIA",
                    "descrizione": "Filtrazione glomerulare ridotta e/o creatinina sierica sopra i livelli di sicurezza clinica.",
                    "biomarcatori": ["Creatinina Sierica", "Velocita di Filtrazione Glomerulare (eGFR)", "Azotemia (Urea)"]
                })

        pcr = latest.get("Proteina C Reattiva (PCR)")
        ves = latest.get("Velocita di Eritrosedimentazione (VES)")

        if pcr or ves:
            p_val = pcr.get("valore_numerico") if pcr else None
            v_val = ves.get("valore_numerico") if ves else None

            if (p_val and p_val > 5.0) or (v_val and v_val > 25):
                findings.append({
                    "titolo": "Stato Flogistico Sistemico Attivo",
                    "sistema": "Infiammatorio",
                    "criticita": "MEDIA",
                    "descrizione": "Incremento concordante degli indici di flogosi aspecifica (PCR / VES).",
                    "biomarcatori": ["Proteina C Reattiva (PCR)", "Velocita di Eritrosedimentazione (VES)"]
                })

        return findings

correlation_engine = CorrelationEngine()
