---
version: alpha
name: Cloudflare Light
description: A high-contrast, performance-forward light system with bright orange hero moments and restrained editorial typography.
colors:
  primary: "#ff5e1f"
  secondary: "#262626"
  tertiary: "#f0f0f0"
  neutral: "#ffffff"
  surface: "#ffffff"
  on-surface: "#262626"
  error: "#d92d20"
  accent-soft: "#fff4ec"
  accent-glow: "#fff1c7"
typography:
  headline-display:
    fontFamily: FT Kunst Grotesk
    fontSize: 56px
    fontWeight: 500
    lineHeight: 67px
    letterSpacing: -1.4px
  headline-lg:
    fontFamily: FT Kunst Grotesk
    fontSize: 43px
    fontWeight: 500
    lineHeight: 48px
    letterSpacing: -1.2px
  headline-md:
    fontFamily: FT Kunst Grotesk
    fontSize: 33px
    fontWeight: 500
    lineHeight: 40px
    letterSpacing: -0.45px
  headline-sm:
    fontFamily: FT Kunst Grotesk
    fontSize: 25px
    fontWeight: 500
    lineHeight: 32px
    letterSpacing: -0.8px
  body-lg:
    fontFamily: FT Kunst Grotesk
    fontSize: 19px
    fontWeight: 400
    lineHeight: 29px
    letterSpacing: -0.48px
  body-md:
    fontFamily: FT Kunst Grotesk
    fontSize: 16px
    fontWeight: 400
    lineHeight: 24px
    letterSpacing: -0.2px
  body-sm:
    fontFamily: FT Kunst Grotesk
    fontSize: 14px
    fontWeight: 400
    lineHeight: 20px
    letterSpacing: -0.1px
  label-lg:
    fontFamily: FT Kunst Grotesk
    fontSize: 16px
    fontWeight: 500
    lineHeight: 24px
    letterSpacing: -0.2px
  label-md:
    fontFamily: FT Kunst Grotesk
    fontSize: 16px
    fontWeight: 500
    lineHeight: 24px
    letterSpacing: -0.2px
  label-sm:
    fontFamily: FT Kunst Grotesk
    fontSize: 12px
    fontWeight: 500
    lineHeight: 16px
    letterSpacing: 0.02em
  mono-sm:
    fontFamily: Apercu Mono Pro
    fontSize: 12px
    fontWeight: 400
    lineHeight: 16px
    letterSpacing: 0.04em
rounded:
  none: 0px
  sm: 4px
  md: 8px
  lg: 12px
  xl: 20px
  full: 9999px
spacing:
  xs: 4px
  sm: 12px
  md: 24px
  lg: 48px
  xl: 80px
  gutter: 24px
  margin: 32px
components:
  button-primary:
    backgroundColor: "{colors.neutral}"
    textColor: "{colors.on-surface}"
    typography: "{typography.label-md}"
    rounded: "{rounded.full}"
    padding: 12px 24px
    height: 50px
  button-secondary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-surface}"
    typography: "{typography.label-md}"
    rounded: "{rounded.full}"
    padding: 12px 24px
    height: 50px
  button-tertiary:
    backgroundColor: "transparent"
    textColor: "{colors.on-surface}"
    typography: "{typography.body-md}"
    rounded: "{rounded.none}"
    padding: 0px
  card:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.neutral}"
    rounded: "{rounded.sm}"
    padding: 32px
  input:
    backgroundColor: "{colors.neutral}"
    textColor: "{colors.on-surface}"
    typography: "{typography.body-md}"
    rounded: "{rounded.full}"
    padding: 12px 16px
  chip:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.neutral}"
    typography: "{typography.label-sm}"
    rounded: "{rounded.full}"
    padding: 8px 16px
  nav-link:
    backgroundColor: "transparent"
    textColor: "{colors.on-surface}"
    typography: "{typography.body-md}"
    rounded: "{rounded.none}"
    padding: 0px
# Cloudflare Light

## Overview
Cloudflare presents a clean, confident, enterprise-oriented light theme with a strong orange accent and lots of white space. The tone is polished and technical, but the hero treatment adds energy and urgency without feeling playful. Overall density is moderate: navigation and utility areas are compact, while primary content blocks are expansive and highly legible.

