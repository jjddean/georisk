# Maritime Risk Data Sources - Quick Reference

## 🎯 PRIORITY SOURCES (Start Here)

### 1. ACLED - Armed Conflict Location & Event Data ⭐⭐⭐
**URL:** https://developer.acleddata.com/  
**Cost:** FREE (requires registration)  
**Coverage:** Global conflict events near ports/coasts  
**Format:** JSON via API  

### 2. OFAC Sanctions List ⭐⭐⭐
**URL:** https://www.treasury.gov/ofac/downloads/  
**Cost:** FREE  
**Coverage:** Sanctioned vessels, ports, entities  
**Format:** XML, CSV  

### 3. ICC-IMB Piracy Reporting Centre ⭐⭐⭐
**URL:** https://www.icc-ccs.org/piracy-reporting-centre  
**Cost:** Subscription required OR free quarterly reports  
**Coverage:** Global piracy incidents  

### 4. Global Terrorism Database (GTD) ⭐⭐
**URL:** https://www.start.umd.edu/gtd/  
**Cost:** FREE (requires registration)  
**Coverage:** Global terrorism incidents (includes maritime)  

## 🌊 CHOKEPOINT DATA (Static Reference)

### Critical Maritime Chokepoints
1. **Strait of Hormuz** (Iran)
2. **Malacca Strait** (Malaysia/Indonesia)
3. **Suez Canal** (Egypt)
4. **Bab-el-Mandeb** (Yemen/Djibouti)
5. **Panama Canal**
6. **Turkish Straits** (Bosphorus)

## 📊 DATA STORAGE CALCULATOR

```
SMALL SETUP
├── Piracy (2y):        25 MB
├── Conflicts (1y):     50 MB
├── Sanctions:          30 MB
├── Chokepoints:         5 MB
└── Country Risk:       10 MB
TOTAL: ~150 MB disk
```

---

## 🔄 UPDATE SCHEDULE RECOMMENDATIONS

```
CRITICAL (Daily):
- OFAC sanctions
- Piracy incidents
- Active conflicts (ACLED)
- Chokepoint status

IMPORTANT (Weekly):
- Port restrictions
- Risk zone recalculation
```
