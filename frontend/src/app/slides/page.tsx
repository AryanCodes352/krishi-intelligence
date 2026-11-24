"use client";

import React, { useState, useRef } from "react";
import Link from "next/link";
import Image from "next/image";

interface SlideInfo {
  index: number;
  title: string;
  subtitle: string;
  speaker: string;
  speakerRole: string;
  image: string;
  notes: string[];
}

const SLIDES: SlideInfo[] = [
  {
    index: 1,
    title: "KRISHI INTELLIGENCE",
    subtitle: "An Agentic AI-Powered Farm Digital Twin with Dynamic Data Provenance & Market Forecasting",
    speaker: "Person 1 (Aryan)",
    speakerRole: "Lead Architect & Live Demo Runner",
    image: "/slides/Slide1.PNG",
    notes: [
      "Welcome respected external examiners, HOD sir, faculty guide, and teachers.",
      "Introduce project title and academic affiliation (KCC ITM CC 492, AKTU).",
      "Introduce the 4-member team ownership: Architecture, ML, Vision, and Database.",
      "Frame the smallholder problem: 85% of UP farmers cultivate < 2 hectares with decoupled weather, market, and soil risks."
    ]
  },
  {
    index: 2,
    title: "The Smallholder Triad & Literature Survey",
    subtitle: "Chapter 1: Background & Comparative Survey Matrix",
    speaker: "Person 1 (Aryan)",
    speakerRole: "Lead Architect",
    image: "/slides/Slide2.PNG",
    notes: [
      "Explain the 3 pain points: Weather surprises, price crashes, and blind urea over-application.",
      "Walk through the literature matrix: Kisan Suvidha is static, Plantix only diagnoses leaves, and KisanGPT hallucinates dangerous doses.",
      "Emphasize: KRISHI is the only platform that grounds advice in verified soil labs, price forecasts, and a stateful Digital Twin."
    ]
  },
  {
    index: 3,
    title: "5-Tier System Architecture & Multi-Agent Fusion",
    subtitle: "Chapter 3: System Architecture & Orchestration",
    speaker: "Person 1 (Aryan)",
    speakerRole: "Lead Architect",
    image: "/slides/Slide3.PNG",
    notes: [
      "Explain the 5-tier architecture: Ingestion -> Provenance Guardrails -> Living Digital Twin -> Predictive Engines -> UI.",
      "Highlight Layer 3: Living Farm Digital Twin tracking GDD thermal clock (base 4.0°C) across 8 wheat stages.",
      "HANDOFF TO PERSON 2: 'I will now hand over to Person 2 to explain our technology stack, weather telemetry, and XGBoost price forecasting model.'"
    ]
  },
  {
    index: 4,
    title: "Technology Stack & External Data Pipelines",
    subtitle: "Chapter 2: System Specifications",
    speaker: "Person 2",
    speakerRole: "Data & ML Engineer",
    image: "/slides/Slide4.PNG",
    notes: [
      "Explain FastAPI async ASGI and Next.js 14 lightweight 87 kB shared bundle.",
      "Explain Open-Meteo: High-res 0.1° grid, FAO-56 evapotranspiration, zero API cost.",
      "Explain AGMARKNET: data.gov.in integration, transport penalty calculation, and offline seed fallback."
    ]
  },
  {
    index: 5,
    title: "XGBoost Price Forecasting & Empirical Validation",
    subtitle: "Chapter 5: Machine Learning Evaluation",
    speaker: "Person 2",
    speakerRole: "Data & ML Engineer",
    image: "/slides/Slide5.PNG",
    notes: [
      "Explain the dual plot: 30-day forecast tracking actuals inside the 95% CI band, and feature importance rankings.",
      "Highlight KPIs: MAE ₹84.30/q, MAPE 3.82%, R² 0.887.",
      "Defend XGBoost: Tabular agricultural datasets have hundreds of rows; XGBoost avoids LSTM overfitting and trains in 8ms.",
      "HANDOFF TO PERSON 3: 'I now hand over to Person 3 to explain our Soil Health Card OCR pipeline and human-in-the-loop confirmation gate.'"
    ]
  },
  {
    index: 6,
    title: "Soil Health Card OCR & Mandatory Confirmation Gate",
    subtitle: "Chapter 3.4 & 4.4: Computer Vision & Safety Engineering",
    speaker: "Person 3",
    speakerRole: "Vision & Methodology Engineer",
    image: "/slides/Slide6.PNG",
    notes: [
      "Explain the 4-step pipeline: Upload -> OCR -> LOCKED REVIEW GATE -> Verified Digital Twin.",
      "Emphasize the locked confirmation gate: unconfirmed OCR NEVER touches the farm profile or triggers fertilizer advisories.",
      "Highlight our cartoon stress test: uploading invalid images safely triggers 'OCR FAILED' and falls back to manual entry with FARMER provenance."
    ]
  },
  {
    index: 7,
    title: "System Methodology: DFD & Sequence Design",
    subtitle: "Chapter 3: Design & Methodology",
    speaker: "Person 3",
    speakerRole: "Vision & Methodology Engineer",
    image: "/slides/Slide7.PNG",
    notes: [
      "Explain Fig 3.2: Level 0 Context DFD and Level 1 Decomposed DFD showing external entities and stores D1-D5.",
      "Explain Fig 3.4: Sequence diagram showing the interactive confirmation modal and provenance upgrade to VERIFIED_LAB_TEST.",
      "HANDOFF TO PERSON 4: 'I now pass the presentation to Person 4 to walk through our Relational Database Schemas, Data Provenance Engine, and 116-test verification suite.'"
    ]
  },
  {
    index: 8,
    title: "Database Architecture & Farm Digital Twin ER Schema",
    subtitle: "Chapter 3.3: Database Engineering",
    speaker: "Person 4",
    speakerRole: "Database & QA Engineer",
    image: "/slides/Slide8.PNG",
    notes: [
      "Explain 3NF relational schema design using SQLAlchemy 2.0 ORM.",
      "Walk through Fig 3.3: Central 'farms' entity with 1-to-N relationships to observations, soil profiles, and predictions.",
      "Point out 'farm_events': every critical action is logged into an immutable transactional ledger for auditability."
    ]
  },
  {
    index: 9,
    title: "Data Provenance Engine & Automated Verification Suite",
    subtitle: "Chapter 3.5 & 5.1: Integrity & QA",
    speaker: "Person 4",
    speakerRole: "Database & QA Engineer",
    image: "/slides/Slide9.PNG",
    notes: [
      "Explain the 4-tier Provenance State Machine: LIVE (<=1d), LATEST_AVAILABLE (2-7d), STALE (>7d), and HISTORICAL_SEED.",
      "Explain the mathematical zero-hallucination guarantee: if data.gov.in drops, the system transparently downgrades provenance.",
      "Walk through the 116-test automated Pytest suite: 100% pass rate in 10.18s with zero TypeScript compiler errors."
    ]
  },
  {
    index: 10,
    title: "Current System Boundaries vs. 4th-Year Major Roadmap",
    subtitle: "Chapter 6: Conclusion & Future Scope",
    speaker: "Person 4",
    speakerRole: "Database & QA Engineer",
    image: "/slides/Slide10.PNG",
    notes: [
      "Be completely honest about prototype boundaries: Wheat in Central UP, periodic lab cards, English web screen.",
      "Walk through 4th-year upgrade roadmap: Multi-crop engine, LoRaWAN IoT probes, Vernacular Voice via Bhashini AI, and Sentinel-2 NDVI satellite imagery.",
      "HANDOFF TO PERSON 1 (ARYAN): 'I now invite our Team Lead, Aryan, to conduct the live software demonstration and conclude our defense.'"
    ]
  },
  {
    index: 11,
    title: "Live Demonstration & Final Viva Defense",
    subtitle: "Full-Stack Software Walkthrough",
    speaker: "Person 1 (Aryan)",
    speakerRole: "Lead Architect & Live Demo Runner",
    image: "/slides/Slide11.PNG",
    notes: [
      "Switch window to http://localhost:3000.",
      "Follow the 4-step path on screen: Digital Twin -> Mandi Net Realization -> Soil Confirmation Gate -> Financial Matrix.",
      "Conclude confidently: 'Thank you respected examiners. My team and I are now open to your technical inquiries and cross-questions.'"
    ]
  }
];

