# Geopolitical Risk Data Sources for Shipping Lane Routing
# =========================================================

"""
Data Sources for Maritime Route Risk Assessment
Covering: Conflicts, piracy, sanctions, weather, port closures, transit fees
"""

## =================================================================
## FREE/PUBLIC DATA SOURCES (Bulk Download Available)
## =================================================================

GEOPOLITICAL_DATA_SOURCES = {
    
    # 1. CONFLICT & SECURITY DATA
    "acled": {
        "name": "Armed Conflict Location & Event Data",
        "url": "https://api.acleddata.com/acled/read",
        "bulk_export": "https://acleddata.com/data-export-tool/",
        "coverage": "Global conflict events, protests, violence",
        "update_frequency": "Weekly",
        "data_size": "~50-100MB (past year)",
        "requires_api_key": True,  # Free registration
        "fields": [
            "event_date", "country", "location", "latitude", "longitude",
            "event_type", "sub_event_type", "fatalities", "notes"
        ],
        "maritime_relevance": "Port disruptions, coastal conflicts, regional instability",
        "notes": "Best source for real-time conflict tracking near ports/straits"
    },
    
    # 2. PIRACY DATA
    "icc_piracy": {
        "name": "ICC International Maritime Bureau Piracy Reports",
        "url": "https://www.icc-ccs.org/piracy-reporting-centre",
        "bulk_export": "Reports available as PDFs/CSV exports",
        "coverage": "Global piracy incidents",
        "update_frequency": "Real-time incidents, quarterly reports",
        "data_size": "~5-10MB per year",
        "requires_api_key": False,
        "fields": [
            "date", "location", "latitude", "longitude", "vessel_type",
            "incident_type", "violence_level", "outcome"
        ],
        "maritime_relevance": "Direct shipping route risk",
        "notes": "Gold standard for piracy data. Somalia, Gulf of Guinea, Malacca Strait hotspots"
    },
    
    # 3. MARITIME INCIDENTS
    "global_terrorism_database": {
        "name": "Global Terrorism Database (GTD)",
        "url": "https://www.start.umd.edu/gtd/",
        "bulk_export": "https://www.start.umd.edu/gtd/access/",
        "coverage": "Global terrorism incidents (includes maritime)",
        "update_frequency": "Annual updates",
        "data_size": "~200MB (full database)",
        "requires_api_key": False,  # Free download
        "fields": [
            "date", "country", "region", "latitude", "longitude",
            "attack_type", "target_type", "weapon_type", "casualties"
        ],
        "maritime_relevance": "Port attacks, vessel hijackings, maritime terrorism",
        "notes": "Filter by attack_type='Hijacking' or target_type='Maritime'"
    },
    
    # 4. SANCTIONS & RESTRICTIONS
    "ofac_sanctions": {
        "name": "US OFAC Sanctions List",
        "url": "https://www.treasury.gov/ofac/downloads/",
        "bulk_export": "https://www.treasury.gov/ofac/downloads/sdn.xml",
        "coverage": "Sanctioned countries, entities, vessels",
        "update_frequency": "Daily",
        "data_size": "~20-30MB",
        "requires_api_key": False,
        "fields": [
            "entity_name", "entity_type", "country", "programs",
            "vessel_imo", "vessel_name", "vessel_flag"
        ],
        "maritime_relevance": "Restricted ports, banned vessels, sanctioned routes",
        "notes": "Critical for Iran, Russia, North Korea, Venezuela routes"
    },
    
    "un_sanctions": {
        "name": "UN Security Council Sanctions",
        "url": "https://www.un.org/securitycouncil/content/un-sc-consolidated-list",
        "bulk_export": "XML/CSV downloads available",
        "coverage": "UN sanctioned entities and countries",
        "update_frequency": "Weekly",
        "data_size": "~10-15MB",
        "requires_api_key": False,
        "maritime_relevance": "International shipping restrictions"
    },
    
    # 5. STRAIT & CHOKEPOINT DATA
    "maritime_chokepoints": {
        "name": "Critical Maritime Chokepoints Database",
        "url": "Custom dataset (need to compile from various sources)",
        "sources": [
            "EIA International Energy Statistics",
            "Maritime traffic data",
            "Naval intelligence reports"
        ],
        "coverage": "Suez, Panama, Hormuz, Malacca, Bab-el-Mandeb, etc.",
        "key_data": [
            "Chokepoint name", "coordinates", "daily_traffic",
            "closure_risk", "alternative_routes", "transit_fees"
        ],
        "data_size": "~1-5MB",
        "maritime_relevance": "Critical for route planning",
        "notes": "Static data + real-time status monitoring needed"
    },
    
    # 6. PORT CLOSURES & RESTRICTIONS
    "gisis_port_state": {
        "name": "IMO GISIS Port State Control",
        "url": "https://gisis.imo.org/",
        "bulk_export": "Requires IMO membership",
        "coverage": "Port inspections, detentions, bans",
        "update_frequency": "Real-time",
        "data_size": "~50-100MB",
        "requires_api_key": True,
        "maritime_relevance": "Port safety, vessel detentions",
        "notes": "Alternative: National PSC databases (free)"
    },
    
    # 7. WEATHER & NATURAL HAZARDS
    "noaa_storms": {
        "name": "NOAA Storm Tracks & Forecasts",
        "url": "https://www.nhc.noaa.gov/data/",
        "bulk_export": "https://www.nhc.noaa.gov/gis/",
        "coverage": "Atlantic, Pacific hurricanes/cyclones",
        "update_frequency": "6-hourly during season",
        "data_size": "~20-50MB per season",
        "requires_api_key": False,
        "maritime_relevance": "Route weather avoidance"
    },
    
    # 8. SHIP TRACKING (AIS DATA)
    "marinetraffic_api": {
        "name": "MarineTraffic AIS Data",
        "url": "https://www.marinetraffic.com/en/ais-api-services",
        "bulk_export": "API access (paid)",
        "coverage": "Real-time vessel positions globally",
        "update_frequency": "Real-time (minutes)",
        "data_size": "Varies by query",
        "requires_api_key": True,  # Paid service
        "maritime_relevance": "Traffic density, vessel movements",
        "notes": "Free tier: limited. Alternative: vesselfinder.com"
    },
    
    # 9. COUNTRY RISK INDICES
    "world_bank_governance": {
        "name": "World Bank Worldwide Governance Indicators",
        "url": "https://info.worldbank.org/governance/wgi/",
        "bulk_export": "Excel/CSV downloads",
        "coverage": "Political stability, rule of law, 200+ countries",
        "update_frequency": "Annual",
        "data_size": "~5-10MB",
        "requires_api_key": False,
        "fields": [
            "country", "year", "political_stability", "control_of_corruption",
            "rule_of_law", "regulatory_quality"
        ],
        "maritime_relevance": "Port country risk assessment"
    },
    
    # 10. GEOPOLITICAL EVENTS
    "gdelt": {
        "name": "GDELT Global Events Database",
        "url": "https://www.gdeltproject.org/",
        "bulk_export": "https://blog.gdeltproject.org/gdelt-2-0-our-global-world-in-realtime/",
        "coverage": "Global news events, mentions, tone",
        "update_frequency": "15-minute updates",
        "data_size": "~10-50GB per day (full), ~1GB filtered",
        "requires_api_key": False,
        "fields": [
            "event_date", "actor1", "actor2", "event_code",
            "latitude", "longitude", "goldstein_scale", "avg_tone"
        ],
        "maritime_relevance": "Early warning for regional tensions",
        "notes": "HUGE dataset. Filter by maritime-relevant event codes"
    },
    
    # 11. MARITIME SECURITY ALERTS
    "mschoa": {
        "name": "Maritime Security Centre Horn of Africa",
        "url": "https://www.mschoa.org/",
        "bulk_export": "Weekly piracy reports (PDF/manual parsing)",
        "coverage": "Indian Ocean, Red Sea, Gulf of Aden",
        "update_frequency": "Weekly",
        "data_size": "~5MB per year",
        "requires_api_key": False,
        "maritime_relevance": "High-risk areas, convoy schedules"
    },
    
    # 12. CUSTOMS & PORT EFFICIENCY
    "world_bank_lpi": {
        "name": "Logistics Performance Index",
        "url": "https://lpi.worldbank.org/",
        "bulk_export": "CSV downloads",
        "coverage": "Port efficiency, customs, infrastructure ratings",
        "update_frequency": "Biennial",
        "data_size": "~2-5MB",
        "requires_api_key": False,
        "maritime_relevance": "Port selection, delay risk"
    }
}


