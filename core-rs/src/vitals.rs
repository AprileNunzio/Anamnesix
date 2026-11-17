use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct VitalMetrics {
    pub daily_steps: Option<u32>,
    pub resting_bpm: Option<f64>,
    pub max_bpm: Option<f64>,
    pub systolic_bp: Option<f64>,
    pub diastolic_bp: Option<f64>,
    pub spo2_avg: Option<f64>,
    pub ahi_index: Option<f64>,
    pub total_apneas: Option<u32>,
    pub sleep_hours: Option<f64>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct VitalsEvaluation {
    pub apnea_severity: String,
    pub bp_category: String,
    pub cardio_status: String,
    pub activity_status: String,
}

pub fn evaluate_vitals(vitals: &VitalMetrics) -> VitalsEvaluation {
    let apnea_severity = match vitals.ahi_index {
        Some(ahi) if ahi < 5.0 => "Fisiologico (<5/h)".to_string(),
        Some(ahi) if ahi < 15.0 => "Sindrome Apnea Ostruttiva Lieve (5-15/h)".to_string(),
        Some(ahi) if ahi < 30.0 => "Sindrome Apnea Ostruttiva Moderata (15-30/h)".to_string(),
        Some(_) => "Sindrome Apnea Ostruttiva Grave (>30/h)".to_string(),
        None => "Dato AHI non presente".to_string(),
    };

    let bp_category = match (vitals.systolic_bp, vitals.diastolic_bp) {
        (Some(sys), Some(dia)) if sys < 120.0 && dia < 80.0 => "Pressione Ottimale (<120/<80)".to_string(),
        (Some(sys), Some(dia)) if sys <= 129.0 && dia <= 84.0 => "Pressione Normale (120-129/80-84)".to_string(),
        (Some(sys), Some(dia)) if sys <= 139.0 || dia <= 89.0 => "Pre-Ipertensione (130-139/85-89)".to_string(),
        (Some(sys), Some(dia)) if sys >= 140.0 || dia >= 90.0 => "Ipertensione Arteriosa (>140/>90)".to_string(),
        _ => "Dati pressori incompleti".to_string(),
    };

    let cardio_status = match vitals.resting_bpm {
        Some(bpm) if bpm < 50.0 => "Bradicardia a riposo".to_string(),
        Some(bpm) if bpm <= 80.0 => "Normofrequenza ottimale".to_string(),
        Some(bpm) if bpm <= 100.0 => "Frequenza basale elevata".to_string(),
        Some(_) => "Tachicardia a riposo".to_string(),
        None => "Non rilevata".to_string(),
    };

    let activity_status = match vitals.daily_steps {
        Some(steps) if steps >= 10000 => "Attivita Fisica Ottimale (>=10k passi)".to_string(),
        Some(steps) if steps >= 7000 => "Attivita Moderata (7k-10k passi)".to_string(),
        Some(steps) if steps >= 4000 => "Attivita Ridotta (4k-7k passi)".to_string(),
        Some(_) => "Sedentarieta (<4k passi)".to_string(),
        None => "Non rilevata".to_string(),
    };

    VitalsEvaluation {
        apnea_severity,
        bp_category,
        cardio_status,
        activity_status,
    }
}
