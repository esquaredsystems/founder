source "https://rubygems.org"

# Only needed to preview the site on your own machine. GitHub Pages ignores
# this file's contents and builds with its own pinned versions.
#
# Jekyll 3.10 is the version GitHub Pages currently builds with, so previewing
# with it means what you see locally is what you get once you push.
gem "jekyll", "~> 3.10"

# The site sets `markdown: kramdown` with `input: GFM` in _config.yml.
gem "kramdown-parser-gfm", "~> 1.1"

# Ruby 3.0+ no longer ships webrick, which `jekyll serve` uses.
gem "webrick", "~> 1.8"

# Ruby 3.4+ no longer ships base64 as a default gem; safe_yaml requires it.
gem "base64"

# Ruby 3.4+ no longer ships bigdecimal as a default gem; Liquid requires it.
gem "bigdecimal"

# Windows and JRuby do not include zoneinfo files.
platforms :mingw, :x64_mingw, :mswin, :jruby do
  gem "tzinfo", ">= 1", "< 3"
  gem "tzinfo-data"
end

# Performance booster for watching directories on Windows.
gem "wdm", "~> 0.1", platforms: [:mingw, :x64_mingw, :mswin]

# If you would rather install the exact gem set GitHub Pages uses, comment out
# the `jekyll` and `kramdown-parser-gfm` lines above and uncomment this one.
# It pulls in far more (including native extensions) and is slower to install.
# gem "github-pages", group: :jekyll_plugins
