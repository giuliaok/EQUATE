# Data Processing Log

## Column Name Cleanup

### Changes Made:
1. Cleaned up column names by:
   - Removing extra spaces
   - Removing `.1` suffixes
   - Standardizing naming convention

### Specific Column Renames:
- `name` → `language_name`
- `country` → `primary_country`
- `Countries_where_spoken` → `countries_where_spoken`
- `iso_code` → `country_iso_code`

## STEM Graduates Data Update
- Identified and updated STEM graduate percentages for countries that had 0% values
- Updated countries and their new STEM graduate percentages:
  - Afghanistan: 11.25%
  - Fiji: 17.15%
  - Israel: 27.46%
  - Sri Lanka: 24.68%
  - Maldives: 3.59%
  - Marshall Islands: 1.29%
  - Malta: 15.42%
  - Nicaragua: 19.54%
  - Aruba: 2.22%
  - Seychelles: 27.17%
  - Turkmenistan: 39.57%
  - American Samoa: 10.38%
  - Puerto Rico: 19.79%
- Data sourced from UNESCO UIS database https://data360.worldbank.org/en/indicator/UNESCO_UIS_GRAD_STEM?sex=M&compBreak1=_Z&view=map
- Changes saved to df.tsv

## STEM Graduates Data Update
- Analyzed the dataset to identify countries with 0% STEM graduates
- Found 77 countries with 0% STEM graduates
- Updated STEM graduate percentages for countries where data was available from UNESCO UIS database:
  - Bolivia: 4.86%
  - Barbados: 8.63%
  - Bhutan: 6.46%
  - Comoros: 6.73%
  - Nepal: 8.59%
  - Palau: 2.13%
  - Trinidad and Tobago: 10.68%
- Skipped updates for Italy and Japan as they had existing data
- Some countries were not found in the UNESCO database and remained at 0%
- Changes saved to df.tsv
source: http://data.un.org/Data.aspx?q=graduate&d=UNESCO&f=series%3AFOSGP_56_F400

