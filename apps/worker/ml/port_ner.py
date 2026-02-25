"""
GeoRisk Pro — Port Entity Extractor
Dictionary-based NER for extracting port names from text.
Covers all planned trade corridors:
  Origin: India, Pakistan, Bangladesh, Vietnam, China, Brazil, Mexico,
          Caribbean, Africa-East/West/South, Turkey
  Destination: EU, UK, USA
"""

import re
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional


@dataclass
class PortEntity:
    name: str
    country: str
    region: str
    corridor: str  # "origin" or "destination"
    aliases: List[str] = None

    def to_dict(self):
        d = asdict(self)
        d.pop("aliases", None)
        return d


# ─── Port Dictionary ─────────────────────────────────────────────
# Each entry: canonical_name → PortEntity
# Aliases are additional search terms that map to the same port

PORT_DATABASE: Dict[str, PortEntity] = {}
ALIAS_MAP: Dict[str, str] = {}  # alias_lowercase → canonical_name


def _register(name: str, country: str, region: str, corridor: str, aliases: List[str] = None):
    """Register a port and its aliases."""
    PORT_DATABASE[name] = PortEntity(
        name=name, country=country, region=region,
        corridor=corridor, aliases=aliases or []
    )
    # Register lowercase aliases for matching
    ALIAS_MAP[name.lower()] = name
    for alias in (aliases or []):
        ALIAS_MAP[alias.lower()] = name


# ═══════════════════════════════════════════════════════════════════
# ORIGIN PORTS
# ═══════════════════════════════════════════════════════════════════

# ─── India ────────────────────────────────────────────────────────
_register("Mumbai", "India", "india", "origin", ["Bombay", "Nhava Sheva", "JNPT", "Jawaharlal Nehru Port"])
_register("Chennai", "India", "india", "origin", ["Madras", "Ennore", "Kamarajar Port"])
_register("Mundra", "India", "india", "origin", ["Adani Mundra"])
_register("Kandla", "India", "india", "origin", ["Deendayal Port"])
_register("Cochin", "India", "india", "origin", ["Kochi", "Vallarpadam"])
_register("Visakhapatnam", "India", "india", "origin", ["Vizag"])
_register("Kolkata", "India", "india", "origin", ["Calcutta", "Haldia"])
_register("Tuticorin", "India", "india", "origin", ["Thoothukudi", "VOC Port"])
_register("Mangalore", "India", "india", "origin", ["New Mangalore Port"])
_register("Pipavav", "India", "india", "origin", ["APM Pipavav"])

# ─── Pakistan ─────────────────────────────────────────────────────
_register("Karachi", "Pakistan", "pakistan", "origin", ["Karachi Port", "KPT"])
_register("Port Qasim", "Pakistan", "pakistan", "origin", ["Qasim", "Muhammad Bin Qasim"])
_register("Gwadar", "Pakistan", "pakistan", "origin", ["Gwadar Port"])

# ─── Bangladesh ───────────────────────────────────────────────────
_register("Chittagong", "Bangladesh", "bangladesh", "origin", ["Chattogram", "Chittagong Port"])
_register("Mongla", "Bangladesh", "bangladesh", "origin", ["Mongla Port"])
_register("Payra", "Bangladesh", "bangladesh", "origin", ["Payra Port"])

# ─── Vietnam ──────────────────────────────────────────────────────
_register("Ho Chi Minh City", "Vietnam", "vietnam", "origin", ["HCMC", "Saigon", "Cat Lai", "Cai Mep", "Vung Tau"])
_register("Hai Phong", "Vietnam", "vietnam", "origin", ["Haiphong", "Lach Huyen"])
_register("Da Nang", "Vietnam", "vietnam", "origin", ["Danang", "Tien Sa"])
_register("Quy Nhon", "Vietnam", "vietnam", "origin", ["Qui Nhon"])

# ─── China ────────────────────────────────────────────────────────
_register("Shanghai", "China", "china", "origin", ["Yangshan", "Waigaoqiao"])
_register("Shenzhen", "China", "china", "origin", ["Yantian", "Shekou", "Chiwan", "Da Chan Bay"])
_register("Ningbo", "China", "china", "origin", ["Ningbo-Zhoushan", "Beilun"])
_register("Qingdao", "China", "china", "origin", ["Tsingtao"])
_register("Xiamen", "China", "china", "origin", ["Amoy"])
_register("Tianjin", "China", "china", "origin", ["Xingang", "Tientsin"])
_register("Guangzhou", "China", "china", "origin", ["Nansha", "Huangpu"])
_register("Dalian", "China", "china", "origin", ["Dairen"])
_register("Fuzhou", "China", "china", "origin", ["Jiangyin"])
_register("Lianyungang", "China", "china", "origin", [])

