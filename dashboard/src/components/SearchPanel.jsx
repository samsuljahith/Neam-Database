import { useState } from "react";
import { api } from "../api";

function confidenceColor(confidence) {
  if (confidence === "high") return "text-green-400";
  if (confidence === "medium") return "text-yellow-400";
  return "text-gray-400";
}

function ResultCard({ result }) {
  const [expanded, setExpanded] = useState(false);
  const exp = result.explanation;

  return (
    <div className="bg-gray-700 rounded-lg p-4 space-y-2">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-white font-mono text-sm">
            {result.score.toFixed(4)}
          </span>
          {exp && (
            <span className={`text-xs font-medium ${confidenceColor(exp.confidence)}`}>
              ● {exp.confidence}
            </span>
          )}
          {result.search_mode && (
            <span className="text-xs bg-gray-600 text-gray-300 px-2 py-0.5 rounded-full">
              {result.search_mode}
            </span>
          )}
        </div>
        {result.source && (
          <span className="text-gray-500 text-xs">{result.source}</span>
        )}
      </div>

      <p className="text-gray-200 text-sm leading-relaxed">{result.text}</p>

      {result.search_mode === "hybrid" && (
        <div className="flex gap-4 text-xs text-gray-400">
          <span>Vector: {result.vector_score?.toFixed(4)}</span>
          <span>BM25: {result.bm25_score?.toFixed(4)}</span>
        </div>
      )}

      {exp && (
        <button
          onClick={() => setExpanded(!expanded)}
          className="text-violet-400 hover:text-violet-300 text-xs transition-colors"
        >
          {expanded ? "▲ Hide" : "▼ Explanation"}
        </button>
      )}

      {expanded && exp && (
        <div className="bg-gray-800 rounded-lg p-3 space-y-1 text-xs text-gray-300">
          <p>{exp.score_interpretation}</p>
          <p>{exp.why}</p>
          {exp.matching_concepts?.length > 0 && (
            <div className="flex flex-wrap gap-1 pt-1">
              {exp.matching_concepts.map((c) => (
                <span key={c} className="bg-violet-900/40 text-violet-300 px-2 py-0.5 rounded-full">
                  {c}
                </span>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default function SearchPanel({ collections }) {
  const [collection, setCollection] = useState("");
  const [query, setQuery] = useState("");
  const [topK, setTopK] = useState(5);
  const [mode, setMode] = useState("hybrid");
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSearch(e) {
    e.preventDefault();
    if (!collection || !query.trim()) return;
    setLoading(true);
    setError("");
    try {
      const res = await api.query(collection, query, topK, mode);
      setResults(res);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="bg-gray-800 rounded-xl p-5">
      <h2 className="text-lg font-semibold text-white mb-4">Search</h2>

      <form onSubmit={handleSearch} className="space-y-3">
        <select
          value={collection}
          onChange={(e) => setCollection(e.target.value)}
          className="w-full bg-gray-700 text-gray-200 text-sm rounded-lg px-3 py-2 border border-gray-600 focus:border-violet-500 focus:outline-none"
        >
          <option value="">Select collection…</option>
          {collections.map((c) => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>

        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Enter your query…"
          className="w-full bg-gray-700 text-gray-200 text-sm rounded-lg px-3 py-2 border border-gray-600 focus:border-violet-500 focus:outline-none placeholder-gray-500"
        />

        <div className="flex items-center gap-4">
          <div className="flex gap-3">
            {["vector", "bm25", "hybrid"].map((m) => (
              <label key={m} className="flex items-center gap-1.5 cursor-pointer">
                <input
                  type="radio"
                  name="mode"
                  value={m}
                  checked={mode === m}
                  onChange={() => setMode(m)}
                  className="accent-violet-500"
                />
                <span className="text-gray-300 text-sm capitalize">{m}</span>
              </label>
            ))}
          </div>

          <div className="flex items-center gap-2 ml-auto">
            <label className="text-gray-400 text-xs">Top K</label>
            <input
              type="number"
              value={topK}
              onChange={(e) => setTopK(Number(e.target.value))}
              min={1}
              max={20}
              className="w-16 bg-gray-700 text-gray-200 text-sm rounded-lg px-2 py-1.5 border border-gray-600 focus:border-violet-500 focus:outline-none text-center"
            />
          </div>
        </div>

        <button
          type="submit"
          disabled={loading || !collection || !query.trim()}
          className="w-full bg-violet-600 hover:bg-violet-500 disabled:opacity-50 text-white text-sm font-medium py-2 rounded-lg transition-colors"
        >
          {loading ? "Searching…" : "Search"}
        </button>
      </form>

      {error && <p className="text-red-400 text-xs mt-3">{error}</p>}

      {results !== null && (
        <div className="mt-4 space-y-3">
          <p className="text-gray-400 text-xs">
            {results.length} result{results.length !== 1 ? "s" : ""}
          </p>
          {results.length === 0 && (
            <p className="text-gray-500 text-sm">No results found.</p>
          )}
          {results.map((r, i) => (
            <ResultCard key={i} result={r} />
          ))}
        </div>
      )}
    </div>
  );
}
