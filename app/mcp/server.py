import json
from typing import Dict, Any, List
from app.profiles.profile_manager import profile_manager
from app.analytics.health_score import health_score_calculator
from app.analytics.radar_anomalies import radar_anomalies_engine
from app.analytics.trends import trends_engine
from app.analytics.correlations import correlation_engine
from app.rag.clinical_rag import clinical_rag_engine

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
