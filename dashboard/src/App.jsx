import { useState, useEffect, useCallback } from "react";
import { api } from "./api";
import CollectionsPanel from "./components/CollectionsPanel";
import IngestPanel from "./components/IngestPanel";
import SearchPanel from "./components/SearchPanel";
import ModelsPanel from "./components/ModelsPanel";

const TABS = ["Search", "Ingest", "Collections", "Models"];

export default function App() {
  const [tab, setTab] = useState("Search");
  const [collections, setCollections] = useState([]);
  const [modelsData, setModelsData] = useState(null);
  const [status, setStatus] = useState("checking");

  const refreshCollections = useCallback(async () => {
    try {
      const res = await api.listCollections();
      setCollections(res.collections || []);
    } catch {}
  }, []);

  useEffect(() => {
    api.health()
      .then(() => setStatus("ok"))
      .catch(() => setStatus("error"));
    refreshCollections();
    api.listModels().then(setModelsData).catch(() => {});
  }, []);

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100">
      {/* Header */}
      <header className="border-b border-gray-700 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-2xl font-bold text-white tracking-tight">NEAM</span>
          <span className="text-gray-500 text-sm">Vector Database</span>
        </div>
        <div className="flex items-center gap-2">
          <span
            className={`w-2 h-2 rounded-full ${
              status === "ok" ? "bg-green-400" : status === "error" ? "bg-red-400" : "bg-yellow-400"
            }`}
          />
          <span className="text-gray-400 text-xs">
            {status === "ok" ? "API connected" : status === "error" ? "API offline" : "Connecting…"}
          </span>
        </div>
      </header>

      {/* Tabs */}
      <div className="border-b border-gray-700 px-6">
        <nav className="flex gap-1">
          {TABS.map((t) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={`px-4 py-3 text-sm font-medium transition-colors border-b-2 -mb-px ${
                tab === t
                  ? "border-violet-500 text-violet-400"
                  : "border-transparent text-gray-400 hover:text-gray-200"
              }`}
            >
              {t}
            </button>
          ))}
        </nav>
      </div>

      {/* Content */}
      <main className="max-w-3xl mx-auto px-6 py-6">
        {tab === "Search" && <SearchPanel collections={collections} />}
        {tab === "Ingest" && (
          <IngestPanel collections={collections} onRefresh={refreshCollections} />
        )}
        {tab === "Collections" && (
          <CollectionsPanel collections={collections} onRefresh={refreshCollections} />
        )}
        {tab === "Models" && <ModelsPanel modelsData={modelsData} />}
      </main>
    </div>
  );
}
