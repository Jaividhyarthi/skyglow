---
name: SKYGLOW
colors:
  surface: '#fff8f4'
  surface-dim: '#e1d9d2'
  surface-bright: '#fff8f4'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#fbf2ec'
  surface-container: '#f5ece6'
  surface-container-high: '#efe7e0'
  surface-container-highest: '#e9e1db'
  on-surface: '#1e1b17'
  on-surface-variant: '#414944'
  inverse-surface: '#34302c'
  inverse-on-surface: '#f8efe9'
  outline: '#717974'
  outline-variant: '#c0c8c3'
  surface-tint: '#3c6756'
  primary: '#184436'
  on-primary: '#ffffff'
  primary-container: '#315c4c'
  on-primary-container: '#a4d2be'
  inverse-primary: '#a2d0bc'
  secondary: '#904c31'
  on-secondary: '#ffffff'
  secondary-container: '#fda685'
  on-secondary-container: '#783920'
  tertiary: '#503900'
  on-tertiary: '#ffffff'
  tertiary-container: '#6c4f0e'
  on-tertiary-container: '#ebc377'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#beedd8'
  primary-fixed-dim: '#a2d0bc'
  on-primary-fixed: '#002116'
  on-primary-fixed-variant: '#234e3f'
  secondary-fixed: '#ffdbcf'
  secondary-fixed-dim: '#ffb59a'
  on-secondary-fixed: '#380d00'
  on-secondary-fixed-variant: '#72351c'
  tertiary-fixed: '#ffdea4'
  tertiary-fixed-dim: '#e9c176'
  on-tertiary-fixed: '#261900'
  on-tertiary-fixed-variant: '#5d4200'
  background: '#fff8f4'
  on-background: '#1e1b17'
  surface-variant: '#e9e1db'
typography:
  display:
    fontFamily: Newsreader
    fontSize: 48px
    fontWeight: '400'
    lineHeight: 56px
    letterSpacing: -0.02em
  display-mobile:
    fontFamily: Newsreader
    fontSize: 32px
    fontWeight: '400'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-lg:
    fontFamily: Newsreader
    fontSize: 36px
    fontWeight: '400'
    lineHeight: 44px
    letterSpacing: -0.015em
  headline-lg-mobile:
    fontFamily: Newsreader
    fontSize: 26px
    fontWeight: '400'
    lineHeight: 34px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Newsreader
    fontSize: 24px
    fontWeight: '500'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Newsreader
    fontSize: 20px
    fontWeight: '500'
    lineHeight: 28px
  title-md:
    fontFamily: Geist
    fontSize: 16px
    fontWeight: '600'
    lineHeight: 24px
    letterSpacing: -0.005em
  title-sm:
    fontFamily: Geist
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
  body-lg:
    fontFamily: Geist
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 26px
  body-md:
    fontFamily: Geist
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 22px
  body-sm:
    fontFamily: Geist
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 18px
  label-md:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.02em
  label-sm:
    fontFamily: JetBrains Mono
    fontSize: 11px
    fontWeight: '500'
    lineHeight: 14px
    letterSpacing: 0.03em
  code-snippet:
    fontFamily: JetBrains Mono
    fontSize: 12.5px
    fontWeight: '400'
    lineHeight: 18px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  gutter: 1.5rem
  gutter-mobile: 1rem
  margin: 2.5rem
  margin-mobile: 1.25rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2.5rem
---

## Brand & Style

This design system establishes an editorial intelligence aesthetic: a fusion of prestigious investigative journalism (*The Financial Times*, *The Atlantic*) with precision developer-grade utility. The platform serves security researchers, open-source maintainers, venture analysts, and enterprise compliance teams evaluating the integrity, pedigree, and threat landscape of open-source software ecosystems.

