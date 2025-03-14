

These are internal notes that won't make much sense to anybody other than me...
-- ymyke













# Release checklist

1. Create new branch with new version number
2. Code...
3. Run tests
4. Update documentation if necessary
5. Rebuild documentation if necessary, `pdoc -o docs -t docs/pdoc-dark-mode tessa`
6. Bump version, e.g., `poetry version 0.9.0` and commit new version
7. Make sure everything is checked in
8. Merge new branch into main
9. Write a summary of the changes and amend to the merge commit: `git commit --amend`
10. Also mention any resolved issues in the merge commit if applicable
11. Tag the merge commit, e.g., `git tag -a v0.9.0` and `git push --tags`
12. Delete the now merged branch
13. Push main
14. Create a new release on GitHub, pointing to the tag
15. Publish on pypi: `poetry build` and `poetry publish`


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


