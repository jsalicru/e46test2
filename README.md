# e46test2

Test repository for a custom instrument cluster layout aiming to match a provided high-quality **render** of a US-spec E36 M cluster as closely as possible (essentially indistinguishable at normal viewing distance).

## Contents
- `layouts/e46test2.json` — the layout (schemaVersion 2)
- `tools/gen_e36.py` — the generator script cloned from upstream (edit this and regenerate the JSON rather than hand-editing the large layout file)

## Approach
The base is the high-quality E36 theme from aidac/apps, which was traced from real cluster photos and already covers the same visual language (MPH dual scale, orange needles, /M badge, oil-temp gauge, bottom LCD).

Further work consists of measuring the reference render and adjusting dial centers, radii, tick groups, label placements, colors, needle rests, and LCD layout in the generator so the output matches the render.

## Usage
Regenerate (once fonts are available or paths adjusted):
```sh
python3 tools/gen_e36.py layouts/e46test2.json
```

For the Cluster Themes app / cluster-render on iDrive 7.
