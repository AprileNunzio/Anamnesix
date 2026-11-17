use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BiomarkerRecord {
    pub name: String,
    pub category: String,
    pub value_numeric: Option<f64>,
    pub value_text: Option<String>,
    pub unit: String,
    pub range_min: Option<f64>,
    pub range_max: Option<f64>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum StatusFlag {
    Normale,
    Basso,
    Alto,
    CriticoBasso,
    CriticoAlto,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BiomarkerEvaluation {
    pub name: String,
    pub category: String,
    pub status: StatusFlag,
    pub percentage_deviation: f64,
    pub clinical_summary: String,
}

pub fn evaluate_single_biomarker(record: &BiomarkerRecord) -> BiomarkerEvaluation {
    if let Some(val) = record.value_numeric {
        let mut status = StatusFlag::Normale;
        let mut dev = 0.0;

        if let Some(min_ref) = record.range_min {
            if val < min_ref {
                dev = if min_ref != 0.0 { ((min_ref - val) / min_ref) * 100.0 } else { 0.0 };
                status = if dev > 30.0 { StatusFlag::CriticoBasso } else { StatusFlag::Basso };
            }
        }

        if let Some(max_ref) = record.range_max {
            if val > max_ref {
                dev = if max_ref != 0.0 { ((val - max_ref) / max_ref) * 100.0 } else { 0.0 };
                status = if dev > 30.0 { StatusFlag::CriticoAlto } else { StatusFlag::Alto };
            }
        }

        let summary = match status {
            StatusFlag::Normale => format!("{}: Valore {:.2} {} nei range fisiologici.", record.name, val, record.unit),
            StatusFlag::Basso | StatusFlag::CriticoBasso => format!("{}: Valore {:.2} {} inferiore alla soglia minima (-{:.1}%).", record.name, val, record.unit, dev),
            StatusFlag::Alto | StatusFlag::CriticoAlto => format!("{}: Valore {:.2} {} superiore alla soglia massima (+{:.1}%).", record.name, val, record.unit, dev),
        };

        BiomarkerEvaluation {
            name: record.name.clone(),
            category: record.category.clone(),
            status,
            percentage_deviation: (dev * 10.0).round() / 10.0,
            clinical_summary: summary,
        }
    } else {
        let txt = record.value_text.as_deref().unwrap_or("Non disponibile");
        let lower = txt.to_lowercase();
        let status = if lower.contains("positivo") || lower.contains("reattivo") || lower.contains("presente") {
            StatusFlag::Alto
        } else {
            StatusFlag::Normale
        };

        BiomarkerEvaluation {
            name: record.name.clone(),
            category: record.category.clone(),
            status,
            percentage_deviation: 0.0,
            clinical_summary: format!("{}: Esito qualitativo {}", record.name, txt),
        }
    }
}

pub fn evaluate_biomarkers_batch(records: &[BiomarkerRecord]) -> Vec<BiomarkerEvaluation> {
    records.iter().map(evaluate_single_biomarker).collect()
}
