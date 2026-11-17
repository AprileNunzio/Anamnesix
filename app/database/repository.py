import uuid
import datetime
from typing import List, Dict, Any, Optional
from app.database.connection import get_db_connection
from app.database.models import AnalitaBase, RefertoCreate

def create_referto(referto: RefertoCreate) -> str:
    referto_id = str(uuid.uuid4())
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    conn = get_db_connection()
    try:
        with conn:
            conn.execute(
                """
                INSERT INTO referti (id, data_prelievo, laboratorio, data_caricamento, file_path, note, stato_revisione)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    referto_id,
                    referto.data_prelievo,
                    referto.laboratorio,
                    now_iso,
                    referto.file_path,
                    referto.note,
                    referto.stato_revisione
                )
            )
            conn.execute(
                """
                INSERT INTO audit_log (timestamp, azione, dettagli)
                VALUES (?, ?, ?)
                """,
                (now_iso, "CREAZIONE_REFERTO", f"Creato referto {referto_id}")
            )
        return referto_id
    finally:
        conn.close()

def save_analiti_for_referto(referto_id: str, analiti: List[AnalitaBase]) -> None:
    conn = get_db_connection()
    try:
        with conn:
            conn.execute("DELETE FROM analiti WHERE referto_id = ?", (referto_id,))
            for item in analiti:
                analita_id = str(uuid.uuid4())
                conn.execute(
                    """
                    INSERT INTO analiti (
                        id, referto_id, categoria, nome_esame_originale, nome_standardizzato,
                        valore_numerico, valore_testuale, unita_misura, range_min, range_max,
                        stato_flag, data_prelievo, laboratorio, note_referto
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        analita_id,
                        referto_id,
                        item.categoria,
                        item.nome_esame_originale,
                        item.nome_standardizzato,
                        item.valore_numerico,
                        item.valore_testuale,
                        item.unita_misura,
                        item.range_min,
                        item.range_max,
                        item.stato_flag,
                        item.data_prelievo,
                        item.laboratorio,
                        item.note_referto
                    )
                )
    finally:
        conn.close()

def confirm_referto_revision(referto_id: str, data_prelievo: str, laboratorio: str, note: Optional[str], analiti: List[AnalitaBase]) -> None:
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    conn = get_db_connection()
    try:
        with conn:
            conn.execute(
                """
                UPDATE referti
                SET data_prelievo = ?, laboratorio = ?, note = ?, stato_revisione = 'CONFERMATO'
                WHERE id = ?
                """,
                (data_prelievo, laboratorio, note, referto_id)
            )
            conn.execute("DELETE FROM analiti WHERE referto_id = ?", (referto_id,))
            for item in analiti:
                analita_id = str(uuid.uuid4())
                conn.execute(
                    """
                    INSERT INTO analiti (
                        id, referto_id, categoria, nome_esame_originale, nome_standardizzato,
                        valore_numerico, valore_testuale, unita_misura, range_min, range_max,
                        stato_flag, data_prelievo, laboratorio, note_referto
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        analita_id,
                        referto_id,
                        item.categoria,
                        item.nome_esame_originale,
                        item.nome_standardizzato,
                        item.valore_numerico,
                        item.valore_testuale,
                        item.unita_misura,
                        item.range_min,
                        item.range_max,
                        item.stato_flag,
                        data_prelievo,
                        laboratorio,
                        item.note_referto
                    )
                )
            conn.execute(
                """
                INSERT INTO audit_log (timestamp, azione, dettagli)
                VALUES (?, ?, ?)
                """,
                (now_iso, "CONFERMA_REVISIONE", f"Referto {referto_id} confermato con {len(analiti)} analiti.")
            )
    finally:
        conn.close()

def get_referto_by_id(referto_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM referti WHERE id = ?", (referto_id,))
        row = cur.fetchone()
        if not row:
            return None
        referto = dict(row)
        cur.execute("SELECT * FROM analiti WHERE referto_id = ? ORDER BY categoria, nome_standardizzato", (referto_id,))
        referto["analiti"] = [dict(r) for r in cur.fetchall()]
        return referto
    finally:
        conn.close()

def list_all_referti() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT r.*, COUNT(a.id) as totale_analiti,
                   SUM(CASE WHEN a.stato_flag != 'NORMALE' THEN 1 ELSE 0 END) as anomalie_count
            FROM referti r
            LEFT JOIN analiti a ON r.id = a.referto_id
            GROUP BY r.id
            ORDER BY r.data_prelievo DESC
            """
        )
        return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()

def delete_referto(referto_id: str) -> bool:
    conn = get_db_connection()
    try:
        with conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM analiti WHERE referto_id = ?", (referto_id,))
            cur.execute("DELETE FROM referti WHERE id = ?", (referto_id,))
            return cur.rowcount > 0
    finally:
        conn.close()

def get_analiti_trend(nome_standardizzato: str) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, referto_id, data_prelievo, laboratorio, valore_numerico,
                   valore_testuale, unita_misura, range_min, range_max, stato_flag
            FROM analiti
            WHERE nome_standardizzato = ?
            ORDER BY data_prelievo ASC
            """,
            (nome_standardizzato,)
        )
        return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()

def get_distinct_biomarkers() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT DISTINCT categoria, nome_standardizzato, unita_misura,
                   COUNT(*) as misurazioni_totali,
                   MAX(data_prelievo) as ultima_data
            FROM analiti
            GROUP BY categoria, nome_standardizzato
            ORDER BY categoria, nome_standardizzato
            """
        )
        return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()

