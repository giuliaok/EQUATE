export const meta = {
  name: 'keyman-macro-adjudicate',
  description: 'Adjudicate Keyman macrolanguage->standard-variety mappings with adversarial verification',
  phases: [
    { title: 'Adjudicate', detail: 'one agent per macrolanguage decides standard variety' },
    { title: 'Verify', detail: 'adversarial skeptic checks each mapping' },
  ],
}

const CANDS = [
  { macro: 'ara', kb: 1, members: [['arb','Standard Arabic'],['arz','Egyptian Arabic'],['apc','Levantine Arabic'],['ary','Moroccan Arabic'],['arq','Algerian Arabic'],['acm','Mesopotamian Arabic'],['afb','Gulf Arabic'],['ars','Najdi Arabic'],['aeb','Tunisian Arabic'],['shu','Chadian Arabic'],['(+13 more regional varieties)','']] },
  { macro: 'aym', kb: 1, members: [['ayr','Central Aymara'],['ayc','Southern Aymara']] },
  { macro: 'bal', kb: 1, members: [['bcc','Southern Balochi'],['bgn','Western Balochi'],['bgp','Eastern Balochi']] },
  { macro: 'doi', kb: 1, members: [['dgo','Dogri']] },
  { macro: 'est', kb: 3, members: [['ekk','Estonian (standard)'],['vro','South Estonian / Voro']] },
  { macro: 'fas', kb: 5, members: [['pes','Western Farsi (Iranian Persian)'],['prs','Dari (Afghan Persian)']] },
  { macro: 'ful', kb: 3, members: [['fuc','Pulaar'],['fuf','Pular'],['ffm','Maasina Fulfulde'],['fub','Adamawa Fulfulde'],['fuh','Western Niger Fulfulde'],['fuv','Hausa States Fulfulde']] },
  { macro: 'gon', kb: 1, members: [['esg','Aheri Gondi'],['gno','Northern Gondi'],['wsg','Adilabad Gondi']] },
  { macro: 'grn', kb: 2, members: [['gug','Paraguayan Guarani'],['gui','Eastern Bolivian Guarani'],['gun','Mbya Guarani'],['nhd','Chiripa']] },
  { macro: 'ipk', kb: 1, members: [['esi','North Alaskan Inupiatun'],['esk','Seward Alaska Inupiatun']] },
  { macro: 'kau', kb: 4, members: [['knc','Central Kanuri'],['kby','Manga Kanuri']] },
  { macro: 'kpe', kb: 1, members: [['gkp','Guinea Kpelle'],['xpe','Liberia Kpelle']] },
  { macro: 'lah', kb: 2, members: [['pnb','Western Panjabi'],['skr','Saraiki'],['hnd','Southern Hindko'],['hno','Northern Hindko']] },
  { macro: 'lav', kb: 4, members: [['lvs','Standard Latvian']] },
  { macro: 'man', kb: 1, members: [['mnk','Mandinka'],['emk','Eastern Maninkakan'],['mlq','Western Maninkakan']] },
  { macro: 'ori', kb: 1, members: [['ory','Odia']] },
  { macro: 'orm', kb: 1, members: [['gaz','West Central Oromo'],['gax','Borana-Arsi-Guji Oromo'],['hae','Eastern Oromo'],['orc','Orma']] },
  { macro: 'pus', kb: 2, members: [['pbt','Southern Pashto (Kandahari)'],['pbu','Northern Pashto (Yusufzai)'],['pst','Central Pashto']] },
  { macro: 'que', kb: 2, members: [['quz','Cusco Quechua'],['quy','Ayacucho Quechua'],['quh','South Bolivian Quechua'],['(+28 more Quechua varieties)','']] },
  { macro: 'rom', kb: 2, members: [['rmy','Vlax Romani'],['rmn','Balkan Romani'],['rmc','Central Romani'],['(+4 more Romani varieties)','']] },
  { macro: 'sqi', kb: 2, members: [['als','Tosk Albanian (basis of Standard Albanian)'],['aln','Gheg Albanian'],['aae','Arbereshe Albanian'],['aat','Arvanitika Albanian']] },
  { macro: 'srd', kb: 1, members: [['src','Logudorese Sardinian'],['sro','Campidanese Sardinian'],['sdc','Sassarese Sardinian'],['sdn','Gallurese Sardinian']] },
  { macro: 'swa', kb: 1, members: [['swh','Swahili (coastal/standard)'],['swc','Congo Swahili']] },
  { macro: 'syr', kb: 1, members: [['aii','Assyrian Neo-Aramaic'],['cld','Chaldean Neo-Aramaic']] },
  { macro: 'tmh', kb: 1, members: [['taq','Tamasheq'],['thv','Tahaggart Tamahaq'],['thz','Tayart Tamajeq'],['ttq','Tawallammat Tamajaq']] },
  { macro: 'zap', kb: 2, members: [['zai','Isthmus Zapotec'],['(+32 more Zapotec varieties)','']] },
  { macro: 'zha', kb: 2, members: [['zyb','Yongbei Zhuang (basis of Standard Zhuang)'],['(+12 more Zhuang varieties)','']] },
]

