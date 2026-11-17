from typing import Optional, List
from pydantic import BaseModel, Field

class AnalitaBase(BaseModel):
    categoria: str
    nome_esame_originale: str
    nome_standardizzato: str
    valore_numerico: Optional[float] = None
    valore_testuale: Optional[str] = None
    unita_misura: str
    range_min: Optional[float] = None
    range_max: Optional[float] = None
    stato_flag: str
    data_prelievo: str
    laboratorio: str
    note_referto: Optional[str] = None

class AnalitaCreate(AnalitaBase):
    referto_id: str

class AnalitaRead(AnalitaBase):
    id: str
    referto_id: str

class ManualAnalitaCreate(BaseModel):
    profile_id: Optional[str] = None
    categoria: str
    nome_esame_originale: str
    nome_standardizzato: str
    valore_numerico: Optional[float] = None
    valore_testuale: Optional[str] = None
    unita_misura: str
    range_min: Optional[float] = None
    range_max: Optional[float] = None
    stato_flag: Optional[str] = None
    data_prelievo: str
    laboratorio: str
    note_referto: Optional[str] = None

class RefertoBase(BaseModel):
    data_prelievo: str
    laboratorio: str
    note: Optional[str] = None

class RefertoCreate(RefertoBase):
    file_path: str
    stato_revisione: str = "BOZZA"

class RefertoRead(RefertoBase):
    id: str
    data_caricamento: str
    file_path: str
    stato_revisione: str
    analiti: List[AnalitaRead] = []

class RefertoRevisionPayload(BaseModel):
    referto_id: str
    data_prelievo: str
    laboratorio: str
    note: Optional[str] = None
    analiti: List[AnalitaBase]

class BodyCompositionBase(BaseModel):
    data_misurazione: str
    peso_kg: float
    altezza_cm: Optional[float] = None
    bmi: Optional[float] = None
    massa_grassa_pct: Optional[float] = None
    acqua_totale_pct: Optional[float] = None
    massa_muscolare_kg: Optional[float] = None
    massa_ossea_kg: Optional[float] = None
    grasso_viscerale: Optional[float] = None
    metabolismo_basale_kcal: Optional[float] = None
    eta_metabolica: Optional[float] = None
    muscolo_scheletrico_pct: Optional[float] = None
    note: Optional[str] = None

class BodyCompositionCreate(BodyCompositionBase):
    profile_id: Optional[str] = None

class BodyCompositionRead(BodyCompositionBase):
    id: str
    profile_id: str

class DailyHealthMetricsBase(BaseModel):
    data: str
    passi_giornalieri: Optional[int] = None
    distanza_km: Optional[float] = None
    calorie_attive_kcal: Optional[float] = None
    bpm_riposo: Optional[float] = None
    bpm_min: Optional[float] = None
    bpm_max: Optional[float] = None
    pressione_sistolica: Optional[float] = None
    pressione_diastolica: Optional[float] = None
    spo2_min: Optional[float] = None
    spo2_media: Optional[float] = None
    indice_apnea_ahi: Optional[float] = None
    episodi_apnea_totali: Optional[int] = None
    durata_desaturazione_minuti: Optional[float] = None
    ore_sonno_totali: Optional[float] = None
    sonno_profondo_minuti: Optional[float] = None
    sonno_rem_minuti: Optional[float] = None
    hrv_ms: Optional[float] = None
    temperatura_corporea: Optional[float] = None
    frequenza_respiratoria: Optional[float] = None
    note: Optional[str] = None

class DailyHealthMetricsCreate(DailyHealthMetricsBase):
    profile_id: Optional[str] = None

class DailyHealthMetricsRead(DailyHealthMetricsBase):
    id: str
    profile_id: str

class AIJobBase(BaseModel):
    job_type: str
    parameters_json: Optional[str] = None

class AIJobCreate(AIJobBase):
    profile_id: Optional[str] = None

class AIJobRead(AIJobBase):
    id: str
    profile_id: str
    status: str
    progress: int
    current_step: Optional[str] = None
    result_json: Optional[str] = None
    error_message: Optional[str] = None
    created_at: str
    updated_at: str
    estimated_completion: Optional[str] = None

CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS referti (
    id TEXT PRIMARY KEY,
    data_prelievo TEXT NOT NULL,
    laboratorio TEXT NOT NULL,
    data_caricamento TEXT NOT NULL,
    file_path TEXT NOT NULL,
    note TEXT,
    stato_revisione TEXT NOT NULL DEFAULT 'BOZZA'
);

