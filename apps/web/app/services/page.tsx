"use client";

import { useState } from "react";

interface Service {
  service_id: string;
  display_name: string;
  description: string;
  department: string;
  jurisdiction: string;
  official_portal: string;
  capabilities: string[];
  required_documents: { document_type: string; display_name: string; mandatory: boolean }[];
  workflow_version: string;
  estimated_processing_time: string | null;
  fees: string | null;
}

const CAPABILITY_LABELS: Record<string, string> = {
  discover: "Discover",
  eligibility_check: "Check Eligibility",
  document_requirements: "Document Requirements",
  new_application: "Apply",
  update_record: "Update Record",
  renew: "Renew",
  track_application: "Track Application",
  raise_grievance: "Raise Grievance",
};

export default function ServicesPage() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Service[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setSearched(true);
    try {
      const res = await fetch(`/api/v1/services/search?q=${encodeURIComponent(query)}`);
      const data = await res.json();
      setResults(data.services || []);
    } catch { setResults([]); }
    setLoading(false);
  };

  const handleResolve = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setSearched(true);
    try {
      const res = await fetch("/api/v1/services/resolve", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ service_query: query }),
      });
      const data = await res.json();
      setResults(data.success && data.data ? [data.data as Service] : []);
    } catch { setResults([]); }
    setLoading(false);
  };

  return (
    <main className="min-h-screen bg-slate-50 dark:bg-slate-900">
      <header className="border-b border-slate-200 dark:border-slate-700 bg-white/80 dark:bg-slate-900/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <a href="/" className="flex items-center gap-2">
              <span className="text-xl font-bold text-slate-900 dark:text-white">GovFlow AI</span>
            </a>
            <nav className="flex items-center gap-4">
              <a href="/" className="text-sm text-slate-600 hover:text-primary-600">Home</a>
              <a href="/apply" className="text-sm text-slate-600 hover:text-primary-600">Apply</a>
            </nav>
          </div>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-4 py-12">
        <h1 className="text-3xl font-bold text-slate-900 dark:text-white mb-2">Find Government Service</h1>
        <p className="text-slate-600 dark:text-slate-300 mb-8">Describe what you need in plain language.</p>

        <div className="flex gap-3 mb-8">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
            placeholder="e.g., I want an income certificate"
            className="input flex-1"
          />
          <button onClick={handleSearch} className="btn-primary" disabled={loading}>
            {loading ? "Searching..." : "Search"}
          </button>
          <button onClick={handleResolve} className="btn-secondary" disabled={loading}>
            AI Resolve
          </button>
        </div>

        {results.length > 0 && (
          <div className="space-y-4">
            <h2 className="text-xl font-semibold text-slate-900 dark:text-white">
              {results.length} service{results.length !== 1 ? "s" : ""} found
            </h2>
            {results.map((service) => (
              <div
                key={service.service_id}
                className="card cursor-pointer hover:shadow-md transition-shadow"
                onClick={() => setSelected(selected === service.service_id ? null : service.service_id)}
              >
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-slate-900 dark:text-white">{service.display_name}</h3>
                    <p className="text-sm text-slate-500">{service.department}</p>
                    <p className="text-slate-600 dark:text-slate-300 mt-2">{service.description}</p>
                  </div>
                  <span className="text-sm text-slate-500 bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded">
                    {service.jurisdiction}
                  </span>
                </div>

                {selected === service.service_id && (
                  <div className="mt-6 pt-4 border-t border-slate-200 dark:border-slate-700">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <h4 className="font-medium text-slate-900 dark:text-white mb-3">Available Actions</h4>
                        <div className="space-y-2">
                          {service.capabilities.map((cap) => (
                            <button
                              key={cap}
                              className="flex items-center gap-2 w-full text-left px-3 py-2 rounded-lg bg-slate-50 dark:bg-slate-800 hover:bg-primary-50 transition-colors"
                            >
                              <span className="text-sm">{CAPABILITY_LABELS[cap] || cap}</span>
                            </button>
                          ))}
                        </div>
                      </div>
                      <div>
                        <h4 className="font-medium text-slate-900 dark:text-white mb-3">Required Documents</h4>
                        <ul className="space-y-2">
                          {service.required_documents.map((doc) => (
                            <li key={doc.document_type} className="flex items-center gap-2 text-sm">
                              <span className={doc.mandatory ? "text-red-500" : "text-slate-400"}>
                                {doc.mandatory ? "●" : "○"}
                              </span>
                              <span>{doc.display_name}</span>
                            </li>
                          ))}
                        </ul>
                        <div className="mt-4 pt-4 border-t border-slate-200 dark:border-slate-700 space-y-2 text-sm text-slate-600">
                          {service.estimated_processing_time && <p>Processing: {service.estimated_processing_time}</p>}
                          {service.fees && <p>Fees: {service.fees}</p>}
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {searched && results.length === 0 && !loading && (
          <div className="text-center py-12">
            <p className="text-slate-500 text-lg">No services found matching &quot;{query}&quot;</p>
            <p className="text-slate-400 mt-2">Try a different search term or use AI Resolve</p>
          </div>
        )}
      </div>
    </main>
  );
}