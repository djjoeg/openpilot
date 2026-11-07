set -e
P=/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pkg
rm -rf "$P/accord-lane-keeping" "$P/accord-lane-keeping.zip"
mkdir -p "$P/accord-lane-keeping"
tar -C /home/claude/deliver --exclude=__pycache__ --exclude=.ruff_cache --exclude=preview -cf - . | tar -C "$P/accord-lane-keeping" -xf -
cd "$P" && zip -qr accord-lane-keeping.zip accord-lane-keeping
unzip -l accord-lane-keeping.zip | tail -1
unzip -l accord-lane-keeping.zip | grep -c "\.stl$"
# sanity: the patches in the package match the ones in deliver, and they apply cleanly were checked earlier; compare checksums
sha1sum accord-lane-keeping/software/*.patch /home/claude/deliver/software/*.patch