CREATE TABLE IF NOT EXISTS analiti (
    id TEXT PRIMARY KEY,
    referto_id TEXT NOT NULL,
    categoria TEXT NOT NULL,
    nome_esame_originale TEXT NOT NULL,
    nome_standardizzato TEXT NOT NULL,
    valore_numerico REAL,
    valore_testuale TEXT,
    unita_misura TEXT NOT NULL,
    range_min REAL,
    range_max REAL,
    stato_flag TEXT NOT NULL,
    data_prelievo TEXT NOT NULL,
    laboratorio TEXT NOT NULL,
    note_referto TEXT,
    FOREIGN KEY (referto_id) REFERENCES referti(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_analiti_standardizzato ON analiti(nome_standardizzato);
CREATE INDEX IF NOT EXISTS idx_analiti_data ON analiti(data_prelievo);
CREATE INDEX IF NOT EXISTS idx_analiti_categoria ON analiti(categoria);
CREATE INDEX IF NOT EXISTS idx_analiti_flag ON analiti(stato_flag);
CREATE INDEX IF NOT EXISTS idx_referti_data ON referti(data_prelievo);

CREATE TABLE IF NOT EXISTS categorie (
    id TEXT PRIMARY KEY,
    nome TEXT NOT NULL UNIQUE,
    descrizione TEXT
);

CREATE TABLE IF NOT EXISTS correlazioni (
    id TEXT PRIMARY KEY,
    titolo TEXT NOT NULL,
    sistema_fisiologico TEXT NOT NULL,
    descrizione TEXT NOT NULL,
    biomarcatori_coinvolti TEXT NOT NULL,
    data_rilevamento TEXT NOT NULL,
    livello_criticita TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    azione TEXT NOT NULL,
    dettagli TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS configurazione (
    chiave TEXT PRIMARY KEY,
    valore TEXT NOT NULL,
    aggiornato_il TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS controlli_fertilita (
    id TEXT PRIMARY KEY,
    profile_id TEXT NOT NULL,
    tipo_controllo TEXT NOT NULL,
    livello TEXT NOT NULL,
    data_esecuzione TEXT,
    stato_controllo TEXT NOT NULL,
    esito TEXT,
    note TEXT
);

CREATE TABLE IF NOT EXISTS imaging_referti (
    id TEXT PRIMARY KEY,
    profile_id TEXT NOT NULL,
    tipologia_esame TEXT NOT NULL,
    organo_distretto TEXT NOT NULL,
    data_esame TEXT NOT NULL,
    file_path TEXT,
    testo_referto TEXT,
    analisi_ai TEXT,
    livello_criticita TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS body_composition (
    id TEXT PRIMARY KEY,
    profile_id TEXT NOT NULL,
    data_misurazione TEXT NOT NULL,
    peso_kg REAL NOT NULL,
    altezza_cm REAL,
    bmi REAL,
    massa_grassa_pct REAL,
    acqua_totale_pct REAL,
    massa_muscolare_kg REAL,
    massa_ossea_kg REAL,
    grasso_viscerale REAL,
    metabolismo_basale_kcal REAL,
    eta_metabolica REAL,
    muscolo_scheletrico_pct REAL,
    note TEXT
);

CREATE TABLE IF NOT EXISTS daily_health_metrics (
    id TEXT PRIMARY KEY,
    profile_id TEXT NOT NULL,
    data TEXT NOT NULL,
    passi_giornalieri INTEGER,
    distanza_km REAL,
    calorie_attive_kcal REAL,
    bpm_riposo REAL,
    bpm_min REAL,
    bpm_max REAL,
    pressione_sistolica REAL,
    pressione_diastolica REAL,
    spo2_min REAL,
    spo2_media REAL,
    indice_apnea_ahi REAL,
    episodi_apnea_totali INTEGER,
    durata_desaturazione_minuti REAL,
    ore_sonno_totali REAL,
    sonno_profondo_minuti REAL,
    sonno_rem_minuti REAL,
    hrv_ms REAL,
    temperatura_corporea REAL,
    frequenza_respiratoria REAL,
    note TEXT
);

CREATE TABLE IF NOT EXISTS ai_analysis_jobs (
    id TEXT PRIMARY KEY,
    profile_id TEXT NOT NULL,
    job_type TEXT NOT NULL,
    status TEXT NOT NULL,
    progress INTEGER NOT NULL DEFAULT 0,
    current_step TEXT,
    parameters_json TEXT,
    result_json TEXT,
    error_message TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    estimated_completion TEXT
);

CREATE INDEX IF NOT EXISTS idx_controlli_profile ON controlli_fertilita(profile_id);
CREATE INDEX IF NOT EXISTS idx_imaging_profile ON imaging_referti(profile_id);
CREATE INDEX IF NOT EXISTS idx_body_comp_profile ON body_composition(profile_id);
CREATE INDEX IF NOT EXISTS idx_daily_health_profile ON daily_health_metrics(profile_id);
CREATE INDEX IF NOT EXISTS idx_ai_jobs_profile ON ai_analysis_jobs(profile_id);
"""