const ADJ_SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['macro','has_single_standard','standard_iso','confidence','reasoning'],
  properties: {
    macro: { type: 'string' },
    has_single_standard: { type: 'boolean' },
    standard_iso: { type: ['string','null'], description: 'ISO 639-3 of the standard variety; MUST be one of the listed member isos; null if no single standard' },
    confidence: { type: 'string', enum: ['high','medium','low'] },
    reasoning: { type: 'string' },
  },
}
const VER_SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['macro','agree','corrected_iso','reasoning'],
  properties: {
    macro: { type: 'string' },
    agree: { type: 'boolean' },
    corrected_iso: { type: ['string','null'] },
    reasoning: { type: 'string' },
  },
}

const results = await pipeline(
  CANDS,
  (c) => agent(
    `You are a sociolinguistics expert. ISO 639-3 macrolanguage "${c.macro}" has these individual member languages present in a dataset:\n` +
    c.members.map(m => `  ${m[0]} = ${m[1]}`).join('\n') +
    `\n\nKeyman provides ${c.kb} keyboard(s) tagged with the generic macrolanguage code "${c.macro}". ` +
    `In practice a keyboard tagged with a macrolanguage code targets the STANDARD / principal written-literary variety, if one exists.\n\n` +
    `Decide: does "${c.macro}" have ONE widely-recognized standard or principal written/literary variety among the members above? ` +
    `If yes (e.g. Arabic->Standard Arabic arb, Persian->Iranian Persian pes, Estonian->ekk, Latvian->lvs, Swahili->swh), set has_single_standard=true and standard_iso to that member's iso. ` +
    `If it is a cover term with no single agreed standard written variety (e.g. Quechua, Zapotec, Romani, Fula, Tuareg, Pashto which has two literary standards), set has_single_standard=false and standard_iso=null. ` +
    `standard_iso MUST be one of the listed member isos (never a "(+N more)" placeholder). Be conservative: map only when the standard is genuinely well-established.`,
    { label: `adj:${c.macro}`, phase: 'Adjudicate', schema: ADJ_SCHEMA }
  ),
  (adj, c) => agent(
    `Skeptical review of a proposed mapping. Macrolanguage "${c.macro}": adjudicated has_single_standard=${adj.has_single_standard}, standard_iso=${adj.standard_iso}, reason="${adj.reasoning}".\n` +
    `Members: ${c.members.map(m=>m[0]+'='+m[1]).join(', ')}.\n\n` +
    `Try to REFUTE. Is the chosen variety truly THE standard written form (not merely the most populous)? Is there genuinely no single standard (should be null)? ` +
    `Default to agree=false when doubtful. corrected_iso = the iso you would use (a member iso) or null.`,
    { label: `ver:${c.macro}`, phase: 'Verify', schema: VER_SCHEMA }
  ).then(v => ({ macro: c.macro, adj, ver: v }))
)

const clean = (results || []).filter(Boolean)
const macroMap = {}
const macroDecisions = []
for (const r of clean) {
  const proposed = r.adj.has_single_standard ? r.adj.standard_iso : null
  const final = r.ver.agree ? proposed : (r.ver.corrected_iso ?? null)
  if (final && final.indexOf('+') === -1) macroMap[r.macro] = final
  macroDecisions.push({
    macro: r.macro,
    proposed_iso: proposed,
    confidence: r.adj.confidence,
    adj_reason: r.adj.reasoning,
    verifier_agree: r.ver.agree,
    verifier_iso: r.ver.corrected_iso,
    ver_reason: r.ver.reasoning,
    final_iso: final,
  })
}
return { macroMap, macroDecisions }
