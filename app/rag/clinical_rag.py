import json
from typing import Dict, Any, List
from app.database.connection import get_db_connection
from app.ai.router import ai_router

CLINICAL_RAG_SYSTEM_PROMPT = """
Sei l'assistente medico personale e consulente clinico di Anamnesix.
Rispondi alle domande dell'utente ESCLUSIVAMENTE sulla base dei dati clinici verificati forniti nel contesto qui sotto.
Regole fondamentali:
1. Rispondi sempre in ITALIANO chiaro, empatico e professionale.
2. Per ogni affermazione clinica, CITA SEMPRE la data esatta del prelievo, il valore registrato, l'unita di misura e il laboratorio di riferimento (es. "[Prelievo del 12/03/2024 - Lab. San Raffaele: Colesterolo LDL = 145 mg/dL, range 0-115]").
3. Se l'utente chiede informazioni su esami non presenti nello storico clinico fornito, dichiara esplicitamente che il dato non e presente nel database.
4. Non inventare dati non presenti nei referti.
5. Includi sempre una raccomandazione finale a consultare il medico per qualsiasi variazione terapeutica.
"""

class ClinicalRAGEngine:
    def __init__(self):
        self.ready = True

    def retrieve_context(self, query: str, profile_id: str | None = None) -> List[Dict[str, Any]]:
        conn = get_db_connection(profile_id=profile_id)
        try:
            cur = conn.cursor()
            words = [w.strip() for w in query.replace("?", " ").replace(",", " ").split() if len(w) > 3]
            results = []

            for word in words:
                cur.execute(
                    """
                    SELECT a.*, r.data_caricamento
                    FROM analiti a
                    JOIN referti r ON a.referto_id = r.id
                    WHERE a.nome_standardizzato LIKE ? OR a.nome_esame_originale LIKE ? OR a.categoria LIKE ?
                    ORDER BY a.data_prelievo DESC
                    LIMIT 20
                    """,
                    (f"%{word}%", f"%{word}%", f"%{word}%")
                )
                rows = [dict(r) for r in cur.fetchall()]
                results.extend(rows)

            if not results:
                cur.execute(
                    """
                    SELECT a.*, r.data_caricamento
                    FROM analiti a
                    JOIN referti r ON a.referto_id = r.id
                    ORDER BY a.data_prelievo DESC
                    LIMIT 40
                    """
                )
                results = [dict(r) for r in cur.fetchall()]

            unique_dict = {}
            for item in results:
                unique_dict[item["id"]] = item
            return list(unique_dict.values())
        finally:
            conn.close()

    async def answer_query(self, query: str, profile_id: str | None = None) -> Dict[str, Any]:
        context_items = self.retrieve_context(query, profile_id=profile_id)

        context_str = json.dumps(context_items[:30], indent=2, ensure_ascii=False)

        user_message = f"""
CONTESTO STORICO CLINICO E REFERTI:
{context_str}

DOMANDA DELL'UTENTE:
{query}
"""

        answer = await ai_router.generate_response(
            system_instruction=CLINICAL_RAG_SYSTEM_PROMPT,
            user_prompt=user_message,
            temperature=0.2
        )

        citations = []
        for item in context_items[:10]:
            citations.append({
                "esame": item.get("nome_standardizzato"),
                "valore": item.get("valore_numerico") if item.get("valore_numerico") is not None else item.get("valore_testuale"),
                "unita": item.get("unita_misura"),
                "data": item.get("data_prelievo"),
                "laboratorio": item.get("laboratorio"),
                "flag": item.get("stato_flag")
            })

        return {
            "query": query,
            "risposta": answer,
            "citazioni": citations
        }

clinical_rag_engine = ClinicalRAGEngine()