### Core Philosophy
- **Investigative Authority**: Information architecture prioritizes depth, provenance, verifiable audit trails, and archival permanence over casual dashboards.
- **Literary Precision**: Interface composition treats code artifacts, security disclosures, and commit graphs with the quiet respect of an analytical whitepaper.
- **Physical Paperwork Metaphor**: Tactile, sunlit surfaces reminiscent of archival document folders, cold-pressed paper stock, and copperplate ink stamps.
- **Deliberate Absence of Tech Gimmicks**: Strictly zero purple/cyan "AI" gradients, zero glassmorphism, zero floating neomorphic glows, and zero dark-mode default tropes. Visual weight derives entirely from deliberate typographic cadence, ruled hairline frames, and unhurried spacing.

## Colors

The palette operates under an uncompromising warm, paper-anchored light paradigm. Surface tiers, borders, and contextual signal tokens are strictly non-digital in tone, referencing archival library papers, deep forest inks, and pigment-derived stains.

### Palette Architecture
- **Canvas Base (`#F8F5EF`)**: Warm ivory foundation simulating unbleached archival sheet. Never pure `#FFFFFF`.
- **Surface Elevation 1 (`#FFFCF7`)**: Pristine cream sheet used for primary content cards, data tables, and elevated dossiers.
- **Surface Elevation 2 (`#EEE8DD`)**: Oatmeal tone for structural sidebars, secondary inspection rails, and interactive code blocks.
- **Border & Rule (`#DDD5C9`)**: Warm taupe hairline divider across all internal grid lines and cards.
- **Typographic Neutral (`#302C28`)**: Deep roast espresso for high-contrast, effortless legibility without the harshness of pure black.
- **Subdued Text Neutral (`#766E65`)**: Muted warm stone for metadata, datestamps, and secondary captions.
- **Primary Brand / Action (`#315C4C`)**: Deep forest green signaling authoritative validation, verified claims, and primary actions.
- **Secondary Accent (`#B96D50`)**: Muted terracotta used for highlighted investigative anomalies and cross-references.
- **Tertiary Accent (`#C7A25A`)**: Antique mustard gold for selective badge accents and key metric callouts.

### Semantic Status Tokens
- **Verified / Safe**: Sage green (`#638A70`) on soft tint background (`#EFF4F0`).
- **Cautionary / Under Review**: Ochre amber (`#B98538`) on soft tint background (`#FAF5EC`).
- **Compromise / Critical Risk**: Brick red (`#B85E52`) on soft tint background (`#F9EFEB`).

## Typography

The typographic hierarchy orchestrates a tri-font structure balancing narrative reportage with computational verification.

1. **Editorial Headlines (`Newsreader`)**: Expressive, historical literary serif bringing intellectual weight and editorial gravitas to dossier titles, entity names, intelligence headers, and executive summaries.
2. **System Interface & Body (`Geist`)**: Rational, high-clarity neo-grotesque engineered for high-density tables, multi-column reading, metadata lists, and form controls.
3. **Evidence & Cryptographic Layer (`JetBrains Mono`)**: Strict tabular monospaced face applied to commit hashes, PGP key footprints, CVSS metrics, semantic versions, and raw payload diffs.

## Layout & Spacing

The layout philosophy mirrors an elite broadsheet newspaper mixed with a dense technical workbench. It utilizes a structured, modular 12-column grid system bounded by generous exterior gutters.

### Layout Mechanics
- **Canvas Shell**: Centered max-width container (`1440px`) resting on the warm ivory `#F8F5EF` canvas.
- **Editorial Columns**: High-density 12-column grid partitioned by explicit 1px `#DDD5C9` vertical hair-rules rather than arbitrary whitespace gaps.
- **Rhythm**: Consistent 8px baseline cadence governing padding and layout intervals. Sections are clearly segmented with hairline borders and quiet vertical margins (`space-xl`).
- **Breakpoints**:
  - **Desktop (≥ 1200px)**: 12 columns, multi-pane reading views (metadata rail + dossier body + telemetry sidebar).
  - **Tablet (768px – 1199px)**: 8 columns, collateral collapsible drawer.
  - **Mobile (< 768px)**: 4 columns, single-column document flow with sticky top breadcrumbs and pinned bottom navigation.

## Elevation & Depth

