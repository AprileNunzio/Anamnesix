from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from app.security.session import session_manager
from app.analytics.health_score import health_score_calculator
from app.analytics.radar_anomalies import radar_anomalies_engine
from app.analytics.trends import trends_engine
from app.analytics.correlations import correlation_engine
from app.analytics.second_opinion import second_opinion_service
from app.database.repository import get_distinct_biomarkers

router = APIRouter(prefix="/api/analytics", tags=["Analitica Clinica"])

def verify_session():
    if session_manager.is_locked():
        raise HTTPException(status_code=401, detail="Sessione bloccata.")

@router.get("/health-score", dependencies=[Depends(verify_session)])
def get_health_score(profile_id: Optional[str] = None):
    return health_score_calculator.calculate_scores(profile_id=profile_id)

@router.get("/radar-anomalies", dependencies=[Depends(verify_session)])
def get_radar_anomalies(profile_id: Optional[str] = None):
    return radar_anomalies_engine.get_ranked_anomalies(profile_id=profile_id)

@router.get("/biomarkers", dependencies=[Depends(verify_session)])
def list_biomarkers():
    return get_distinct_biomarkers()

@router.get("/trend/{biomarker_name}", dependencies=[Depends(verify_session)])
def get_trend(biomarker_name: str, profile_id: Optional[str] = None):
    return trends_engine.get_analyte_trend_data(biomarker_name, profile_id=profile_id)

@router.get("/correlations", dependencies=[Depends(verify_session)])
def get_correlations(profile_id: Optional[str] = None):
    return correlation_engine.evaluate_correlations(profile_id=profile_id)

@router.post("/second-opinion", dependencies=[Depends(verify_session)])
async def generate_second_opinion(profile_id: Optional[str] = None):
    try:
        report = await second_opinion_service.generate_report(profile_id=profile_id)
        return {"status": "success", "report": report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore generazione Second Opinion: {str(e)}")
