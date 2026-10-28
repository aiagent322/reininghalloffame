# Reining Hall of Fame

Independent Bridle & Bit editorial archive, published at https://reininghalloffame.com.

The site is static HTML/CSS. The existing Cloudflare Pages workflow deploys `main`
and purges the configured Cloudflare zone after deployment.

## Content maintenance

`data/honorees.json` records NRHA's official recognition years and categories,
checked on October 28, 2026 against https://nrha.com/hall-fame/.
Joint listings are kept together as NRHA publishes them. The 120 Hall of Fame
records include 65 people/organization listings and 55 horses. The 24 Dale
Wilkinson Lifetime Achievement records are separate; these counts are records,
not a count of unique people.

`scripts/build_archive.py` creates the archive, class pages, profiles, category
pages, redirects, sitemap and corrected homepage content. Detailed recent
biographies link to their respective NRHA announcements. Older profiles use
concise, source-confirmed recognition records instead of the previous broken
or unverified biographies. The 2026 pages distinguish selection from the
forthcoming December 2 recognition ceremony.

After updating and verifying content:

```sh
python3 scripts/build_archive.py
python3 scripts/check_archive.py
git diff --check
```

Keep original slugs in the redirect map when consolidating aliases. An award
recipient who is also a Hall of Fame inductee has a distinct record in each
category. Do not label Lifetime Achievement alone as Hall of Fame induction.

The generated pages retain the original leather, cream and gold palette,
typography and profile layout. Analytics and the homepage advertising zone are
preserved. No public runtime service or language model is required.
