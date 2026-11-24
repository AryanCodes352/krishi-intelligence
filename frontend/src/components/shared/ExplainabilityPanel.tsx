import React from 'react';

interface ExplainabilityPanelProps {
  signals: Array<{ signal: string; value: string; direction: string; weight: string }>;
  data_used: string[];
  reasoning_steps: string[];
  conclusion: string;
  confidence: string;
  data_quality: string;
  important_note?: string;
}

export const ExplainabilityPanel = ({
  signals,
  data_used,
  reasoning_steps,
  conclusion,
  confidence,
  data_quality,
  important_note,
}: ExplainabilityPanelProps) => {
  return (
    <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-200 text-sm mt-4 space-y-5">
      <div className="flex items-center justify-between border-b border-gray-100 pb-3">
        <h4 className="font-serif font-bold text-lg text-krishi-green-dark">
          Explainability & Decision Logic
        </h4>
        <div className="flex items-center gap-2">
          <span className="text-[11px] bg-krishi-green/10 text-krishi-green px-2 py-0.5 rounded-full font-medium">
            Audit-Ready Traceability
          </span>
        </div>
      </div>

      {/* Key Signals (Signal → Value → Weight) */}
      <div>
        <div className="flex items-center justify-between mb-2.5">
          <h5 className="font-semibold text-gray-800 text-xs uppercase tracking-wider">
            Key Signals (Signal → Value → Weight)
          </h5>
          <span className="text-[11px] text-gray-500 font-medium">
            Model Input Drivers
          </span>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {(signals || []).map((s, i) => {
            const isUnavailable = !s.value || s.value === 'DATA UNAVAILABLE';
            const dir = (s.direction || '').toLowerCase();
            const weightBadge = isUnavailable
              ? 'bg-gray-100 text-gray-500 border-gray-200'
              : s.weight === 'HIGH'
              ? 'bg-amber-50 text-amber-800 border-amber-200 font-semibold'
              : 'bg-emerald-50 text-emerald-800 border-emerald-200 font-medium';

            const valueColor = isUnavailable
              ? 'text-gray-400 italic'
              : dir === 'positive'
              ? 'text-emerald-700'
              : dir === 'negative'
              ? 'text-rose-700'
              : 'text-gray-800';

            return (
              <div
                key={i}
                className="bg-gray-50/80 p-3 rounded-lg border border-gray-200 flex flex-col justify-between hover:border-gray-300 transition-colors"
              >
                <div className="flex items-center justify-between gap-2 mb-1.5">
                  <span className="text-gray-600 text-xs font-medium truncate" title={s.signal}>
                    {s.signal}
                  </span>
                  <span className={`text-[10px] px-2 py-0.5 rounded border uppercase tracking-wider shrink-0 ${weightBadge}`}>
                    {s.weight || 'MEDIUM'}
                  </span>
                </div>
                <div className="flex items-baseline justify-between mt-1">
                  <span className={`text-sm font-bold tracking-tight ${valueColor}`}>
                    {s.value || 'DATA UNAVAILABLE'}
                  </span>
                  <span className="text-[10px] text-gray-400 capitalize">
                    {isUnavailable ? '—' : dir}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Step-by-Step Reasoning */}
      <div>
        <h5 className="font-semibold text-gray-800 text-xs uppercase tracking-wider mb-2">
          Step-by-Step Numerical Reasoning
        </h5>
        <div className="bg-gray-50 rounded-lg p-3.5 border border-gray-200">
          <ol className="list-decimal list-outside ml-4 text-gray-700 space-y-2 text-xs leading-relaxed font-normal">
            {(reasoning_steps || []).map((step, i) => (
              <li key={i} className="pl-1">
                {step}
              </li>
            ))}
          </ol>
        </div>
      </div>

      {/* Conclusion */}
      <div className="bg-emerald-50/80 border border-emerald-200 p-4 rounded-lg">
        <h5 className="font-semibold text-emerald-900 text-xs uppercase tracking-wider mb-1.5">
          Recommendation Rationale
        </h5>
        <p className="text-emerald-950 text-xs leading-relaxed font-medium">
          {conclusion}
        </p>
      </div>

      {/* Verified Data Sources */}
      {data_used && data_used.length > 0 && (
        <div>
          <h5 className="font-semibold text-gray-800 text-xs uppercase tracking-wider mb-1.5">
            Verified Data Sources
          </h5>
          <ul className="text-[11px] text-gray-600 space-y-1 list-disc list-outside ml-4">
            {data_used.map((source, i) => (
              <li key={i}>{source}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Confidence and Quality Footer */}
      <div className="flex flex-wrap items-center justify-between gap-4 text-xs pt-3 border-t border-gray-200 text-gray-500">
        <div className="flex items-center gap-4">
          <div>
            <span>Confidence: </span>
            <span className="font-semibold text-gray-800">{confidence}</span>
          </div>
          <div>
            <span>Data Quality: </span>
            <span className="font-semibold text-gray-800">{data_quality}</span>
          </div>
        </div>
        <span className="text-[11px] text-gray-400">All predictions traceable to source</span>
      </div>

      {important_note && (
        <div className="text-[11px] text-amber-800 bg-amber-50/80 border border-amber-200/80 p-3 rounded-lg leading-relaxed">
          <strong>Decision-Support Notice:</strong> {important_note}
        </div>
      )}
    </div>
  );
};

