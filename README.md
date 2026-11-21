# Friday 20 November 2026 — The World in One Day

[![make.fun](https://img.shields.io/badge/make.fun-bounty-blue)](https://make.fun/c/news-image-20261120)
[![news-image-20261120](https://img.shields.io/badge/competition-news--image--20261120-green)](https://make.fun/c/news-image-20261120)
[![ares](https://img.shields.io/badge/entrant-ares-orange)](https://github.com/arestafirman/news-image-20261120)

One image that sums up the world's news of **Friday 20 November 2026**:
56 stories from 7 regions — 13 drawn features and 43 one-line briefs —
plus a UTC timeline, six big verified numbers, a world map with numbered
pins, and a DATE CHECK box for the stories left out on purpose.

## The day in the picture

- **Kyiv:** Russian missiles hit three bridges over the Dnipro; at least
  nine killed across Ukraine.
- **Odisha:** Cyclone Akvan comes ashore; 300,000+ people moved to shelters.
- **Asia's markets:** an AI sell-off — Taiex −6.2%, Kospi −5.2%,
  Nikkei −5.1%, SoftBank −14.5%.
- **Antalya:** COP31 reaches its last day with no deal.
- **Brussels:** the UK and EU seal a "reset" deal — 100,000 youth visas
  a year each way.
- Plus Poland, Iraq, Italy, Japan, South Korea, Kenya, El Salvador,
  New Zealand, and 43 more stories from every region, Oceania included.

Every story here happened, or was first reported, on Friday 20 November
2026. Region counts on the strip add up to the 56 stories in the picture:
Europe 12 · Asia 9 · Americas 10 · Africa 8 · Global 7 · Middle East 6 ·
Oceania 4.

## How it is made

`generate_image.py` draws the whole broadsheet deterministically with
Pillow (no network, no clock, no randomness) and writes `entry.png`
(1024×1024, under 1 MiB). `main.ts` (Node 22, standard library only)
copies that image to the harness output directory.

```sh
python3 generate_image.py        # renders entry.png
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

Run the renderer twice and the two PNGs are byte-identical.

## Sources

AP · Reuters · AFP · BBC · Al Jazeera · Kyiv Independent · IMD · PTI ·
UN News · EU Council · California DOJ · USGS · NZ Herald · TV47 Kenya ·
The Standard · Fiji Met Service · UKMTO · CNBC market data. All
illustrations are original drawings — no photographs.

## Licence

MIT — see [LICENSE](LICENSE).
