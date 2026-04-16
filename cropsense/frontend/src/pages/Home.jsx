import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, BarChart3, Binary, HeartPulse, CheckCircle2, Eco } from 'lucide-react';
import { motion } from 'framer-motion';

const Home = () => {
  const navigate = useNavigate();

  return (
    <div className="overflow-hidden">
      {/* Hero Section */}
      <section className="relative h-[850px] min-h-[600px] flex items-center overflow-hidden">
        <div className="absolute inset-0 z-0">
          <img 
            src="https://images.unsplash.com/photo-1523348837708-15d4a09cfac2?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80" 
            alt="Vibrant green agricultural field" 
            className="w-full h-full object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-r from-background/95 via-background/50 to-transparent"></div>
        </div>

        <div className="relative z-10 px-8 md:px-16 lg:px-24 max-w-4xl">
          <motion.h1 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="font-headline text-5xl md:text-7xl font-extrabold tracking-tight text-on-background mb-6 leading-[1.1]"
          >
            Detect Crop Disease Instantly. <br/>
            <span className="bg-gradient-to-r from-primary to-primary-container bg-clip-text text-transparent">Predict Your Yield Accurately.</span>
          </motion.h1>
          <motion.p 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="text-on-surface-variant text-lg md:text-xl max-w-2xl mb-10 font-body"
          >
            Harnessing the power of precision AI to provide farmers with real-time insights, disease diagnostics, and predictive analytics for sustainable organic growth.
          </motion.p>
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="flex flex-col sm:flex-row gap-4"
          >
            <button 
              onClick={() => navigate('/detect')}
              className="bg-gradient-to-br from-primary to-primary-container text-white px-8 py-4 rounded-xl font-semibold flex items-center justify-center gap-2 hover:opacity-90 transition-all active:scale-95 shadow-lg shadow-primary/20"
            >
              Detect Disease <ArrowRight className="w-5 h-5" />
            </button>
            <button 
              onClick={() => navigate('/yield')}
              className="bg-surface-container-highest text-on-surface px-8 py-4 rounded-xl font-semibold flex items-center justify-center gap-2 hover:bg-surface-container-high transition-all active:scale-95"
            >
              Predict Yield <BarChart3 className="w-5 h-5" />
            </button>
          </motion.div>
        </div>
      </section>

      {/* Stats Bar */}
      <section className="bg-surface-container-low py-12 px-8">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-8">
            {[
              { label: 'Training Images', value: '54,000+' },
              { label: 'Disease Classes', value: '38' },
              { label: 'Crops Supported', value: '15+' },
              { label: 'Accuracy Rate', value: '95%+' },
            ].map((stat, i) => (
              <div key={i} className="flex flex-col items-center lg:items-start border-l-2 border-primary/20 pl-6">
                <span className="font-headline text-3xl font-bold text-primary">{stat.value}</span>
                <span className="font-label text-sm uppercase tracking-widest text-on-surface-variant">{stat.label}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Feature Section */}
      <section className="py-24 px-8 bg-surface">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col md:flex-row justify-between items-end mb-16 gap-4">
            <div className="max-w-2xl">
              <h2 className="font-headline text-4xl font-bold tracking-tight mb-4">Cultivating Intelligence</h2>
              <p className="text-on-surface-variant font-body">Our suite of precision tools provides end-to-end support for modern sustainable agriculture.</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
            <div className="md:col-span-8 bg-surface-container-lowest p-8 rounded-[2rem] group relative overflow-hidden transition-all hover:bg-surface-container-low border border-outline/5">
              <div className="relative z-10 h-full flex flex-col">
                <div className="w-14 h-14 bg-primary/10 rounded-full flex items-center justify-center mb-6 text-primary">
                  <Binary className="w-8 h-8" />
                </div>
                <h3 className="font-headline text-2xl font-bold mb-3">Disease Detection</h3>
                <p className="text-on-surface-variant mb-8 max-w-md">Upload a photo of your crop leaves and our AI identifies issues within seconds, covering blights, rusts, and nutrient deficiencies.</p>
                <div className="mt-auto">
                  <button onClick={() => navigate('/detect')} className="bg-primary text-white px-6 py-3 rounded-full font-medium active:scale-95 transition-transform">Run Analysis</button>
                </div>
              </div>
            </div>

            <div className="md:col-span-4 bg-primary text-white p-8 rounded-[2rem] flex flex-col justify-between relative overflow-hidden shadow-xl shadow-primary/20">
              <div className="relative z-10">
                <BarChart3 className="w-10 h-10 mb-6" />
                <h3 className="font-headline text-2xl font-bold mb-3">Yield Prediction</h3>
                <p className="text-white/80">Using satellite data and historic growth patterns to forecast your harvest volume accurately.</p>
              </div>
              <div className="mt-12 relative z-10">
                <div className="h-2 w-full bg-white/20 rounded-full overflow-hidden">
                  <div className="h-full bg-primary-fixed w-[85%]"></div>
                </div>
                <p className="text-xs mt-2 text-white/60 uppercase tracking-widest font-label">Confidence: 85%</p>
              </div>
            </div>

            <div className="md:col-span-12 bg-surface-container-high p-10 rounded-[2rem] flex flex-col md:flex-row items-center gap-12 overflow-hidden border border-outline/5">
              <div className="flex-1">
                <HeartPulse className="w-12 h-12 text-secondary mb-6" />
                <h3 className="font-headline text-3xl font-bold mb-4">Treatment Guide</h3>
                <p className="text-on-surface-variant text-lg mb-6">Found a disease? Get instant, localized recommendations for organic treatments, preventative care, and integrated pest management tailored to your specific ecosystem.</p>
                <ul className="space-y-3 mb-8">
                  {['Organic-first solutions', 'Localized product sourcing', 'Sustainability impact metrics'].map((item, i) => (
                    <li key={i} className="flex items-center gap-3 text-on-surface">
                      <CheckCircle2 className="w-5 h-5 text-primary" />
                      {item}
                    </li>
                  ))}
                </ul>
                <button className="bg-on-surface text-surface px-8 py-3 rounded-full font-medium">View Library</button>
              </div>
              <div className="flex-1 w-full md:w-auto h-64 md:h-80 rounded-2xl overflow-hidden shadow-2xl relative group">
                <img 
                  src="https://images.unsplash.com/photo-1595113316349-9fa4978663e8?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80" 
                  alt="Farmer inspecting organic crops" 
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                />
                <div className="absolute top-4 left-4 bg-surface/80 backdrop-blur px-4 py-2 rounded-full flex items-center gap-2 border border-outline/10">
                  <div className="w-2 h-2 bg-primary rounded-full animate-pulse"></div>
                  <span className="text-xs font-bold uppercase tracking-widest">Organic Certified</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 px-8">
        <div className="max-w-7xl mx-auto rounded-[3rem] bg-surface-container-lowest p-12 md:p-24 text-center relative overflow-hidden border border-outline/5 shadow-2xl shadow-black/5">
          <div className="relative z-10 max-w-3xl mx-auto">
            <h2 className="font-headline text-4xl md:text-5xl font-bold mb-8 text-on_surface">Ready to modernize your farm?</h2>
            <p className="text-on-surface-variant text-lg mb-12">Join thousands of farmers using CropSense to improve their bottom line while staying true to the land.</p>
            <div className="flex flex-wrap justify-center gap-6">
              <button className="bg-primary text-white px-10 py-5 rounded-xl font-bold text-lg hover:shadow-xl transition-all hover:-translate-y-1">Get Started Free</button>
              <button className="bg-transparent text-primary border-2 border-primary px-10 py-5 rounded-xl font-bold text-lg hover:bg-primary/5 transition-all">Request Demo</button>
            </div>
          </div>
          <div className="absolute top-0 left-0 w-full h-full opacity-5 pointer-events-none">
            <div className="grid grid-cols-12 h-full gap-4 rotate-12 scale-150">
              <div className="col-span-1 bg-primary h-full"></div>
              <div className="col-span-2 bg-primary/40 h-full"></div>
              <div className="col-span-1 bg-primary h-full"></div>
              <div className="col-span-3 bg-primary/20 h-full"></div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;
