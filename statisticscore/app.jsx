import * as Sentry from "@sentry/browser";

Sentry.init({
  dsn: "https://9e7d8f743b524be1941923c21df3e747@bugsink.jasmine.uber.space/1",

  // Alternatively, use `process.env.npm_package_version` for a dynamic release version
  // if your build tool supports it.
  release: "statistics@latest",

  integrations: [],
  tracesSampleRate: 0,
});
