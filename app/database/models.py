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
"""