# ─── Brazil ───────────────────────────────────────────────────────
_register("Santos", "Brazil", "brazil", "origin", ["Porto de Santos"])
_register("Paranaguá", "Brazil", "brazil", "origin", ["Paranagua"])
_register("Rio Grande", "Brazil", "brazil", "origin", ["Porto do Rio Grande"])
_register("Itajaí", "Brazil", "brazil", "origin", ["Itajai", "Navegantes"])
_register("Suape", "Brazil", "brazil", "origin", ["Porto de Suape"])
_register("Salvador", "Brazil", "brazil", "origin", ["Porto de Salvador"])
_register("Vitória", "Brazil", "brazil", "origin", ["Vitoria", "Tubarão"])
_register("Manaus", "Brazil", "brazil", "origin", ["Porto de Manaus"])

# ─── Mexico ───────────────────────────────────────────────────────
_register("Manzanillo", "Mexico", "mexico", "origin", ["Manzanillo Mexico"])
_register("Lázaro Cárdenas", "Mexico", "mexico", "origin", ["Lazaro Cardenas", "Lazaro"])
_register("Veracruz", "Mexico", "mexico", "origin", ["Puerto de Veracruz"])
_register("Altamira", "Mexico", "mexico", "origin", ["Puerto de Altamira"])
_register("Ensenada", "Mexico", "mexico", "origin", [])

# ─── Caribbean ────────────────────────────────────────────────────
_register("Kingston", "Jamaica", "caribbean", "origin", ["Kingston Container Terminal"])
_register("Freeport", "Bahamas", "caribbean", "origin", ["Freeport Bahamas", "Freeport Container Port"])
_register("Port of Spain", "Trinidad and Tobago", "caribbean", "origin", ["Port-of-Spain"])
_register("Bridgetown", "Barbados", "caribbean", "origin", ["Bridgetown Port"])
_register("Caucedo", "Dominican Republic", "caribbean", "origin", ["DP World Caucedo"])
_register("Colón", "Panama", "caribbean", "origin", ["Colon", "Manzanillo International Terminal", "MIT Panama"])
_register("San Juan", "Puerto Rico", "caribbean", "origin", ["San Juan PR"])
_register("Pointe-à-Pitre", "Guadeloupe", "caribbean", "origin", ["Pointe a Pitre"])
_register("Fort-de-France", "Martinique", "caribbean", "origin", [])
_register("Castries", "Saint Lucia", "caribbean", "origin", [])

# ─── Africa-East ──────────────────────────────────────────────────
_register("Mombasa", "Kenya", "africa_east", "origin", ["Mombasa Port", "Kilindini"])
_register("Dar es Salaam", "Tanzania", "africa_east", "origin", ["Dar Port", "DSM Port"])
_register("Djibouti", "Djibouti", "africa_east", "origin", ["Doraleh"])
_register("Maputo", "Mozambique", "africa_east", "origin", ["Maputo Port"])
_register("Beira", "Mozambique", "africa_east", "origin", ["Beira Port"])
_register("Port Sudan", "Sudan", "africa_east", "origin", ["Port Sudan"])
_register("Nacala", "Mozambique", "africa_east", "origin", [])
_register("Toamasina", "Madagascar", "africa_east", "origin", ["Tamatave"])