## =================================================================
## COMMERCIAL/PREMIUM SOURCES (More Comprehensive)
## =================================================================

COMMERCIAL_SOURCES = {
    
    "risk_intelligence": {
        "name": "Risk Intelligence Maritime Risk System",
        "url": "https://www.riskintelligence.eu/",
        "cost": "~$10,000-50,000/year",
        "coverage": "Real-time maritime security intelligence",
        "maritime_relevance": "Industry gold standard for shipping risk"
    },
    
    "dryad_global": {
        "name": "Dryad Global Maritime Intelligence",
        "url": "https://www.dryadglobal.com/",
        "cost": "~$15,000-30,000/year",
        "coverage": "Real-time piracy, security threats",
        "maritime_relevance": "Detailed incident reports, risk maps"
    },
    
    "ihsmarkit": {
        "name": "IHS Markit Sea-web",
        "url": "https://ihsmarkit.com/products/sea-web-maritime-reference.html",
        "cost": "Enterprise pricing",
        "coverage": "Vessel data, port data, fleet intelligence",
        "maritime_relevance": "Comprehensive vessel tracking"
    },
    
    "windward": {
        "name": "Windward Maritime Risk Platform",
        "url": "https://windward.ai/",
        "cost": "Enterprise pricing",
        "coverage": "AI-powered risk scoring, sanctions screening",
        "maritime_relevance": "Automated compliance, dark activity detection"
    }
}