export default function SlidesPage() {
  const [currentIdx, setCurrentIdx] = useState(0);
  const [showNotes, setShowNotes] = useState(false);
  const [isZoomed, setIsZoomed] = useState(false);

  // Touch Swipe Handling for Mobile
  const touchStartX = useRef<number | null>(null);
  const touchEndX = useRef<number | null>(null);

  const minSwipeDistance = 50;

  const onTouchStart = (e: React.TouchEvent) => {
    touchEndX.current = null;
    touchStartX.current = e.targetTouches[0].clientX;
  };

  const onTouchMove = (e: React.TouchEvent) => {
    touchEndX.current = e.targetTouches[0].clientX;
  };

  const onTouchEnd = () => {
    if (!touchStartX.current || !touchEndX.current) return;
    const distance = touchStartX.current - touchEndX.current;
    const isLeftSwipe = distance > minSwipeDistance;
    const isRightSwipe = distance < -minSwipeDistance;

    if (isLeftSwipe) {
      handleNext();
    } else if (isRightSwipe) {
      handlePrev();
    }
  };

  const current = SLIDES[currentIdx];

  const handleNext = () => {
    setCurrentIdx((prev) => (prev < SLIDES.length - 1 ? prev + 1 : 0));
  };

  const handlePrev = () => {
    setCurrentIdx((prev) => (prev > 0 ? prev - 1 : SLIDES.length - 1));
  };

  return (
    <div className="min-h-screen bg-slate-100 text-slate-900 flex flex-col font-sans">
      {/* Top Academic Masthead */}
      <header className="border-b border-slate-200 bg-white/95 backdrop-blur px-3 sm:px-6 py-2.5 sticky top-0 z-50 flex items-center justify-between shadow-sm">
        <div className="flex items-center gap-2 sm:gap-3">
          <Link
            href="/"
            className="text-emerald-700 hover:text-emerald-800 font-bold tracking-wide text-xs sm:text-sm flex items-center gap-1 bg-emerald-50 hover:bg-emerald-100 px-2.5 py-1 rounded-md border border-emerald-200 transition"
          >
            ← App
          </Link>
          <span className="text-slate-300 hidden sm:inline">|</span>
          <div className="flex flex-col">
            <span className="text-xs sm:text-sm font-bold text-slate-900 leading-tight">
              KRISHI Intelligence — Academic Defense Deck
            </span>
            <span className="text-[10px] sm:text-xs text-slate-500 hidden sm:inline">
              KCC ITM, Greater Noida (CC 492) • B.Tech CSE Mini-Project
            </span>
          </div>
        </div>

        {/* Quick Action Download Buttons */}
        <div className="flex items-center gap-2">
          <a
            href="/slides/KRISHI_Intelligence_KCC_Presentation.pdf"
            target="_blank"
            rel="noopener noreferrer"
            className="px-2.5 sm:px-3 py-1.5 text-xs font-semibold rounded-md bg-emerald-600 text-white hover:bg-emerald-700 transition shadow-sm flex items-center gap-1.5"
            title="Open Vector PDF (Best for phones)"
          >
            <span>📄</span>
            <span className="hidden xs:inline">Open</span> PDF
          </a>
          <a
            href="/slides/KRISHI_Intelligence_KCC_Presentation.pptx"
            download
            className="px-2.5 sm:px-3 py-1.5 text-xs font-semibold rounded-md bg-blue-600 text-white hover:bg-blue-700 transition shadow-sm flex items-center gap-1.5"
            title="Download PowerPoint PPTX"
          >
            <span>📊</span>
            <span className="hidden xs:inline">Get</span> PPTX
          </a>
        </div>
      </header>

      {/* Main Slide Presentation Stage */}
      <main className="flex-1 max-w-5xl w-full mx-auto p-2 sm:p-5 flex flex-col items-center justify-start">
        {/* Mobile Swipe / Tap Tip */}
        <div className="w-full mb-2 flex items-center justify-between text-[11px] sm:text-xs text-slate-500 px-1">
          <span className="flex items-center gap-1">
            <span>📱</span>
            <span>Swipe left/right to navigate • Tap slide to expand</span>
          </span>
          <span className="font-semibold text-slate-600">
            Slide {current.index} of {SLIDES.length}
          </span>
        </div>

        {/* Slide Card Container */}
        <div className="w-full bg-white rounded-xl border border-slate-300 shadow-md overflow-hidden flex flex-col">
          {/* Slide Header Info Bar */}
          <div className="px-3 sm:px-4 py-2 bg-slate-50 border-b border-slate-200 flex items-center justify-between text-xs sm:text-sm">
            <div className="flex items-center gap-2 truncate">
              <span className="px-2 py-0.5 rounded font-mono font-bold bg-emerald-100 text-emerald-800 border border-emerald-300 text-xs">
                {current.index} / {SLIDES.length}
              </span>
              <span className="font-bold text-slate-900 truncate text-xs sm:text-sm">
                {current.title}
              </span>
            </div>
            <div className="flex items-center gap-1.5 sm:gap-2 text-xs">
              <span className="px-2 py-0.5 rounded bg-blue-100 text-blue-800 border border-blue-300 font-semibold whitespace-nowrap text-[11px] sm:text-xs">
                {current.speaker}
              </span>
              <button
                onClick={() => setShowNotes(!showNotes)}
                className={`px-2 py-0.5 rounded border text-xs font-semibold transition ${
                  showNotes
                    ? "bg-amber-100 text-amber-900 border-amber-400"
                    : "bg-white text-slate-700 border-slate-300 hover:bg-slate-100"
                }`}
              >
                {showNotes ? "Hide Notes" : "Speaker Notes"}
              </button>
            </div>
          </div>

          {/* High-Resolution Slide Image (Touch Swipe Enabled) */}
          <div
            className="relative w-full aspect-[16/9] bg-white flex items-center justify-center overflow-hidden cursor-zoom-in"
            onTouchStart={onTouchStart}
            onTouchMove={onTouchMove}
            onTouchEnd={onTouchEnd}
            onClick={() => setIsZoomed(true)}
            title="Tap to zoom in fullscreen"
          >
            <Image
              src={current.image}
              alt={`Slide ${current.index}: ${current.title}`}
              fill
              className="object-contain"
              priority
              sizes="(max-width: 1200px) 100vw, 1200px"
            />
          </div>

          {/* Presenter Notes Accordion (Grounded Viva Cues) */}
          {showNotes && (
            <div className="p-3 sm:p-4 bg-amber-50/60 border-t border-amber-200 text-xs sm:text-sm">
              <div className="flex items-center justify-between mb-2">
                <span className="font-bold text-amber-900 tracking-wide uppercase text-[11px] sm:text-xs">
                  Spoken Script & Viva Cues ({current.speaker})
                </span>
                <span className="text-slate-600 text-xs font-medium">{current.speakerRole}</span>
              </div>
              <ul className="space-y-1.5 text-slate-800">
                {current.notes.map((note, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <span className="text-emerald-700 font-bold">•</span>
                    <span className="leading-relaxed">{note}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Bottom Slide Navigation Controls */}
          <div className="px-3 sm:px-4 py-2.5 bg-slate-50 border-t border-slate-200 flex items-center justify-between">
            <button
              onClick={handlePrev}
              className="px-3.5 py-1.5 rounded-lg bg-white border border-slate-300 hover:bg-slate-100 text-slate-800 text-xs sm:text-sm font-bold transition flex items-center gap-1 shadow-sm active:scale-95"
            >
              <span>◀</span>
              <span>Prev</span>
            </button>

            {/* Thumbnail Dot Pager */}
            <div className="flex items-center gap-1 sm:gap-1.5 overflow-x-auto max-w-[50%] px-2 py-1">
              {SLIDES.map((s, idx) => (
                <button
                  key={s.index}
                  onClick={() => setCurrentIdx(idx)}
                  className={`w-2 h-2 sm:w-2.5 sm:h-2.5 rounded-full transition-all ${
                    idx === currentIdx
                      ? "bg-emerald-600 scale-125 ring-2 ring-emerald-300"
                      : "bg-slate-300 hover:bg-slate-400"
                  }`}
                  aria-label={`Go to slide ${s.index}`}
                />
              ))}
            </div>

            <button
              onClick={handleNext}
              className="px-3.5 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white text-xs sm:text-sm font-bold transition flex items-center gap-1 shadow-sm active:scale-95"
            >
              <span>Next</span>
              <span>▶</span>
            </button>
          </div>
        </div>

        {/* Mobile-Optimized Quick Action Tiles */}
        <div className="w-full mt-3 sm:mt-4 grid grid-cols-1 sm:grid-cols-3 gap-2.5 sm:gap-3 text-xs sm:text-sm">
          <a
            href="/slides/KRISHI_Intelligence_KCC_Presentation.pdf"
            target="_blank"
            rel="noopener noreferrer"
            className="p-3 rounded-lg bg-white border border-slate-300 hover:border-emerald-500 transition flex items-center gap-3 shadow-sm hover:shadow"
          >
            <span className="text-2xl">📱</span>
            <div>
              <div className="font-bold text-slate-900">Open Vector PDF</div>
              <div className="text-slate-500 text-[11px] sm:text-xs">
                Pure vector crispness on phones (no font reflow)
              </div>
            </div>
          </a>

          <a
            href="/slides/KRISHI_Intelligence_KCC_Presentation.pptx"
            download
            className="p-3 rounded-lg bg-white border border-slate-300 hover:border-blue-500 transition flex items-center gap-3 shadow-sm hover:shadow"
          >
            <span className="text-2xl">💻</span>
            <div>
              <div className="font-bold text-slate-900">Download PowerPoint</div>
              <div className="text-slate-500 text-[11px] sm:text-xs">
                Clean Academic White .pptx with speaker notes
              </div>
            </div>
          </a>

          <Link
            href="/farm/092275bd-d37b-4f1a-bf56-94f12dd52095"
            className="p-3 rounded-lg bg-white border border-slate-300 hover:border-amber-500 transition flex items-center gap-3 shadow-sm hover:shadow"
          >
            <span className="text-2xl">🌾</span>
            <div>
              <div className="font-bold text-slate-900">Launch Live Demo App</div>
              <div className="text-slate-500 text-[11px] sm:text-xs">
                Farm Digital Twin & Mandi Decision Engine
              </div>
            </div>
          </Link>
        </div>
      </main>

      {/* Fullscreen High-Res Zoom Modal */}
      {isZoomed && (
        <div
          className="fixed inset-0 z-50 bg-black/90 flex flex-col items-center justify-center p-2 backdrop-blur-sm"
          onClick={() => setIsZoomed(false)}
        >
          <div className="absolute top-3 right-3 flex items-center gap-2">
            <span className="text-white text-xs bg-black/60 px-2 py-1 rounded">
              Tap anywhere to close
            </span>
            <button
              onClick={() => setIsZoomed(false)}
              className="text-white bg-slate-800 hover:bg-slate-700 px-3 py-1.5 rounded-full font-bold text-sm"
            >
              ✕
            </button>
          </div>
          <div className="relative w-full h-[85vh] max-w-6xl">
            <Image
              src={current.image}
              alt={`Fullscreen Slide ${current.index}`}
              fill
              className="object-contain"
              priority
            />
          </div>
        </div>
      )}
    </div>
  );
}
