# Design System Specification: Kinetic Harmony

## 1. Overview & Creative North Star
The "Плечом к плечу" (Shoulder to Shoulder) experience is defined by the Creative North Star: **"The Collective Pulse."** 

Unlike traditional fitness apps that feel clinical or aggressive, this system prioritizes a high-end editorial aesthetic that balances the rugged nature of outdoor workouts with the sophisticated calm of community. We move beyond the "standard" Bento Grid by treating the layout as a living organism. Through intentional asymmetry, breathing room, and a shift from rigid borders to tonal depth, we create a UI that feels less like a utility and more like a premium digital companion.

## 2. Colors & Surface Philosophy
The palette utilizes a sophisticated Material-based tonal range centered around a high-octane Primary Orange, balanced by expansive, breathable neutrals.

### The Palette
- **Primary (`#9b2f00`):** Used for brand identity and high-impact actions.
- **Primary Container (`#c2410c`):** The "Community Pulse" color. Use this for hero Bento cells or active states.
- **Surface Tiers:** 
    - `surface-container-lowest` (#ffffff): Use for top-level cards to achieve maximum lift.
    - `surface-container-low` (#f3f4f5): Use for the main background of the app.
    - `surface-container-high` (#e7e8e9): Use for "sunken" interactive areas or secondary groupings.

### The "No-Line" Rule
To maintain a premium, editorial feel, **1px solid borders are strictly prohibited for sectioning.** Boundaries must be defined solely through background color shifts. A `surface-container-lowest` card sitting on a `surface-container-low` background provides enough contrast to be accessible while appearing infinitely more modern than a stroked box.

### The "Glass & Gradient" Rule
For floating action buttons (FABs) or navigation overlays, utilize **Glassmorphism**. Use a semi-transparent `surface` color with a `24px` backdrop blur. 
*Pro-tip:* For main CTA buttons, use a subtle linear gradient from `primary` to `primary-container` at a 135° angle to give the element "soul" and a tactile, three-dimensional quality.

## 3. Typography: Editorial Precision
The typography system uses **Inter** to bridge the gap between technical outdoor gear and human-centric community.

| Role | Token | Size/Weight | Purpose |
| :--- | :--- | :--- | :--- |
| **Display** | `display-md` | 2.75rem / Bold | High-impact workout stats. |
| **Headline** | `headline-sm` | 1.5rem / Semibold | Main screen headers (18px equivalent in base-16). |
| **Title** | `title-md` | 1.125rem / Medium | Bento cell titles. |
| **Body** | `body-md` | 0.875rem / Regular | Descriptive text (14px equivalent). |
| **Label** | `label-sm` | 0.6875rem / Medium | Micro-copy and secondary metadata. |

**The Hierarchy Rule:** Never center-align typography in a Bento cell unless it is a single-value stat. Use left-alignment with generous 12px internal padding to create a structured, "newspaper" scan pattern.

## 4. Elevation & Depth: Tonal Layering
We reject the standard "drop shadow" in favor of **Ambient Dimensionality.**

- **The Layering Principle:** Instead of shadows, stack your containers. Place a `surface-container-lowest` card (Pure White) on top of a `surface-container-low` background. This creates a natural, soft lift.
- **Ambient Shadows:** Shadows are reserved only for "floating" elements (e.g., active workout timers). Use `y=8, blur=24` with only `4-8%` opacity. The shadow color must be a tinted version of `on-surface` (dark navy/brown) rather than pure black to avoid a "dirty" look.
- **The "Ghost Border" Fallback:** If high-sunlight outdoor legibility requires a border, use the `outline-variant` token at **15% opacity**. It should be felt, not seen.

## 5. Components & The Bento Modular Grid
The Bento Grid uses a **16px gutter** and a **24px corner radius (`md`)** to maintain a friendly, approachable silhouette.

### Bento Cells (Cards)
*   **Forbid dividers.** Use `body-sm` typography or `8px` vertical spacing to separate content. 
*   **Internal Padding:** Uniform `12px` on all sides.
*   **Interactive State:** On press, a cell should scale down to `98%` and shift its background to `surface-container-highest`.

### Buttons
*   **Primary:** `primary-container` background with `on-primary` text. Use `full` (pill-shape) rounding.
*   **Secondary:** `surface-container-high` background. No border.
*   **Tertiary:** No background. `primary` text color with a `600` weight.

### Specialist Community Components
*   **The "Pulse" Chip:** A small chip using `tertiary-fixed` (#d8e2ff) to indicate active community workouts.
*   **The Workout Slot:** A vertical list item using `surface-container-lowest`. Instead of a divider line, use a `4px` left-accent bar in `primary` to denote the active selection.

## 6. Do’s and Don’ts

### Do
*   **Do** use asymmetrical grid spans (e.g., one wide 2-column cell followed by two 1-column cells) to create visual rhythm.
*   **Do** use `surface-variant` for inactive or "empty" states to create a "hollowed-out" effect.
*   **Do** prioritize whitespace. If a card feels crowded, move the metadata to a `label-sm` tier or increase the card's grid span.

### Don’t
*   **Don't** use pure black `#000000` for text. Use `on-surface` (#191c1d) to maintain the "Calm" mood.
*   **Don't** use 1px solid borders to separate list items. Use the spacing scale to create separation through "void."
*   **Don't** mix corner radiuses. Every container, whether it's a small chip or a large hero card, must follow the `md` (24px) or `sm` (8px) logic—never "in-between" values.