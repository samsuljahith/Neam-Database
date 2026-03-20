import { useState } from "react";
import { api } from "../api";

export default function CollectionsPanel({ collections, onRefresh }) {
  const [newName, setNewName] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleCreate(e) {
    e.preventDefault();
    if (!newName.trim()) return;
    setLoading(true);
    setError("");
    try {
      await api.createCollection(newName.trim());
      setNewName("");
      onRefresh();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete(name) {
    if (!confirm(`Delete collection "${name}"?`)) return;
    try {
      await api.deleteCollection(name);
      onRefresh();
    } catch (err) {
      alert(err.message);
    }
  }

  return (
    <div className="bg-gray-800 rounded-xl p-5">
      <h2 className="text-lg font-semibold text-white mb-4">Collections</h2>

      <div className="space-y-2 mb-4">
        {collections.length === 0 && (
          <p className="text-gray-500 text-sm">No collections yet.</p>
        )}
        {collections.map((name) => (
          <div
            key={name}
            className="flex items-center justify-between bg-gray-700 rounded-lg px-3 py-2"
          >
            <span className="text-gray-200 text-sm font-mono">📁 {name}</span>
            <button
              onClick={() => handleDelete(name)}
              className="text-gray-500 hover:text-red-400 text-xs transition-colors"
            >
              Delete
            </button>
          </div>
        ))}
      </div>

      <form onSubmit={handleCreate} className="flex gap-2">
        <input
          value={newName}
          onChange={(e) => setNewName(e.target.value)}
          placeholder="New collection name"
          className="flex-1 bg-gray-700 text-gray-200 text-sm rounded-lg px-3 py-2 border border-gray-600 focus:border-violet-500 focus:outline-none placeholder-gray-500"
        />
        <button
          type="submit"
          disabled={loading || !newName.trim()}
          className="bg-violet-600 hover:bg-violet-500 disabled:opacity-50 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
        >
          {loading ? "..." : "+ Create"}
        </button>
      </form>
      {error && <p className="text-red-400 text-xs mt-2">{error}</p>}
    </div>
  );
}
