import React, { useState, useRef } from 'react';
import { 
  Upload, 
  Image as ImageIcon, 
  Search, 
  AlertTriangle, 
  ShieldCheck, 
  Activity, 
  X,
  Loader2,
  Stethoscope,
  Leaf
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { diseaseService } from '../services/api';
import toast from 'react-hot-toast';

const DiseaseDetection = () => {
    const [selectedFile, setSelectedFile] = useState(null);
    const [preview, setPreview] = useState(null);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const fileInputRef = useRef(null);

    const handleFileSelect = (e) => {
        const file = e.target.files[0];
        if (file) {
            setSelectedFile(file);
            const reader = new FileReader();
            reader.onloadend = () => setPreview(reader.result);
            reader.readAsDataURL(file);
        }
    };

    const handleUpload = async () => {
        if (!selectedFile) return;
        setLoading(true);
        try {
            const data = await diseaseService.predict(selectedFile);
            setResult(data);
            toast.success('Analysis complete!');
        } catch (error) {
            console.error(error);
            toast.error('Failed to analyze the leaf image.');
        } finally {
            setLoading(false);
        }
    };

    const clear = () => {
        setResult(null);
        setSelectedFile(null);
        setPreview(null);
        if (fileInputRef.current) fileInputRef.current.value = '';
    };

    return (
        <div className="max-w-7xl mx-auto w-full px-8 py-12">
            <header className="mb-12">
                <span className="text-primary font-bold tracking-[0.2em] uppercase text-xs mb-3 block">Plant Pathology AI</span>
                <h1 className="text-5xl font-extrabold tracking-tight font-headline mb-4">Leaf Diagnostic Engine</h1>
                <p className="text-on-surface-variant text-lg max-w-2xl">
                    Upload a high-resolution photo of a crop leaf to identify infestations, blights, and deficiencies with surgical precision.
                </p>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
                {/* Upload Section */}
                <section className="space-y-6">
                    <div 
                        onClick={() => fileInputRef.current?.click()}
                        className={`relative border-2 border-dashed rounded-[2rem] h-[500px] flex flex-col items-center justify-center cursor-pointer transition-all overflow-hidden ${
                            preview ? 'border-primary' : 'border-surface-container-highest hover:bg-surface-container-low'
                        }`}
                    >
                        {preview ? (
                            <>
                                <img src={preview} alt="Leaf preview" className="w-full h-full object-cover" />
                                <div className="absolute inset-0 bg-black/20 group-hover:bg-black/40 transition-colors"></div>
                                <button 
                                    onClick={(e) => { e.stopPropagation(); clear(); }}
                                    className="absolute top-4 right-4 bg-white/10 backdrop-blur-md p-2 rounded-full text-white hover:bg-white/20"
                                >
                                    <X className="w-6 h-6" />
                                </button>
                            </>
                        ) : (
                            <div className="text-center p-8 space-y-4">
                                <div className="w-20 h-20 bg-primary/10 rounded-full flex items-center justify-center mx-auto text-primary">
                                    <ImageIcon className="w-10 h-10" />
                                </div>
                                <div>
                                    <p className="text-xl font-bold font-headline">Click or drag leaf image</p>
                                    <p className="text-on-surface-variant text-sm mt-1">Supports High Res JPG/PNG. Min 224x224px.</p>
                                </div>
                            </div>
                        )}
                        <input type="file" ref={fileInputRef} hidden accept="image/*" onChange={handleFileSelect} />
                    </div>

                    <div className="flex gap-4">
                        <button 
                            disabled={!selectedFile || loading}
                            onClick={handleUpload}
                            className={`flex-grow py-4 rounded-2xl font-bold flex items-center justify-center gap-3 transition-all ${
                                !selectedFile || loading ? 'bg-surface-container text-on-surface-variant' : 'bg-primary text-white shadow-xl shadow-primary/20 hover:-translate-y-1'
                            }`}
                        >
                            {loading ? <Loader2 className="animate-spin" /> : <Search className="w-5 h-5" />}
                            Run Diagnostics
                        </button>
                    </div>
                </section>

                {/* Results Section */}
                <section>
                    <AnimatePresence mode="wait">
                        {result ? (
                            <motion.div 
                                key="result"
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="space-y-6"
                            >
                                {/* Results Card */}
                                <div className="bg-surface-container-lowest rounded-[2rem] p-8 border border-outline/5 shadow-2xl shadow-black/5">
                                    <div className="flex items-center justify-between mb-8">
                                        <div className="flex items-center gap-4">
                                            <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center">
                                                <Stethoscope className="text-primary w-6 h-6" />
                                            </div>
                                            <div>
                                                <h3 className="text-2xl font-extrabold font-headline">{result.disease}</h3>
                                                <p className="text-xs text-on-surface-variant font-bold uppercase tracking-widest">{result.confidence}% Confidence Match</p>
                                            </div>
                                        </div>
                                        <div className={`px-4 py-1.5 rounded-full text-xs font-bold uppercase tracking-wider ${
                                            result.treatment_data.severity === 'Normal' ? 'bg-primary-fixed text-on-primary-fixed' : 'bg-error-container text-error'
                                        }`}>
                                            {result.treatment_data.severity}
                                        </div>
                                    </div>

                                    <div className="space-y-8">
                                        {/* Description */}
                                        <div className="bg-surface-container-low p-6 rounded-3xl">
                                            <h4 className="text-sm font-bold text-on-surface-variant uppercase mb-2">Internal Description</h4>
                                            <p className="text-on-surface leading-relaxed">{result.treatment_data.description}</p>
                                        </div>

                                        {/* Treatments Grid */}
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                            <div className="space-y-4">
                                                <h4 className="text-sm font-bold text-primary flex items-center gap-2">
                                                    <AlertTriangle className="w-4 h-4" /> IMMEDIATE ACTION
                                                </h4>
                                                <ul className="space-y-2">
                                                    {result.treatment_data.treatments.map((t, i) => (
                                                        <li key={i} className="text-sm flex gap-3 text-on-surface">
                                                            <div className="w-1.5 h-1.5 rounded-full bg-primary mt-1.5 shrink-0"></div>
                                                            {t}
                                                        </li>
                                                    ))}
                                                </ul>
                                            </div>
                                            <div className="space-y-4">
                                                <h4 className="text-sm font-bold text-on-surface-variant flex items-center gap-2">
                                                    <ShieldCheck className="w-4 h-4" /> PREVENTATIVE CARE
                                                </h4>
                                                <ul className="space-y-2">
                                                    {result.treatment_data.prevention.map((p, i) => (
                                                        <li key={i} className="text-sm flex gap-3 text-on-surface-variant">
                                                            <div className="w-1.5 h-1.5 rounded-full bg-outline mt-1.5 shrink-0"></div>
                                                            {p}
                                                        </li>
                                                    ))}
                                                </ul>
                                            </div>
                                        </div>

                                        {/* Hindi Note */}
                                        <div className="bg-primary/5 p-6 rounded-3xl border border-primary/10">
                                            <div className="flex items-center gap-2 mb-2">
                                                <Leaf className="w-4 h-4 text-primary" />
                                                <span className="text-xs font-bold text-primary uppercase">किसान सलाह</span>
                                            </div>
                                            <p className="text-lg text-primary font-medium leading-relaxed">{result.note_hindi}</p>
                                        </div>
                                    </div>
                                </div>
                            </motion.div>
                        ) : (
                            <div className="h-full flex flex-col justify-center items-center text-center p-12 space-y-6">
                                <div className="w-32 h-32 bg-surface-container rounded-full flex items-center justify-center animate-pulse">
                                    <Activity className="w-16 h-16 text-on-surface-variant/20" />
                                </div>
                                <div className="space-y-2">
                                    <h3 className="text-2xl font-bold font-headline">Waiting for Input</h3>
                                    <p className="text-on-surface-variant max-w-sm">
                                        Once you upload a photo, our neural network will scan for disease patterns and provide a full organic medical report.
                                    </p>
                                </div>
                            </div>
                        )}
                    </AnimatePresence>
                </section>
            </div>
        </div>
    );
};

export default DiseaseDetection;
