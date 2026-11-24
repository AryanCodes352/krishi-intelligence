'use client';
import React from 'react';
import Link from 'next/link';
import { ArrowRight, BarChart3, ShieldAlert, Sprout } from 'lucide-react';

export default function LandingPage() {
  return (
    <div className="flex flex-col min-h-[calc(100vh-80px)] -mt-4 sm:-mt-6 lg:-mt-8 -mx-4 sm:-mx-6 lg:-mx-8">
      {/* Hero Section */}
      <div className="relative bg-krishi-green-dark overflow-hidden flex-1 flex flex-col justify-center items-center text-center px-4 py-20">
        <div className="absolute inset-0 opacity-10 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-krishi-gold via-krishi-green-dark to-krishi-green-dark"></div>
        
        <div className="relative z-10 max-w-4xl mx-auto space-y-8">
          <h1 className="font-serif text-5xl md:text-7xl font-bold text-krishi-cream leading-tight">
            See the data. <br />
            <span className="text-krishi-gold">Understand the risk.</span><br />
            Make the right decision.
          </h1>
          
          <p className="text-xl md:text-2xl text-gray-300 max-w-2xl mx-auto">
            AI-powered agricultural decision support for Indian farmers, transforming complex data into clear action.
          </p>
          
          <div className="pt-8">
            <Link 
              href="/onboard" 
              className="inline-flex items-center gap-2 bg-krishi-gold hover:bg-krishi-gold-light text-krishi-green-dark px-8 py-4 rounded-full font-bold text-lg transition-all transform hover:scale-105 shadow-lg"
            >
              Get Started — It's Free
              <ArrowRight className="w-5 h-5" />
            </Link>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="bg-krishi-cream py-20 px-4">
        <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-8">
          <FeatureCard 
            icon={<ShieldAlert className="w-10 h-10 text-krishi-green" />}
            title="Location-Based Risk Alerts"
            description="Weather anomalies, agricultural risks, and soil condition assessments evaluated for your farm's location and district."
          />
          <FeatureCard 
            icon={<BarChart3 className="w-10 h-10 text-krishi-gold" />}
            title="Market Intelligence"
            description="Predictive price models and historical mandi analysis providing risk-adjusted decision support to help evaluate selling options."
          />
          <FeatureCard 
            icon={<Sprout className="w-10 h-10 text-krishi-soil" />}
            title="Expert Guidance"
            description="AI agronomist guidance contextualized with your crop stage, soil estimates, and weather conditions."
          />
        </div>
      </div>
      
      <footer className="bg-gray-900 text-gray-400 py-8 text-center text-sm">
        <p>KRISHI Intelligence • Academic Mini Project • Democratizing Agricultural Decision Intelligence for Farmers</p>
      </footer>
    </div>
  );
}

const FeatureCard = ({ icon, title, description }: { icon: React.ReactNode, title: string, description: string }) => (
  <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
    <div className="bg-gray-50 w-16 h-16 rounded-xl flex items-center justify-center mb-6">
      {icon}
    </div>
    <h3 className="font-serif text-2xl font-bold text-krishi-green-dark mb-4">{title}</h3>
    <p className="text-gray-600 leading-relaxed">{description}</p>
  </div>
);
