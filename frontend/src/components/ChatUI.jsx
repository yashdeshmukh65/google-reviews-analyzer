import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Send, Search, Loader2, BarChart2, AlertCircle, MessageSquare, Database, FileSpreadsheet, BrainCircuit } from 'lucide-react';
import Plot from 'react-plotly.js';
import Sentiment from 'sentiment';

// Common Vite/CommonJS mapping interoperability bugfix
const PlotComponent = Plot.default || Plot;

class ErrorBoundary extends React.Component {
  constructor(props) { super(props); this.state = { hasError: false, error: null, info: null }; }
  static getDerivedStateFromError(error) { return { hasError: true, error }; }
  componentDidCatch(error, info) { this.setState({ info }); console.error(error, info); }
  render() {
    if (this.state.hasError) {
      return (
        <div className="flex flex-col h-screen w-full items-center justify-center bg-slate-950 text-red-400 font-mono p-10">
          <AlertCircle className="w-16 h-16 mb-6 text-red-500" />
          <h1 className="text-3xl font-bold mb-2">Fatal React Exception</h1>
          <div className="bg-red-950/50 p-6 rounded-xl border border-red-800 max-w-4xl w-full">
            <pre className="whitespace-pre-wrap text-sm">{this.state.error?.toString()}</pre>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export default function ChatUI() {
  const [url, setUrl] = useState('');
  const [scrapeLimit, setScrapeLimit] = useState(100);
  const [activeTab, setActiveTab] = useState('scrape');
  const [uploadFile, setUploadFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isScraping, setIsScraping] = useState(false);
  const [scrapeStatus, setScrapeStatus] = useState('');
  
  const [globalData, setGlobalData] = useState([]);
  const [showDashboard, setShowDashboard] = useState(false);
  const [dashboardMode, setDashboardMode] = useState('executive'); // 'executive' or 'insights'
  const [advancedData, setAdvancedData] = useState(null);
  const [llmInsights, setLlmInsights] = useState(null);
  const [isInsightsLoading, setIsInsightsLoading] = useState(false);

  const [messages, setMessages] = useState([
    { role: 'assistant', content: "Welcome to ReviewAI. Connect a Google Maps link or upload an offline CSV to begin extracting intelligence." }
  ]);
  const [inputVal, setInputVal] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  
  const chatEndRef = useRef(null);
  
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const loadAdvancedInsights = async () => {
      setDashboardMode('insights');
      if (advancedData) return; 
      
      setIsInsightsLoading(true);
      const activeUrl = globalData[0]?.business_url || url || uploadFile?.name || "Uploaded_CSV";
      try {
          const advRes = await axios.get(`${API_BASE}/advanced_data?url=${encodeURIComponent(activeUrl)}`);
          setAdvancedData(advRes.data);
          
          try {
              const llmRes = await axios.post(`${API_BASE}/insights`, { url: activeUrl, limit: 100 });
              setLlmInsights(llmRes.data);
          } catch(e) { console.error("LLM Insights fail", e); }
      } catch(e) {
          console.error("Advanced Data fail", e);
      }
      setIsInsightsLoading(false);
  };

  const handleUpload = async () => {
    if (!uploadFile) return;
    setIsUploading(true);
    setAdvancedData(null);
    setMessages(prev => [...prev, { role: 'user', content: `Uploaded file: ${uploadFile.name}` }]);
    setMessages(prev => [...prev, { role: 'assistant', content: 'Processing CSV matrix traversing NLP Pipelines...' }]);
    try {
      const formData = new FormData();
      formData.append("file", uploadFile);
      const res = await axios.post(`${API_BASE}/upload`, formData);
      if (res.data.status === "completed") {
         const dataRes = await axios.get(`${API_BASE}/data?url=${encodeURIComponent(res.data.url)}`);
         if (dataRes.data && dataRes.data.length > 0) {
            setGlobalData(dataRes.data);
            setShowDashboard(false);
            setDashboardMode('executive');
            setMessages(prev => [...prev, {
               role: 'assistant',
               content: `✅ Successfully compiled ${dataRes.data.length} records into the memory bank! Click the prominent "Analyze Data" button in the right viewport to command the visualization matrix.`,
            }]);
         }
      } else {
         setMessages(prev => [...prev, { role: 'assistant', content: `Upload failed: ${res.data.error || "Corrupted payload."}` }]);
      }
    } catch (err) {
      setMessages(prev => [...prev, { role: 'assistant', content: `Upload error: ${err.message}` }]);
    }
    setIsUploading(false);
  };

  const handleScrape = async () => {
    if (!url) return;
    setIsScraping(true);
    setAdvancedData(null);
    setScrapeStatus(`Initializing remote scrape sequence for ${scrapeLimit} nodes...`);
    
    try {
      await axios.post(`${API_BASE}/scrape`, { url, limit: scrapeLimit });
      setScrapeStatus(`Scraping active. Harvesting nodes and engaging NLP engines...`);
      
      let attempts = 0;
      const pollData = setInterval(async () => {
        attempts++;
        if (attempts > 50) { 
          clearInterval(pollData);
          setScrapeStatus('Scraper latency timeout. Attempt offline CSV mode instead.');
          setIsScraping(false);
          return;
        }
        try {
          const statusRes = await axios.get(`${API_BASE}/status?url=${encodeURIComponent(url)}`);
          if (statusRes.data && ['completed', 'failed'].includes(statusRes.data.status)) {
            clearInterval(pollData);
            if (statusRes.data.status === 'failed') {
               setScrapeStatus('Remote Google Maps block triggered. Halting scrape.');
               setIsScraping(false);
               return;
            }
            const res = await axios.get(`${API_BASE}/data?url=${encodeURIComponent(url)}`);
            if (res.data && res.data.length > 0) {
              setScrapeStatus('');
              setIsScraping(false);
              setGlobalData(res.data);
              setShowDashboard(false);
              setDashboardMode('executive');
              setMessages(prev => [...prev, { role: 'assistant', content: `✅ Extracted ${res.data.length} LIVE reviews! The data is primed. Click "Analyze Data" in the right dashboard interface to view the metrics.` }]);
            } else {
               setScrapeStatus('Extraction finished but yielded 0 valid reviews.');
               setIsScraping(false);
            }
          }
        } catch (e) { console.warn("Polling dropped", e); }
      }, 3000);
    } catch (err) {
      setScrapeStatus('Network refusal. Target offline.');
      setIsScraping(false);
    }
  };

  const handleSend = async () => {
    if (!inputVal.trim()) return;
    const userMsg = inputVal.trim();
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setInputVal('');
    setIsTyping(true);
    
    try {
      const activeUrl = globalData[0]?.business_url || url || uploadFile?.name || "Uploaded_CSV";
      const { data } = await axios.post(`${API_BASE}/chat`, { query: userMsg, url: activeUrl });
      const assistantMsg = {
        role: 'assistant',
        content: data.answer,
        chartData: getChartData(data.graph, data.data),
        rawData: data.data
      };
      setMessages(prev => [...prev, assistantMsg]);
    } catch (err) {
      const errMsg = err.response?.data?.detail || err.message || "Unknown error";
      setMessages(prev => [...prev, { role: 'assistant', content: `Oops! Query failed: ${errMsg}` }]);
    } finally {
      setIsTyping(false);
    }
  };
  
  const generateDashboardCharts = (data) => {
    if (!data || data.length === 0) return null;

    const ratingsCount = {1:0, 2:0, 3:0, 4:0, 5:0};
    data.forEach(r => { const rounded = Math.round(r.rating) || 1; if(ratingsCount[rounded] !== undefined) ratingsCount[rounded]++; });
    const ratingDist = [{ x: ['1 Star', '2 Stars', '3 Stars', '4 Stars', '5 Stars'], y: Object.values(ratingsCount), type: 'bar', marker: { color: ['#ef4444', '#f97316', '#eab308', '#84cc16', '#22c55e'] } }];

    const sentimentCount = { "Positive": 0, "Negative": 0, "Neutral": 0 };
    data.forEach(r => { 
       const sent = r.sentiment || "Neutral";
       if(sentimentCount[sent] !== undefined) sentimentCount[sent]++; 
    });
    const sentimentPie = [{ labels: Object.keys(sentimentCount), values: Object.values(sentimentCount), type: 'pie', hole: 0.5, marker: { colors: ['#22c55e', '#ef4444', '#64748b'] } }];

    const sentimentRatings = { "Positive": [], "Negative": [], "Neutral": [] };
    data.forEach(r => { 
        const sent = r.sentiment || "Neutral";
        if(sentimentRatings[sent]) sentimentRatings[sent].push(r.rating); 
    });
    const avgSentRatings = Object.keys(sentimentRatings).map(k => sentimentRatings[k].length ? (sentimentRatings[k].reduce((a,b)=>a+b,0)/sentimentRatings[k].length).toFixed(2) : 0);
    const avgSentChart = [{ x: Object.keys(sentimentRatings), y: avgSentRatings, type: 'bar', marker: { color: ['#22c55e', '#ef4444', '#64748b'] } }];

    const lengthByRating = {1:[], 2:[], 3:[], 4:[], 5:[]};
    data.forEach(r => { 
        const rounded = Math.round(r.rating) || 1; 
        if(lengthByRating[rounded]) lengthByRating[rounded].push((r.review_text || "").length); 
    });
    const avgLength = Object.values(lengthByRating).map(arr => arr.length ? Math.round(arr.reduce((a,b)=>a+b,0)/arr.length) : 0);
    const lengthChart = [{ x: ['1 Star', '2 Stars', '3 Stars', '4 Stars', '5 Stars'], y: avgLength, type: 'scatter', mode: 'lines+markers', marker: { color: '#3b82f6', size: 12, line: {color: '#60a5fa', width: 2} }, line: {color: '#3b82f6', width: 3} }];

    const words = {};
    const stopWords = ['the','and','to','a','was','is','of','it','in','for','that','i','this','but','they','with','on','you','have','we','are','so','not','very','my','as','at','be','had','food','place','good','great','service', 'there', 'were', 'which', 'just', 'like', 'can'];
    data.forEach(r => {
        (r.review_text || "").toLowerCase().replace(/[^a-z\s]/g, '').split(/\s+/).forEach(w => {
            if (w.length > 3 && !stopWords.includes(w)) { words[w] = (words[w] || 0) + 1; }
        });
    });
    const topWords = Object.entries(words).sort((a,b) => b[1] - a[1]).slice(0, 5);
    const topWordsChart = [{ x: topWords.map(w => w[0]), y: topWords.map(w => w[1]), type: 'bar', marker: { color: '#8b5cf6', borderRadius: 4 } }];

    const sentimentLine = [];
    ['Positive', 'Negative', 'Neutral'].forEach((sent, idx) => {
        const counts = [0, 0, 0, 0, 0];
        data.forEach(r => { 
            if((r.sentiment || "Neutral") === sent) { counts[(Math.round(r.rating)||1)-1]++; } 
        });
        sentimentLine.push({ x: ['1 Star', '2 Stars', '3 Stars', '4 Stars', '5 Stars'], y: counts, name: sent, type: 'bar', marker: { color: ['#22c55e', '#ef4444', '#64748b'][idx] } });
    });

    return [
       { title: "Sentiment Breakdown", data: sentimentPie, layoutParams: {} },
       { title: "Global Rating Distribution", data: ratingDist, layoutParams: {} },
       { title: "Avg Rating per Sentiment Classifier", data: avgSentChart, layoutParams: {} },
       { title: "Correlation: Review Text Length vs Stars", data: lengthChart, layoutParams: {} },
       { title: "Primary Lexical Drivers (Top 5)", data: topWordsChart, layoutParams: {} },
       { title: "Compound Sentiment Decomposition", data: sentimentLine, layoutParams: { barmode: 'stack' } }
    ];
  };

  const generateAdvancedCharts = () => {
     if (!advancedData) return [];
     
     // Aspect Sentiment Overview
     const aspectCounts = {}; // { food: { pos: 0, neg: 0 } }
     advancedData.aspects?.forEach(a => {
        if (!aspectCounts[a.aspect]) aspectCounts[a.aspect] = { Positive: 0, Negative: 0, Neutral: 0 };
        aspectCounts[a.aspect][a.sentiment_score]++;
     });
     
     const aspectLabels = Object.keys(aspectCounts);
     const aspectChartData = [];
     ['Positive', 'Negative', 'Neutral'].forEach((sent, idx) => {
        aspectChartData.push({
           x: aspectLabels, 
           y: aspectLabels.map(l => aspectCounts[l][sent]), 
           name: sent, type: 'bar', 
           marker: { color: ['#22c55e', '#ef4444', '#64748b'][idx] }
        });
     });

     // Time-Series Anomalies (Rating vs Volume per Month)
     const timeMap = {}; // { '2023-10': { totalRating: 0, count: 0 } }
     globalData.forEach(r => {
        let period = 'Unknown';
        if (r.date && r.date !== 'Unknown') {
            const parsed = new Date(r.date);
            if (!isNaN(parsed)) period = `${parsed.getFullYear()}-${String(parsed.getMonth()+1).padStart(2,'0')}`;
        }
        if (!timeMap[period]) timeMap[period] = { total: 0, count: 0 };
        timeMap[period].total += r.rating;
        timeMap[period].count++;
     });
     // Sort periods
     const sortedPeriods = Object.keys(timeMap).sort().filter(p => p !== 'Unknown');
     const counts = sortedPeriods.map(p => timeMap[p].count);
     const ratings = sortedPeriods.map(p => (timeMap[p].total / timeMap[p].count).toFixed(2));
     
     const timeChart = [
        { x: sortedPeriods, y: counts, name: 'Volume', type: 'scatter', mode: 'lines+markers', marker: {color: '#8b5cf6'}, yaxis: 'y' },
        { x: sortedPeriods, y: ratings, name: 'Avg Rating', type: 'scatter', mode: 'lines', marker: {color: '#10b981'}, yaxis: 'y2' }
     ];

     return [
        { title: "Aspect-Based Sentiment Decomposition", data: aspectChartData, layoutParams: { barmode: 'group' } },
        { title: "Volume vs Rating Stability (Anomalies over Time)", data: timeChart, layoutParams: { yaxis2: { overlaying: 'y', side: 'right', gridcolor: 'transparent' } } }
     ];
  };

  const getChartData = (graphInfo, rawData) => {
      if (!graphInfo || !graphInfo.requires_graph || !rawData || rawData.length === 0) return null;
      const keys = Object.keys(rawData[0]);
      if (keys.length < 2) return null; 
      let x = [], y = [];
      rawData.forEach(row => { x.push(row[keys[0]]); y.push(row[keys[1]]); });
      if (graphInfo.chart_type === 'pie') {
          return [{ labels: x, values: y, type: 'pie', hole: 0.4, marker: { colors: ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444', '#ec4899', '#14b8a6'] } }];
      }
      return [{ x: x, y: y, type: graphInfo.chart_type === 'bar' ? 'bar' : 'scatter', mode: graphInfo.chart_type === 'line' ? 'lines+markers' : 'none', marker: { color: '#6366f1' } }];
  };

  const downloadCSV = (data, filename) => {
    if (!data || data.length === 0) return;
    const keys = Object.keys(data[0]);
    const csvContent = [ keys.join(','), ...data.map(row => keys.map(k => `"${String(row[k]).replace(/"/g, '""')}"`).join(',')) ].join('\n'); 
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.setAttribute("download", filename + ".csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };
  
  return (
    <ErrorBoundary>
      <div className="flex flex-col lg:flex-row h-screen w-full bg-[#0a0f1c] text-slate-100 font-sans overflow-hidden">
        
        {/* LEFT PANEL | Control & Chat */}
        <div className="w-full lg:w-[480px] xl:w-[500px] h-[55vh] lg:h-screen flex flex-col border-b lg:border-b-0 lg:border-r border-slate-800/80 bg-[#0f1525] shadow-2xl relative z-20 flex-shrink-0">
          <div className="px-6 py-5 bg-gradient-to-b from-[#151c2e] to-[#0f1525] border-b border-slate-800/60 flex items-center justify-between">
             <div className="flex items-center gap-3">
                 <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-500 to-indigo-500 flex items-center justify-center shadow-lg shadow-blue-500/30">
                    <Database className="w-5 h-5 text-white" />
                 </div>
                 <div>
                    <h1 className="text-xl font-bold tracking-tight text-white leading-tight">Review<span className="text-blue-400">AI</span></h1>
                    <p className="text-[10px] text-slate-400 font-semibold uppercase tracking-wider">Enterprise Intelligence Engine</p>
                 </div>
             </div>
          </div>
          <div className="px-6 py-5 border-b border-slate-800/60 bg-[#121827]">
             <div className="flex bg-[#0a0f1c] rounded-xl p-1 mb-4 border border-slate-800 shadow-inner">
               <button onClick={() => setActiveTab('scrape')} className={`flex-1 py-2 text-xs font-bold rounded-lg transition-all flex justify-center items-center gap-2 ${activeTab==='scrape' ? 'bg-indigo-600 text-white shadow-md' : 'text-slate-400 hover:text-slate-200'}`}><Search className="w-3 h-3"/> Web Scraper</button>
               <button onClick={() => setActiveTab('upload')} className={`flex-1 py-2 text-xs font-bold rounded-lg transition-all flex justify-center items-center gap-2 ${activeTab==='upload' ? 'bg-blue-600 text-white shadow-md' : 'text-slate-400 hover:text-slate-200'}`}><FileSpreadsheet className="w-3 h-3"/> Data Upload</button>
             </div>
             {activeTab === 'scrape' ? (
                <div className="flex gap-2">
                   <input type="text" value={url} onChange={(e) => setUrl(e.target.value)} placeholder="Target URL..." className="flex-1 bg-[#1a2133] border border-slate-700 text-sm py-2.5 px-4 rounded-xl focus:outline-none focus:ring-1 focus:ring-indigo-500 transition-all font-medium placeholder-slate-500"/>
                   <input type="number" value={scrapeLimit} onChange={(e) => setScrapeLimit(Number(e.target.value))} className="w-20 bg-[#1a2133] border border-slate-700 text-sm py-2.5 px-3 rounded-xl focus:outline-none focus:ring-1 focus:ring-indigo-500 text-center"/>
                   <button onClick={handleScrape} disabled={isScraping || !url} className="bg-indigo-600 hover:bg-indigo-500 p-2.5 rounded-xl disabled:opacity-50 transition-all shadow-lg active:scale-95 text-white">
                      {isScraping ? <Loader2 className="w-5 h-5 animate-spin"/> : <Search className="w-5 h-5"/>}
                   </button>
                </div>
             ) : (
                <div className="flex gap-2">
                   <input type="file" accept=".csv" onChange={(e) => setUploadFile(e.target.files[0])} className="flex-1 bg-[#1a2133] border border-slate-700 text-xs p-2 rounded-xl text-slate-300 file:bg-[#252f47] file:text-indigo-300 file:border-0 file:px-3 file:py-1 file:rounded-lg file:mr-3 hover:file:bg-[#2e3a57] transition-all cursor-pointer"/>
                   <button onClick={handleUpload} disabled={isUploading || !uploadFile} className="bg-blue-600 hover:bg-blue-500 px-5 rounded-xl disabled:opacity-50 transition-all shadow-lg text-white">
                      {isUploading ? <Loader2 className="w-5 h-5 animate-spin"/> : <Send className="w-5 h-5"/>}
                   </button>
                </div>
             )}
             {scrapeStatus && <p className="mt-3 text-[11px] font-semibold text-indigo-400 tracking-wide text-center animate-pulse">{scrapeStatus}</p>}
          </div>
          <div className="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-thin scrollbar-thumb-slate-700">
             {messages.map((msg, i) => (
                <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-in slide-in-from-bottom-2`}>
                   <div className={`max-w-[90%] md:max-w-[85%] rounded-2xl p-4 ${msg.role === 'user' ? 'bg-blue-600 text-white rounded-br-sm shadow-md' : 'bg-[#1e273a] text-slate-200 border border-slate-700/60 rounded-bl-sm shadow-xl'} text-[14px] leading-relaxed font-medium`}>
                      {msg.content}
                      {msg.chartData && (
                         <div className="mt-4 bg-[#111724] rounded-xl p-3 border border-slate-700/50 shadow-inner">
                            <div className="flex justify-between items-center mb-2 px-1"><span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">AI Insight Render</span></div>
                            <PlotComponent data={msg.chartData} layout={{ autosize: true, paper_bgcolor: 'transparent', plot_bgcolor: 'transparent', font: { color: '#94a3b8' }, margin: { t: 5, r: 5, l: 30, b: 20 }, xaxis: { gridcolor: '#1e293b' }, yaxis: { gridcolor: '#1e293b' } }} useResizeHandler={true} style={{width: "100%", height: "200px"}} config={{displayModeBar: false}} />
                         </div>
                      )}
                   </div>
                </div>
             ))}
             {isTyping && (
               <div className="flex justify-start"><div className="bg-[#1e273a] border border-slate-700/60 text-slate-400 rounded-2xl rounded-bl-sm p-4 flex items-center gap-3 shadow-xl"><Loader2 className="w-4 h-4 animate-spin text-blue-400" /><span className="text-[13px] font-semibold">Correlating matrix sequences...</span></div></div>
             )}
             <div ref={chatEndRef} className="h-1" />
          </div>
          <div className="p-5 bg-gradient-to-t from-[#0f1525] to-transparent pt-8">
            <form onSubmit={(e) => { e.preventDefault(); handleSend(); }} className="relative flex items-center">
              <MessageSquare className="absolute left-4 w-5 h-5 text-slate-500" />
              <input type="text" value={inputVal} onChange={(e) => setInputVal(e.target.value)} placeholder="Interrogate the underlying data..." className="w-full bg-[#1a2233] border border-slate-700/80 rounded-2xl py-3.5 pl-12 pr-14 text-white placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-blue-500 shadow-inner text-sm"/>
              <button type="submit" disabled={!inputVal.trim() || isTyping} className="absolute right-2 p-2 bg-blue-500 hover:bg-blue-400 text-white rounded-xl disabled:bg-slate-700 transition-all shadow-md"><Send className="w-4 h-4" /></button>
            </form>
          </div>
        </div>

        {/* RIGHT PANEL | Executive Dashboard Canvas */}
        <div className="flex-1 h-[45vh] lg:h-screen overflow-y-auto bg-[#050811] relative scrollbar-thin scrollbar-thumb-slate-800 p-6 lg:p-12">
           {!showDashboard ? (
               <div className="h-full flex flex-col items-center justify-center text-center max-w-lg mx-auto">
                   <div className="w-24 h-24 bg-slate-900/50 rounded-full flex items-center justify-center border border-slate-800/80 mb-8 shadow-2xl"><BarChart2 className="w-10 h-10 text-slate-600" /></div>
                   <h2 className="text-3xl font-extrabold text-transparent bg-clip-text bg-gradient-to-br from-slate-200 to-slate-500 mb-3">No Analytics Rendered</h2>
                   <p className="text-slate-500 text-[15px] leading-relaxed mb-10 font-medium">Link a Google Maps target or upload raw CSV coordinates to compile an enterprise-grade visual taxonomy layout.</p>
                   {globalData.length > 0 && (
                      <button onClick={() => setShowDashboard(true)} className="px-10 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 font-extrabold rounded-2xl shadow-xl transition-all flex items-center gap-3">
                         <BarChart2 className="w-6 h-6" /> Deploy Visualization Matrix
                      </button>
                   )}
               </div>
           ) : (
               <div className="max-w-7xl mx-auto animate-in slide-in-from-bottom-6 duration-700 ease-out pb-20">
                  <div className="flex flex-col md:flex-row md:items-end justify-between mb-8 pb-6 border-b border-white/5">
                     <div>
                        <h2 className="text-3xl lg:text-4xl font-black text-white tracking-tight leading-tight mb-2">Executive Interface.</h2>
                        <p className="text-slate-400 text-sm font-semibold tracking-wide uppercase">Operational Canvas reading <span className="text-blue-400 font-bold">{globalData.length}</span> verified entities.</p>
                     </div>
                     <div className="flex gap-3 mt-5 md:mt-0">
                        <button onClick={() => { setDashboardMode('executive'); }} className={`px-5 py-2.5 text-xs font-extrabold tracking-wider uppercase rounded-xl border transition-all shadow-lg flex items-center gap-2 ${dashboardMode === 'executive' ? 'bg-blue-600 border-blue-500/50 text-white' : 'bg-[#151d2d] border-blue-500/20 text-blue-400 hover:bg-[#1c263b] hover:text-blue-300'}`}>
                           <BarChart2 className="w-4 h-4"/> Core Data
                        </button>
                        <button onClick={loadAdvancedInsights} className={`px-5 py-2.5 text-xs font-extrabold tracking-wider uppercase rounded-xl border transition-all shadow-lg flex items-center gap-2 ${dashboardMode === 'insights' ? 'bg-fuchsia-600 border-fuchsia-500/50 text-white' : 'bg-[#1d152d] border-fuchsia-500/20 text-fuchsia-400 hover:bg-[#2d1d3d] hover:text-fuchsia-300'}`}>
                           {isInsightsLoading ? <Loader2 className="w-4 h-4 animate-spin"/> : <BrainCircuit className="w-4 h-4"/>} AI Insights
                        </button>
                        <button onClick={() => downloadCSV(globalData, 'System_Export')} className="px-5 py-2.5 bg-[#151d2d] hover:bg-[#1c263b] text-slate-400 hover:text-slate-300 text-xs font-extrabold tracking-wider uppercase rounded-xl border border-slate-500/20 transition-all shadow-lg flex items-center gap-2">
                           Registry
                        </button>
                     </div>
                  </div>

                  {dashboardMode === 'executive' ? (
                      <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
                          {generateDashboardCharts(globalData)?.map((chart, i) => (
                             <div key={i} className="bg-[#0f1525] border border-white/5 rounded-3xl p-7 shadow-2xl hover:border-blue-500/30 hover:shadow-blue-500/5 transition-all duration-300 group">
                                <h3 className="text-[12px] font-black text-slate-300 uppercase tracking-[0.2em] mb-8 flex items-center gap-3"><div className="w-1.5 h-1.5 rounded-full bg-blue-500 group-hover:scale-[2.5] transition-all"/>{chart.title}</h3>
                                <div className="w-full h-[340px]">
                                   <PlotComponent data={chart.data} layout={{ autosize: true, paper_bgcolor: 'transparent', plot_bgcolor: 'transparent', font: { color: '#64748b', family: 'Inter' }, margin: { t: 0, r: 0, l: 35, b: 35 }, xaxis: { gridcolor: '#1e293b' }, yaxis: { gridcolor: '#1e293b' }, showlegend: chart.title.includes("Decomposition") || chart.title.includes("Breakdown"), legend: { orientation: "h", y: -0.15, font: {size: 11, color: '#94a3b8'} }, ...chart.layoutParams }} useResizeHandler={true} style={{width: "100%", height: "100%"}} config={{displayModeBar: false}} />
                                </div>
                             </div>
                          ))}
                      </div>
                  ) : (
                      <div className="space-y-8 animate-in slide-in-from-right-8 duration-500">
                          {/* Groq AI Executive LLM Summary */}
                          <div className="bg-gradient-to-br from-[#1b1429] to-[#0f1525] border border-fuchsia-500/30 rounded-3xl p-8 shadow-2xl shadow-fuchsia-900/10">
                              <h3 className="text-[12px] font-black text-fuchsia-400 uppercase tracking-[0.2em] mb-6 flex items-center gap-3"><BrainCircuit className="w-4 h-4"/> AI Executive Anomaly Synthesis</h3>
                              {isInsightsLoading ? (
                                  <div className="flex flex-col items-center justify-center py-10 opacity-50"><Loader2 className="w-8 h-8 animate-spin text-fuchsia-500 mb-4"/><p className="text-sm font-semibold tracking-wider uppercase">Interrogating Cognitive Models...</p></div>
                              ) : (
                                  <ul className="space-y-4 pl-2">
                                      {llmInsights?.insights?.map((ins, idx) => (
                                          <li key={idx} className="flex gap-4 items-start bg-black/20 p-4 rounded-xl border border-white/5"><div className="mt-1 w-2 h-2 rounded-full bg-fuchsia-500 flex-shrink-0"/><p className="text-slate-200 leading-relaxed font-medium">{ins}</p></li>
                                      ))}
                                  </ul>
                              )}
                          </div>
                          
                          {/* Python ML Generated Word Clouds */}
                          <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
                             <div className="bg-[#0f1525] border border-emerald-500/20 rounded-3xl p-7 shadow-2xl group">
                                <h3 className="text-[12px] font-black text-emerald-400 uppercase tracking-[0.2em] mb-4">Positive Lexicon Drivers</h3>
                                <p className="text-xs text-slate-500 mb-6 font-medium">Rendered via Python Tfidf ML Image Buffer</p>
                                <div className="w-full flex justify-center bg-[#0a0f1c] rounded-2xl overflow-hidden border border-white/5 h-[340px]">
                                   {isInsightsLoading ? <Loader2 className="w-8 h-8 animate-spin mt-20 opacity-20"/> : (advancedData?.pos_wordcloud ? <img src={`data:image/png;base64,${advancedData.pos_wordcloud}`} className="w-full h-full object-cover" alt="Positive Words"/> : <div className="text-slate-600 mt-20 font-bold">Insufficient Positive Nodes</div>)}
                                </div>
                             </div>
                             <div className="bg-[#0f1525] border border-rose-500/20 rounded-3xl p-7 shadow-2xl group">
                                <h3 className="text-[12px] font-black text-rose-400 uppercase tracking-[0.2em] mb-4">Negative Lexicon Drivers</h3>
                                <p className="text-xs text-slate-500 mb-6 font-medium">Rendered via Python Tfidf ML Image Buffer</p>
                                <div className="w-full flex justify-center bg-[#0a0f1c] rounded-2xl overflow-hidden border border-white/5 h-[340px]">
                                   {isInsightsLoading ? <Loader2 className="w-8 h-8 animate-spin mt-20 opacity-20"/> : (advancedData?.neg_wordcloud ? <img src={`data:image/png;base64,${advancedData.neg_wordcloud}`} className="w-full h-full object-cover" alt="Negative Words"/> : <div className="text-slate-600 mt-20 font-bold">Insufficient Negative Nodes</div>)}
                                </div>
                             </div>
                          </div>

                          <div className="grid grid-cols-1 gap-8">
                              {generateAdvancedCharts().map((chart, i) => (
                                <div key={i} className="bg-[#0f1525] border border-white/5 rounded-3xl p-7 shadow-2xl transition-all duration-300 group">
                                   <h3 className="text-[12px] font-black text-slate-300 uppercase tracking-[0.2em] mb-8 flex items-center gap-3"><div className="w-1.5 h-1.5 rounded-full bg-blue-500"/>{chart.title}</h3>
                                   <div className="w-full h-[350px]">
                                      <PlotComponent data={chart.data} layout={{ autosize: true, paper_bgcolor: 'transparent', plot_bgcolor: 'transparent', font: { color: '#64748b' }, margin: { t: 0, r: 0, l: 35, b: 35 }, xaxis: { gridcolor: '#1e293b' }, yaxis: { gridcolor: '#1e293b' }, ...chart.layoutParams }} useResizeHandler={true} style={{width: "100%", height: "100%"}} config={{displayModeBar: false}} />
                                   </div>
                                </div>
                              ))}
                          </div>
                      </div>
                  )}

               </div>
           )}
        </div>
      </div>
    </ErrorBoundary>
  );
}
