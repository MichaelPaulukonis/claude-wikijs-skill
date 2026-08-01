# Example: daily journal convention

This is one convention for journaling with the wikijs skill - adapt paths,
titles, and section structure to your own wiki. Nothing here is enforced by
`wikijs.py`.

- Entry path: `journal/{year}/{month}/{day}-{weekday}` - month/day zero-padded,
  weekday lowercase full name. Example: `journal/2026/07/18-saturday`
- Entry title: `{day} {Weekday}` - e.g. `18 Saturday`
- Entry body starts empty; append plain lines under the title, promote anything
  longer than a couple of lines to its own `## Section`
- Parent pages: `journal` has `## Years`, `journal/{year}` has `## Months`,
  `journal/{year}/{month}` has `## Entries` with day links sorted by day
- Journaling flow: `get` today's page; if missing, `create` it (and any missing
  parents top-down, adding the link to each parent's list section); then
  `update --append`
- When linking a wiki page in a response, prefix with your wiki's base URL
  (e.g. `http://localhost/`) rather than a bare path - bare paths aren't
  clickable in most chat UIs.
