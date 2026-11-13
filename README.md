# 8bit

Tooling for generating 8-bit style short videos.

## data/
- `countries-50m.json` — world country shapes (TopoJSON) from [world-atlas](https://github.com/topojson/world-atlas) (Natural Earth, public domain).
- `states-10m.json` — US state shapes from [us-atlas](https://github.com/topojson/us-atlas).
- `flags/*.png` — country flags rasterized from [flag-icons](https://github.com/lipis/flag-icons) (MIT, see `flags/LICENSE-flag-icons.txt`) with `tools/rasterize_flags.js`.

Regenerate flags:

    npm install flag-icons playwright
    node tools/rasterize_flags.js node_modules/flag-icons/flags/4x3 data/flags
