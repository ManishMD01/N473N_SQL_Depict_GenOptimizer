from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os, re, json
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Oracle SQL Plan Analyzer")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Sample data
SAMPLE_SQL = """SELECT c.customer_name, SUM(t.amount) AS total_amount
FROM transactions t
JOIN customers c ON c.customer_id = t.customer_id
WHERE t.trans_date >= DATE '2025-01-01'
GROUP BY c.customer_name;"""

SAMPLE_PLAN = """Plan hash value: 1234567890

------------------------------------------------------------------------------------------------------------------
| Id  | Operation            | Name         | Starts | E-Rows | A-Rows | A-Time   | Buffers |  OMem |  1Mem | Used-Mem |
------------------------------------------------------------------------------------------------------------------
|   0 | SELECT STATEMENT     |              |      1 |        |   1000 | 00:00:04|   12000 |       |       |          |
|   1 |  HASH GROUP BY       |              |      1 |   1000 |   1000 | 00:00:04|   12000 |  1024K|  1024K| 1024K (0)|
|   2 |   HASH JOIN          |              |      1 |  10000000 |  10000000 | 00:00:03|   11000 |  2048K|  2048K| 2048K (0)|
|   3 |    TABLE ACCESS FULL | CUSTOMERS    |      1 |   5000 |   5000 | 00:00:00|     100 |       |       |          |
|   4 |    TABLE ACCESS FULL | TRANSACTIONS |      1 |  10000000 |  10000000 | 00:00:03|   10900 |       |       |          |
------------------------------------------------------------------------------------------------------------------"""

def parse_plan(plan_text: str) -> List[Dict[str, Any]]:
    rows = []
    for line in plan_text.splitlines():
        m = re.search(r'\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*([^|]*?)\s*\|\s*(\d+)?\s*\|\s*([\d,]*)\s*\|\s*([\d,]*)\s*\|\s*([\d:.]+)?\s*\|\s*([\d,]*)', line)
        if m and m.group(2).strip() and ('OPERATION' not in m.group(2).upper()):
            op = m.group(2).strip()
            name = m.group(3).strip()
            starts = m.group(4) or "1"
            erows = (m.group(5) or "0").replace(",","")
            arows = (m.group(6) or "0").replace(",","")
            atime = m.group(7) or ""
            bufs = (m.group(8) or "0").replace(",","")
            if op in ("Id","Operation"):
                continue
            rows.append({"id": int(m.group(1)), "operation": op, "name": name, "starts": int(starts or 1),
                         "erows": int(erows) if erows else 0, "arows": int(arows) if arows else 0,
                         "atime": atime, "buffers": int(bufs) if bufs else 0})
    return rows

def build_graphs(parsed: List[Dict[str, Any]]):
    if not parsed:
        parsed = [{"id":1,"operation":"TABLE ACCESS FULL","name":"TABLE","arows":1000}]
    current_nodes = []
    for r in parsed:
        current_nodes.append({"id":f"n{r['id']}","label":r.get("name") or r["operation"],"op":r["operation"],"rows":r.get("arows") or r.get("erows") or 1,"color":"amber"})
    current_edges = []
    for i in range(len(current_nodes)-1):
        current_edges.append({"id":f"ce{i}","source":current_nodes[i]["id"],"target":current_nodes[i+1]["id"],"label":current_nodes[i]["op"]})
    # efficient same nodes but green
    efficient_nodes = [dict(n, color="green") for n in current_nodes]
    efficient_edges = list(current_edges)
    return current_nodes, current_edges, efficient_nodes, efficient_edges

class AnalyzeRequest(BaseModel):
    sql: Optional[str] = None
    plan: Optional[str] = None

@app.get("/api/sample")
def sample():
    return {"sql": SAMPLE_SQL, "plan": SAMPLE_PLAN}

@app.post("/api/analyze")
def analyze(req: AnalyzeRequest):
    plan = req.plan or SAMPLE_PLAN
    parsed = parse_plan(plan)
    cn, ce, en, ee = build_graphs(parsed)
    optimized_sql = """SELECT c.customer_name, t.total_amount
FROM customers c
JOIN (
  SELECT customer_id, SUM(amount) AS total_amount
  FROM transactions
  WHERE trans_date >= DATE '2025-01-01'
  GROUP BY customer_id
) t ON c.customer_id = t.customer_id;"""
    suggestions = [
        "Late Aggregation (Group-By Pushdown): pre-aggregate transactions by customer_id before join.",
        "Predicate Pushdown: filter trans_date inside subquery.",
        "Unindexed Filter: CREATE INDEX idx_trans_date ON transactions(trans_date);",
    ]
    return {
        "parsed": parsed,
        "current": {"nodes": cn, "edges": ce},
        "efficient": {"nodes": en, "edges": ee},
        "optimized_sql": optimized_sql,
        "suggestions": suggestions,
    }

import pathlib
_dist = pathlib.Path(__file__).resolve().parent.parent / "frontend" / "dist"
if _dist.exists():
    app.mount("/", StaticFiles(directory=str(_dist), html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
