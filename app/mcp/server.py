import json
from typing import Dict, Any, List
from app.profiles.profile_manager import profile_manager
from app.analytics.health_score import health_score_calculator
from app.analytics.radar_anomalies import radar_anomalies_engine
from app.analytics.trends import trends_engine
from app.analytics.correlations import correlation_engine
from app.rag.clinical_rag import clinical_rag_engine
from app.fertility.protocols.female_protocols import get_female_fertility_protocol
from app.fertility.protocols.male_protocols import get_male_fertility_protocol
from app.fertility.calculators.ovarian_reserve import calculate_ovarian_reserve
from app.fertility.calculators.semen_quality import evaluate_semen_sample
from app.fertility.imaging_analyzer import imaging_analyzer

MCP_TOOLS = [
    {
        "name": "list_family_profiles",
        "description": "Elenca tutti i membri della famiglia registrati nel software Anamnesix con il loro ID e parentela.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "get_patient_clinical_summary",
        "description": "Restituisce l'Health Score e la sintesi clinica per il profilo familiare specificato.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "profile_id": {"type": "string", "description": "ID del membro della famiglia"}
            },
            "required": ["profile_id"]
        }
    },
    {
        "name": "get_out_of_range_anomalies",
        "description": "Ottiene tutti gli analiti fuori range con scostamento percentuale e persistenza temporale.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "profile_id": {"type": "string", "description": "ID del membro della famiglia"}
            },
            "required": ["profile_id"]
        }
    },
    {
        "name": "get_biomarker_history",
        "description": "Restituisce l'andamento storico cronologico e il trend di un biomarcatore specifico.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "nome_standardizzato": {"type": "string", "description": "Nome standardizzato dell'esame (es. Colesterolo LDL, Glicemia, Ferritina)"},
                "profile_id": {"type": "string", "description": "ID del membro della famiglia"}
            },
            "required": ["nome_standardizzato", "profile_id"]
        }
    },
    {
        "name": "evaluate_health_correlations",
        "description": "Esegue l'analisi incrociata dei pannelli clinici per rilevare quadri fisiopatologici complessi.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "profile_id": {"type": "string", "description": "ID del membro della famiglia"}
            },
            "required": ["profile_id"]
        }
    },
    {
        "name": "query_clinical_rag",
        "description": "Interroga in linguaggio naturale lo storico clinico e i referti tramite motore RAG dedicato con citazioni.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "domanda": {"type": "string", "description": "Domanda clinica dell'utente"},
                "profile_id": {"type": "string", "description": "ID del membro della famiglia"}
            },
            "required": ["domanda", "profile_id"]
        }
    },
    {
        "name": "get_fertility_protocol",
        "description": "Fornisce il protocollo clinico dettagliato e la checklist esami per eta e genere.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "genere": {"type": "string", "enum": ["femminile", "maschile"], "description": "Genere del paziente"},
                "eta": {"type": "integer", "description": "Eta anagrafica del paziente in anni"}
            },
            "required": ["genere", "eta"]
        }
    },
    {
        "name": "calculate_ovarian_reserve",
        "description": "Calcola la stima della riserva ovarica e della risposta follicolare da AMH, AFC ed eta.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "eta": {"type": "integer", "description": "Eta anagrafica in anni"},
                "amh": {"type": "number", "description": "Livello di Ormone Anti-Mulleriano in ng/mL"},
                "afc": {"type": "integer", "description": "Conta follicoli antrali ecografica"}
            },
            "required": ["eta"]
        }
    },
    {
        "name": "evaluate_semen_sample",
        "description": "Valuta i parametri di spermiogramma secondo le linee guida WHO 6th edition.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "volume_ml": {"type": "number", "description": "Volume eiaculato in mL"},
                "concentration_m_ml": {"type": "number", "description": "Concentrazione spermatozoi in milioni/mL"},
                "progressive_motility_pct": {"type": "number", "description": "Motilita progressiva (PR) in percentuale"},
                "total_motility_pct": {"type": "number", "description": "Motilita totale in percentuale"},
                "normal_morphology_pct": {"type": "number", "description": "Morfologia normale in percentuale"},
                "leukocytes_m_ml": {"type": "number", "description": "Leucociti in milioni/mL"},
                "ph": {"type": "number", "description": "pH seminale"}
            }
        }
    },
    {
        "name": "analyze_imaging_scan",
        "description": "Analizza referti o descrizioni di scansioni diagnostiche (TAC, RMN, ecografia testicolare, ecografia transvaginale).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "report_text": {"type": "string", "description": "Testo del referto radiologico o ecografico"},
                "tipologia_esame": {"type": "string", "description": "Tipo di esame strumentale"},
                "organo_distretto": {"type": "string", "description": "Distretto anatomico esaminato"}
            },
            "required": ["report_text"]
        }
    }
]

