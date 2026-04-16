import React, { useState } from 'react';
import { 
  MapPin, 
  Sprout, 
  CloudRain, 
  TrendingUp, 
  BarChart, 
  BadgeCheck, 
  Zap, 
  Satellite,
  ChevronRight,
  Loader2
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { yieldService } from '../services/api';
import toast from 'react-hot-toast';

const YieldPrediction = () => {
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [formData, setFormData] = useState({
        crop: 'Wheat',
        state: 'Punjab',
        season: 'Kharif',
        soil_type: 'Alluvial',
        irrigation_type: 'Sprinkler',
        soil_ph: 6.5,
        nitrogen: 80,
        phosphorus: 40,
        potassium: 60,
        rainfall: 450,
        temperature: 25,
        fertiliser_used: 150,
        pesticide_used: 1.5,
        area: 1.0,
    });

    const handleChange = (e) => {
        const { name, value, type } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: type === 'number' || type === 'range' ? parseFloat(value) : value
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            const data = await yieldService.predict(formData);
            setResult(data);
            toast.success('Prediction generated successfully!');
        } catch (error) {
            console.error(error);
            toast.error('Failed to get prediction from server.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-[1440px] mx-auto w-full px-8 py-12">
            <motion.div 
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                className="mb-12"
            >
                <h1 className="text-5xl font-extrabold tracking-tight mb-2 font-headline">Yield Forecast</h1>
                <p className="text-on-surface-variant max-w-2xl leading-relaxed">
                    Leverage precision AI models to estimate crop output based on soil health, local climate patterns, and historical farm performance.
                </p>
            </motion.div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-start">
                {/* Form Section */}
                <section className="lg:col-span-5">
                    <form onSubmit={handleSubmit} className="space-y-10">
                        {/* Crop/Location */}
                        <div className="space-y-4">
                            <div className="flex items-center gap-3">
                                <MapPin className="text-primary w-6 h-6" />
                                <h2 className="text-xl font-bold font-headline">Crop & Location</h2>
                            </div>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div className="flex flex-col gap-1.5">
                                    <label className="text-xs font-semibold text-on-surface-variant uppercase tracking-wider">Crop</label>
                                    <select 
                                        name="crop"
                                        value={formData.crop}
                                        onChange={handleChange}
                                        className="w-full bg-surface-container-low border-none rounded-xl px-4 py-3 focus:ring-1 focus:ring-primary outline-none"
                                    >
                                        {['Wheat', 'Rice', 'Maize', 'Soybean', 'Cotton', 'Sugarcane', 'Tomato', 'Potato'].map(c => (
                                            <option key={c} value={c}>{c}</option>
                                        ))}
                                    </select>
                                </div>
                                <div className="flex flex-col gap-1.5">
                                    <label className="text-xs font-semibold text-on-surface-variant uppercase tracking-wider">State</label>
                                    <select 
                                        name="state"
                                        value={formData.state}
                                        onChange={handleChange}
                                        className="w-full bg-surface-container-low border-none rounded-xl px-4 py-3 focus:ring-1 focus:ring-primary outline-none"
                                    >
                                        {['Punjab', 'Haryana', 'Maharashtra', 'Uttar Pradesh', 'Sikkim', 'West Bengal', 'Karnataka', 'Tamil Nadu'].map(s => (
                                            <option key={s} value={s}>{s}</option>
                                        ))}
                                    </select>
                                </div>
                            </div>
                        </div>

                        {/* Soil Health */}
                        <div className="space-y-6">
                            <div className="flex items-center gap-3">
                                <Sprout className="text-primary w-6 h-6" />
                                <h2 className="text-xl font-bold font-headline">Soil Health Indicators</h2>
                            </div>
                            <div className="space-y-8">
                                <div className="space-y-3">
                                    <div className="flex justify-between items-center">
                                        <label className="text-sm font-medium">Nitrogen (N)</label>
                                        <span className="bg-primary-fixed px-3 py-0.5 rounded-full text-xs font-bold text-on-primary-fixed">{formData.nitrogen} mg/kg</span>
                                    </div>
                                    <input 
                                        type="range" min="0" max="150" name="nitrogen"
                                        value={formData.nitrogen} onChange={handleChange}
                                        className="custom-slider" 
                                    />
                                </div>
                                <div className="space-y-3">
                                    <div className="flex justify-between items-center">
                                        <label className="text-sm font-medium">Phosphorus (P)</label>
                                        <span className="bg-surface-container-highest px-3 py-0.5 rounded-full text-xs font-bold">{formData.phosphorus} mg/kg</span>
                                    </div>
                                    <input 
                                        type="range" min="0" max="100" name="phosphorus"
                                        value={formData.phosphorus} onChange={handleChange}
                                        className="custom-slider" 
                                    />
                                </div>
                                <div className="grid grid-cols-2 gap-4">
                                    <div className="flex flex-col gap-1.5">
                                        <label className="text-xs font-semibold text-on-surface-variant uppercase tracking-wider">Soil pH</label>
                                        <input 
                                            type="number" step="0.1" name="soil_ph"
                                            value={formData.soil_ph} onChange={handleChange}
                                            className="bg-surface-container-low border-none rounded-xl px-4 py-3 focus:ring-1 focus:ring-primary"
                                        />
                                    </div>
                                    <div className="flex flex-col gap-1.5">
                                        <label className="text-xs font-semibold text-on-surface-variant uppercase tracking-wider">Area (Hectares)</label>
                                        <input 
                                            type="number" step="0.1" name="area"
                                            value={formData.area} onChange={handleChange}
                                            className="bg-surface-container-low border-none rounded-xl px-4 py-3 focus:ring-1 focus:ring-primary"
                                        />
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Climate */}
                        <div className="space-y-4">
                            <div className="flex items-center gap-3">
                                <CloudRain className="text-primary w-6 h-6" />
                                <h2 className="text-xl font-bold font-headline">Climate & Irrigation</h2>
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div className="flex flex-col gap-1.5">
                                    <label className="text-xs font-semibold text-on-surface-variant uppercase tracking-wider">Expected Rainfall (mm)</label>
                                    <input 
                                        type="number" name="rainfall"
                                        value={formData.rainfall} onChange={handleChange}
                                        className="bg-surface-container-low border-none rounded-xl px-4 py-3 focus:ring-1 focus:ring-primary"
                                    />
                                </div>
                                <div className="flex flex-col gap-1.5">
                                    <label className="text-xs font-semibold text-on-surface-variant uppercase tracking-wider">Irrigation</label>
                                    <select 
                                        name="irrigation_type"
                                        value={formData.irrigation_type} onChange={handleChange}
                                        className="bg-surface-container-low border-none rounded-xl px-4 py-3 focus:ring-1 focus:ring-primary"
                                    >
                                        <option value="Drip">Drip</option>
                                        <option value="Sprinkler">Sprinkler</option>
                                        <option value="Surface">Surface</option>
                                    </select>
                                </div>
                            </div>
                        </div>

                        <button 
                            disabled={loading}
                            className="w-full bg-gradient-to-r from-primary to-primary-container text-white font-bold py-4 rounded-xl shadow-lg hover:shadow-xl transition-all transform hover:-translate-y-0.5 flex items-center justify-center gap-2"
                        >
                            {loading ? <Loader2 className="animate-spin" /> : 'Predict Yield'}
                        </button>
                    </form>
                </section>

                {/* Results Section */}
                <section className="lg:col-span-7">
                    <AnimatePresence mode="wait">
                        {result ? (
                            <motion.div 
                                key="result"
                                initial={{ opacity: 0, scale: 0.95 }}
                                animate={{ opacity: 1, scale: 1 }}
                                exit={{ opacity: 0, scale: 0.95 }}
                                className="bg-surface-container-lowest rounded-[2rem] p-8 lg:p-12 relative overflow-hidden shadow-2xl shadow-black/5"
                            >
                                <div className="absolute top-0 right-0 w-64 h-64 bg-primary-fixed/20 rounded-full blur-[80px] -mr-32 -mt-32"></div>
                                <div className="relative z-10 space-y-12">
                                    {/* Hero Metric */}
                                    <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
                                        <div>
                                            <span className="text-xs font-bold text-primary uppercase tracking-[0.2em] mb-3 block">Estimated Production</span>
                                            <div className="flex items-baseline gap-2">
                                                <h2 className="text-7xl font-extrabold text-on-surface tracking-tighter">{result.predicted_yield.toLocaleString()}</h2>
                                                <span className="text-2xl font-medium text-on-surface-variant">kg/hectare</span>
                                            </div>
                                        </div>
                                        <div className={`px-4 py-3 rounded-2xl flex items-center gap-3 ${result.pct_vs_avg >= 0 ? 'bg-primary-fixed' : 'bg-error-container text-error'}`}>
                                            <TrendingUp className={`w-5 h-5 ${result.pct_vs_avg >= 0 ? 'text-primary' : 'text-error'}`} />
                                            <span className={`font-bold ${result.pct_vs_avg >= 0 ? 'text-on-primary-fixed' : 'text-error'}`}>
                                                {Math.abs(result.pct_vs_avg)}% {result.pct_vs_avg >= 0 ? 'Above' : 'Below'} Avg
                                            </span>
                                        </div>
                                    </div>

                                    {/* Range Bar */}
                                    <div className="space-y-4">
                                        <div className="flex justify-between text-sm font-semibold">
                                            <span>Projected Variance</span>
                                            <span className="text-on-surface-variant">{result.range.low.toLocaleString()} — {result.range.high.toLocaleString()} kg/ha</span>
                                        </div>
                                        <div className="relative h-6 bg-surface-container-low rounded-full overflow-hidden">
                                            <div className="absolute left-1/4 right-1/4 h-full bg-gradient-to-r from-primary/40 via-primary to-primary/40 rounded-full"></div>
                                            <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-1 h-8 bg-on-surface border-2 border-surface rounded-full"></div>
                                        </div>
                                        <div className="flex justify-between text-[10px] text-on-surface-variant uppercase tracking-widest font-bold">
                                            <span>Low Yield</span>
                                            <span>Median</span>
                                            <span>High Yield</span>
                                        </div>
                                    </div>

                                    {/* Sub Cards */}
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                        <div className="bg-surface-container-low rounded-3xl p-6 space-y-4">
                                            <h3 className="text-sm font-bold text-on-surface-variant uppercase tracking-wider">Regional Baseline</h3>
                                            <div className="flex items-center gap-4">
                                                <div className="w-12 h-12 rounded-full bg-surface-container-highest flex items-center justify-center">
                                                    <BarChart className="text-secondary" />
                                                </div>
                                                <div>
                                                    <div className="text-xl font-bold">{result.state_average.toLocaleString()} kg/ha</div>
                                                    <div className="text-xs text-on-surface-variant">{formData.state} average</div>
                                                </div>
                                            </div>
                                        </div>
                                        <div className="bg-surface-container-low rounded-3xl p-6 space-y-4">
                                            <h3 className="text-sm font-bold text-on-surface-variant uppercase tracking-wider">System Rating</h3>
                                            <div className="flex items-center gap-4">
                                                <div className="w-12 h-12 rounded-full bg-surface-container-highest flex items-center justify-center">
                                                    <BadgeCheck className="text-primary" />
                                                </div>
                                                <div>
                                                    <div className="text-xl font-bold">{result.rating}</div>
                                                    <div className="text-xs text-on-surface-variant">Production potential</div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Recommendation */}
                                    <div className="bg-primary-container text-white rounded-[2rem] p-8 flex flex-col md:flex-row gap-8 items-center">
                                        <div className="flex-grow space-y-2">
                                            <h3 className="text-xl font-bold flex items-center gap-2">
                                                <Zap className="w-6 h-6 fill-current" />
                                                Optimization Protocol
                                            </h3>
                                            <p className="text-sm opacity-90 leading-relaxed">
                                                To achieve results above regional averages, monitor soil moisture closely. 
                                                Predicted total production for {formData.area} hectares is <b>{result.total_production.toLocaleString()} kg</b>.
                                            </p>
                                        </div>
                                        <button className="bg-white text-primary font-bold px-6 py-3 rounded-xl whitespace-nowrap hover:bg-opacity-90 transition-colors">
                                            View Reports
                                        </button>
                                    </div>
                                </div>
                            </motion.div>
                        ) : (
                            <motion.div 
                                key="placeholder"
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                className="h-full flex flex-col justify-center items-center text-center p-12 border-2 border-dashed border-surface-container rounded-[2rem]"
                            >
                                <div className="w-24 h-24 bg-surface-container-low rounded-full flex items-center justify-center mb-6">
                                    <Satellite className="w-12 h-12 text-on-surface-variant/30" />
                                </div>
                                <h3 className="text-2xl font-bold text-on-surface mb-2">Ready for Analysis</h3>
                                <p className="text-on-surface-variant max-w-sm">
                                    Fill out the farm parameters and climate data to generate your precision yield forecast.
                                </p>
                            </motion.div>
                        )}
                    </AnimatePresence>

                    {/* Satellite Insight */}
                    <div className="mt-8 bg-surface-container-low rounded-[2rem] p-2 overflow-hidden h-64 relative group border border-outline/5 shadow-xl shadow-black/5">
                        <img 
                            src="https://images.unsplash.com/photo-1500382017468-9049fed747ef?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80" 
                            alt="Farmland Satellite" 
                            className="w-full h-full object-cover rounded-[1.75rem] group-hover:scale-105 transition-transform duration-700" 
                        />
                        <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-transparent"></div>
                        <div className="absolute bottom-6 left-6 text-white flex items-center gap-3">
                            <div className="w-10 h-10 rounded-full glass-panel flex items-center justify-center">
                                <Satellite className="w-5 h-5 text-white" />
                            </div>
                            <div>
                                <div className="text-sm font-bold">Field-Level Real-Time Analysis</div>
                                <div className="text-xs opacity-80">Connected via CropSense Satellite Engine</div>
                            </div>
                        </div>
                    </div>
                </section>
            </div>
        </div>
    );
};

export default YieldPrediction;
