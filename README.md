# Tsogo Alumni Society — Archive Website

Static archive of [tsogoalumni.org.za](https://tsogoalumni.org.za), hosted on GitHub Pages.

> **The Tsogo Alumni Society is currently on hiatus.** This site preserves the work and history of the society from 2009 to 2020.

---

## About the Society

The Tsogo Alumni Society was established to connect alumni of **Tsogo High School** (later Tsogo Secondary School) in Pretoria, South Africa. Run entirely by volunteers, the society:

- Organised annual career and study expos for current learners
- Ran bursary and scholarship programmes
- Hosted alumni networking events
- Supported school infrastructure improvement projects
- Published alumni profiles and community news

**NPO Registration No. 053-952-NPO**

---

## About This Repository

This repository contains the Jekyll source for the archived Tsogo Alumni Society website. It was converted from the original WordPress site (exported as a static HTML archive in January 2020) into a maintainable Jekyll site.

### What's in the archive

| Content | Count |
|---|---|
| Blog posts (Markdown) | 90 |
| Years covered | 2009–2020 |
| Categories | Alumni Profiles, Career Expo, Bursaries, School & Learners, Society News, and more |

### Site structure

```
tsogo-jekyll-archive/
├── _config.yml           # Jekyll + Minimal Mistakes configuration
├── _posts/               # 90 blog posts as Markdown (YYYY-MM-DD-slug.md)
├── _pages/               # Static pages (about, society, executive, year archive)
├── _data/navigation.yml  # Site navigation
├── _includes/            # Archive notice banner, year nav
├── _sass/                # Custom Tsogo brand skin (green #16b513 + gold #f0c040)
├── assets/
│   ├── css/main.scss     # SASS entry point
│   └── images/           # Logo and images
├── index.md              # Homepage (splash layout)
├── CNAME                 # Custom domain: tsogoalumni.org.za
├── Gemfile               # Ruby gem dependencies
└── convert.py            # Script used to convert HTML archive → Markdown
```

---

## Theme

Built with [Minimal Mistakes](https://mmistakes.github.io/minimal-mistakes/) Jekyll theme with a custom `tsogo` skin matching the original site's brand colours:

- **Green** `#16b513` — primary colour, links, navigation
- **Gold** `#f0c040` — accent colour, headings on archive pages
- **Dark** `#1a2a1a` — footer and hero overlay

---

## Local Development

**Requirements:** Ruby, Bundler

```bash
# Install dependencies
bundle install

# Serve locally with live reload
bundle exec jekyll serve --livereload
# Visit http://localhost:4000
```

---

## Deployment

The site deploys automatically via **GitHub Pages** on every push to `main`.

GitHub Pages builds the Jekyll source and serves it at:
- **https://tsogoalumni.org.za** (custom domain via CNAME)
- **https://tsogoalum.github.io** (GitHub Pages default)

### DNS configuration (at your registrar)

```
A     @   185.199.108.153
A     @   185.199.109.153
A     @   185.199.110.153
A     @   185.199.111.153
CNAME www tsogoalum.github.io
```

MX records for email forwarding (`info@tsogoalumni.org.za`) should be configured separately and are independent of the GitHub Pages A records.

---

## Contact

Email: [info@tsogoalumni.org.za](mailto:info@tsogoalumni.org.za)

Responses may be delayed — the society is currently on hiatus.

### Archived social media

- Facebook (Alumni Society): [facebook.com/tsogoalum](https://www.facebook.com/tsogoalum/)
- Facebook (Tsogo High School): [facebook.com/TsogoHighSchool](https://www.facebook.com/TsogoHighSchool)
- Twitter / X: [@tsogoalum](https://twitter.com/tsogoalum)

These accounts are no longer actively managed.