## Colors
- **Primary (#ff5e1f):** The signature Cloudflare orange, used for large hero surfaces, accents, and prominent promotional moments. It feels energetic, protective, and unmistakably branded.
- **Secondary (#262626):** Deep charcoal used for body copy, navigation, and dark text on light backgrounds. It provides strong contrast without the harshness of pure black.
- **Tertiary (#f0f0f0):** A light neutral used for subtle separators, low-emphasis surfaces, and structural borders when needed. It keeps the UI airy and unobtrusive.
- **Neutral / Surface (#ffffff):** The dominant canvas color for the page and component backgrounds. It supports a clean, spacious, enterprise feel.
- **On-surface (#262626):** Primary readable text color on white or light surfaces, matching the secondary token for consistency.
- **Error (#d92d20):** Reserved for alerts and failures; it should stay visually distinct from the brand orange so warning states do not blur into the core identity.
- **Accent-soft (#fff4ec):** A pale peach tint that can support subtle warmth behind cards, panels, or callouts without competing with the main orange.
- **Accent-glow (#fff1c7):** A soft warm highlight useful for luminous hero effects and ambient emphasis, echoing the glowing lower edge seen in the screenshot.

## Typography
FT Kunst Grotesk is the primary voice across the system, giving the interface a modern, human, and slightly editorial character. Headline levels are medium weight and tightly tracked, with negative letter spacing that keeps large text compact and authoritative. Body text stays regular weight for readability, while labels and buttons move to 500 weight for clearer utility emphasis.

Use the largest styles for the main hero and section intros: `headline-display` for the primary statement, `headline-lg` and `headline-md` for supporting section titles, and `headline-sm` for smaller feature headers. `body-lg` and `body-md` cover marketing paragraphs and interface copy, with `body-sm` for secondary metadata. `label-md` is the preferred button and navigation weight, while `label-sm` supports small badges, pills, and utility text. The `mono-sm` style can be used for technical or system-like annotations when a coded accent is needed.

Uppercase is not dominant in the observed UI; instead, the brand relies on sentence case with confident spacing and size. Small pills and utility items may use compact tracking, but the system should avoid exaggerated letter spacing unless it is clearly decorative or mono-spaced.

## Layout
The layout is centered and container-based, with a wide maximum width and generous lateral gutters. The hero card sits in a large framed area with strong horizontal breathing room, while smaller navigation items remain tightly grouped at the top. Spacing follows a clean stepped rhythm using 4px, 12px, 24px, 48px, and 80px increments.

Section padding should feel generous, especially for major marketing blocks and feature showcases. Cards and callouts should typically use 32px internal padding, with 24px as a common minimum for smaller modules. Use larger vertical gaps between content groups to preserve the spacious, premium feel and to keep dense technical content from becoming visually heavy.

## Elevation & Depth
The system is mostly flat and depends on contrast, scale, and color blocking rather than heavy shadows. Depth is created through bright surfaces against white surroundings, subtle borders, and the occasional soft glow or inset highlight in hero treatments. When elevation is needed, it should be restrained and atmospheric rather than material-heavy.

Cards may use a faint multi-layer shadow, but it should stay soft and low-opacity. Avoid dramatic drop shadows; Cloudflare’s hierarchy comes from strong brand color, clean spacing, and crisp type rather than obvious floating layers.

## Shapes
The shape language is mostly controlled and rounded, with pill-shaped interactive elements and gently softened content containers. Buttons, chips, and small utility controls use `rounded.full` for a modern, approachable profile. Larger cards use `rounded.sm` so the page still feels structured and architectural.

Avoid sharp decorative cutouts or highly irregular forms. The design should feel engineered and dependable, with just enough rounding to soften the interface.

## Components
Buttons should follow two main patterns: a filled white primary button (`button-primary`) for the most important action, and a filled orange secondary button (`button-secondary`) for brand-forward emphasis. Both use pill radii, 12px by 24px padding, and a 50px height to match the prominent CTA style in the screenshot. Hover states should remain subtle, using slight tint shifts or contrast adjustments rather than animation-heavy effects. `button-tertiary` is best reserved for plain text links or utility actions.

Cards should use the `card` token: orange background, white text, 32px padding, and a small 4px radius. Keep card content centered or carefully aligned, with generous internal spacing and minimal border treatment. Any card used over the page background should feel like a headline stage, not a generic panel.

Inputs should be white, pill-shaped, and understated, matching the calm utility controls in the header. Use clear text contrast, minimal chrome, and focus states that rely on color or border emphasis rather than shadows. Search and compact controls should align closely with button sizing to preserve visual rhythm.

Chips and announcement pills should be compact, fully rounded, and highly legible. Use the `chip` style for conference banners, status tags, and contextual labels. Nav links should remain simple and low-friction, with no heavy styling beyond spacing and text weight.

Lists, checkboxes, and radio buttons were not prominent in the screenshot, so they should inherit the same visual discipline: subtle borders, strong contrast, and compact sizing. If they are introduced, they should feel functional rather than ornamental.

## Do's and Don'ts
- Do use strong white space to make the orange brand color feel premium and intentional.
- Do keep buttons pill-shaped and consistently sized, especially for key CTAs.
- Do use FT Kunst Grotesk for nearly all UI text to preserve brand consistency.
- Do keep shadows minimal and rely on color contrast for hierarchy.
- Don't introduce heavy glassmorphism, deep shadows, or complex skeuomorphic surfaces.
- Don't mix in unrelated accent colors that compete with the core orange and charcoal palette.
- Don't over-round cards or layout containers; reserve the fullest radii for buttons and pills.
- Don't compress headings too tightly; maintain the airy, editorial spacing seen in the hero.