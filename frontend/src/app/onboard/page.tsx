'use client';
import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import { Loader2, Info } from 'lucide-react';

const isCropSupported = (crop: string): boolean => {
  return crop.trim().toLowerCase() === 'wheat';
};

export default function OnboardPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    farmer_name: '',
    state: 'Uttar Pradesh',
    district: 'Lucknow',
    location: '',
    crop: 'Wheat',
    crop_variety: 'HD-2967',
    sowing_date: '2025-11-15',
    farm_area_acres: 3,
    has_soil_test: 'no'
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setError('');
    const { name, value } = e.target;
    if (name === 'crop') {
      const isWheat = value.trim().toLowerCase() === 'wheat';
      setFormData(prev => ({
        ...prev,
        crop: value,
        crop_variety: isWheat ? (prev.crop_variety || 'HD-2967') : '',
      }));
      return;
    }
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const nextStep = () => {
    if (step === 1) {
      if (!formData.farmer_name.trim()) {
        setError('Please enter the farmer name to continue.');
        return;
      }
      if (!formData.state) {
        setError('Please select a state.');
        return;
      }
      if (!formData.district) {
        setError('Please select a district.');
        return;
      }
      if (!formData.location.trim()) {
        setError('Please enter your village/location.');
        return;
      }
    }
    if (step === 2) {
      if (!formData.crop) {
        setError('Please select a crop.');
        return;
      }
      if (!isCropSupported(formData.crop)) {
        setError(
          'This prototype currently supports Wheat only. ' +
          'Market Intelligence and ML price prediction are available for Wheat. ' +
          'Rice, Mustard and other crops will be supported in a future version.'
        );
        return;
      }
      if (!formData.sowing_date) {
        setError('Please choose a sowing date.');
        return;
      }
      if (!formData.farm_area_acres || Number(formData.farm_area_acres) <= 0) {
        setError('Please enter a valid farm area in acres.');
        return;
      }
    }
    setError('');
    setStep(s => Math.min(s + 1, 3));
  };

  const prevStep = () => {
    setError('');
    setStep(s => Math.max(s - 1, 1));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.farmer_name.trim()) {
      setError('Farmer name is required.');
      setStep(1);
      return;
    }
    if (!isCropSupported(formData.crop)) {
      setError(
        'This prototype currently supports Wheat only. ' +
        'Market Intelligence and ML price prediction are available for Wheat. ' +
        'Rice, Mustard and other crops will be supported in a future version.'
      );
      setStep(2);
      return;
    }
    setIsLoading(true);
    setError('');
    
    const payload = {
      ...formData,
      farmer_name: formData.farmer_name.trim(),
      location: formData.location.trim() || formData.district,
      farm_area_acres: Number(formData.farm_area_acres),
      soil_data_available: formData.has_soil_test === 'yes',
      lat: 26.8467,
      lon: 80.9462
    };

    const res = await api.onboardFarm(payload);
    
    if (res && res.farm_id) {
      router.push(`/farm/${res.farm_id}`);
    } else {
      setIsLoading(false);
      setError('Unable to save farm profile. Please verify the backend is running and try again.');
    }
  };

  return (
    <div className="max-w-2xl mx-auto py-12">
      <div className="mb-8">
        <h1 className="text-3xl font-serif font-bold text-krishi-green-dark mb-2">Farm Setup</h1>
        <p className="text-gray-600">Let's get your farm profile created for personalized intelligence.</p>
        
        {/* Progress Bar */}
        <div className="flex gap-2 mt-6">
          {[1, 2, 3].map(i => (
            <div key={i} className={`h-2 flex-1 rounded-full ${step >= i ? 'bg-krishi-green' : 'bg-gray-200'}`} />
          ))}
        </div>
      </div>

      <form onSubmit={handleSubmit} className="bg-white p-6 sm:p-8 rounded-2xl shadow-sm border border-gray-100">
        {error && (
          <div className="p-3 bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg mb-4">
            {error}
          </div>
        )}
        {step === 1 && (
          <div className="space-y-4 animate-in fade-in slide-in-from-right-4">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Location Details</h2>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Farmer Name</label>
              <input required type="text" name="farmer_name" value={formData.farmer_name} onChange={handleChange} className="w-full border-gray-300 rounded-md shadow-sm p-2 border focus:ring-krishi-green focus:border-krishi-green" placeholder="John Doe" />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">State</label>
                <select required name="state" value={formData.state} onChange={handleChange} className="w-full border-gray-300 rounded-md shadow-sm p-2 border">
                  <option value="">Select State</option>
                  <option value="Uttar Pradesh">Uttar Pradesh</option>
                  <option value="Punjab">Punjab</option>
                  <option value="Haryana">Haryana</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">District</label>
                <select required name="district" value={formData.district} onChange={handleChange} className="w-full border-gray-300 rounded-md shadow-sm p-2 border">
                  <option value="">Select District</option>
                  <option value="Lucknow">Lucknow</option>
                  <option value="Kanpur Nagar">Kanpur Nagar</option>
                  <option value="Unnao">Unnao</option>
                </select>
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Village / Location</label>
              <input required type="text" name="location" value={formData.location} onChange={handleChange} className="w-full border-gray-300 rounded-md shadow-sm p-2 border" placeholder="Village name" />
            </div>
          </div>
        )}

        {step === 2 && (
          <div className="space-y-4 animate-in fade-in slide-in-from-right-4">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Crop Information</h2>
            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="block text-sm font-medium text-gray-700">Crop</label>
                <span className="text-xs bg-emerald-50 text-krishi-green font-medium px-2 py-0.5 rounded border border-emerald-200">
                  Wheat currently supported
                </span>
              </div>
              <select required name="crop" value={formData.crop} onChange={handleChange} className="w-full border-gray-300 rounded-md shadow-sm p-2 border">
                <option value="">Select Crop</option>
                <option value="Wheat">Wheat (Supported)</option>
                <option value="Rice">Rice (Upcoming)</option>
                <option value="Mustard">Mustard (Upcoming)</option>
              </select>
            </div>

            {formData.crop && !isCropSupported(formData.crop) && (
              <div className="p-4 bg-amber-50 border border-amber-200 rounded-xl text-amber-900 text-sm">
                <div className="flex items-start gap-3">
                  <Info className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
                  <div className="space-y-1">
                    <p className="font-semibold text-amber-900">
                      This prototype currently supports Wheat only.
                    </p>
                    <p className="text-amber-800 text-xs">
                      Market Intelligence and ML price prediction are available for Wheat.
                    </p>
                    <p className="text-amber-800 text-xs">
                      Rice, Mustard and other crops will be supported in a future version.
                    </p>
                  </div>
                </div>
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Crop Variety (Optional)</label>
              <input
                type="text"
                name="crop_variety"
                value={formData.crop_variety}
                onChange={handleChange}
                className="w-full border-gray-300 rounded-md shadow-sm p-2 border"
                placeholder={isCropSupported(formData.crop) ? "e.g., HD-2967" : "e.g., Variety name (Optional)"}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Sowing Date</label>
                <input required type="date" name="sowing_date" value={formData.sowing_date} onChange={handleChange} className="w-full border-gray-300 rounded-md shadow-sm p-2 border" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Area (Acres)</label>
                <input required type="number" min="0.1" step="0.1" name="farm_area_acres" value={formData.farm_area_acres} onChange={handleChange} className="w-full border-gray-300 rounded-md shadow-sm p-2 border" />
              </div>
            </div>
          </div>
        )}

        {step === 3 && (
          <div className="space-y-4 animate-in fade-in slide-in-from-right-4">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Soil Data</h2>
            
            {formData.crop && !isCropSupported(formData.crop) && (
              <div className="p-4 bg-amber-50 border border-amber-200 rounded-xl text-amber-900 text-sm">
                <div className="flex items-start gap-3">
                  <Info className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
                  <div className="space-y-1">
                    <p className="font-semibold text-amber-900">
                      This prototype currently supports Wheat only.
                    </p>
                    <p className="text-amber-800 text-xs">
                      Market Intelligence and ML price prediction are available for Wheat.
                    </p>
                    <p className="text-amber-800 text-xs">
                      Rice, Mustard and other crops will be supported in a future version.
                    </p>
                  </div>
                </div>
              </div>
            )}

            <div className="space-y-3">
              <label className="flex items-center gap-3 p-4 border rounded-lg cursor-pointer hover:bg-gray-50">
                <input type="radio" name="has_soil_test" value="no" checked={formData.has_soil_test === 'no'} onChange={handleChange} className="w-4 h-4 text-krishi-green" />
                <div>
                  <div className="font-medium text-gray-900">Use regional estimates</div>
                  <div className="text-sm text-gray-500">AI will estimate soil quality based on your district</div>
                </div>
              </label>
              
              <label className="flex items-center gap-3 p-4 border rounded-lg cursor-pointer hover:bg-gray-50">
                <input type="radio" name="has_soil_test" value="yes" checked={formData.has_soil_test === 'yes'} onChange={handleChange} className="w-4 h-4 text-krishi-green" />
                <div>
                  <div className="font-medium text-gray-900">I have soil test results</div>
                  <div className="text-sm text-gray-500">Enter parameters manually for higher accuracy</div>
                </div>
              </label>
            </div>

            {formData.has_soil_test === 'yes' && (
              <div className="grid grid-cols-2 gap-4 pt-4 border-t">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Nitrogen (N)</label>
                  <input type="number" className="w-full border-gray-300 rounded-md p-2 border" placeholder="kg/ha" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Phosphorus (P)</label>
                  <input type="number" className="w-full border-gray-300 rounded-md p-2 border" placeholder="kg/ha" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Potassium (K)</label>
                  <input type="number" className="w-full border-gray-300 rounded-md p-2 border" placeholder="kg/ha" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">pH</label>
                  <input type="number" step="0.1" className="w-full border-gray-300 rounded-md p-2 border" placeholder="0-14" />
                </div>
              </div>
            )}
          </div>
        )}

        <div className="mt-8 flex justify-between">
          {step > 1 ? (
            <button type="button" onClick={prevStep} className="px-6 py-2 text-gray-600 hover:text-gray-900 font-medium">Back</button>
          ) : <div></div>}
          
          {step < 3 ? (
            <button
              type="button"
              onClick={nextStep}
              disabled={step === 2 && !isCropSupported(formData.crop)}
              className={`px-6 py-2 rounded-lg font-medium transition-colors ${
                step === 2 && !isCropSupported(formData.crop)
                  ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                  : 'bg-krishi-green text-white hover:bg-krishi-green-dark'
              }`}
            >
              Next Step
            </button>
          ) : (
            <button
              type="submit"
              disabled={isLoading || !isCropSupported(formData.crop)}
              className={`px-6 py-2 rounded-lg font-bold flex items-center gap-2 transition-colors ${
                !isCropSupported(formData.crop)
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-krishi-gold text-krishi-green-dark hover:bg-krishi-gold-light'
              }`}
              title={!isCropSupported(formData.crop) ? 'This prototype currently supports Wheat only.' : undefined}
            >
              {isLoading && <Loader2 className="w-4 h-4 animate-spin" />}
              Analyze My Farm
            </button>
          )}
        </div>
      </form>
    </div>
  );
}
