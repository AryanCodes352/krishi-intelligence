'use client';
import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import { DataSourcesResponse } from '@/lib/types';
import { ArrowLeft, Database, Activity, Search } from 'lucide-react';
import { DataBadge } from '@/components/shared/DataBadge';
import { cn } from '@/lib/utils';

export default function DataSourcesPage() {
  const router = useRouter();
  const [data, setData] = useState<DataSourcesResponse | null>(null);

  useEffect(() => {
    const load = async () => {
      const res = await api.getDataSources();
      setData(res);
    };
    load();
  }, []);

  if (!data) return <div className="p-8 text-center animate-pulse">Loading data sources...</div>;

  return (
    <div className="space-y-6 pb-20 max-w-4xl mx-auto">
      <button onClick={() => router.back()} className="flex items-center gap-2 text-gray-600 hover:text-gray-900">
        <ArrowLeft className="w-4 h-4" /> Back to Dashboard
      </button>

      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-serif font-bold text-gray-900 flex items-center gap-3">
            <Search className="w-8 h-8 text-krishi-green" /> Data Sources & Transparency
          </h1>
          <p className="text-gray-600 mt-2">Every number has a source. Here's exactly where your data comes from.</p>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 flex flex-wrap gap-6 items-center justify-between mb-8">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 bg-green-50 rounded-full flex items-center justify-center text-green-600">
            <Activity className="w-6 h-6" />
          </div>
          <div>
            <p className="text-sm text-gray-500 font-medium">System Status</p>
            <p className="text-lg font-bold text-gray-900">{data.active_count} of {data.total_count} connected</p>
          </div>
        </div>
        <div>
          <p className="text-sm text-gray-500 font-medium mb-1">Overall Data Quality</p>
          <span className={cn(
            "px-3 py-1 rounded-full text-xs font-bold",
            data.overall_quality === 'HIGH' ? 'bg-green-100 text-green-800' :
            data.overall_quality === 'MEDIUM' ? 'bg-amber-100 text-amber-800' : 'bg-red-100 text-red-800'
          )}>
            {data.overall_quality}
          </span>
        </div>
      </div>

      <div className="space-y-4">
        {data.sources.map((source, i) => (
          <div key={i} className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <div className="p-6">
              <div className="flex flex-col md:flex-row justify-between md:items-center gap-4 mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center text-gray-500">
                    <Database className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="font-bold text-lg text-gray-900">{source.name}</h3>
                    <p className="text-sm text-gray-500">{source.provider}</p>
                  </div>
                </div>
                <DataBadge type={source.status as any} />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
                <div>
                  <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Variables Provided</p>
                  <div className="flex flex-wrap gap-2">
                    {source.variables.map(v => (
                      <span key={v} className="bg-gray-100 text-gray-700 text-xs px-2 py-1 rounded border border-gray-200">
                        {v}
                      </span>
                    ))}
                  </div>
                </div>
                <div className="space-y-3 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-500">Coverage</span>
                    <span className="font-medium text-gray-900">{source.coverage}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Data Quality</span>
                    <span className="font-medium text-gray-900">{source.data_quality}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Last Updated</span>
                    <span className="font-medium text-gray-900">{new Date(source.last_updated).toLocaleString()}</span>
                  </div>
                </div>
              </div>

              {source.notes && (
                <div className="mt-6 p-3 bg-gray-50 rounded-lg border border-gray-100 text-sm text-gray-600">
                  <strong>Note:</strong> {source.notes}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
