

These are internal notes that won't make much sense to anybody other than me...
-- ymyke














# How to build pdoc documentation:

`pdoc -o docs -t docs/pdoc-dark-mode tessa`

- Maybe try the pdoc workflow Github action to automate this. Would require
  requirements.txt in the folder, which can be generated via `poetry export -f
  requirements.txt --output requirements.txt`

To simply run the doc locally, use this:

`pdoc -t docs/pdoc-dark-mode tessa`


## MetricHistory

- What about MetricHistory? -- I guess this is part of alerts? Or should this be another
  separate package? If so, why? -- Or should the whole thing be a library and alerts,
  ticker, metric history etc. be packages within it? -- Would MetricHistory be a
  glorified / persistent cache for tessa?

# Low prio stuff

- Do we have a timezone issue? Do the different APIs return datetimes in different
  timezones and should the standardized?


