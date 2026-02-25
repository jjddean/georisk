# Maritime Geopolitical Risk Routing App - Implementation Guide

## 📊 Data Storage Requirements

### Storage Breakdown

```
MINIMAL SETUP (Small Fleet, Regional Routes)
├── Piracy incidents (2 years)        ~25 MB
├── Conflict zones (ACLED, 1 year)    ~50 MB
├── OFAC sanctions                    ~30 MB
├── Chokepoint data                   ~5 MB
└── Country risk indices              ~10 MB
TOTAL: ~120 MB in memory, ~150 MB on disk

STANDARD SETUP (Medium Fleet, Global Routes)
├── Piracy incidents (5 years)        ~50 MB
├── Conflict zones (ACLED, 3 years)   ~150 MB
├── All sanctions (OFAC, UN, EU)      ~80 MB
├── Port state control                ~100 MB
├── Historical incidents              ~200 MB
├── Weather data                      ~100 MB
└── Chokepoint + risk zones           ~20 MB
TOTAL: ~400 MB in memory, ~700 MB on disk

ENTERPRISE SETUP (Large Fleet, Real-time)
├── Full incident database (10 years) ~500 MB
├── GDELT filtered events             ~1 GB
├── AIS tracking data (selective)     ~2 GB
├── News aggregation                  ~500 MB
├── Historical patterns               ~3 GB
└── All reference data                ~500 MB
TOTAL: ~1.5 GB in memory, ~7.5 GB on disk
```

### Recommended Architecture

```
TIER 1: IN-MEMORY (Instant Access)
- Last 24 months piracy incidents
- Last 12 months conflict events
- Current sanctions lists
- Chokepoint real-time status
- High-risk zones (computed)
Size: ~200-400 MB
Access: <10ms

TIER 2: SQLITE (Fast Queries)
- Historical incidents (5+ years)
- Country risk profiles
- Port efficiency data
- Seasonal patterns
Size: ~1-3 GB
Access: ~50-100ms with indexes

TIER 3: API/REAL-TIME (On Demand)
- Current weather forecasts
- Breaking security alerts
- Live AIS vessel tracking
- Port status updates
Access: When needed
```

## 🌐 Free Data Sources - Step by Step

### 1. ACLED (Armed Conflict Data) ⭐ PRIORITY

**Best for:** Coastal conflicts, port disruptions, regional instability

```python
# Registration: https://developer.acleddata.com/
# Get FREE API key

import httpx

def download_acled_data(api_key, email):
    """Download last 12 months of conflict data"""
    
    params = {
        'key': api_key,
        'email': email,
        'event_date': '2023-02-01',  # Start date
        'event_date_where': '>=',
        'limit': 50000,
        'fields': 'event_id_cnty|event_date|year|time_precision|disorder_type|event_type|sub_event_type|actor1|actor2|admin1|admin2|admin3|location|latitude|longitude|geo_precision|source|notes|fatalities|timestamp'
    }
    
    with httpx.Client() as client:
        response = client.get(
            'https://api.acleddata.com/acled/read',
            params=params
        )
        data = response.json()['data']
    
    # Filter for maritime-relevant events
    maritime_events = [
        event for event in data
        if any(keyword in event.get('notes', '').lower() 
               for keyword in ['port', 'coast', 'ship', 'vessel', 'maritime', 'naval'])
        or event.get('location', '').lower() in ['port', 'harbor', 'coast']
    ]
    
    return maritime_events
```

### 2. OFAC Sanctions ⭐ PRIORITY

**Best for:** Vessel blacklists, port restrictions, compliance

```python
import xml.etree.ElementTree as ET
import httpx

def download_ofac_sanctions():
    """Download current OFAC sanctions list"""
    
    with httpx.Client() as client:
        # Download SDN list (Specially Designated Nationals)
        response = client.get('https://www.treasury.gov/ofac/downloads/sdn.xml')
        
    # Parse XML
    root = ET.fromstring(response.content)
    
    # Extract vessel-related entities
    vessels = []
    for entry in root.findall('.//sdnEntry'):
        if entry.find('.//vesselInfo') is not None:
            vessel = {
                'imo': entry.find('.//vesselInfo/imo').text if entry.find('.//vesselInfo/imo') is not None else None,
                'name': entry.find('.//lastName').text if entry.find('.//lastName') is not None else None,
                'flag': entry.find('.//vesselInfo/callSign').text if entry.find('.//vesselInfo/callSign') is not None else None,
                'programs': [p.text for p in entry.findall('.//program')]
            }
            vessels.append(vessel)
    
    return vessels
```

## 📈 Scaling Considerations

### For Small Fleet (1-10 vessels)

```
Storage: 200 MB RAM, 500 MB disk
Update: Daily
Infrastructure: Single server
Cost: $0 (free data sources)
```

### For Medium Fleet (10-100 vessels)

```
Storage: 500 MB RAM, 2 GB disk
Update: Every 6 hours
Infrastructure: Single server with cache
Cost: $0-50/month
```

## 🔐 Security Recommendations

1. **Data Validation**: Verify data sources before use
2. **Access Control**: Restrict API access with API keys
3. **Audit Logging**: Log all risk assessments
4. **Data Encryption**: Encrypt sensitive route data
5. **Backup**: Daily backups of risk database

---

**Next Steps:**

1. Run `python apps/worker/risk/maritime_risk_manager.py` to see demo
2. Register for ACLED API key (free)
3. Download OFAC sanctions XML
4. Integrate real data sources
5. Setup daily scheduler
