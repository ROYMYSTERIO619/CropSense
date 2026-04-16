import React from 'react';
import { 
  TrendingUp, 
  Activity, 
  Target, 
  ShieldAlert, 
  History,
  ArrowUpRight,
  PieChart as PieChartIcon
} from 'lucide-react';
import { motion } from 'framer-motion';

const Dashboard = () => {
    // Mock data for the dashboard visuals as requested in the design
    const kpis = [
        { label: 'Total Analyses', value: '12,842', trend: '+14.2%', color: 'text-primary' },
        { label: 'Most Common', value: 'Late Blight', sub: 'Affecting 32% of alerts', color: 'text-secondary' },
        { label: 'Healthy Crops', value: '88.4%', progress: 88, color: 'text-primary' },
        { label: 'Avg Confidence', value: '97.2%', sub: 'Based on 1.2M points', color: 'text-on-surface-variant' }
    ];

    const topDiseases = [
        { name: 'Late Blight', cases: '4.2k', width: '85%' },
        { name: 'Leaf Rust', cases: '2.8k', width: '65%' },
        { name: 'Powdery Mildew', cases: '1.9k', width: '45%' },
        { name: 'Black Rot', cases: '1.1k', width: '30%' },
        { name: 'Root Rot', cases: '0.8k', width: '20%' },
    ];

    return (
        <div className="max-w-[1600px] mx-auto w-full px-8 py-10">
            <header className="mb-12">
                <h1 className="text-5xl font-extrabold font-headline tracking-tighter text-on-surface mb-2">Disease Analytics Dashboard</h1>
                <p className="text-on-surface-variant text-lg">Precision monitoring and predictive health insights for your harvest.</p>
            </header>

            {/* KPI Row */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
                {kpis.map((kpi, i) => (
                    <motion.div 
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: i * 0.1 }}
                        key={i} 
                        className="bg-surface-container-lowest p-8 rounded-2xl shadow-sm border border-outline/5 flex flex-col justify-between"
                    >
                        <div>
                            <p className="text-on-surface-variant text-xs font-bold tracking-wider uppercase mb-2">{kpi.label}</p>
                            <h3 className={`text-4xl font-headline font-extrabold text-on-surface`}>{kpi.value}</h3>
                        </div>
                        {kpi.trend && (
                            <div className="mt-4 flex items-center gap-2 text-primary text-sm font-bold">
                                <TrendingUp className="w-4 h-4" />
                                {kpi.trend} from last month
                            </div>
                        )}
                        {kpi.sub && <div className="mt-4 text-xs font-bold text-on-surface-variant opacity-70 italic">{kpi.sub}</div>}
                        {kpi.progress && (
                            <div className="mt-4 h-2 w-full bg-surface-container rounded-full overflow-hidden">
                                <div className="h-full bg-primary" style={{ width: `${kpi.progress}%` }}></div>
                            </div>
                        )}
                    </motion.div>
                ))}
            </div>

            {/* Charts Row */}
            <div className="grid grid-cols-1 lg:grid-cols-5 gap-8 mb-12">
                {/* Distribution (Donut style) */}
                <div className="lg:col-span-2 bg-surface-container-lowest p-8 rounded-3xl border border-outline/5 shadow-sm">
                    <h4 className="text-xl font-headline font-bold mb-8 flex items-center gap-2">
                        <PieChartIcon className="w-5 h-5" /> Disease Distribution
                    </h4>
                    <div className="relative flex items-center justify-center py-10">
                        <div className="w-48 h-48 rounded-full border-[20px] border-primary-fixed relative">
                            <div className="absolute inset-[-20px] rounded-full border-[20px] border-secondary-container" style={{ clipPath: 'polygon(50% 50%, 50% 0, 100% 0, 100% 50%)' }}></div>
                            <div className="absolute inset-[-20px] rounded-full border-[20px] border-error" style={{ clipPath: 'polygon(50% 50%, 0 50%, 0 100%, 50% 100%)' }}></div>
                            <div className="absolute inset-0 flex flex-col items-center justify-center">
                                <span className="text-2xl font-bold font-headline">5 Types</span>
                            </div>
                        </div>
                    </div>
                    <div className="grid grid-cols-2 gap-4 mt-8">
                        {['Healthy (60%)', 'Late Blight (25%)', 'Rust (10%)', 'Other (5%)'].map((label, i) => (
                            <div key={i} className="flex items-center gap-2">
                                <div className={`w-3 h-3 rounded-full ${i === 0 ? 'bg-primary-fixed' : i === 1 ? 'bg-secondary-container' : i === 2 ? 'bg-error' : 'bg-on-surface-variant'}`}></div>
                                <span className="text-xs text-on-surface-variant">{label}</span>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Frequency Bar Chart */}
                <div className="lg:col-span-3 bg-surface-container-low p-8 rounded-3xl">
                    <h4 className="text-xl font-headline font-bold mb-8 flex items-center gap-2">
                        <Target className="w-5 h-5" /> Frequency Analysis
                    </h4>
                    <div className="space-y-6">
                        {topDiseases.map((d, i) => (
                            <div key={i} className="space-y-2">
                                <div className="flex justify-between text-xs font-bold text-on-surface-variant uppercase tracking-wider">
                                    <span>{d.name}</span>
                                    <span>{d.cases} cases</span>
                                </div>
                                <div className="h-4 w-full bg-surface-container-highest rounded-full overflow-hidden">
                                    <div className="h-full bg-primary" style={{ width: d.width, opacity: 1 - (i * 0.15) }}></div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Recent Table */}
            <div className="bg-surface-container-lowest rounded-3xl shadow-sm border border-outline/5 overflow-hidden">
                <div className="px-8 py-8 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                    <h4 className="text-2xl font-headline font-bold flex items-center gap-2">
                        <History className="w-6 h-6" /> Recent Analyses
                    </h4>
                    <button className="px-6 py-2.5 bg-surface-container-highest text-on-surface text-sm font-bold rounded-xl hover:bg-surface-container transition-colors">
                        View Full History
                    </button>
                </div>
                <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse">
                        <thead>
                            <tr className="bg-surface-container-low/50">
                                <th className="px-8 py-5 text-xs font-bold text-on-surface-variant uppercase tracking-widest">Crop / Variety</th>
                                <th className="px-8 py-5 text-xs font-bold text-on-surface-variant uppercase tracking-widest">Detection</th>
                                <th className="px-8 py-5 text-xs font-bold text-on-surface-variant uppercase tracking-widest">Confidence</th>
                                <th className="px-8 py-5 text-xs font-bold text-on-surface-variant uppercase tracking-widest">Severity</th>
                                <th className="px-8 py-5 text-xs font-bold text-on-surface-variant uppercase tracking-widest">Timestamp</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-surface-container-low">
                            {[
                                { crop: 'Russet Potato', disease: 'Late Blight', conf: '98.4%', sev: 'Critical', time: '2 mins ago' },
                                { crop: 'Sweet Pea', disease: 'Healthy', conf: '99.1%', sev: 'Optimal', time: '15 mins ago' },
                                { crop: 'Roma Tomato', disease: 'Leaf Mold', conf: '94.2%', sev: 'Warning', time: '1 hour ago' },
                                { crop: 'Sweet Corn', disease: 'Common Rust', conf: '87.5%', sev: 'Warning', time: '3 hours ago' }
                            ].map((row, i) => (
                                <tr key={i} className="hover:bg-surface-container-low/30 transition-colors cursor-pointer">
                                    <td className="px-8 py-6 font-semibold text-on-surface">{row.crop}</td>
                                    <td className="px-8 py-6 text-on-surface font-medium">{row.disease}</td>
                                    <td className="px-8 py-6 text-on-surface-variant font-mono">{row.conf}</td>
                                    <td className="px-8 py-6">
                                        <span className={`px-3 py-1 text-[10px] font-bold rounded-full uppercase tracking-tight ${
                                            row.sev === 'Critical' ? 'bg-error-container text-error' : 
                                            row.sev === 'Optimal' ? 'bg-primary-fixed text-on-primary-fixed' : 
                                            'bg-secondary-fixed text-on-secondary-fixed'
                                        }`}>
                                            {row.sev}
                                        </span>
                                    </td>
                                    <td className="px-8 py-6 text-on-surface-variant text-sm">{row.time}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
