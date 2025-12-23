import random

def generate_mock_hotspots():
    features = []
    
    # 1. Load Real Data
    import os
    import json
    
    real_data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'hotspots_real.json')
    if os.path.exists(real_data_path):
        try:
            with open(real_data_path, 'r') as f:
                real_data = json.load(f)
                features.extend(real_data.get('features', []))
        except Exception as e:
            print(f"Failed to load real data: {e}")

    # 2. Augment with Simulated Data to reach target count (1000+)
    # Specialized zones for requested cities: San Mateo, Hayward, Berkeley
    augment_zones = [
        (37.520, 37.580, -122.350, -122.280), # San Mateo / Belmont / Foster City
        (37.600, 37.700, -122.120, -122.040), # Hayward / Union City
        (37.840, 37.900, -122.320, -122.230), # Berkeley / Albany / El Cerrito
        (37.580, 37.620, -122.420, -122.360), # Millbrae / Burlingame
        (37.780, 37.840, -122.300, -122.200), # Oakland / Piedmont
        (37.380, 37.460, -122.180, -122.100), # Palo Alto / Los Altos
        (37.720, 37.800, -122.500, -122.380), # SF City
    ]
    
    total_needed = 1200
    current_count = len(features)
    needed = max(0, total_needed - current_count)
    
    for i in range(needed):
        # Pick a random zone or general Bay Area
        if i < 200: # Ensure at least 200 are in the specific user-requested cities
            lat_min, lat_max, lng_min, lng_max = random.choice(augment_zones)
            # Add some jitter to spread them out around the city center
            lat = random.uniform(lat_min - 0.05, lat_max + 0.05)
            lng = random.uniform(lng_min - 0.05, lng_max + 0.05)
        else:
            # Safe Land Zones to avoid SF Bay
            safe_land_zones = [
                (37.30, 37.50, -122.10, -121.80), # South Bay / San Jose
                (37.50, 37.60, -122.05, -121.90), # Fremont / Newark Inland
                (37.60, 37.75, -122.10, -121.95), # Hayward / Castro Valley Hills
                (37.45, 37.60, -122.30, -122.15), # Peninsula Inland (Redwood City/San Carlos)
                (37.75, 37.85, -122.25, -122.15), # Oakland/Berkeley Hills
            ]
            lat_min, lat_max, lng_min, lng_max = random.choice(safe_land_zones)
            lat = random.uniform(lat_min, lat_max)
            lng = random.uniform(lng_min, lng_max)

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
            
        # Create a small polygon (mock footprint)
        delta = 0.001 # ~100m
        coordinates = [
            [lng - delta, lat - delta],
            [lng + delta, lat - delta],
            [lng + delta, lat + delta],
            [lng - delta, lat + delta],
            [lng - delta, lat - delta]
        ]
        
        feature = {
            "type": "Feature",
            "properties": {
                "id": f"sim_{current_count + i}",
                "risk_score": risk_score,
                "risk_level": risk_level,
                "color": color,
                "vegetation_density": f"{random.randint(40, 90)}%"
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [coordinates]
            }
        }
        features.append(feature)
        
    return {
        "type": "FeatureCollection",
        "features": features
    }
    
    # Define safe inland zones (Lat min, Lat max, Lng min, Lng max)
