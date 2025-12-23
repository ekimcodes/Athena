import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Polygon, Popup, useMap } from 'react-leaflet';
import axios from 'axios';
import clsx from 'clsx';

// Fix Leaflet's default icon issue
import L from 'leaflet';
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41]
});
L.Marker.prototype.options.icon = DefaultIcon;

const CALIFORNIA_CENTER = [37.6, -122.3]; // Bay Area Center

function HotspotLayer({ onSelectHotspot }) {
    const [hotspots, setHotspots] = useState(null);

    useEffect(() => {
        axios.get('/api/v1/hotspots')
            .then(res => {
                setHotspots(res.data);
            })
            .catch(err => console.error("Failed to fetch hotspots", err));
    }, []);

    if (!hotspots) return null;

    return (
        <>
            {hotspots.features.map((feature, idx) => {
                // GeoJSON uses [lng, lat], Leaflet uses [lat, lng]
                // But my scanner.py generated output manually. Let's check scanner.py again.
                // scanner.py: coordinates = [[lng, lat], ...]
                // Leaflet Polygon expects [lat, lng].
                // I need to swap them.
                const coordinates = feature.geometry.coordinates[0].map(coord => [coord[1], coord[0]]);
                const props = feature.properties;

                return (
                    <Polygon
                        key={props.id}
                        positions={coordinates}
                        pathOptions={{
                            color: props.color,
                            fillColor: props.color,
                            fillOpacity: 0.4,
                            weight: 2
                        }}
                        eventHandlers={{
                            click: () => onSelectHotspot(props)
                        }}
                    >
                        <Popup>
                            <div className="text-slate-800">
                                <h3 className="font-bold">Hotspot {props.id}</h3>
                                <p>Risk: <span style={{ color: props.color }}>{props.risk_level}</span></p>
                                <p>Score: {props.risk_score}</p>
                            </div>
                        </Popup>
                    </Polygon>
                );
            })}
        </>
    );
}

export default function MapView({ onSelectHotspot }) {
    return (
        <MapContainer
            center={CALIFORNIA_CENTER}
            zoom={10}
            scrollWheelZoom={true}
            className="w-full h-full bg-slate-900"
        >
            <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a>'
                url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
            />
            <HotspotLayer onSelectHotspot={onSelectHotspot} />
        </MapContainer>
    );
}
