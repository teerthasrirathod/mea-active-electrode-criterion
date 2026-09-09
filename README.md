# An undeclared free parameter underneath *in vitro* microelectrode array metrics

Analysis code and recorded outputs for the paper of that title
(Teertha Sri Rathod Banoth, Independent Researcher, Khammam, Telangana, India).
Archived at <https://doi.org/10.5281/zenodo.22099882>.

Every quantity reported in the paper is regenerated from published files by one
of the scripts here. Nothing in this repository is a redistribution: all inputs
are the published files of Kapucu et al. (2022), released under CC BY 4.0, and
are obtained from the dataset itself.

## Getting the data

The Comparative MEA Dataset is deposited at G-Node/GIN,
<https://doi.org/10.12751/g-node.wvr3jf>, and described in
Kapucu, F. E., Vinogradov, A., Hyvärinen, T., Ylä-Outinen, L., and Narkilahti, S.
(2022), *Scientific Data*, <https://doi.org/10.1038/s41597-022-01242-4>.

The scripts expect it unpacked beside them as `data/<plate>/`, for example
`data/hPSC_MEA1/spikes/` and `data/hPSC_MEA1/summary/`. `data/` is gitignored.
GIN serves no HTTP range requests, so `scripts/fetch_spikes.py` and
`scripts/stream_h5.py` exist to work around that; `scripts/harvest_datainfo.py`
collects the per-recording metadata.

## What produces what

| script | produces |
|---|---|
| `verify_reproduction_348.py` | reproduction of the published counts, all 348 values |
| `verify_rat_na_cells.py` | whether Rat_MEA1's twelve bare `NA` cells are unrecorded wells or zeros |
| `verify_all.py` | first implementation, written independently; the 336-value basis, kept as the cross-check |
| `day3_threshold_landscape.py` | counts under each published criterion; Figure 1 |
| `derive_duration.py`, `duration_consistency.py` | recovered analysis duration |
| `ttx_ceiling_two_plates.py` | silenced-electrode distributions, both plates |
| `bound_inactive.py` | upper bound on recorded hardware failure |
| `figure4_replication.py` | MEA1 vs MEA2 correlation; Figure 2 |
| `figure3_ttx_distribution.py` | silenced-electrode distribution; Figure 3 |
| `threshold_suppression.py` | flagged-electrode position; anomalous-day distributions |
| `verify_threshold_suppression.py` | independent second implementation of the above |
| `claim_map.py` | every claim in the frozen set to its script and its number |

The reproduction of the published counts was implemented twice independently.
`verify_all.py` was written from scratch on 10 August 2026 without reusing the
earlier code, on the 336-value basis; `verify_reproduction_348.py` recomputes
over all 348 published cells after `verify_rat_na_cells.py` established that the
twelve bare `NA` entries on Rat_MEA1 are recorded wells returning zero rather
than missing recordings. The two agree where they overlap, and
`artefacts/reproduction_348.txt` reports both bases side by side.

## artefacts/

The recorded output of each script — the run of record for every number in the
paper. `claim_map_output.txt` is the map from each claim to the script and the
artefact that produce it.

`claim_map.py` validates that map against the manuscript source and against the
frozen claim set. The claim set is in `claim-set/`; the manuscript source is not
redistributed, so the script cannot be re-run against a fresh clone and the
committed output is the run of record.

## claim-set/

The frozen claim set, the record of the five claims withdrawn under it, and the
audit decisions log from the line-by-line pass. Deposited on posting day, with
`claim-set/README.md` describing what each file is. They are the working files
as written, not a version prepared for a reader.

## figures/

The three figures carried by the paper, as produced by the scripts above.

## Licence

The code in this repository is MIT-licensed (see `LICENSE`). The inputs it reads
are CC BY 4.0, © Kapucu et al. (2022), and are not redistributed here.

## Citation

If you use this code, please cite the paper and the underlying dataset. The
dataset is the more important of the two: the per-recording noisy-electrode
lists and the per-electrode spike times, published alongside the summary values,
are what make this reanalysis possible at all.
