export default function ModelsPanel({ modelsData }) {
  if (!modelsData) return null;

  const { current, available } = modelsData;

  return (
    <div className="bg-gray-800 rounded-xl p-5">
      <h2 className="text-lg font-semibold text-white mb-4">Models</h2>

      <div className="bg-violet-900/30 border border-violet-700 rounded-lg p-3 mb-4">
        <p className="text-violet-300 text-xs font-medium uppercase tracking-wide mb-1">Active</p>
        <p className="text-white text-sm font-mono">{current.model}</p>
        <div className="flex gap-3 mt-1 text-xs text-gray-400">
          <span>Provider: {current.provider}</span>
          <span>Dim: {current.dimension}</span>
        </div>
      </div>

      <div className="space-y-4">
        {Object.entries(available).map(([key, group]) => (
          <div key={key}>
            <div className="flex items-center gap-2 mb-2">
              <span className="text-gray-300 text-sm font-medium capitalize">{group.provider}</span>
              <span className="text-gray-500 text-xs">— {group.description}</span>
            </div>
            <div className="space-y-1.5">
              {group.models.map((m) => (
                <div
                  key={m.name}
                  className={`flex items-center justify-between rounded-lg px-3 py-2 ${
                    m.name === current.model
                      ? "bg-violet-900/40 border border-violet-700"
                      : "bg-gray-700"
                  }`}
                >
                  <div>
                    <span className="text-gray-200 text-xs font-mono">{m.name}</span>
                    {m.default && (
                      <span className="ml-2 text-xs text-violet-400">default</span>
                    )}
                  </div>
                  <div className="flex gap-3 text-xs text-gray-500">
                    <span>{m.dimension}d</span>
                    <span>{m.speed}</span>
                    <span>{m.quality}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
