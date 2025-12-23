import osmnx as ox
import geopandas as gpd
import random
import os
import argparse
from shapely.geometry import Point

# Configure OSMnx
ox.settings.use_cache = True
ox.settings.log_console = True

def ingest_regions(places):
    all_features = []
    
    for place_name in places:
        print(f"Fetching power lines for: {place_name}...")
        try:
            # Fetch the graph - Reduce radius to 4km and add sleep to avoid timeout
            import time
            time.sleep(5) 
            print(f"  > Querying 4km radius...")
            G = ox.graph_from_address(place_name, dist=4000, dist_type='bbox', custom_filter='["power"="line"]', simplify=True)
            
            # Convert to GeoDataFrame
            gdf_nodes, gdf_edges = ox.graph_to_gdfs(G)
            
            if gdf_edges.empty:
                print(f"No power lines found in {place_name}.")
                continue

            print(f"Found {len(gdf_edges)} segments in {place_name}.")
            
            # Project to UTM for accurate buffering (meters)
            gdf_edges_proj = gdf_edges.to_crs(gdf_edges.estimate_utm_crs())
            
            # Buffer by 50 meters
            hotspots_proj = gdf_edges_proj.buffer(50)
            
            # Convert back to EPSG:4326 (Lat/Lon) for Leaflet
            hotspots = hotspots_proj.to_crs(epsg=4326)
            
            for idx, geometry in hotspots.items():
                
                # Mock Risk Data
                risk_score = random.randint(30, 95)
                if risk_score > 80:
                    risk_level = "CRITICAL"
                    color = "#EF4444"
                elif risk_score > 50:
                    risk_level = "MODERATE"
                    color = "#EAB308"
                else:
                    risk_level = "LOW"
                    color = "#22C55E"
                
                # Use the OSM ID if available, else generic index
                osm_id = str(idx[0]) if isinstance(idx, tuple) else str(idx)

                feature = {
                    "type": "Feature",
                    "properties": {
                        "id": f"{place_name.split(',')[0]}_{osm_id}", 
                        "rating": risk_level, # Legacy field match?
                        "risk_score": risk_score,
                        "risk_level": risk_level,
                        "color": color,
                        "vegetation_density": f"{random.randint(40, 90)}%"
                    },
                    "geometry": geometry.__geo_interface__
                }
                all_features.append(feature)
                
        except Exception as e:
            print(f"Error fetching {place_name}: {e}")

    # Save Combined
    output_data = {
        "type": "FeatureCollection",
        "features": all_features
    }
    
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'hotspots_real.json')
    
    import json
    with open(output_path, 'w') as f:
        json.dump(output_data, f)
        
    print(f"Saved total {len(all_features)} hotspots to {output_path}")

if __name__ == "__main__":
    # Northern California Coverage - Cities (to avoid timeouts)
    regions = [
        "San Francisco, California",
        "Oakland, California",
        "Berkeley, California",
        "Palo Alto, California",
        "San Jose, California",
        "Fremont, California",
        "Hayward, California",
        "San Mateo, California",
        "Redwood City, California",
        "Mountain View, California",
        "Sunnyvale, California",
        "Santa Clara, California",
        "Daly City, California",
        "San Leandro, California",
        "Richmond, California",
        "Sacramento, California",
    ]
    
    ingest_regions(regions)
