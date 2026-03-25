'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Settings, Droplet, Newspaper, Sparkles, CheckCircle, AlertCircle, Loader2, Sun, Moon, Clock, Copy, Linkedin } from 'lucide-react';

const PostCard = ({ title, content, isIdea }) => {
  const [copied, setCopied] = useState(false);
  
  const handleCopy = () => {
    navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handlePost = () => {
    // Topmate uses the hidden text parameter to pre-fill the post box directly!
    const linkedInUrl = `https://www.linkedin.com/feed/?shareActive=true&text=${encodeURIComponent(content)}`;
    window.open(linkedInUrl, '_blank');
  };

  return (
    <motion.div 
      whileHover={{ y: -4 }}
      className="glass-card mt-4 transition-all" 
      style={{ 
        background: 'var(--surface)', 
        borderLeft: isIdea ? '4px solid var(--primary)' : '4px solid var(--secondary)',
        boxShadow: '0 4px 6px rgba(0,0,0,0.05)'
      }}
    >
      {title && (
        <h3 className="text-gradient" style={{ borderBottom: '1px solid var(--surface-border)', paddingBottom: '16px', fontSize: '1.25rem' }}>
          {title}
        </h3>
      )}
      <div className={title ? "mt-6" : ""} style={{ color: 'var(--foreground)', opacity: 0.9 }}>
        <pre style={{ whiteSpace: 'pre-wrap', fontType: 'inherit', fontFamily: 'inherit', fontSize: '0.95rem', lineHeight: '1.6' }}>
          {content}
        </pre>
      </div>
      <div className="flex gap-4 mt-6 pt-4" style={{ borderTop: '1px solid var(--surface-border)' }}>
        <button onClick={handleCopy} className="btn-secondary" style={{ flex: 1, justifyContent: 'center' }}>
          {copied ? <CheckCircle size={16} color="var(--success)" /> : <Copy size={16} />}
          {copied ? 'Copied!' : 'Copy Text'}
        </button>
        <button onClick={handlePost} className="btn-primary" style={{ flex: 1, justifyContent: 'center' }}>
          <Linkedin size={16} />
          Post to LinkedIn
        </button>
      </div>
    </motion.div>
  );
};


export default function Home() {
  const [activeTab, setActiveTab] = useState('posts'); // ceo, posts, ideas
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState({ ceo: null, posts: null, ideas: null });
  const [availableDates, setAvailableDates] = useState([]);
  const [selectedDate, setSelectedDate] = useState(null);
  const [error, setError] = useState(null);
  const [theme, setTheme] = useState('dark');

  const fetchCache = async (date = null) => {
    try {
      const url = date ? `/api/cache?date=${date}` : '/api/cache';
      const res = await fetch(url);
      const data = await res.json();
      
      setResults({
        ceo: data.ceo?.data || data.ceo?.posts || null, // Handle both old and new formats
        posts: data.posts?.data || null,
        ideas: data.ideas?.data || null
      });
      
      if (data.availableDates) setAvailableDates(data.availableDates);
      if (data.selectedDate) setSelectedDate(data.selectedDate);
    } catch (err) {
      console.error("Failed to load cache:", err);
    }
  };

  useEffect(() => {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'light') {
      setTheme('light');
      document.body.classList.add('light-theme');
    }
    fetchCache();
  }, []);

  const toggleTheme = () => {
    const newTheme = theme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
    localStorage.setItem('theme', newTheme);
    if (newTheme === 'light') document.body.classList.add('light-theme');
    else document.body.classList.remove('light-theme');
  };

  const triggerWorkflow = async () => {
    setLoading(true); 
    setError(null);
    try {
      const res = await fetch('/api/trigger', { method: "POST" });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Failed to trigger workflow');
      setTriggeringStatus('starting');
      pollWorkflowStatus();
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  const [triggeringStatus, setTriggeringStatus] = useState(null);

  const pollWorkflowStatus = async () => {
    let progress = 0;
    const progressInterval = setInterval(() => {
      progress += 1;
      if (progress >= 100) {
        clearInterval(progressInterval);
        setTriggeringStatus('completed');
        setLoading(false);
        fetchCache(); // Refresh without full reload
      }
    }, 600);
  };

  return (
    <div className="flex-col min-h-screen py-8 gap-8">
      {/* Header */}
      <header className="flex justify-between items-center mb-8 animate-fade-in">
        <div>
          <h1 className="text-gradient hover:scale-105 transition-transform" style={{ cursor: 'pointer' }}>Content Generator</h1>
          <p style={{ color: 'var(--primary)', fontWeight: '500' }}>Vitti Capital AI Dashboard</p>
        </div>
        <div className="flex gap-4 items-center">
          {/* Date Selector */}
          <div className="flex items-center gap-2 glass-card py-2 px-4" style={{ borderRadius: '12px' }}>
            <Clock size={16} color="var(--primary)" />
            <select 
              value={selectedDate || ''} 
              onChange={(e) => fetchCache(e.target.value)}
              style={{ background: 'transparent', color: 'var(--foreground)', border: 'none', outline: 'none', cursor: 'pointer', fontSize: '0.9rem' }}
            >
              {availableDates.map(date => (
                <option key={date} value={date} style={{ background: 'var(--surface)' }}>{date === availableDates[0] ? `Today (${date})` : date}</option>
              ))}
            </select>
          </div>
          <button className="btn-secondary" onClick={toggleTheme} aria-label="Toggle Theme">
            {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
          </button>
        </div>
      </header>

      {/* Error Toast */}
      {error && (
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="flex items-center gap-2 p-4 mb-6" style={{ backgroundColor: 'rgba(239, 68, 68, 0.1)', color: 'var(--error)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: '12px' }}>
          <AlertCircle size={20} />
          <p>{error}</p>
        </motion.div>
      )}

      {/* Tabs */}
      <div className="flex gap-4 mb-4 animate-fade-in" style={{ animationDelay: '0.1s' }}>
        <button className={`btn-secondary ${activeTab === 'ceo' ? 'btn-primary' : ''}`} onClick={() => setActiveTab('ceo')}>
          <Newspaper size={18} />
          CEO News
        </button>
        <button className={`btn-secondary ${activeTab === 'posts' ? 'btn-primary' : ''}`} onClick={() => setActiveTab('posts')}>
          <Linkedin size={18} />
          LinkedIn Posts
        </button>
        <button className={`btn-secondary ${activeTab === 'ideas' ? 'btn-primary' : ''}`} onClick={() => setActiveTab('ideas')}>
          <Sparkles size={18} />
          Gen. Ideas
        </button>
      </div>

      {/* Triggering Overlay */}
      <AnimatePresence>
        {loading && triggeringStatus && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="fixed inset-0 z-50 flex items-center justify-center p-6" style={{ background: 'rgba(0,0,0,0.7)', backdropFilter: 'blur(10px)' }}>
            <motion.div initial={{ scale: 0.9, y: 20 }} animate={{ scale: 1, y: 0 }} className="glass-card max-w-md w-full p-8 text-center" style={{ border: '1px solid var(--primary-glow)' }}>
              <Loader2 className="spinner mb-6 mx-auto" size={48} color="var(--primary)" />
              <h2 className="text-gradient mb-2">Generating...</h2>
              <div className="w-full bg-black/20 rounded-full h-2 mb-8 overflow-hidden mt-4">
                <motion.div initial={{ width: '0%' }} animate={{ width: '100%' }} transition={{ duration: 60, ease: "linear" }} className="h-full" style={{ background: 'linear-gradient(90deg, var(--primary), var(--secondary))' }} />
              </div>
              <p className="mt-4 text-xs italic" style={{ opacity: 0.5 }}>Processing your content cloud... Please wait.</p>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Content Area */}
      <div className="glass-card animate-fade-in" style={{ minHeight: '60vh', animationDelay: '0.2s', position: 'relative', overflow: 'hidden' }}>
        <div style={{ position: 'absolute', top: '-10%', right: '-5%', width: '300px', height: '300px', background: 'var(--primary-glow)', filter: 'blur(100px)', zIndex: 0, opacity: 0.4, pointerEvents: 'none' }} />
        
        <AnimatePresence mode="wait">
          {activeTab === 'ceo' && (
            <motion.div key="ceo" initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 10 }} className="flex-col gap-6" style={{ position: 'relative', zIndex: 1 }}>
              <div className="flex justify-between items-center mb-6">
                <div>
                  <h2>Institutional Financial News</h2>
                  <p style={{ opacity: 0.7 }}>Analyzing ASX movements and VC deals for the CEO.</p>
                </div>
                <button className="btn-primary" onClick={triggerWorkflow} disabled={loading}>
                  <Sparkles size={18} /> Run CEO Pipeline
                </button>
              </div>
              {results.ceo ? (
                <div className="grid gap-6">
                  {results.ceo.map((item, idx) => (
                    <PostCard key={idx} title={item.topic || item.headline} content={item.post} isIdea={false} />
                  ))}
                </div>
              ) : <EmptyState icon={<Newspaper size={48}/>} msg="No CEO news logged for this date." />}
            </motion.div>
          )}

          {activeTab === 'posts' && (
            <motion.div key="posts" initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 10 }} className="flex-col gap-6" style={{ position: 'relative', zIndex: 1 }}>
              <div className="flex justify-between items-center mb-6">
                <div>
                  <h2>LinkedIn Drafts</h2>
                  <p style={{ opacity: 0.7 }}>Premium conversational posts generated from your bookmarks.</p>
                </div>
                <button className="btn-primary" onClick={triggerWorkflow} disabled={loading}>
                  <Sparkles size={18} /> Run Raindrop Pipeline
                </button>
              </div>
              {results.posts ? (
                <div className="grid gap-6">
                  {results.posts.map((post, idx) => (
                    <PostCard key={idx} content={post} isIdea={false} />
                  ))}
                </div>
              ) : <EmptyState icon={<Linkedin size={48}/>} msg="No LinkedIn posts logged for this date." />}
            </motion.div>
          )}

          {activeTab === 'ideas' && (
            <motion.div key="ideas" initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 10 }} className="flex-col gap-6" style={{ position: 'relative', zIndex: 1 }}>
              <div className="flex justify-between items-center mb-6">
                <div>
                  <h2>Content Concepts & Ideas</h2>
                  <p style={{ opacity: 0.7 }}>Creative hooks and strategies for future engagement.</p>
                </div>
                <button className="btn-primary" onClick={triggerWorkflow} disabled={loading}>
                  <Sparkles size={18} /> Run Raindrop Pipeline
                </button>
              </div>
              {results.ideas ? (
                <div className="grid gap-6">
                  {results.ideas.map((idea, idx) => (
                    <PostCard key={idx} content={idea} isIdea={true} />
                  ))}
                </div>
              ) : <EmptyState icon={<Sparkles size={48}/>} msg="No ideas logged for this date." />}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}

const EmptyState = ({ icon, msg }) => (
  <div className="py-20 text-center flex-col items-center gap-4" style={{ background: 'rgba(255,255,255,0.03)', borderRadius: '24px', border: '1px dashed var(--surface-border)' }}>
    <div style={{ opacity: 0.3 }}>{icon}</div>
    <p style={{ opacity: 0.5, fontSize: '1.1rem' }}>{msg}</p>
  </div>
);
