'use client';
import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import { ExpertResponse, FarmProfile } from '@/lib/types';
import { ArrowLeft, Bot, Send, User, AlertTriangle, Sprout } from 'lucide-react';
import { cn } from '@/lib/utils';

export default function ExpertPage() {
  const params = useParams();
  const router = useRouter();
  const [farm, setFarm] = useState<FarmProfile | null>(null);
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [history, setHistory] = useState<Array<{ role: 'user' | 'assistant', content: string | ExpertResponse }>>([]);

  useEffect(() => {
    if (typeof params.id === 'string') {
      api.getFarm(params.id).then(res => {
        if (res) setFarm(res);
      });
    }
  }, [params.id]);

  const handleSend = async (question: string) => {
    if (!question.trim()) return;
    
    setHistory(prev => [...prev, { role: 'user', content: question }]);
    setQuery('');
    setIsLoading(true);
    
    if (typeof params.id === 'string') {
      const res = await api.askExpert(params.id, question);
      if (res && res.answer) {
        setHistory(prev => [...prev, { role: 'assistant', content: res }]);
      } else {
        setHistory(prev => [
          ...prev, 
          { 
            role: 'assistant', 
            content: { 
              answer: 'Unable to generate guidance from the available farm data.', 
              why: 'Network request or farm intelligence services were temporarily unavailable.',
              what_to_do: ['Verify internet connectivity', 'Consult Kisan Call Centre toll-free at 1800-180-1551'],
              confidence: 'Not available',
              data_used: [],
              local_resources: ['Kisan Call Centre: 1800-180-1551'],
              expert_verification_required: true 
            } 
          }
        ]);
      }
    }
    setIsLoading(false);
  };

  const quickQuestions = [
    "What fertilizer should I apply next?",
    "My wheat leaves are turning yellow",
    "Is this a good time to sell?",
    "There are insects on my crop"
  ];

  return (
    <div className="space-y-6 max-w-4xl mx-auto h-[calc(100vh-120px)] flex flex-col">
      <button onClick={() => router.back()} className="flex items-center gap-2 text-gray-600 hover:text-gray-900 flex-none">
        <ArrowLeft className="w-4 h-4" /> Back to Dashboard
      </button>

      <div className="flex-none">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div>
            <h1 className="text-3xl font-serif font-bold text-krishi-green-dark flex items-center gap-3">
              <Bot className="w-8 h-8" /> Ask an Expert
            </h1>
            <p className="text-sm text-gray-500 mt-1">AI Agronomist powered by KRISHI Data Engine</p>
          </div>
          {farm && (
            <div className="flex flex-wrap items-center gap-2 bg-white border border-emerald-200 shadow-sm rounded-xl px-3.5 py-2 text-xs">
              <span className="font-semibold text-emerald-900 flex items-center gap-1.5">
                <Sprout className="w-4 h-4 text-emerald-700" />
                {farm.crop} {farm.crop_variety ? `(${farm.crop_variety})` : ''}
              </span>
              <span className="text-gray-300">•</span>
              <span className="bg-blue-50 text-blue-800 border border-blue-200 px-2 py-0.5 rounded font-medium">
                Stage: {farm.crop_stage}
              </span>
              <span className="text-gray-300">•</span>
              <span className="text-gray-600">
                {farm.district}, {farm.state}
              </span>
            </div>
          )}
        </div>
      </div>

      <div className="flex-1 bg-white rounded-2xl shadow-sm border border-gray-200 flex flex-col overflow-hidden">
        {/* Chat History */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-gray-50/50">
          {history.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center space-y-6 text-gray-500">
              <Bot className="w-16 h-16 text-gray-300" />
              <div>
                <p className="font-medium text-gray-900 mb-1">
                  {farm ? `Hello! I'm your AI Agronomist for ${farm.crop}.` : "Hello! I'm your AI Agronomist."}
                </p>
                <p className="text-sm max-w-md">
                  {farm
                    ? `I have your farm context for ${farm.crop} (${farm.crop_stage} stage in ${farm.district}). Ask any questions about crop health, risk management, fertilizers, or market timing.`
                    : "I analyze your farm's weather, soil, and market data to give you personalized advice. How can I help you today?"}
                </p>
              </div>
              <div className="flex flex-wrap justify-center gap-2 mt-4 max-w-lg">
                {quickQuestions.map(q => (
                  <button key={q} onClick={() => handleSend(q)} className="px-3 py-1.5 bg-white border border-gray-200 rounded-full text-xs hover:border-krishi-green hover:text-krishi-green transition-colors">
                    {q}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            history.map((msg, i) => {
              const content = msg.content as ExpertResponse;
              return (
                <div key={i} className={cn("flex gap-4 max-w-[85%]", msg.role === 'user' ? 'ml-auto' : '')}>
                  {msg.role === 'assistant' && (
                    <div className="w-8 h-8 rounded-full bg-krishi-green flex items-center justify-center text-white flex-shrink-0">
                      <Bot className="w-4 h-4" />
                    </div>
                  )}
                  
                  <div className={cn(
                    "p-5 rounded-2xl text-sm leading-relaxed",
                    msg.role === 'user' ? 'bg-krishi-green text-white rounded-tr-none' : 'bg-white border border-gray-200 shadow-sm rounded-tl-none'
                  )}>
                    {msg.role === 'user' ? (
                      <p className="font-medium">{msg.content as string}</p>
                    ) : (
                      <div className="space-y-4">
                        {/* Contextual Farm Badge */}
                        {content.farm_context && (
                          <div className="flex flex-wrap items-center gap-2 pb-2.5 border-b border-gray-100 text-[11px]">
                            {content.farm_context.crop && (
                              <span className="bg-emerald-50 text-emerald-800 border border-emerald-200 px-2 py-0.5 rounded font-medium">
                                Crop: {content.farm_context.crop}
                              </span>
                            )}
                            {content.farm_context.stage && (
                              <span className="bg-blue-50 text-blue-800 border border-blue-200 px-2 py-0.5 rounded font-medium">
                                Stage: {content.farm_context.stage}
                              </span>
                            )}
                            {content.farm_context.location && (
                              <span className="bg-gray-100 text-gray-700 px-2 py-0.5 rounded">
                                Location: {content.farm_context.location}
                              </span>
                            )}
                            {content.farm_context.soil_source && (
                              <span className="bg-amber-50 text-amber-800 border border-amber-200 px-2 py-0.5 rounded font-medium">
                                Soil: {content.farm_context.soil_source === 'REGIONAL_ESTIMATE' ? 'Regional Estimate' : 'Field Test'}
                              </span>
                            )}
                          </div>
                        )}

                        {/* Section 1: ANSWER */}
                        <div>
                          <span className="text-[10px] font-bold uppercase tracking-wider text-krishi-green-dark block mb-1">
                            Answer
                          </span>
                          <p className="text-gray-900 leading-relaxed font-semibold">
                            {content.answer || "Unable to generate guidance from the available farm data."}
                          </p>
                        </div>
                        
                        {/* Section 2: WHY */}
                        {content.why && (
                          <div className="bg-amber-50/70 p-3 rounded-lg border border-amber-200/80">
                            <span className="text-[10px] font-bold uppercase tracking-wider text-amber-900 block mb-1">
                              Why (Farm Data Signals)
                            </span>
                            <p className="text-gray-700 text-xs leading-relaxed">
                              {content.why}
                            </p>
                          </div>
                        )}

                        {/* Section 3: WHAT TO DO */}
                        {(content.what_to_do || content.recommended_actions) && (
                          <div>
                            <span className="text-[10px] font-bold uppercase tracking-wider text-gray-700 block mb-1">
                              What To Do (Practical Steps)
                            </span>
                            <ol className="list-decimal list-outside ml-4 text-gray-700 text-xs space-y-1.5">
                              {(content.what_to_do || content.recommended_actions)!.map((step, j) => (
                                <li key={j} className="pl-0.5">{step}</li>
                              ))}
                            </ol>
                          </div>
                        )}

                        {/* Section 4: WHEN TO GET EXPERT HELP */}
                        {content.when_to_escalate && (
                          <div className="bg-rose-50/70 p-3 rounded-lg border border-rose-200/80 text-xs">
                            <span className="text-[10px] font-bold uppercase tracking-wider text-rose-900 block mb-1">
                              When To Get Expert Help
                            </span>
                            <p className="text-rose-950 leading-relaxed">
                              {content.when_to_escalate}
                            </p>
                          </div>
                        )}

                        {/* Section 5: DATA USED */}
                        <div>
                          <span className="text-[10px] font-bold uppercase tracking-wider text-gray-500 block mb-1">
                            Data Used
                          </span>
                          {content.data_used && content.data_used.length > 0 ? (
                            <ul className="list-disc list-outside ml-4 text-gray-600 text-[11px] space-y-0.5">
                              {content.data_used.map((source, j) => (
                                <li key={j}>{source}</li>
                              ))}
                            </ul>
                          ) : (
                            <p className="text-gray-400 italic text-[11px]">Sources: Not available</p>
                          )}
                        </div>

                        {/* Section 6: CONFIDENCE & VERIFICATION BAR */}
                        <div className="pt-3 border-t border-gray-100 flex flex-wrap items-center justify-between gap-2 text-[10px]">
                          <div className="flex items-center gap-2">
                            <span className={cn(
                              "px-2.5 py-1 rounded-md font-semibold tracking-wider uppercase border",
                              content.confidence === 'HIGH' ? 'bg-green-100 text-green-800 border-green-300' :
                              content.confidence === 'MEDIUM' ? 'bg-amber-100 text-amber-800 border-amber-300' : 
                              content.confidence === 'LOW' ? 'bg-rose-100 text-rose-800 border-rose-300' :
                              'bg-gray-100 text-gray-600 border-gray-200'
                            )}>
                              Confidence: {content.confidence || 'Not available'}
                            </span>

                            <span className="text-gray-400 font-medium">
                              Engine: {content.engine === 'gemini' ? 'Gemini 1.5' : 'KRISHI Data Engine'}
                            </span>
                          </div>
                          
                          {content.expert_verification_required && (
                            <span className="flex items-center gap-1 text-amber-700 font-medium">
                              <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
                              Needs Field Verification
                            </span>
                          )}
                        </div>

                        {/* Local Resources Contacts */}
                        {content.local_resources && content.local_resources.length > 0 && (
                          <div className="text-[11px] text-gray-500 pt-2 border-t border-gray-100 flex flex-wrap gap-x-4 gap-y-1">
                            <span className="font-semibold text-gray-600">Local Contacts:</span>
                            {content.local_resources.map((res, j) => (
                              <span key={j} className="text-krishi-green-dark font-medium">{res}</span>
                            ))}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                  
                  {msg.role === 'user' && (
                    <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center text-gray-600 flex-shrink-0">
                      <User className="w-4 h-4" />
                    </div>
                  )}
                </div>
              );
            })
          )}
          {isLoading && (
            <div className="flex gap-4 max-w-[85%]">
              <div className="w-8 h-8 rounded-full bg-krishi-green flex items-center justify-center text-white flex-shrink-0"><Bot className="w-4 h-4" /></div>
              <div className="p-4 rounded-2xl bg-white border border-gray-200 shadow-sm rounded-tl-none">
                <div className="flex gap-1">
                  <div className="w-2 h-2 bg-gray-300 rounded-full animate-bounce" />
                  <div className="w-2 h-2 bg-gray-300 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                  <div className="w-2 h-2 bg-gray-300 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }} />
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Input */}
        <div className="p-4 bg-white border-t border-gray-200">
          <form 
            onSubmit={(e) => { e.preventDefault(); handleSend(query); }}
            className="flex gap-2"
          >
            <input 
              type="text" 
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Describe your concern or question..." 
              className="flex-1 bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-krishi-green/50 focus:border-krishi-green text-sm"
              disabled={isLoading}
            />
            <button 
              type="submit" 
              disabled={isLoading || !query.trim()}
              className="bg-krishi-green text-white px-5 rounded-xl hover:bg-krishi-green-dark transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
            >
              <Send className="w-5 h-5" />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
