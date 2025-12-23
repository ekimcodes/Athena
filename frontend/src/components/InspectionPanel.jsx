import React, { useState, useRef } from 'react';
import axios from 'axios';
import { AlertTriangle, CheckCircle, Webcam, Activity, X } from 'lucide-react';
import clsx from 'clsx';

export default function InspectionPanel({ hotspot, onClose }) {
    const [imageInfo, setImageInfo] = useState(null);
    const [analysis, setAnalysis] = useState(null);
    const [loading, setLoading] = useState(false);
    const [imageDims, setImageDims] = useState({ w: 0, h: 0 });

    // Reset state when selecting a new hotspot
    React.useEffect(() => {
        setImageInfo(null);
        setAnalysis(null);
        setLoading(false);
    }, [hotspot?.id]);

    const handleSimulate = async () => {
        setLoading(true);
        setAnalysis(null);
        try {
            const res = await axios.get('/api/v1/inspect/random');
            setImageInfo(res.data);
            setLoading(false);
        } catch (err) {
            console.error(err);
            setLoading(false);
        }
    };

    const handleAnalyze = async () => {
        if (!imageInfo) return;
        setLoading(true);
        try {
            const res = await axios.post('/api/v1/inspect/analyze', {
                image_id: imageInfo.image_id
            });
            setAnalysis(res.data);
            setLoading(false);
        } catch (err) {
            console.error(err);
            setLoading(false);
        }
    };

    const onImageLoad = (e) => {
        setImageDims({
            w: e.target.naturalWidth,
            h: e.target.naturalHeight
        });
    };

    if (!hotspot) {
        return (
            <div className="p-6 text-slate-400 text-center">
                <Activity className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>Select a Hotspot on the map to begin inspection.</p>
            </div>
        );
    }

    return (
        <div className="bg-slate-800 text-slate-100 h-full flex flex-col shadow-2xl overflow-y-auto">
            {/* Header */}
            <div className="p-4 border-b border-slate-700 flex justify-between items-center bg-slate-900">
                <div>
                    <h2 className="text-lg font-bold text-white flex items-center gap-2">
                        <AlertTriangle className={clsx("w-5 h-5", {
                            'text-red-500': hotspot.risk_level === 'CRITICAL',
                            'text-yellow-500': hotspot.risk_level === 'MODERATE',
                            'text-green-500': hotspot.risk_level === 'LOW'
                        })} />
                        Hotspot #{hotspot.id}
                    </h2>
                    <span className="text-xs text-slate-400 uppercase tracking-wider">{hotspot.risk_level} RISK</span>
                </div>
                <button onClick={onClose} className="p-1 hover:bg-slate-700 rounded transition">
                    <X className="w-5 h-5" />
                </button>
            </div>

            {/* Content */}
            <div className="p-4 space-y-6 flex-1">
                {/* Stats */}
                <div className="grid grid-cols-2 gap-4">
                    <div className="bg-slate-700/50 p-3 rounded-lg">
                        <span className="text-xs text-slate-400 block">Vegetation Density</span>
                        <span className="text-xl font-mono">{hotspot.vegetation_density}</span>
                    </div>
                    <div className="bg-slate-700/50 p-3 rounded-lg">
                        <span className="text-xs text-slate-400 block">Risk Score</span>
                        <span className="text-xl font-mono text-athena-accent">{hotspot.risk_score}/100</span>
                    </div>
                </div>

                {/* Drone Simulation */}
                <div className="space-y-3">
                    <div className="flex justify-between items-center">
                        <h3 className="font-semibold text-sm uppercase text-slate-400">Drone Live Feed</h3>
                        {!imageInfo && (
                            <button
                                onClick={handleSimulate}
                                className="px-3 py-1 bg-athena-accent text-slate-900 text-sm font-bold rounded hover:bg-sky-400 transition"
                            >
                                Launch Drone
                            </button>
                        )}
                    </div>

                    <div className="relative aspect-video bg-black rounded-lg overflow-hidden border border-slate-700 group">
                        {!imageInfo ? (
                            <div className="absolute inset-0 flex flex-col items-center justify-center text-slate-500 space-y-2">
                                <Webcam className="w-10 h-10 opacity-50" />
                                <span className="text-sm">Signal Offline</span>
                            </div>
                        ) : (
                            <>
                                <img
                                    src={imageInfo.url}
                                    className="w-full h-full object-contain"
                                    onLoad={onImageLoad}
                                    alt="Drone Feed"
                                />

                                {/* Overlay */}
                                {analysis && imageDims.w > 0 && (
                                    <svg
                                        viewBox={`0 0 ${imageDims.w} ${imageDims.h}`}
                                        className="absolute inset-0 w-full h-full pointer-events-none"
                                    >
                                        {analysis.detections.map((det, idx) => {
                                            const pointsStr = det.points.map(p => p.join(',')).join(' ');
                                            const isVeg = det.label.includes('tree') || det.label.includes('vegetation');
                                            const isCable = det.label.includes('cable') || det.label.includes('wire');
                                            const color = isVeg ? 'lime' : (isCable ? 'cyan' : 'orange');

                                            return (
                                                <polygon
                                                    key={idx}
                                                    points={pointsStr}
                                                    fill="none"
                                                    stroke={color}
                                                    strokeWidth="3"
                                                    className="opacity-80"
                                                />
                                            )
                                        })}
                                    </svg>
                                )}
                            </>
                        )}

                        {loading && (
                            <div className="absolute inset-0 bg-black/60 flex items-center justify-center backdrop-blur-sm">
                                <Activity className="w-8 h-8 text-athena-accent animate-spin" />
                            </div>
                        )}
                    </div>

                    {imageInfo && !analysis && (
                        <button
                            onClick={handleAnalyze}
                            disabled={loading}
                            className="w-full py-2 bg-slate-700 hover:bg-slate-600 text-white rounded font-medium transition flex items-center justify-center gap-2"
                        >
                            <Activity className="w-4 h-4" /> Run Inference
                        </button>
                    )}
                </div>

                {/* Analysis Results */}
                {analysis && (
                    <div className={clsx("p-4 rounded-lg border", {
                        "bg-red-500/10 border-red-500/50": analysis.risk_detected,
                        "bg-green-500/10 border-green-500/50": !analysis.risk_detected
                    })}>
                        <div className="flex items-start gap-3">
                            {analysis.risk_detected ? (
                                <AlertTriangle className="w-6 h-6 text-red-500 shrink-0" />
                            ) : (
                                <CheckCircle className="w-6 h-6 text-green-500 shrink-0" />
                            )}
                            <div>
                                <h4 className={clsx("font-bold text-sm", {
                                    "text-red-400": analysis.risk_detected,
                                    "text-green-400": !analysis.risk_detected
                                })}>
                                    {analysis.risk_detected ? 'THREAT DETECTED' : 'CLEARANCE OK'}
                                </h4>
                                <p className="text-sm text-slate-300 mt-1">{analysis.details}</p>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
