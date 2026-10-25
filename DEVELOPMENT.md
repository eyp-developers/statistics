# Notes on development

## Frontend stuff

The current state of our frontend code is miserable, so from now onwards let's use modern frontend tooling and get rid of some old ugly dependencies whenever we can.

### statisticscore/app.jsx

This is the new entrypoint for all frontend code. As of writing only the Sentry SDK lives in there together with the configuration for Bugsink.

### Building

After making a change, run `npm run build` to rebuild `bundle.js`, which will hopefully one day contain all of our frontend code.
