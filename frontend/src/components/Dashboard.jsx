import React, { useState } from 'react';
import MapView from './MapView';
import InspectionPanel from './InspectionPanel';
import { Layers } from 'lucide-react';

export default function Dashboard() {
    const [selectedHotspot, setSelectedHotspot] = useState(null);

    return (
        <div className="flex h-screen w-screen bg-slate-900 text-slate-100 overflow-hidden">
            {/* Sidebar / Inspection Panel */}
            <div className="w-[400px] border-r border-slate-800 bg-slate-900 flex-shrink-0 z-20 relative">
                <InspectionPanel
                    hotspot={selectedHotspot}
                    onClose={() => setSelectedHotspot(null)}
                />
            </div>

            {/* Main Content (Map) */}
            <div className="flex-1 relative z-10">
                <div className="absolute top-4 right-4 z-[9999] bg-slate-800/90 backdrop-blur p-2 rounded shadow-xl border border-slate-700">
                    <div className="flex items-center gap-2 text-xs font-bold text-slate-300">
                        <Layers className="w-4 h-4 text-athena-accent" />
                        <span>ATHENA UVM PLATFORM</span>
                    </div>
                </div>
                <MapView onSelectHotspot={setSelectedHotspot} />
            </div>
        </div>
    );
}