Visual hierarchy rejects drop shadows and translucent layering. Instead, depth is established entirely through **Tonal Surface Framing and Fine-Rule Enclosures**.

### Tactile Mechanics
- **Ground Floor**: Base application backdrop uses `#F8F5EF`.
- **Foreground Dossiers**: Elevated items rest on `#FFFCF7` bordered by razor-sharp 1px solid `#DDD5C9`.
- **Inset Recesses**: Code viewports, hash verifiers, and secondary inspector bars use sunken surface `#EEE8DD`.
- **Shadow Elimination**: Box shadows are strictly forbidden (`box-shadow: none`), except for an ultra-subtle ambient paper offset reserved solely for transient floating popovers and contextual dropdown menus (`0 4px 12px rgba(48, 44, 40, 0.05)`).
- **Physical Demarcations**: Sections divide cleanly with continuous solid 1px hairline rules, echoing print journal columns.

## Shapes

The design system enforces a restrained shape geometry. Large border radii, pill geometries, and playful curves are prohibited.

### Geometry Rules
- **Micro Radii (4px)**: Form inputs, contextual tags, badge pills, table selections, and standard action buttons (`roundedness: 1` equivalent to `0.25rem`).
- **Structural Radii (6px to 8px max)**: Master dossiers, analytical cards, modal windows, and tabbed panels.
- **Square Edges (0px)**: Data table cells, column dividers, vertical split-panes, and embedded code inspection terminals.

## Components

### Buttons
- **Primary**: Solid forest green (`#315C4C`), cream text (`#FFFCF7`), 4px corner radius, hairline inset ring, medium font weight (`Geist 14px`). Hover shifts gently to a darkened pine (`#25483B`).
- **Secondary / Outline**: Warm cream background (`#FFFCF7`), 1px solid `#DDD5C9` border, espresso text (`#302C28`). Hover shifts surface to oatmeal (`#EEE8DD`).
- **Ghost**: Transparent background, text colored `#302C28`, underline reveal on hover.

### Badges & Reputation Chips
- Monospace typographic treatment (`JetBrains Mono`, 11px uppercase).
- Height: 22px, corner radius: 4px.
- Minimal hairline border matching the status tint.
- **Risk Indicator (Compromised/Malicious)**: Tinted background (`#F9EFEB`), border (`#E4B8B2`), text (`#B85E52`).
- **Verified Maintainer**: Tinted background (`#EFF4F0`), border (`#B0C9B8`), text (`#315C4C`).
- **Suspicious Anomaly**: Tinted background (`#FAF5EC`), border (`#E0CEB0`), text (`#B98538`).

### Data Tables & Evidence Lists
- Header cells: `label-sm` in warm gray (`#766E65`), uppercase, bottom hairline border in `#DDD5C9`.
- Rows: Background `#FFFCF7`, alternating subtly with `#FDFBF8` for zebra striping. Row hover applies an immediate `#F5EFE6` wash.
- Cell dividers: Vertical hairline borders in `#DDD5C9` between structural metric columns.

### Form Inputs & Filters
- Background: `#FFFCF7`, border: 1px solid `#DDD5C9`, corner radius: 4px, text: `#302C28`.
- Focus state: Border transitions to `#315C4C` with a clean 1px outer offset ring in `#315C4C` (no blurred focus rings).
- Placeholder: Muted warm gray (`#766E65`).

### Dossier Cards & Panels
- Base container: `#FFFCF7` surface encapsulated by 1px solid `#DDD5C9`.
- Header section: Editorial headline in `Newsreader`, divided from the card body by a continuous horizontal rule.
- Code blocks: Sunken `#EEE8DD` container, monospace code layout, and copyable hash indicators.

### Intelligence Artifacts (Specialty Components)
- **Provenance Breadcrumb**: Monospace tree displaying repository lineage (`git:commit`, `pypi:package`, `npm:scope`) with arrow glyphs (`→`).
- **Reputation Scorecard**: High-contrast editorial card featuring display serif numerals, contextual warning stamps, and cryptographic verification seals.