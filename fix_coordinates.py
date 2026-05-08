"""
fix_coordinates.py
──────────────────
Replaces bogus random lat/lon in your ELK fake dataset with real country
centroid coordinates (+ small random jitter so dots don't all stack).
Run locally before re-ingesting into Elasticsearch.

Usage:
    python fix_coordinates.py elk-dataset-1.csv elk-dataset-1-fixed.csv
"""

import csv
import sys
import random

# Country name → (lat, lon) centroids
# Covers the countries present in the fake dataset + common ones
COUNTRY_CENTROIDS = {
    "Afghanistan": (33.93911, 67.709953),
    "Albania": (41.153332, 20.168331),
    "Algeria": (28.033886, 1.659626),
    "Angola": (-11.202692, 17.873887),
    "Argentina": (-38.416097, -63.616672),
    "Australia": (-25.274398, 133.775136),
    "Austria": (47.516231, 14.550072),
    "Azerbaijan": (40.143105, 47.576927),
    "Bangladesh": (23.684994, 90.356331),
    "Belgium": (50.503887, 4.469936),
    "Bolivia": (-16.290154, -63.588653),
    "Bosnia and Herzegovina": (43.915886, 17.679076),
    "Brazil": (-14.235004, -51.92528),
    "Bulgaria": (42.733883, 25.48583),
    "Cambodia": (12.565679, 104.990963),
    "Canada": (56.130366, -106.346771),
    "Chad": (15.454166, 18.732207),
    "Chile": (-35.675147, -71.542969),
    "China": (35.86166, 104.195397),
    "Colombia": (4.570868, -74.297333),
    "Congo": (-0.228021, 15.827659),
    "Cuba": (21.521757, -77.781167),
    "Cyprus": (35.126413, 33.429859),
    "Democratic Republic of the Congo": (-4.038333, 21.758664),
    "Denmark": (56.26392, 9.501785),
    "Dominican Republic": (18.735693, -70.162651),
    "Ecuador": (-1.831239, -78.183406),
    "Egypt": (26.820553, 30.802498),
    "Ethiopia": (9.145, 40.489673),
    "Finland": (61.92411, 25.748151),
    "France": (46.227638, 2.213749),
    "Gabon": (-0.803689, 11.609444),
    "Germany": (51.165691, 10.451526),
    "Greece": (39.074208, 21.824312),
    "Guatemala": (15.783471, -90.230759),
    "Guinea": (9.945587, -9.696645),
    "Guyana": (4.860416, -58.93018),
    "Iceland": (64.963051, -19.020835),
    "India": (20.593684, 78.96288),
    "Indonesia": (-0.789275, 113.921327),
    "Iran": (32.427908, 53.688046),
    "Iraq": (33.223191, 43.679291),
    "Ireland": (53.41291, -8.24389),
    "Israel": (31.046051, 34.851612),
    "Italy": (41.87194, 12.56738),
    "Japan": (36.204824, 138.252924),
    "Jordan": (30.585164, 36.238414),
    "Kazakhstan": (48.019573, 66.923684),
    "Kenya": (-0.023559, 37.906193),
    "Laos": (19.85627, 102.495496),
    "Lebanon": (33.854721, 35.862285),
    "Libya": (26.3351, 17.228331),
    "Liberia": (6.428055, -9.429499),
    "Madagascar": (-18.766947, 46.869107),
    "Malaysia": (4.210484, 101.975766),
    "Mali": (17.570692, -3.996166),
    "Mauritania": (21.00789, -10.940835),
    "Mexico": (23.634501, -102.552784),
    "Mongolia": (46.862496, 103.846656),
    "Morocco": (31.791702, -7.09262),
    "Mozambique": (-18.665695, 35.529562),
    "Myanmar": (21.913965, 95.956223),
    "Namibia": (-22.95764, 18.49041),
    "Nepal": (28.394857, 84.124008),
    "New Zealand": (-40.900557, 174.885971),
    "Nicaragua": (12.865416, -85.207229),
    "Niger": (17.607789, 8.081666),
    "Nigeria": (9.081999, 8.675277),
    "North Korea": (40.339852, 127.510093),
    "Norway": (60.472024, 8.468946),
    "Oman": (21.512583, 55.923255),
    "Pakistan": (30.375321, 69.345116),
    "Palau": (7.51498, 134.58252),
    "Panama": (8.537981, -80.782127),
    "Papua New Guinea": (-6.314993, 143.95555),
    "Paraguay": (-23.442503, -58.443832),
    "Peru": (-9.189967, -75.015152),
    "Philippines": (12.879721, 121.774017),
    "Poland": (51.919438, 19.145136),
    "Portugal": (39.399872, -8.224454),
    "Romania": (45.943161, 24.96676),
    "Russia": (61.52401, 105.318756),
    "Saudi Arabia": (23.885942, 45.079162),
    "Senegal": (14.497401, -14.452362),
    "South Africa": (-30.559482, 22.937506),
    "South Korea": (35.907757, 127.766922),
    "Spain": (40.463667, -3.74922),
    "Sri Lanka": (7.873054, 80.771797),
    "Sudan": (12.862807, 30.217636),
    "Sweden": (60.128161, 18.643501),
    "Syria": (34.802075, 38.996815),
    "Taiwan": (23.69781, 120.960515),
    "Tanzania": (-6.369028, 34.888822),
    "Thailand": (15.870032, 100.992541),
    "Tunisia": (33.886917, 9.537499),
    "Turkey": (38.963745, 35.243322),
    "Turkmenistan": (38.969719, 59.556278),
    "Ukraine": (48.379433, 31.16558),
    "United Kingdom": (55.378051, -3.435973),
    "United States": (37.09024, -95.712891),
    "Uruguay": (-32.522779, -55.765835),
    "Venezuela": (6.42375, -66.58973),
    "Vietnam": (14.058324, 108.277199),
    "Yemen": (15.552727, 48.516388),
    "Zambia": (-13.133897, 27.849332),
    "Zimbabwe": (-19.015438, 29.154857),
    # Fake/invalid countries in dataset → map to nearest real country
    "Falkland Islands (Malvinas)": (-51.796253, -59.523613),
    "Heard Island and McDonald Islands": (-53.1, 73.5),
    "Cape Verde": (16.002082, -24.013197),
}

JITTER = 2.5  # degrees of random spread so dots don't stack on centroid

def jitter(val):
    return val + random.uniform(-JITTER, JITTER)

def fix_row_dataset1(row):
    for prefix in ["Source", "Destination"]:
        country = row.get(f"{prefix} Geolocation Country", "").strip()
        if country in COUNTRY_CENTROIDS:
            lat, lon = COUNTRY_CENTROIDS[country]
            row[f"{prefix} Geolocation Latitude"] = round(jitter(lat), 6)
            row[f"{prefix} Geolocation Longitude"] = round(jitter(lon), 6)
    return row

def process(input_path, output_path):
    with open(input_path, newline='', encoding='utf-8') as fin, \
         open(output_path, 'w', newline='', encoding='utf-8') as fout:

        reader = csv.DictReader(fin)
        writer = csv.DictWriter(fout, fieldnames=reader.fieldnames)
        writer.writeheader()

        fixed = 0
        for row in reader:
            original_lat = row.get("Source Geolocation Latitude", "")
            row = fix_row_dataset1(row)
            if row.get("Source Geolocation Latitude") != original_lat:
                fixed += 1
            writer.writerow(row)

    print(f"Done! Fixed coordinates for {fixed} rows → {output_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python fix_coordinates.py <input.csv> <output.csv>")
        sys.exit(1)
    process(sys.argv[1], sys.argv[2])