# ─── Africa-West ──────────────────────────────────────────────────
_register("Lagos", "Nigeria", "africa_west", "origin", ["Apapa", "Tin Can Island", "Lekki Deep Sea"])
_register("Tema", "Ghana", "africa_west", "origin", ["Tema Port", "MPS Terminal"])
_register("Abidjan", "Ivory Coast", "africa_west", "origin", ["Port d'Abidjan", "Abidjan Port"])
_register("Dakar", "Senegal", "africa_west", "origin", ["Dakar Port"])
_register("Douala", "Cameroon", "africa_west", "origin", ["Douala Port", "Port of Douala"])
_register("Lomé", "Togo", "africa_west", "origin", ["Lome", "Lomé Container Terminal"])
_register("Cotonou", "Benin", "africa_west", "origin", ["Cotonou Port"])
_register("Conakry", "Guinea", "africa_west", "origin", ["Conakry Port"])
_register("Freetown", "Sierra Leone", "africa_west", "origin", [])
_register("Nouakchott", "Mauritania", "africa_west", "origin", ["Port de l'Amitié"])
_register("Pointe-Noire", "Republic of Congo", "africa_west", "origin", ["Pointe Noire"])
_register("Libreville", "Gabon", "africa_west", "origin", ["Owendo"])
_register("Luanda", "Angola", "africa_west", "origin", ["Porto de Luanda"])

# ─── Africa-South ─────────────────────────────────────────────────
_register("Durban", "South Africa", "africa_south", "origin", ["Durban Port"])
_register("Cape Town", "South Africa", "africa_south", "origin", ["Cape Town Port"])
_register("Port Elizabeth", "South Africa", "africa_south", "origin", ["Gqeberha", "Coega"])
_register("Richards Bay", "South Africa", "africa_south", "origin", [])
_register("Walvis Bay", "Namibia", "africa_south", "origin", ["Walvis Bay Port"])

# ─── Turkey ───────────────────────────────────────────────────────
_register("Mersin", "Turkey", "turkey", "origin", ["Mersin International Port", "MIP"])
_register("Ambarlı", "Turkey", "turkey", "origin", ["Ambarli", "Istanbul Port", "Kumport", "Marport"])
_register("Izmir", "Turkey", "turkey", "origin", ["Aliaga", "Alsancak", "Nemport"])
_register("Gemlik", "Turkey", "turkey", "origin", ["Gemport", "Borusan"])
_register("Iskenderun", "Turkey", "turkey", "origin", ["Isdemir", "Limak Iskenderun"])
_register("Trabzon", "Turkey", "turkey", "origin", ["Trabzon Port"])
_register("Antalya", "Turkey", "turkey", "origin", ["Antalya Port"])


# ═══════════════════════════════════════════════════════════════════
# DESTINATION PORTS
# ═══════════════════════════════════════════════════════════════════

# ─── EU ───────────────────────────────────────────────────────────
_register("Rotterdam", "Netherlands", "eu", "destination", ["Europoort", "Maasvlakte"])
_register("Antwerp", "Belgium", "eu", "destination", ["Antwerp-Bruges", "Antwerpen"])
_register("Hamburg", "Germany", "eu", "destination", ["Hamburger Hafen"])
_register("Le Havre", "France", "eu", "destination", ["LeHavre"])
_register("Zeebrugge", "Belgium", "eu", "destination", [])
_register("Piraeus", "Greece", "eu", "destination", ["Athens Port"])
_register("Genoa", "Italy", "eu", "destination", ["Genova"])
_register("Valencia", "Spain", "eu", "destination", ["Valenciaport"])
_register("Barcelona", "Spain", "eu", "destination", [])
_register("Algeciras", "Spain", "eu", "destination", [])
_register("Bremerhaven", "Germany", "eu", "destination", [])
_register("Marseille", "France", "eu", "destination", ["Fos-sur-Mer"])
_register("Gdansk", "Poland", "eu", "destination", ["DCT Gdansk"])
_register("Koper", "Slovenia", "eu", "destination", [])
_register("Gioia Tauro", "Italy", "eu", "destination", [])

# ─── UK ───────────────────────────────────────────────────────────
_register("Felixstowe", "UK", "uk", "destination", ["Port of Felixstowe"])
_register("Southampton", "UK", "uk", "destination", ["Port of Southampton", "DP World Southampton"])
_register("London Gateway", "UK", "uk", "destination", ["DP World London Gateway"])
_register("Liverpool", "UK", "uk", "destination", ["Port of Liverpool", "Peel Ports"])
_register("Tilbury", "UK", "uk", "destination", ["Port of Tilbury"])
_register("Immingham", "UK", "uk", "destination", ["Port of Immingham"])