## STEM Graduates Data Update 
- Analyzed the dataset to identify languages with 0% STEM graduates
- Found 2,050 languages with 0% STEM graduates
- Updated STEM graduate percentages for territories using data from their parent countries:
  - Isle of Man: 26.32% (using United Kingdom's data)
  - Jersey: 26.32% (using United Kingdom's data)
- Changes saved to df.tsv

## STEM Graduates Data Update
- Analyzed the dataset to identify languages with 0% STEM graduates
- Found 2,045 languages with 0% STEM graduates
- Updated STEM graduate percentages for specific cases:
  - Latin (Italy): 24.20% (using Italy's data)
  - Kosovo: 28.13% (using Serbia's data)
- Changes saved to df.tsv

## STEM Graduates Data Update
- Analyzed the dataset to identify languages with 0% STEM graduates
- Found 2,045 languages with 0% STEM graduates
- Updated STEM graduate percentages for specific cases:
  - Yemen: 46.15% (using Oman's data as reference)
- Changes saved to df.tsv

## STEM Graduates Data Update
- Analyzed the dataset to identify languages with 0% STEM graduates
- Found 2,036 languages with 0% STEM graduates
- Updated STEM graduate percentages for specific cases:
  - Pakistan: 8.31% (calculated from data: 157,102 STEM graduates out of 1,891,244 total graduates) source: https://pakistanlink.org/Community/2023/Feb23/17/11.HTM?utm_source=chatgpt.com
- Changes saved to df.tsv

## STEM Graduates Data Update
- Analyzed the dataset to identify languages with 0% STEM graduates
- Found 1,992 languages with 0% STEM graduates
- Updated STEM graduate percentages for specific cases:
  - Macao S.A.R: 11.37% (data from UNESCO UIS database, 2023)
- Changes saved to df.tsv

## STEM Graduates Data Update
- Analyzed the dataset to identify languages with 0% STEM graduates
- Found 1,991 languages with 0% STEM graduates
- Updated STEM graduate percentages for specific cases:
  - China: 38.46% (calculated from data: 4.7 million STEM graduates out of 12.22 million total graduates in 2016)
  - Source: World Economic Forum and Chinese government statistics
  - Chinese stem grad is ~ 4.7 million in  2016,, source https://www.weforum.org/stories/2023/03/which-countries-students-are-getting-most-involved-in-stem/
  - total member is 12.22 million , source https://english.www.gov.cn/archive/statistics/202411/14/content_WS67358fe7c6d0868f4e8ecee6.html#:~:text=BEIJING%2C%20Nov.,official%20data%20released%20on%20Thursday.

- Changes saved to df.tsv

## African Education Statistics
Source: https://thedocs.worldbank.org/en/doc/764421611934520379-0090022021/original/OneAfricaTEandCovidupdated.pdf

### Tertiary Enrollment Rates by Country
- Mauritius: 40%
- Cabo Verde: 23.6%
- Ghana: 15%
- Togo: 15%
- Lesotho: 10%
- Niger: 4.4%

## STEM Graduates Data Update
- Analyzed the dataset to identify languages with 0% STEM graduates
- Updated STEM graduate percentages for specific cases:
  - Central African Republic: 21.33558% (using data from Cameroon as reference for similar regional context)
  - Congo Republic: 15.14% - Source: https://data360.worldbank.org/en/indicator/UNESCO_UIS_GRAD_STEM?sex=M&compBreak1=_Z&view=map
- Changes saved to df.tsv


## STEM Graduates Data Update
- Analyzed the dataset to identify languages with 0% STEM graduates
- Updated STEM graduate percentages for specific cases:
  - Tanzania - 13.649 Source: https://data360.worldbank.org/en/indicator/UNESCO_UIS_GRAD_STEM?sex=M&compBreak1=_Z&view=map
  - eSwatini - 4.069 Source: https://data360.worldbank.org/en/indicator/UNESCO_UIS_GRAD_STEM?sex=M&compBreak1=_Z&view=map
- Changes saved to df.tsv

## STEM Graduates Data Update - Regional Proxy Approximations
- Analyzed countries lacking STEM graduate data and used regional proxies for approximation
- Updated STEM graduate percentages using data from similar countries based on:
  - Geographic proximity
  - Shared language/colonial heritage
  - Similar education systems
  - Comparable development indicators

### Proxy Country Relationships

| Target Country | Proxy Country | Rationale |
|----------------|---------------|-----------|
| Mayotte | France | French overseas territory; directly follows French education system |
| Réunion | France | French overseas department; education system aligned with France |
| Gabon | Cameroon | Francophone neighbors with similar regional education patterns |
| Guinea-Bissau | Mozambique | Both Lusophone; similar colonial influence and educational challenges |
| Libya | Algeria | North African, Arab-speaking, similar post-secondary education structure |
| Mali | Burkina Faso | Francophone West Africa; similar education development and access |
| Malawi | Zambia | Anglophone Southern Africa; similar tertiary education levels |
| Nigeria | Ghana | Anglophone West Africa; large, diverse education systems; strong tertiary sector in Ghana used for benchmarking |
| Somalia | Ethiopia | Horn of Africa; both with under-resourced tertiary systems |
| South Sudan | Uganda | Geographic and historical ties; Uganda has stronger tertiary data |
| São Tomé and Principe | Angola | Lusophone countries; shared colonial heritage and small-scale systems |
| eSwatini | Lesotho | Southern Africa; similar income level and educational constraints |
| Togo | Benin | Francophone West Africa; comparable demographics and schooling structures |
| Zambia | Zimbabwe | Southern African neighbors; similar challenges and historical context |
| Ivory Coast | Burkina Faso | Francophone West Africa; similar colonial legacy, socio-economic status, and tertiary education development |
| Guinea | Burkina Faso | Shared language (French), similar education indicators, and regional position |
| Senegal | Burkina Faso | All three are part of the Francophone West African bloc; Burkina Faso provides more accessible comparative education data |
| Equatorial Guinea | Cameroon | Geographic proximity, similar size, Central African region, and French/Spanish colonial educational influence; Cameroon has better data availability |
| French Guiana | France | French overseas department; uses French national education system and statistics |
| Paraguay | Bolivia | Landlocked South American country with similar economic and educational development indicators; better data availability |
| Suriname | Guyana | Geographic neighbor with similar population size, post-colonial structure, and tertiary education patterns |
| French Polynesia | France | French overseas territory; follows French national education system |
| New Caledonia | France | French overseas territory with centralized educational administration |
| Wallis and Futuna | France | Also a French territory with aligned systems |
| Federated States of Micronesia | Marshall Islands | Micronesian region, similar size and education infrastructure |
| Pitcairn Islands | Fiji | Pitcairn is UK-administered but too small for direct data; Fiji as regional anchor |
| Kiribati | Fiji | Pacific Island with similar economic level and better data in Fiji |
| Nauru | Fiji | Small Pacific Island nation; shares regional education networks |
| Cook Islands | New Zealand | Associated with NZ; education system influenced and supported by NZ |
| Niue | New Zealand | Also associated with NZ; shares governance and education models |
| Papua New Guinea | Indonesia | Shared border and regional development dynamics; Indonesia has stronger tertiary data |
| Solomon Islands | Fiji | Regional neighbor with similar post-colonial education systems |
| East Timor (Timor-Leste) | Indonesia | Geographical proximity, shared post-colonial development struggles |
| Tonga | Fiji | South Pacific neighbors, similar economic status and education needs |
| Tuvalu | Fiji | Also in regional education partnerships with Fiji |
| Taiwan | South Korea | Economically developed; South Korea used as East Asian benchmark with full data availability |
| Guam | United States | U.S. territory; governed by U.S. federal education laws and systems |
| Northern Mariana Islands | United States | U.S. territory with alignment to U.S. educational structure |
| Vanuatu | Fiji | Regional education partner, similar size and structure |
| Greenland | Denmark | Autonomous territory of Denmark; follows Danish educational policies |
| Haiti | Dominican Republic | Shared island, Francophone vs. Hispanic contrast, but closest data-rich neighbor |
| Jamaica | Trinidad and Tobago | Anglophone Caribbean; T&T has more advanced tertiary education stats |
| Sint Maarten | Netherlands | Dutch territory; education system influenced by the Netherlands |
| Saint Vincent and the Grenadines | Dominican | Geographic, linguistic, and economic similarities; similar tertiary structure |

- Changes saved to df.tsv

## Endangerment Status 
- The 125 languages missing Endangerment Status data in [UNESCO WAL](https://en.wal.unesco.org/) have been assigned the approximative 'Potentially vulnerable' tag. In the future, more specific information on those languages could be retrieved from Ethnologue: Ethnologue, however, uses its own endangerment classification system. Pros and cons to be reviewed. The languages have the isocodes: 

| ISO Code |  |  | |  |  | |  |  |  |
|----------|----------|----------|----------|----------|----------|----------|----------|----------|----------|
| xvi      | dgw      | xul      | xni      | xww      | rnr      | dmd      | pnj      | yxl      | yga      |
| jbi      | yxg      | xpt      | xwk      | axe      | xyt      | xyj      | xyk      | gtu      | yyr      |
| dwu      | urf      | lja      | bos      | caj      | gqn      | kav      | xra      | pog      | xri      |
| gub      | pok      | slj      | nmj      | kym      | tsk      | mjg      | dnj      | mct      | kel      |
| fom      | mnh      | inj      | frk      | xnz      | sdt      | zrp      | ina      | epo      | oco      |
| sik      | hrv      | lur      | ssq      | szn      | mqc      | mxn      | kgw      | bzq      | lau      |
| puc      | kfi      | gac      | wsg      | dso      | esg      | kex      | ahr      | kru      | twm      |
| yol      | sth      | prd      | otk      | nrf      | sxm      | krr      | tgr      | bgl      | ltz      |
| lvs      | jbe      | zkd      | szd      | izz      | geg      | jjr      | scv      | act      | vel      |
| twd      | sdz      | stl      | nob      | lmh      | gyo      | pgd      | inp      | nom      | akl      |
| fbl      | lbl      | ubl      | ebk      | gar      | kze      | tbv      | hrc      | sam      | xss      |
| dgl      | srp      | rui      | css      | kju      | wnw      | xpq      | xlb      | ctc      | sno      |
| ska      | rpn      | ngh      | gic      | gku      |          |          |          |          |          |


## literacy rate
- Empty columns filled with the [CIA World Factbook](https://www.cia.gov/the-world-factbook/field/literacy/) when possible, when no data is available (mostly for highly developed countries) literacy approximated to 100%.    

## Educational Attainment Score Proxy Mapping
- Created proxy mappings for educational attainment scores based on similar relationships as STEM graduate percentages
- Used proxy countries with reliable data to estimate scores for territories and countries with limited data
- Considered factors such as:
  - Historical and current governance relationships
  - Educational system similarities
  - Geographic and cultural proximity
  - Economic development level
  - Data availability and quality

### Proxy Country Relationships for Educational Attainment

| Target Country | Proxy Country | Rationale |
|----------------|---------------|-----------|
| French Polynesia | France | French overseas territory; directly follows French education system |
| New Caledonia | France | French overseas territory; education aligned with French national system |
| Wallis and Futuna | France | Also a French territory; same education governance |
| Pitcairn Islands | Fiji | UK territory with no local higher education; Fiji is regional anchor |
| Greenland | Denmark | Autonomous territory of Denmark; follows Danish education policy |
| Isle of Man | United Kingdom | British Crown Dependency; education governed under UK influence |
| Jersey | United Kingdom | Similar to Isle of Man; UK-aligned education structure |
| Maldives | Sri Lanka | Geographic and cultural proximity; similar education development levels |
| Marshall Islands | United States | Compact of Free Association with U.S.; uses U.S.-influenced system |
| Malta | Italy | EU member with shared regional dynamics; Italy as larger neighbor with data |
| Aruba | Netherlands | Dutch constituent country; education system follows Dutch model |
| Sint Maarten | Netherlands | Dutch constituent country; education policy based on Dutch system |
| Nauru | Fiji | Small Pacific nation; Fiji serves as education hub for region |
| Cook Islands | New Zealand | Self-governing in free association with NZ; aligned education system |
| Niue | New Zealand | Same as Cook Islands; NZ-supported education |
| Palau | United States | Compact of Free Association with U.S.; American education system |
| Seychelles | Mauritius | Small island nations in Indian Ocean; Mauritius has richer data |
| Tuvalu | Fiji | Pacific neighbor; part of regional education partnerships |
| Taiwan | South Korea | Similar economic tier; South Korea has robust STEM data |
| American Samoa | United States | U.S. territory; follows U.S. federal education standards |
| Guam | United States | U.S. territory; governed under U.S. education system |
| Northern Mariana Islands | United States | U.S. commonwealth; U.S. education system applies |
| Puerto Rico | United States | U.S. territory with strong data coverage |

### Educational Attainment Score Calculation Methods

Two different approaches were used to calculate educational attainment scores:

1. For Latin (Italy):
   - Calculated the average of all educational attainment scores within Italy
   - This provides a more localized and contextually relevant score
   - Reflects the specific regional educational characteristics

2. For All Other Countries/Territories:
   - Used the direct average score from their designated proxy country
   - Example: French Polynesia uses France's average score
   - Example: Greenland uses Denmark's average score
   - This approach leverages the established proxy relationships detailed above


- Changes saved to df.tsv

## R&D Data Filling Update
- Completed filling in missing R&D data for countries using proxy relationships
- Applied proxy mapping based on:
  - Geographic proximity
  - Educational system similarities
  - Colonial and linguistic heritage
  - Economic development levels
  - Administrative relationships

### Key Proxy Relationships Used:
```python
proxy_mapping = {
    "Afghanistan": "Pakistan",  # Regional and educational similarity
    "Benin": "Burkina Faso",  # Francophone West Africa, shared colonial heritage
    "Bangladesh": "India",  # Regional similarity, shared historical education roots
    "Belize": "Jamaica",  # Anglophone Caribbean context
    "Barbados": "Trinidad and Tobago",  # Regional and economic peer
    "Bhutan": "Nepal",  # Geographically and economically similar
    "Central African Republic": "Cameroon",  # Regional peer with more data
    "Cameroon": "Burkina Faso",  # Used for multiple francophone comparisons
    "Nigeria": "Ghana",  # Education system and scale comparison
    "Comoros": "Mozambique",  # Indian Ocean, Lusophone regionally comparable
    "Dominica": "Trinidad and Tobago",  # Caribbean with better education stats
    "Eritrea": "Ethiopia",  # Shared history, border, and educational challenges
    "Fiji": "New Zealand",  # Educational partnerships and influence
    "French Guiana": "France",  # Overseas department; French education applies
    "French Polynesia": "France",  # Follows French education system
    "Mayotte": "France",  # French territory
    "New Caledonia": "France",  # French territory
    "Réunion": "France",  # French territory
    "Wallis and Futuna": "France",  # French territory
    "Federated States of Micronesia": "Marshall Islands",  # Regional peer
    "Pitcairn Islands": "Fiji",  # Regional anchor
    "Guinea": "Burkina Faso",  # West African francophone proxy
    "Guinea-Bissau": "Mozambique",  # Lusophone proxy
    "Equatorial Guinea": "Cameroon",  # Regional proximity and language overlap
    "Grenada": "Trinidad and Tobago",  # Anglophone Caribbean
    "Guyana": "Trinidad and Tobago",  # Regional peer with stronger data
    "Haiti": "Dominica",  # Shared island, better data
    "Isle of Man": "United Kingdom",  # UK Crown dependency
    "Jersey": "United Kingdom",  # Same as above
    "Kiribati": "Fiji",  # Pacific Island with shared education networks
    "Lebanon": "Egypt",  # MENA region with stronger education stats
    "Liberia": "Ghana",  # West African Anglophone peer
    "Libya": "Algeria",  # North African Arab-speaking peer
    "Maldives": "Sri Lanka",  # Regional neighbor with shared educational features
    "Marshall Islands": "United States of America",  # Compact of Free Association
    "Malta": "Italy",  # European Mediterranean peer
    "Malawi": "Zambia",  # Southern Africa comparison
    "Niger": "Burkina Faso",  # Francophone West Africa
    "Aruba": "Netherlands",  # Dutch constituent country
    "Sint Maarten": "Netherlands",  # Same as Aruba
    "Nauru": "Fiji",  # Regional peer with available data
    "Cook Islands": "New Zealand",  # Free association, NZ education system
    "Niue": "New Zealand",  # Same as Cook Islands
    "Palau": "United States of America",  # Compact of Free Association
    "Solomon Islands": "Fiji",  # Regional anchor
    "Sierra Leone": "Ghana",  # Anglophone West Africa
    "Somalia": "Ethiopia",  # Regional and contextual similarity
    "South Sudan": "Uganda",  # Geographic and post-conflict education system
    "São Tomé and Principe": "Angola",  # Lusophone small states
    "Suriname": "Guyana",  # Regional peer
    "Seychelles": "Mauritius",  # Small island nations with education parallels
    "Turkmenistan": "Kazakhstan",  # Post-Soviet, Central Asia peer
    "East Timor": "Indonesia",  # Neighbor and former administrator
    "Tonga": "Fiji",  # Pacific regional partner
    "Tuvalu": "Fiji",  # Same as Tonga
    "Taiwan": "South Korea",  # Economically developed peer
    "American Samoa": "United States of America",  # U.S. territory
    "Guam": "United States of America",  # U.S. territory
    "Northern Mariana Islands": "United States of America",  # U.S. commonwealth
    "Puerto Rico": "United States of America",  # U.S. territory
    "Italy": "Italy",  # Has its own data
    "Vanuatu": "Fiji",  # Regional educational hub
    "Samoa": "Fiji",  # Regional peer
    "Kosovo": "Republic of Serbia",  # Parent country proxy
    "Yemen": "Oman",  # Regional peer with better data
    "Pakistan": "Pakistan",  # Direct data available
    "Zimbabwe": "Zambia"  # Southern Africa peer
}
```

- Changes saved to df.tsv
