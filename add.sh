N=100

aws s3 ls s3://pmc-oa-opendata/ --no-sign-request \
| awk '{print $2}' \
| head -n $N \
| while read d; do
    prefix="${d%/}"
    out="data/pmc_sample/$prefix.xml"
    if [ -f "$out" ]; then
      echo "Skipping existing: $out"
      continue
    fi
    aws s3 cp "s3://pmc-oa-opendata/$prefix/$prefix.xml" "$out" --no-sign-request || true
  done