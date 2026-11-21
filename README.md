# e46test2

Store-ready source for an **E46 M3** instrument cluster theme.

Add this repository as a source in the MGU Store (`jsalicru/e46test2`).  
Install **Cluster Themes**.  
Select **E46 M3** in the theme list.

The layout is built to match the provided render (dual MPH/km/h, orange needles, /M badge, oil-temp gauge, classic orange LCD) and covers the cluster so only that theme is visible.

## Structure
- `apps/cluster_themes/` — the app
- `apps/cluster_themes/hud/layouts/e46test2.json` — the E46 M3 layout
- `shared/` — rendering engine including E36/E46 widget support
- `mgu-repo.json` — Store catalog definition
