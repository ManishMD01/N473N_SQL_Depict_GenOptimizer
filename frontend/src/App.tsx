import { useEffect, useState } from "react";
import { ReactFlow, Background, Controls, useNodesState, useEdgesState, Handle, Position, ReactFlowProvider, useReactFlow } from "@xyflow/react";
import type { Node, Edge } from "@xyflow/react";
import "@xyflow/react/dist/style.css";

type GNode = { id: string; label: string; op: string; rows: number; color: string };

const colorMap: Record<string, string> = { red: "border-red-500 bg-red-50", amber: "border-amber-500 bg-amber-50", green: "border-green-500 bg-green-50" };

function TableNode({ data }: { data: any }) {
  const n: GNode = data.node;
  const rows = Math.max(1, Math.min(6, Math.round(Math.log10(n.rows + 1))));
  return (
    <div className={`border-2 rounded-lg p-2 w-40 ${colorMap[n.color] || "border-gray-300 bg-white"}`}>
      <Handle type="target" position={Position.Left} />
      <div className="text-xs font-bold">{n.label}</div>
      <div className="text-[10px] text-gray-600">{n.op}</div>
      <div className="mt-1 grid gap-0.5" style={{ gridTemplateRows: `repeat(${rows}, 1fr)` }}>
        {Array.from({ length: rows }).map((_, i) => (
          <div key={i} className="h-1 bg-gray-400 rounded" />
        ))}
      </div>
      <div className="text-[10px] mt-1 font-mono">{n.rows.toLocaleString()} rows</div>
      <Handle type="source" position={Position.Right} />
    </div>
  );
}

const nodeTypes = { table: TableNode };

function Panel({ title, nodes, edges }: { title: string; nodes: GNode[]; edges: any[] }) {
  const [ns, setNodes] = useNodesState<Node>([]);
  const [es, setEdges] = useEdgesState<Edge>([]);
  const { fitView } = useReactFlow();
  useEffect(() => {
    const flowNodes: Node[] = nodes.map((n) => ({ id: n.id, type: "table", data: { node: n }, position: { x: 0, y: 0 } }));
    const flowEdges: Edge[] = edges.map((e) => ({ id: e.id, source: e.source, target: e.target, label: e.label, animated: true }));
    flowNodes.forEach((n,i)=>{ n.position={x:i*200,y:0}; });
    setNodes(flowNodes);
    setEdges(flowEdges);
    setTimeout(() => fitView(), 50);
  }, [nodes, edges]);
  return (
    <div className="flex-1 border rounded-lg overflow-hidden">
      <div className="bg-gray-100 px-3 py-2 font-semibold text-sm">{title}</div>
      <div style={{height:"320px"}}>
        <ReactFlow nodes={ns} edges={es} nodeTypes={nodeTypes} fitView>
          <Background />
          <Controls />
        </ReactFlow>
      </div>
    </div>
  );
}

export default function App() {
  const [sql, setSql] = useState("");
  const [plan, setPlan] = useState("");
  const [cur, setCur] = useState<{ nodes: GNode[]; edges: any[] }>({ nodes: [], edges: [] });
  const [eff, setEff] = useState<{ nodes: GNode[]; edges: any[] }>({ nodes: [], edges: [] });
  const [optSql, setOptSql] = useState("");
  const [sugg, setSugg] = useState<string[]>([]);
  const [status, setStatus] = useState("");

  const analyze = async () => {
    try {
      setStatus("Analyzing...");
      const r = await fetch("/api/analyze", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ sql, plan }) });
      const d = await r.json();
      setCur(d.current); setEff(d.efficient); setOptSql(d.optimized_sql); setSugg(d.suggestions);
      setStatus("Done");
    } catch (e) { console.error(e); setStatus("Error: "+String(e)); }
  };


  return (
    <ReactFlowProvider>
    <div className="p-4 space-y-4">
      <h1 className="text-xl font-bold">Oracle SQL Execution Plan Analyzer & Visual Query Optimizer</h1>
      <div className="grid grid-cols-2 gap-3">
        <textarea className="border p-2 h-40 font-mono text-xs" value={sql} onChange={(e) => setSql(e.target.value)} placeholder="SQL" />
        <textarea className="border p-2 h-40 font-mono text-xs" value={plan} onChange={(e) => setPlan(e.target.value)} placeholder="Plan" />
      </div>
      <button onClick={analyze} className="bg-blue-600 text-white px-4 py-2 rounded relative z-10 cursor-pointer">Analyze & Optimize</button>
      <span className="ml-3 text-sm">{status}</span>
      <div className="flex gap-3">
        <Panel title="Current / Inefficient Execution Plan" nodes={cur.nodes} edges={cur.edges} />
        <Panel title="AI-Optimized / Efficient Execution Plan" nodes={eff.nodes} edges={eff.edges} />
      </div>
      {optSql && (
        <div className="border rounded p-3">
          <div className="font-semibold text-sm mb-1">Optimized SQL</div>
          <pre className="text-xs font-mono whitespace-pre-wrap">{optSql}</pre>
          <ul className="mt-2 text-xs list-disc pl-5">{sugg.map((s, i) => <li key={i}>{s}</li>)}</ul>
        </div>
      )}
    </div>
    </ReactFlowProvider>
  );
}