## =================================================================
## DATA STORAGE REQUIREMENTS
## =================================================================

STORAGE_ESTIMATES = {
    
    "minimal_setup": {
        "description": "Basic routing with major risk indicators",
        "datasets": [
            "Piracy incidents (last 5 years): ~25MB",
            "Major conflict zones (ACLED): ~50MB",
            "OFAC sanctions list: ~30MB",
            "Critical chokepoints data: ~5MB",
            "Country risk indices: ~10MB"
        ],
        "total_storage": "~120MB",
        "refresh_frequency": "Weekly",
        "suitable_for": "Small fleet, regional routes"
    },
    
    "standard_setup": {
        "description": "Comprehensive risk assessment",
        "datasets": [
            "Piracy incidents (10 years): ~50MB",
            "Global conflicts (ACLED): ~100MB",
            "Terrorism database: ~200MB",
            "All sanctions lists: ~50MB",
            "Port state control: ~100MB",
            "Weather data: ~100MB",
            "Ship tracking (selective): ~200MB",
            "GDELT events (filtered): ~500MB"
        ],
        "total_storage": "~1.3GB",
        "refresh_frequency": "Daily",
        "suitable_for": "Medium fleet, global routes"
    },
    
    "enterprise_setup": {
        "description": "Real-time intelligence with historical depth",
        "datasets": [
            "All above datasets: ~1.3GB",
            "Full GDELT events (30 days): ~5GB",
            "Detailed AIS tracking: ~2GB",
            "Historical patterns (3 years): ~5GB",
            "News aggregation: ~1GB",
            "Custom intelligence: ~1GB"
        ],
        "total_storage": "~15GB",
        "refresh_frequency": "Hourly/Real-time",
        "suitable_for": "Large fleet, global operations"
    }
}


## =================================================================
## RECOMMENDED ARCHITECTURE
## =================================================================

ARCHITECTURE = {
    
    "tier_1_core_data": {
        "description": "Load in memory (instant access)",
        "datasets": [
            "Piracy hotspots (last 2 years)",
            "Active conflict zones",
            "Current sanctions",
            "Chokepoint status",
            "Port restrictions"
        ],
        "size": "~200MB",
        "access": "In-memory search (<10ms)"
    },
    
    "tier_2_reference_data": {
        "description": "Load on demand (SQLite)",
        "datasets": [
            "Historical incidents (5+ years)",
            "Country risk profiles",
            "Port efficiency data",
            "Weather patterns"
        ],
        "size": "~1GB",
        "access": "SQLite queries (<100ms)"
    },
    
    "tier_3_live_data": {
        "description": "API calls for real-time updates",
        "datasets": [
            "Current weather forecasts",
            "Breaking news events",
            "Vessel positions (AIS)",
            "Port status updates"
        ],
        "access": "API calls when needed"
    }
}


## =================================================================
## SAMPLE IMPLEMENTATION NOTES
## =================================================================

"""
RECOMMENDED APPROACH:

1. Core Risk Factors (In-Memory, ~200MB):
   - Piracy incidents (last 24 months)
   - Active conflicts (last 12 months)
   - Current sanctions
   - Chokepoint data
   - High-risk zones
   
   → Update: Daily via scheduler
   → Search: Instant (<10ms)
   → Use: dataset_manager.py pattern

2. Historical Context (SQLite, ~1GB):
   - Full incident history
   - Country risk scores
   - Port performance data
   
   → Update: Weekly
   → Search: SQL queries (~50-100ms)
   → Use: SQLite with indexes

3. Real-Time Intelligence (API):
   - Weather forecasts
   - Breaking security alerts
   - Live vessel tracking
   
   → Update: On-demand
   → Use: Direct API calls

TOTAL STORAGE: ~1.5GB
TOTAL RAM: ~200-300MB
QUERY SPEED: <50ms for route risk calculation
UPDATE COST: $0 (all free sources)
"""