def get_all_anomalies() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT a.*, r.data_caricamento
            FROM analiti a
            JOIN referti r ON a.referto_id = r.id
            WHERE a.stato_flag != 'NORMALE'
            ORDER BY a.data_prelievo DESC
            """
        )
        return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()

def get_all_analiti_for_rag() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT a.id, a.referto_id, a.categoria, a.nome_standardizzato, a.nome_esame_originale,
                   a.valore_numerico, a.valore_testuale, a.unita_misura, a.range_min, a.range_max,
                   a.stato_flag, a.data_prelievo, a.laboratorio, a.note_referto
            FROM analiti a
            ORDER BY a.data_prelievo DESC
            """
        )
        return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()

def set_config_value(chiave: str, valore_criptato: str) -> None:
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    conn = get_db_connection()
    try:
        with conn:
            conn.execute(
                """
                INSERT INTO configurazione (chiave, valore, aggiornato_il)
                VALUES (?, ?, ?)
                ON CONFLICT(chiave) DO UPDATE SET valore=excluded.valore, aggiornato_il=excluded.aggiornato_il
                """,
                (chiave, valore_criptato, now_iso)
            )
    finally:
        conn.close()

def get_config_value(chiave: str) -> Optional[str]:
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT valore FROM configurazione WHERE chiave = ?", (chiave,))
        row = cur.fetchone()
        return row["valore"] if row else None
    finally:
        conn.close()

def save_controllo_fertilita(profile_id: str, tipo_controllo: str, livello: str, stato_controllo: str, data_esecuzione: Optional[str] = None, esito: Optional[str] = None, note: Optional[str] = None) -> str:
    controllo_id = str(uuid.uuid4())
    conn = get_db_connection(profile_id=profile_id)
    try:
        with conn:
            conn.execute(
                """
                INSERT INTO controlli_fertilita (id, profile_id, tipo_controllo, livello, data_esecuzione, stato_controllo, esito, note)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (controllo_id, profile_id, tipo_controllo, livello, data_esecuzione, stato_controllo, esito, note)
            )
        return controllo_id
    finally:
        conn.close()

def list_controlli_fertilita(profile_id: str) -> List[Dict[str, Any]]:
    conn = get_db_connection(profile_id=profile_id)
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT * FROM controlli_fertilita
            WHERE profile_id = ?
            ORDER BY livello ASC, tipo_controllo ASC
            """,
            (profile_id,)
        )
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()

def update_stato_controllo_fertilita(controllo_id: str, stato_controllo: str, data_esecuzione: Optional[str] = None, esito: Optional[str] = None, profile_id: Optional[str] = None) -> bool:
    conn = get_db_connection(profile_id=profile_id)
    try:
        with conn:
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE controlli_fertilita
                SET stato_controllo = ?, data_esecuzione = COALESCE(?, data_esecuzione), esito = COALESCE(?, esito)
                WHERE id = ?
                """,
                (stato_controllo, data_esecuzione, esito, controllo_id)
            )
            return cur.rowcount > 0
    finally:
        conn.close()

def delete_controllo_fertilita(controllo_id: str, profile_id: Optional[str] = None) -> bool:
    conn = get_db_connection(profile_id=profile_id)
    try:
        with conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM controlli_fertilita WHERE id = ?", (controllo_id,))
            return cur.rowcount > 0
    finally:
        conn.close()

def save_imaging_referto(profile_id: str, tipologia_esame: str, organo_distretto: str, data_esame: str, file_path: str, testo_referto: str, analisi_ai: str, livello_criticita: str) -> str:
    imaging_id = str(uuid.uuid4())
    conn = get_db_connection(profile_id=profile_id)
    try:
        with conn:
            conn.execute(
                """
                INSERT INTO imaging_referti (id, profile_id, tipologia_esame, organo_distretto, data_esame, file_path, testo_referto, analisi_ai, livello_criticita)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (imaging_id, profile_id, tipologia_esame, organo_distretto, data_esame, file_path, testo_referto, analisi_ai, livello_criticita)
            )
        return imaging_id
    finally:
        conn.close()

def list_imaging_referti(profile_id: str) -> List[Dict[str, Any]]:
    conn = get_db_connection(profile_id=profile_id)
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT * FROM imaging_referti
            WHERE profile_id = ?
            ORDER BY data_esame DESC
            """,
            (profile_id,)
        )
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()

def get_imaging_referto_by_id(imaging_id: str, profile_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    conn = get_db_connection(profile_id=profile_id)
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM imaging_referti WHERE id = ?", (imaging_id,))
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def delete_imaging_referto(imaging_id: str, profile_id: Optional[str] = None) -> bool:
    conn = get_db_connection(profile_id=profile_id)
    try:
        with conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM imaging_referti WHERE id = ?", (imaging_id,))
            return cur.rowcount > 0
    finally:
        conn.close()
