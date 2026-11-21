# e46test2 — E46 M3 cluster layout

Drop-in layout for the Cluster Themes app on BMW iDrive 7 (MGU).

When loaded on the car it draws a full-cluster theme intended to look essentially indistinguishable from the provided render of a US-spec classic M cluster (dual MPH/km/h scale, orange needles, /M badge, oil-temp gauge, fuel & coolant, orange LCD).

## File
- `layouts/e46test2.json` — schemaVersion 2 layout (theme: e46m3)

## On the car
Copy `e46test2.json` into the Cluster Themes app’s `data/layouts/` folder (or use `scripts/deploy.sh` from the upstream apps repo).  
Select the layout named `e46test2` (or “E46 M3”) in the app.  
The theme covers the cluster so only the designed gauges and LCD are visible.

## Notes
Base structure comes from the high-fidelity E36-style theme in aidac/apps (photo-traced proportions, shader-drawn face, inertia needles).  
Tuned and rebranded here as the E46 M3 test layout to match the target render.