class MCPServer:
    def __init__(self):
        self.ready = True

    def list_tools(self) -> List[Dict[str, Any]]:
        return MCP_TOOLS

    async def execute_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        profile_id = arguments.get("profile_id")

        if name == "list_family_profiles":
            profiles = profile_manager.list_profiles()
            return {"content": [{"type": "text", "text": json.dumps(profiles, ensure_ascii=False)}]}

        elif name == "get_patient_clinical_summary":
            summary = health_score_calculator.calculate_scores(profile_id=profile_id)
            return {"content": [{"type": "text", "text": json.dumps(summary, ensure_ascii=False)}]}

        elif name == "get_out_of_range_anomalies":
            anomalies = radar_anomalies_engine.get_ranked_anomalies(profile_id=profile_id)
            return {"content": [{"type": "text", "text": json.dumps(anomalies, ensure_ascii=False)}]}

        elif name == "get_biomarker_history":
            nome = arguments.get("nome_standardizzato", "")
            trend = trends_engine.get_analyte_trend_data(nome_standardizzato=nome, profile_id=profile_id)
            return {"content": [{"type": "text", "text": json.dumps(trend, ensure_ascii=False)}]}

        elif name == "evaluate_health_correlations":
            corr = correlation_engine.evaluate_correlations(profile_id=profile_id)
            return {"content": [{"type": "text", "text": json.dumps(corr, ensure_ascii=False)}]}

        elif name == "query_clinical_rag":
            domanda = arguments.get("domanda", "")
            rag_res = await clinical_rag_engine.answer_query(query=domanda, profile_id=profile_id)
            return {"content": [{"type": "text", "text": json.dumps(rag_res, ensure_ascii=False)}]}

        elif name == "get_fertility_protocol":
            genere = str(arguments.get("genere", "femminile")).lower()
            eta = int(arguments.get("eta", 30))
            if "masch" in genere:
                protocollo = get_male_fertility_protocol(eta)
            else:
                protocollo = get_female_fertility_protocol(eta)
            return {"content": [{"type": "text", "text": json.dumps(protocollo, ensure_ascii=False)}]}

        elif name == "calculate_ovarian_reserve":
            eta = int(arguments.get("eta", 30))
            amh = arguments.get("amh")
            afc = arguments.get("afc")
            res_ov = calculate_ovarian_reserve(eta=eta, amh=amh, afc=afc)
            return {"content": [{"type": "text", "text": json.dumps(res_ov, ensure_ascii=False)}]}

        elif name == "evaluate_semen_sample":
            res_semen = evaluate_semen_sample(
                volume_ml=arguments.get("volume_ml"),
                concentration_m_ml=arguments.get("concentration_m_ml"),
                progressive_motility_pct=arguments.get("progressive_motility_pct"),
                total_motility_pct=arguments.get("total_motility_pct"),
                normal_morphology_pct=arguments.get("normal_morphology_pct"),
                leukocytes_m_ml=arguments.get("leukocytes_m_ml"),
                ph=arguments.get("ph")
            )
            return {"content": [{"type": "text", "text": json.dumps(res_semen, ensure_ascii=False)}]}

        elif name == "analyze_imaging_scan":
            rep_text = arguments.get("report_text", "")
            tipo = arguments.get("tipologia_esame", "ECO_GENERICA")
            distr = arguments.get("organo_distretto", "Pelvi")
            rep_res = await imaging_analyzer.analyze_imaging(
                report_text=rep_text,
                tipologia_esame=tipo,
                organo_distretto=distr
            )
            return {"content": [{"type": "text", "text": json.dumps(rep_res, ensure_ascii=False)}]}

        else:
            return {"isError": True, "content": [{"type": "text", "text": f"Strumento MCP non riconosciuto: {name}"}]}

    async def handle_json_rpc(self, request_json: Dict[str, Any]) -> Dict[str, Any]:
        req_id = request_json.get("id")
        method = request_json.get("method")
        params = request_json.get("params", {})

        if method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"tools": self.list_tools()}
            }
        elif method == "tools/call":
            tool_name = params.get("name", "")
            tool_args = params.get("arguments", {})
            res = await self.execute_tool(tool_name, tool_args)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": res
            }
        else:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Metodo non trovato: {method}"}
            }

mcp_server = MCPServer()