# ─── USA ──────────────────────────────────────────────────────────
_register("Newark", "USA", "usa", "destination", ["Port Newark", "Elizabeth", "NY/NJ", "Port of New York"])
_register("Los Angeles", "USA", "usa", "destination", ["LA Port", "Port of LA", "San Pedro"])
_register("Long Beach", "USA", "usa", "destination", ["Port of Long Beach", "POLB"])
_register("Savannah", "USA", "usa", "destination", ["Port of Savannah", "Garden City Terminal"])
_register("Houston", "USA", "usa", "destination", ["Port of Houston", "Bayport"])
_register("Miami", "USA", "usa", "destination", ["PortMiami", "Port of Miami"])
_register("Charleston", "USA", "usa", "destination", ["Port of Charleston"])
_register("Norfolk", "USA", "usa", "destination", ["Virginia Port", "Newport News"])
_register("Seattle", "USA", "usa", "destination", ["Port of Seattle", "Tacoma", "Northwest Seaport Alliance"])
_register("Oakland", "USA", "usa", "destination", ["Port of Oakland"])
_register("Baltimore", "USA", "usa", "destination", ["Port of Baltimore"])
_register("New Orleans", "USA", "usa", "destination", ["Port of New Orleans", "Port NOLA"])

# ─── Transshipment Hubs (critical waypoints) ─────────────────────
_register("Singapore", "Singapore", "transshipment", "hub", ["PSA Singapore", "Jurong Port"])
_register("Colombo", "Sri Lanka", "transshipment", "hub", ["Colombo Port"])
_register("Jebel Ali", "UAE", "transshipment", "hub", ["Dubai Port", "DP World Jebel Ali"])
_register("Tanger Med", "Morocco", "transshipment", "hub", ["Tangier", "Tanger"])
_register("Port Klang", "Malaysia", "transshipment", "hub", ["Westport", "Northport"])
_register("Salalah", "Oman", "transshipment", "hub", ["Port of Salalah"])
_register("Jeddah", "Saudi Arabia", "transshipment", "hub", ["Jeddah Islamic Port"])
_register("Port Said", "Egypt", "transshipment", "hub", ["East Port Said", "Suez Canal"])
_register("Malta", "Malta", "transshipment", "hub", ["Marsaxlokk", "Malta Freeport"])


# ═══════════════════════════════════════════════════════════════════
# Extractor Logic
# ═══════════════════════════════════════════════════════════════════

class PortEntityExtractor:
    """Extract port entities from text using dictionary + regex matching."""

    def __init__(self):
        # Pre-compile regex patterns for all aliases (sorted longest-first to avoid partial matches)
        all_terms = sorted(ALIAS_MAP.keys(), key=len, reverse=True)
        # Escape special regex chars and build pattern
        escaped = [re.escape(term) for term in all_terms]
        self._pattern = re.compile(
            r'\b(' + '|'.join(escaped) + r')\b',
            re.IGNORECASE
        )

    def extract_ports(self, text: str) -> List[Dict]:
        """Extract all port entities from text. Returns list of port dicts."""
        if not text:
            return []

        matches = self._pattern.findall(text)
        seen = set()
        results = []

        for match in matches:
            canonical = ALIAS_MAP.get(match.lower())
            if canonical and canonical not in seen:
                seen.add(canonical)
                port = PORT_DATABASE[canonical]
                results.append(port.to_dict())

        return results

    def extract_corridors(self, ports: List[Dict]) -> List[str]:
        """Identify trade corridors from extracted ports.
        Returns list like ['india → eu', 'africa_west → usa'].
        """
        origins = set()
        destinations = set()
        hubs = set()

        for port in ports:
            if port["corridor"] == "origin":
                origins.add(port["region"])
            elif port["corridor"] == "destination":
                destinations.add(port["region"])
            elif port["corridor"] == "hub":
                hubs.add(port["region"])

        corridors = []
        for origin in origins:
            for dest in destinations:
                corridors.append(f"{origin} → {dest}")

        # If only origins or only destinations found, flag as partial
        if origins and not destinations:
            for origin in origins:
                corridors.append(f"{origin} → ?")
        elif destinations and not origins:
            for dest in destinations:
                corridors.append(f"? → {dest}")

        return corridors

    def get_port_count(self) -> int:
        """Return total number of ports in dictionary."""
        return len(PORT_DATABASE)

    def get_alias_count(self) -> int:
        """Return total number of searchable terms (ports + aliases)."""
        return len(ALIAS_MAP)
