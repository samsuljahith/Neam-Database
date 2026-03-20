import { useState, useRef } from "react";
import { api } from "../api";

export default function IngestPanel({ collections, onRefresh }) {
  const [collection, setCollection] = useState("");
  const [text, setText] = useState("");
  const [source, setSource] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [dragging, setDragging] = useState(false);
  const fileRef = useRef();

  function handleFile(file) {
    if (!file) return;
    setSource(file.name);
    const reader = new FileReader();
    reader.onload = (e) => setText(e.target.result);
    reader.readAsText(file);
  }

  async function handleSubmit(e) {
    e.preventDefault();
    if (!collection || !text.trim()) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const res = await api.ingest(collection, text, source || "manual");
      setResult(res);
      setText("");
      setSource("");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="bg-gray-800 rounded-xl p-5">
      <h2 className="text-lg font-semibold text-white mb-4">Ingest</h2>

      <form onSubmit={handleSubmit} className="space-y-3">
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

        {/* Drop zone */}
        <div
          onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
          onDragLeave={() => setDragging(false)}
          onDrop={(e) => {
            e.preventDefault();
            setDragging(false);
            handleFile(e.dataTransfer.files[0]);
          }}
          onClick={() => fileRef.current.click()}
          className={`border-2 border-dashed rounded-lg p-4 text-center cursor-pointer transition-colors ${
            dragging ? "border-violet-400 bg-violet-900/20" : "border-gray-600 hover:border-gray-500"
          }`}
        >
          <p className="text-gray-400 text-sm">
            {source ? `📄 ${source}` : "Drop a file here or click to browse"}
          </p>
          <input
            ref={fileRef}
            type="file"
            accept=".txt,.md,.pdf"
            className="hidden"
            onChange={(e) => handleFile(e.target.files[0])}
          />
        </div>

        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Or paste text directly…"
          rows={5}
          className="w-full bg-gray-700 text-gray-200 text-sm rounded-lg px-3 py-2 border border-gray-600 focus:border-violet-500 focus:outline-none placeholder-gray-500 resize-none"
        />

        <input
          value={source}
          onChange={(e) => setSource(e.target.value)}
          placeholder="Source label (optional)"
          className="w-full bg-gray-700 text-gray-200 text-sm rounded-lg px-3 py-2 border border-gray-600 focus:border-violet-500 focus:outline-none placeholder-gray-500"
        />

        <button
          type="submit"
          disabled={loading || !collection || !text.trim()}
          className="w-full bg-violet-600 hover:bg-violet-500 disabled:opacity-50 text-white text-sm font-medium py-2 rounded-lg transition-colors"
        >
          {loading ? "Ingesting…" : "Ingest"}
        </button>
      </form>

      {result && (
        <div className="mt-3 bg-green-900/30 border border-green-700 rounded-lg p-3">
          <p className="text-green-400 text-sm">
            ✓ Stored {result.chunks_stored} chunk{result.chunks_stored !== 1 ? "s" : ""}
          </p>
        </div>
      )}
      {error && <p className="text-red-400 text-xs mt-2">{error}</p>}
    </div>
  );
}
