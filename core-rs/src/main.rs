use anamnesix_core::{
    biomarkers::{BiomarkerRecord, evaluate_biomarkers_batch},
    bioimpedance::{BodyMetrics, calculate_bioimpedance},
    vitals::{VitalMetrics, evaluate_vitals},
    crypto::{derive_argon2_key, encrypt_aes256_gcm, decrypt_aes256_gcm},
};
use std::time::Instant;

fn main() {
    println!("=== ANAMNESIX RUST NATIVE ENGINE BENCHMARK & TEST ===");

    let mut batch = Vec::with_capacity(100_000);
    for i in 0..100_000 {
        batch.push(BiomarkerRecord {
            name: format!("Biomarcatore_{}", i),
            category: "Biochimica Clinica".to_string(),
            value_numeric: Some(85.0 + (i as f64 % 40.0)),
            value_text: None,
            unit: "mg/dL".to_string(),
            range_min: Some(70.0),
            range_max: Some(100.0),
        });
    }

    let start = Instant::now();
    let evaluations = evaluate_biomarkers_batch(&batch);
    let duration = start.elapsed();

    println!("Valutati {} biomarcatori in {:.2?}", evaluations.len(), duration);

    let body = BodyMetrics {
        weight_kg: 74.5,
        height_cm: Some(178.0),
        fat_percentage: Some(14.8),
        water_percentage: Some(59.2),
        muscle_kg: Some(60.2),
        bone_kg: Some(3.3),
        visceral_fat_rating: Some(4),
        age: Some(34),
        is_male: Some(true),
    };
    let bia_res = calculate_bioimpedance(&body);
    println!("BIA BMI: {:?}, Categoria: {}, BMR: {:?} kcal", bia_res.bmi, bia_res.bmi_category, bia_res.bmr_kcal);

    let vitals = VitalMetrics {
        daily_steps: Some(11200),
        resting_bpm: Some(58.0),
        max_bpm: Some(145.0),
        systolic_bp: Some(118.0),
        diastolic_bp: Some(76.0),
        spo2_avg: Some(98.2),
        ahi_index: Some(2.1),
        total_apneas: Some(14),
        sleep_hours: Some(7.8),
    };
    let vit_res = evaluate_vitals(&vitals);
    println!("Vitals: Apnea: {}, Pressione: {}", vit_res.apnea_severity, vit_res.bp_category);

    let salt = [42u8; 16];
    let key = derive_argon2_key("MasterPasswordSicura2026!", &salt).expect("Key derivation failed");
    let test_data = b"Dati Sanitari Clinici Cifrati Zero Knowledge";
    let (ciphertext, nonce) = encrypt_aes256_gcm(test_data, &key).expect("Encryption failed");
    let decrypted = decrypt_aes256_gcm(&ciphertext, &nonce, &key).expect("Decryption failed");
    assert_eq!(test_data, &decrypted[..]);
    println!("Crittografia AES-256-GCM + Argon2id verificata con successo.");
}
