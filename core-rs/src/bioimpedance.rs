use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BodyMetrics {
    pub weight_kg: f64,
    pub height_cm: Option<f64>,
    pub fat_percentage: Option<f64>,
    pub water_percentage: Option<f64>,
    pub muscle_kg: Option<f64>,
    pub bone_kg: Option<f64>,
    pub visceral_fat_rating: Option<u32>,
    pub age: Option<u32>,
    pub is_male: Option<bool>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BioimpedanceAnalysis {
    pub bmi: Option<f64>,
    pub bmi_category: String,
    pub bmr_kcal: Option<f64>,
    pub fat_free_mass_kg: Option<f64>,
    pub visceral_fat_risk: String,
    pub hydration_status: String,
}

pub fn calculate_bioimpedance(metrics: &BodyMetrics) -> BioimpedanceAnalysis {
    let bmi = if let Some(h) = metrics.height_cm {
        if h > 0.0 {
            let m = h / 100.0;
            Some((metrics.weight_kg / (m * m) * 10.0).round() / 10.0)
        } else {
            None
        }
    } else {
        None
    };

    let bmi_category = match bmi {
        Some(val) if val < 18.5 => "Sottopeso",
        Some(val) if val < 25.0 => "Normopeso",
        Some(val) if val < 30.0 => "Sovrappeso",
        Some(_) => "Obesita",
        None => "Non calcolabile",
    }.to_string();

    let fat_free_mass_kg = if let Some(fat_pct) = metrics.fat_percentage {
        let fat_mass = metrics.weight_kg * (fat_pct / 100.0);
        Some(((metrics.weight_kg - fat_mass) * 10.0).round() / 10.0)
    } else {
        metrics.muscle_kg
    };

    let bmr_kcal = if let (Some(h), Some(age), Some(is_male)) = (metrics.height_cm, metrics.age, metrics.is_male) {
        let base = (10.0 * metrics.weight_kg) + (6.25 * h) - (5.0 * age as f64);
        let val = if is_male { base + 5.0 } else { base - 161.0 };
        Some(val.round())
    } else if let Some(ffm) = fat_free_mass_kg {
        Some((370.0 + (21.6 * ffm)).round())
    } else {
        None
    };

    let visceral_fat_risk = match metrics.visceral_fat_rating {
        Some(lvl) if lvl <= 9 => "Normale (1-9)".to_string(),
        Some(lvl) if lvl <= 14 => "Aumentato (10-14)".to_string(),
        Some(_) => "Critico Elevato (15+)".to_string(),
        None => "Non rilevato".to_string(),
    };

    let hydration_status = match metrics.water_percentage {
        Some(w) if w >= 55.0 && w <= 65.0 => "Idratazione Fisiologica Ottimale".to_string(),
        Some(w) if w < 55.0 => "Tendenza alla Disidratazione".to_string(),
        Some(_) => "Iperidratazione / Ritenzione".to_string(),
        None => "Non rilevata".to_string(),
    };

    BioimpedanceAnalysis {
        bmi,
        bmi_category,
        bmr_kcal,
        fat_free_mass_kg,
        visceral_fat_risk,
        hydration_status,
    }
}
