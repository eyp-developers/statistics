(() => {
  // node_modules/@sentry/core/build/esm/debug-build.js
  var DEBUG_BUILD = typeof __SENTRY_DEBUG__ === "undefined" || __SENTRY_DEBUG__;

  // node_modules/@sentry/core/build/esm/utils/worldwide.js
  var GLOBAL_OBJ = globalThis;

  // node_modules/@sentry/core/build/esm/utils/version.js
  var SDK_VERSION = "11.9.0";

  // node_modules/@sentry/core/build/esm/carrier.js
  function getMainCarrier() {
    getSentryCarrier(GLOBAL_OBJ);
    return GLOBAL_OBJ;
  }
  function getSentryCarrier(carrier) {
    const __SENTRY__ = carrier.__SENTRY__ = carrier.__SENTRY__ || {};
    __SENTRY__.version = __SENTRY__.version || SDK_VERSION;
    return __SENTRY__[SDK_VERSION] = __SENTRY__[SDK_VERSION] || {};
  }
  function getGlobalSingleton(name, creator, obj = GLOBAL_OBJ) {
    const __SENTRY__ = obj.__SENTRY__ = obj.__SENTRY__ || {};
    const carrier = __SENTRY__[SDK_VERSION] = __SENTRY__[SDK_VERSION] || {};
    return carrier[name] || (carrier[name] = creator());
  }

  // node_modules/@sentry/core/build/esm/utils/debug-logger.js
  var CONSOLE_LEVELS = [
    "debug",
    "info",
    "warn",
    "error",
    "log",
    "assert",
    "trace"
  ];
  var PREFIX = "Sentry Logger ";
  var originalConsoleMethods = {};
  function consoleSandbox(callback) {
    if (!("console" in GLOBAL_OBJ)) {
      return callback();
    }
    const console2 = GLOBAL_OBJ.console;
    const wrappedFuncs = {};
    const wrappedLevels = Object.keys(originalConsoleMethods);
    wrappedLevels.forEach((level) => {
      const originalConsoleMethod = originalConsoleMethods[level];
      wrappedFuncs[level] = console2[level];
      console2[level] = originalConsoleMethod;
    });
    try {
      return callback();
    } finally {
      wrappedLevels.forEach((level) => {
        console2[level] = wrappedFuncs[level];
      });
    }
  }
  function enable() {
    _getLoggerSettings().enabled = true;
  }
  function disable() {
    _getLoggerSettings().enabled = false;
  }
  function isEnabled() {
    return _getLoggerSettings().enabled;
  }
  function log(...args) {
    _maybeLog("log", ...args);
  }
  function warn(...args) {
    _maybeLog("warn", ...args);
  }
  function error(...args) {
    _maybeLog("error", ...args);
  }
  function _maybeLog(level, ...args) {
    if (!DEBUG_BUILD) {
      return;
    }
    if (isEnabled()) {
      consoleSandbox(() => {
        GLOBAL_OBJ.console[level](`${PREFIX}[${level}]:`, ...args);
      });
    }
  }
  function _getLoggerSettings() {
    if (!DEBUG_BUILD) {
      return { enabled: false };
    }
    return getGlobalSingleton("loggerSettings", () => ({ enabled: false }));
  }
  var debug = {
    /** Enable logging. */
    enable,
    /** Disable logging. */
    disable,
    /** Check if logging is enabled. */
    isEnabled,
    /** Log a message. */
    log,
    /** Log a warning. */
    warn,
    /** Log an error. */
    error
  };

  // node_modules/@sentry/core/build/esm/utils/stacktrace.js
  var STACKTRACE_FRAME_LIMIT = 50;
  var UNKNOWN_FUNCTION = "?";
  var WEBPACK_ERROR_REGEXP = /\(error: (.*)\)/;
  var STRIP_FRAME_REGEXP = /captureMessage|captureException/;
  function createStackParser(...parsers) {
    const sortedParsers = parsers.sort((a, b) => a[0] - b[0]).map((p) => p[1]);
    return (stack, skipFirstLines = 0, framesToPop = 0) => {
      const frames = [];
      const lines = stack.split("\n");
      for (let i = skipFirstLines; i < lines.length; i++) {
        let line = lines[i];
        if (line.length > 1024) {
          line = line.slice(0, 1024);
        }
        const cleanedLine = WEBPACK_ERROR_REGEXP.test(line) ? line.replace(WEBPACK_ERROR_REGEXP, "$1") : line;
        if (cleanedLine.includes("Error: ")) {
          continue;
        }
        for (const parser of sortedParsers) {
          const frame = parser(cleanedLine);
          if (frame) {
            frames.push(frame);
            break;
          }
        }
        if (frames.length >= STACKTRACE_FRAME_LIMIT + framesToPop) {
          break;
        }
      }
      return stripSentryFramesAndReverse(frames.slice(framesToPop));
    };
  }
  function stackParserFromStackParserOptions(stackParser) {
    if (Array.isArray(stackParser)) {
      return createStackParser(...stackParser);
    }
    return stackParser;
  }
  function stripSentryFramesAndReverse(stack) {
    if (!stack.length) {
      return [];
    }
    const localStack = Array.from(stack);
    if (/sentryWrapped/.test(getLastStackFrame(localStack).function || "")) {
      localStack.pop();
    }
    localStack.reverse();
    if (STRIP_FRAME_REGEXP.test(getLastStackFrame(localStack).function || "")) {
      localStack.pop();
      if (STRIP_FRAME_REGEXP.test(getLastStackFrame(localStack).function || "")) {
        localStack.pop();
      }
    }
    return localStack.slice(0, STACKTRACE_FRAME_LIMIT).map((frame) => ({
      ...frame,
      filename: frame.filename || getLastStackFrame(localStack).filename,
      function: frame.function || UNKNOWN_FUNCTION
    }));
  }
  function getLastStackFrame(arr) {
    return arr[arr.length - 1] || {};
  }
  var defaultFunctionName = "<anonymous>";
  function getFunctionName(fn) {
    try {
      if (!fn || typeof fn !== "function") {
        return defaultFunctionName;
      }
      return fn.name || defaultFunctionName;
    } catch {
      return defaultFunctionName;
    }
  }
  function getFramesFromEvent(event) {
    const exception = event.exception;
    if (exception) {
      const frames = [];
      try {
        exception.values.forEach((value) => {
          if (value.stacktrace.frames) {
            frames.push(...value.stacktrace.frames);
          }
        });
        return frames;
      } catch {
        return void 0;
      }
    }
    return void 0;
  }

  // node_modules/@sentry/core/build/esm/instrument/handlers.js
  var handlers = {};
  var instrumented = {};
  function addHandler(type, handler) {
    handlers[type] = handlers[type] || [];
    handlers[type].push(handler);
    return () => {
      const typeHandlers = handlers[type];
      if (typeHandlers) {
        const index = typeHandlers.indexOf(handler);
        if (index !== -1) {
          typeHandlers.splice(index, 1);
        }
      }
    };
  }
  function maybeInstrument(type, instrumentFn) {
    if (!instrumented[type]) {
      instrumented[type] = true;
      try {
        instrumentFn();
      } catch (e) {
        DEBUG_BUILD && debug.error(`Error while instrumenting ${type}`, e);
      }
    }
  }
  function triggerHandlers(type, data) {
    const typeHandlers = type && handlers[type];
    if (!typeHandlers) {
      return;
    }
    for (const handler of typeHandlers) {
      try {
        handler(data);
      } catch (e) {
        DEBUG_BUILD && debug.error(
          `Error while triggering instrumentation handler.
Type: ${type}
Name: ${getFunctionName(handler)}
Error:`,
          e
        );
      }
    }
  }

  // node_modules/@sentry/core/build/esm/instrument/globalError.js
  var _oldOnErrorHandler = null;
  function addGlobalErrorInstrumentationHandler(handler) {
    const type = "error";
    addHandler(type, handler);
    maybeInstrument(type, instrumentError);
  }
  function instrumentError() {
    _oldOnErrorHandler = GLOBAL_OBJ.onerror;
    GLOBAL_OBJ.onerror = function(msg, url, line, column, error2) {
      const handlerData = {
        column,
        error: error2,
        line,
        msg,
        url
      };
      triggerHandlers("error", handlerData);
      if (_oldOnErrorHandler) {
        return _oldOnErrorHandler.apply(this, arguments);
      }
      return false;
    };
    GLOBAL_OBJ.onerror.__SENTRY_INSTRUMENTED__ = true;
  }

  // node_modules/@sentry/core/build/esm/instrument/globalUnhandledRejection.js
  var _oldOnUnhandledRejectionHandler = null;
  function addGlobalUnhandledRejectionInstrumentationHandler(handler) {
    const type = "unhandledrejection";
    addHandler(type, handler);
    maybeInstrument(type, instrumentUnhandledRejection);
  }
  function instrumentUnhandledRejection() {
    _oldOnUnhandledRejectionHandler = GLOBAL_OBJ.onunhandledrejection;
    GLOBAL_OBJ.onunhandledrejection = function(e) {
      const handlerData = e;
      triggerHandlers("unhandledrejection", handlerData);
      if (_oldOnUnhandledRejectionHandler) {
        return _oldOnUnhandledRejectionHandler.apply(this, arguments);
      }
      return true;
    };
    GLOBAL_OBJ.onunhandledrejection.__SENTRY_INSTRUMENTED__ = true;
  }

  // node_modules/@sentry/core/build/esm/utils/is.js
  var objectToString = Object.prototype.toString;
  function isError(wat) {
    switch (objectToString.call(wat)) {
      case "[object Error]":
      case "[object Exception]":
      case "[object DOMException]":
      case "[object WebAssembly.Exception]":
        return true;
      default:
        return isInstanceOf(wat, Error);
    }
  }
  function isBuiltin(wat, className) {
    return objectToString.call(wat) === `[object ${className}]`;
  }
  function isErrorEvent(wat) {
    return isBuiltin(wat, "ErrorEvent");
  }
  function isDOMError(wat) {
    return isBuiltin(wat, "DOMError");
  }
  function isDOMException(wat) {
    return isBuiltin(wat, "DOMException");
  }
  function isString(wat) {
    return isBuiltin(wat, "String");
  }
  function isParameterizedString(wat) {
    return typeof wat === "object" && wat !== null && "__sentry_template_string__" in wat && "__sentry_template_values__" in wat;
  }
  function isPrimitive(wat) {
    return wat === null || isParameterizedString(wat) || typeof wat !== "object" && typeof wat !== "function";
  }
  function isPlainObject(wat) {
    return isBuiltin(wat, "Object");
  }
  function isObjectLike(wat) {
    return typeof wat === "object" && wat !== null;
  }
  function isEvent(wat) {
    return typeof Event !== "undefined" && isInstanceOf(wat, Event);
  }
  function isRegExp(wat) {
    return isBuiltin(wat, "RegExp");
  }
  function isThenable(wat) {
    return Boolean(wat?.then && typeof wat.then === "function");
  }
  function isInstanceOf(wat, base) {
    try {
      return wat instanceof base;
    } catch {
      return false;
    }
  }
  function isRequest(request) {
    return typeof Request !== "undefined" && isInstanceOf(request, Request);
  }

  // node_modules/@sentry/core/build/esm/utils/object.js
  function fill(source, name, replacementFactory) {
    if (!(name in source)) {
      return;
    }
    const original = source[name];
    if (typeof original !== "function") {
      return;
    }
    const wrapped = replacementFactory(original);
    if (typeof wrapped === "function") {
      markFunctionWrapped(wrapped, original);
    }
    try {
      source[name] = wrapped;
    } catch {
      DEBUG_BUILD && debug.log(`Failed to replace method "${name}" in object`, source);
    }
  }
  function addNonEnumerableProperty(obj, name, value) {
    try {
      Object.defineProperty(obj, name, {
        // enumerable: false, // the default, so we can save on bundle size by not explicitly setting it
        value,
        writable: true,
        configurable: true
      });
    } catch {
      DEBUG_BUILD && debug.log(`Failed to add non-enumerable property "${String(name)}" to object`, obj);
    }
  }
  function markFunctionWrapped(wrapped, original) {
    try {
      const proto = original.prototype || {};
      wrapped.prototype = original.prototype = proto;
      addNonEnumerableProperty(wrapped, "__sentry_original__", original);
    } catch {
    }
  }
  function getOriginalFunction(func) {
    return func.__sentry_original__;
  }
  function convertToPlainObject(value) {
    if (isError(value)) {
      return {
        message: value.message,
        name: value.name,
        stack: value.stack,
        ...getOwnProperties(value)
      };
    }
    if (isEvent(value)) {
      const { type, target, currentTarget, detail } = value;
      return {
        type,
        target,
        currentTarget,
        ...detail ? { detail } : {},
        ...getOwnProperties(value)
      };
    }
    return value;
  }
  function getOwnProperties(obj) {
    if (isObjectLike(obj)) {
      return Object.fromEntries(Object.entries(obj));
    }
    return {};
  }
  function extractExceptionKeysForMessage(exception) {
    const keys = Object.keys(convertToPlainObject(exception));
    keys.sort();
    return !keys[0] ? "[object has no keys]" : keys.join(", ");
  }

  // node_modules/@sentry/core/build/esm/utils/randomSafeContext.js
  var RESOLVED_RUNNER;
  function withRandomSafeContext(cb) {
    if (RESOLVED_RUNNER !== void 0) {
      return RESOLVED_RUNNER ? RESOLVED_RUNNER(cb) : cb();
    }
    const sym = /* @__PURE__ */ Symbol.for("__SENTRY_SAFE_RANDOM_ID_WRAPPER__");
    const globalWithSymbol = GLOBAL_OBJ;
    if (sym in globalWithSymbol && typeof globalWithSymbol[sym] === "function") {
      RESOLVED_RUNNER = globalWithSymbol[sym];
      return RESOLVED_RUNNER(cb);
    }
    RESOLVED_RUNNER = null;
    return cb();
  }
  function safeMathRandom() {
    return withRandomSafeContext(() => Math.random());
  }
  function safeDateNow() {
    return withRandomSafeContext(() => Date.now());
  }

  // node_modules/@sentry/core/build/esm/utils/normalizationHints.js
  var SENTRY_SKIP_NORMALIZATION = /* @__PURE__ */ Symbol.for("sentry.skipNormalization");
  var SENTRY_OVERRIDE_NORMALIZATION_DEPTH = /* @__PURE__ */ Symbol.for("sentry.overrideNormalizationDepth");
  function hasSkipNormalizationHint(value) {
    return Boolean(value[SENTRY_SKIP_NORMALIZATION]);
  }
  function getNormalizationDepthOverrideHint(value) {
    const v = value[SENTRY_OVERRIDE_NORMALIZATION_DEPTH];
    return typeof v === "number" ? v : void 0;
  }

  // node_modules/@sentry/core/build/esm/utils/normalize.js
  var stringifier;
  function setNormalizeStringifier(newStringifier) {
    stringifier = newStringifier;
  }
  function normalize(input, depth = 100, maxProperties = Infinity) {
    try {
      return visit("", input, depth, maxProperties);
    } catch (err) {
      return { ERROR: `**non-serializable** (${err})` };
    }
  }
  function normalizeToSize(object, depth = 3, maxSize = 100 * 1024) {
    const normalized = normalize(object, depth);
    if (jsonSize(normalized) > maxSize) {
      return normalizeToSize(object, depth - 1, maxSize);
    }
    return normalized;
  }
  function visit(key, value, depth = Infinity, maxProperties = Infinity, memo = memoBuilder()) {
    const [memoize, unmemoize] = memo;
    if (value == null || // this matches null and undefined -> eqeq not eqeqeq
    ["boolean", "string"].includes(typeof value) || typeof value === "number" && Number.isFinite(value)) {
      return value;
    }
    const stringified = stringifyValue(key, value);
    if (!stringified.startsWith("[object ")) {
      return stringified;
    }
    if (hasSkipNormalizationHint(value)) {
      return value;
    }
    const overrideDepth = getNormalizationDepthOverrideHint(value);
    const remainingDepth = overrideDepth !== void 0 ? overrideDepth : depth;
    if (remainingDepth === 0) {
      return stringified.replace("object ", "");
    }
    if (memoize(value)) {
      return "[Circular ~]";
    }
    const valueWithToJSON = value;
    if (valueWithToJSON && typeof valueWithToJSON.toJSON === "function") {
      try {
        const jsonValue = valueWithToJSON.toJSON();
        return visit("", jsonValue, remainingDepth - 1, maxProperties, memo);
      } catch {
      }
    }
    const normalized = Array.isArray(value) ? [] : {};
    let numAdded = 0;
    const visitable = convertToPlainObject(value);
    for (const visitKey in visitable) {
      if (!Object.prototype.hasOwnProperty.call(visitable, visitKey)) {
        continue;
      }
      if (numAdded >= maxProperties) {
        normalized[visitKey] = "[MaxProperties ~]";
        break;
      }
      const visitValue = visitable[visitKey];
      normalized[visitKey] = visit(visitKey, visitValue, remainingDepth - 1, maxProperties, memo);
      numAdded++;
    }
    unmemoize(value);
    return normalized;
  }
  function stringifyValue(key, value) {
    try {
      if (stringifier) {
        const stringified = stringifier(value);
        if (stringified) {
          return stringified;
        }
      }
      if (typeof global !== "undefined" && value === global) {
        return "[Global]";
      }
      if (typeof value === "number" && !Number.isFinite(value)) {
        return `[${value}]`;
      }
      if (typeof value === "function") {
        return `[Function: ${getFunctionName(value)}]`;
      }
      if (typeof value === "symbol") {
        return `[${String(value)}]`;
      }
      if (typeof value === "bigint") {
        return `[BigInt: ${String(value)}]`;
      }
      const objName = getConstructorName(value);
      return `[object ${objName}]`;
    } catch (err) {
      return `**non-serializable** (${err})`;
    }
  }
  function getConstructorName(value) {
    const prototype = Object.getPrototypeOf(value);
    return prototype?.constructor ? prototype.constructor.name : "null prototype";
  }
  function utf8Length(value) {
    return ~-encodeURI(value).split(/%..|./).length;
  }
  function jsonSize(value) {
    return utf8Length(JSON.stringify(value));
  }
  function memoBuilder() {
    const inner = /* @__PURE__ */ new WeakSet();
    function memoize(obj) {
      if (inner.has(obj)) {
        return true;
      }
      inner.add(obj);
      return false;
    }
    function unmemoize(obj) {
      inner.delete(obj);
    }
    return [memoize, unmemoize];
  }

  // node_modules/@sentry/core/build/esm/utils/string.js
  function truncate(str, max = 0) {
    if (typeof str !== "string" || max === 0) {
      return str;
    }
    return str.length <= max ? str : `${str.slice(0, max)}...`;
  }
  function safeJoin(input, delimiter) {
    if (!Array.isArray(input)) {
      return "";
    }
    const output = [];
    for (let i = 0; i < input.length; i++) {
      const value = input[i];
      if (isPrimitive(value)) {
        output.push(String(value));
      } else if (value instanceof Error) {
        output.push(value.message ? `${value.name}: ${value.message}` : value.name);
      } else {
        output.push(stringifyValue(void 0, value));
      }
    }
    return output.join(delimiter);
  }
  function isMatchingPattern(value, pattern, requireExactStringMatch = false) {
    if (!isString(value)) {
      return false;
    }
    if (isRegExp(pattern)) {
      return pattern.test(value);
    }
    if (isString(pattern)) {
      return requireExactStringMatch ? value === pattern : value.includes(pattern);
    }
    if (typeof pattern === "function") {
      return pattern(value);
    }
    return false;
  }
  function stringMatchesSomePattern(testString, patterns = [], requireExactStringMatch = false) {
    for (const pattern of patterns) {
      if (isMatchingPattern(testString, pattern, requireExactStringMatch)) {
        return true;
      }
    }
    return false;
  }

  // node_modules/@sentry/core/build/esm/utils/misc.js
  function getCrypto() {
    const gbl = GLOBAL_OBJ;
    return gbl.crypto || gbl.msCrypto;
  }
  var emptyUuid;
  function getRandomByte() {
    return safeMathRandom() * 16;
  }
  function uuid4(crypto = getCrypto()) {
    try {
      if (crypto?.randomUUID) {
        return withRandomSafeContext(() => crypto.randomUUID()).replace(/-/g, "");
      }
    } catch {
    }
    if (!emptyUuid) {
      emptyUuid = "10000000100040008000" + 1e11;
    }
    return emptyUuid.replace(
      /[018]/g,
      (c) => (
        // eslint-disable-next-line no-bitwise
        (c ^ (getRandomByte() & 15) >> c / 4).toString(16)
      )
    );
  }
  function getFirstException(event) {
    return event.exception?.values?.[0];
  }
  function getEventDescription(event) {
    const { message, event_id: eventId } = event;
    if (message) {
      return message;
    }
    const firstException = getFirstException(event);
    if (firstException) {
      if (firstException.type && firstException.value) {
        return `${firstException.type}: ${firstException.value}`;
      }
      return firstException.type || firstException.value || eventId || "<unknown>";
    }
    return eventId || "<unknown>";
  }
  function addExceptionTypeValue(event, value, type) {
    const exception = event.exception = event.exception || {};
    const values = exception.values = exception.values || [];
    const firstException = values[0] = values[0] || {};
    if (!firstException.value) {
      firstException.value = value || "";
    }
    if (!firstException.type) {
      firstException.type = type || "Error";
    }
  }
  function addExceptionMechanism(event, newMechanism) {
    const firstException = getFirstException(event);
    if (!firstException) {
      return;
    }
    applyExceptionMechanism(firstException, newMechanism);
  }
  function addExceptionMechanismToCapturedException(event, newMechanism) {
    const exceptions = event.exception?.values;
    const capturedException = exceptions?.find((exception) => exception.mechanism?.exception_id === 0) ?? exceptions?.[0];
    if (!capturedException) {
      return;
    }
    applyExceptionMechanism(capturedException, newMechanism);
  }
  function applyExceptionMechanism(exception, newMechanism) {
    const defaultMechanism = { type: "generic", handled: true };
    const currentMechanism = exception.mechanism;
    exception.mechanism = { ...defaultMechanism, ...currentMechanism, ...newMechanism };
    if (newMechanism && "data" in newMechanism) {
      exception.mechanism.data = { ...currentMechanism?.data, ...newMechanism.data };
    }
  }
  function checkOrSetAlreadyCaught(exception) {
    if (isAlreadyCaptured(exception)) {
      return true;
    }
    try {
      addNonEnumerableProperty(exception, "__sentry_captured__", true);
    } catch {
    }
    return false;
  }
  function isAlreadyCaptured(exception) {
    try {
      return exception.__sentry_captured__;
    } catch {
    }
  }

  // node_modules/@sentry/core/build/esm/utils/time.js
  var ONE_SECOND_IN_MS = 1e3;
  var CLOCK_DRIFT_THRESHOLD_MS = 1e3;
  var MAX_TIME_ORIGIN_SEGMENTS = 100;
  function dateTimestampInSeconds() {
    return safeDateNow() / ONE_SECOND_IN_MS;
  }
  var _timeOriginSegments = [];
  function createUnixTimestampInSecondsFunc() {
    const { performance: performance2 } = GLOBAL_OBJ;
    if (!performance2?.now || !performance2.timeOrigin) {
      if (performance2?.now) {
        _timeOriginSegments = [{ from: 0, origin: safeDateNow() - withRandomSafeContext(() => performance2.now()) }];
      }
      return dateTimestampInSeconds;
    }
    let correctedTimeOrigin = performance2.timeOrigin;
    _timeOriginSegments = [{ from: 0, origin: correctedTimeOrigin }];
    let isFirstCall = true;
    let lastCheckedPerformanceNow = 0;
    return () => {
      return withRandomSafeContext(() => {
        const performanceNow = performance2.now();
        const dateNow = Date.now();
        if (Math.abs(correctedTimeOrigin + performanceNow - dateNow) > CLOCK_DRIFT_THRESHOLD_MS) {
          correctedTimeOrigin = dateNow - performanceNow;
          if (isFirstCall) {
            _timeOriginSegments = [{ from: 0, origin: correctedTimeOrigin }];
          } else {
            _timeOriginSegments.push({ from: lastCheckedPerformanceNow, origin: correctedTimeOrigin });
            if (_timeOriginSegments.length > MAX_TIME_ORIGIN_SEGMENTS) {
              _timeOriginSegments.splice(1, 1);
            }
          }
        }
        isFirstCall = false;
        lastCheckedPerformanceNow = performanceNow;
        return (correctedTimeOrigin + performanceNow) / ONE_SECOND_IN_MS;
      });
    };
  }
  var _cachedTimestampInSecondsFn;
  function timestampInSeconds() {
    const func = _cachedTimestampInSecondsFn ?? (_cachedTimestampInSecondsFn = createUnixTimestampInSecondsFunc());
    return func();
  }

  // node_modules/@sentry/core/build/esm/session.js
  function makeSession(context) {
    const startingTime = timestampInSeconds();
    const session = {
      sid: uuid4(),
      init: true,
      timestamp: startingTime,
      started: startingTime,
      duration: 0,
      status: "ok",
      errors: 0,
      ignoreDuration: false,
      toJSON: () => sessionToJSON(session)
    };
    if (context) {
      updateSession(session, context);
    }
    return session;
  }
  function updateSession(session, context = {}) {
    if (context.user) {
      if (!session.ipAddress && context.user.ip_address) {
        session.ipAddress = context.user.ip_address;
      }
      if (!session.did && !context.did) {
        session.did = context.user.id || context.user.email || context.user.username;
      }
    }
    session.timestamp = context.timestamp || timestampInSeconds();
    if (context.abnormal_mechanism) {
      session.abnormal_mechanism = context.abnormal_mechanism;
    }
    if (context.ignoreDuration) {
      session.ignoreDuration = context.ignoreDuration;
    }
    if (context.sid) {
      session.sid = context.sid.length === 32 ? context.sid : uuid4();
    }
    if (context.init !== void 0) {
      session.init = context.init;
    }
    if (!session.did && context.did) {
      session.did = `${context.did}`;
    }
    if (typeof context.started === "number") {
      session.started = context.started;
    }
    if (session.ignoreDuration) {
      session.duration = void 0;
    } else if (typeof context.duration === "number") {
      session.duration = context.duration;
    } else {
      const duration = session.timestamp - session.started;
      session.duration = duration >= 0 ? duration : 0;
    }
    if (context.release) {
      session.release = context.release;
    }
    if (context.environment) {
      session.environment = context.environment;
    }
    if (!session.ipAddress && context.ipAddress) {
      session.ipAddress = context.ipAddress;
    }
    if (!session.userAgent && context.userAgent) {
      session.userAgent = context.userAgent;
    }
    if (typeof context.errors === "number") {
      session.errors = context.errors;
    }
    if (context.status) {
      session.status = context.status;
    }
  }
  function closeSession(session, status) {
    let context = {};
    if (status) {
      context = { status };
    } else if (session.status === "ok") {
      context = { status: "exited" };
    }
    updateSession(session, context);
  }
  function sessionToJSON(session) {
    return {
      sid: `${session.sid}`,
      init: session.init,
      // Make sure that sec is converted to ms for date constructor
      started: new Date(session.started * 1e3).toISOString(),
      timestamp: new Date(session.timestamp * 1e3).toISOString(),
      status: session.status,
      errors: session.errors,
      did: typeof session.did === "number" || typeof session.did === "string" ? `${session.did}` : void 0,
      duration: session.duration,
      abnormal_mechanism: session.abnormal_mechanism,
      attrs: {
        release: session.release,
        environment: session.environment,
        ip_address: session.ipAddress,
        user_agent: session.userAgent
      }
    };
  }

  // node_modules/@sentry/core/build/esm/utils/merge.js
  function merge(initialObj, mergeObj, levels = 2) {
    if (!mergeObj || typeof mergeObj !== "object" || levels <= 0) {
      return mergeObj;
    }
    if (initialObj && Object.keys(mergeObj).length === 0) {
      return initialObj;
    }
    const output = { ...initialObj };
    for (const key in mergeObj) {
      if (Object.prototype.hasOwnProperty.call(mergeObj, key)) {
        output[key] = merge(output[key], mergeObj[key], levels - 1);
      }
    }
    return output;
  }

  // node_modules/@sentry/core/build/esm/utils/propagationContext.js
  function generateTraceId() {
    return uuid4();
  }
  function generateSpanId() {
    return uuid4().substring(16);
  }

  // node_modules/@sentry/core/build/esm/scope.js
  var DEFAULT_MAX_BREADCRUMBS = 100;
  var Scope = class _Scope {
    // NOTE: Any field which gets added here should get added not only to the constructor but also to the `clone` method.
    constructor() {
      this._notifyingListeners = false;
      this._scopeListeners = [];
      this._eventProcessors = [];
      this._breadcrumbs = [];
      this._attachments = [];
      this._user = {};
      this._tags = {};
      this._attributes = {};
      this._extra = {};
      this._contexts = {};
      this._sdkProcessingMetadata = {};
      addNonEnumerableProperty(this, "refs", {});
      this._propagationContext = {
        traceId: generateTraceId(),
        sampleRand: safeMathRandom()
      };
    }
    /**
     * Clone all data from this scope into a new scope.
     */
    clone() {
      const newScope = new _Scope();
      newScope._breadcrumbs = [...this._breadcrumbs];
      newScope._tags = { ...this._tags };
      newScope._attributes = { ...this._attributes };
      newScope._extra = { ...this._extra };
      newScope._contexts = { ...this._contexts };
      if (this._contexts.flags) {
        newScope._contexts.flags = {
          values: [...this._contexts.flags.values]
        };
      }
      newScope._user = this._user;
      newScope._level = this._level;
      newScope._session = this._session;
      newScope._transactionName = this._transactionName;
      newScope._fingerprint = this._fingerprint;
      newScope._eventProcessors = [...this._eventProcessors];
      newScope._attachments = [...this._attachments];
      newScope._sdkProcessingMetadata = { ...this._sdkProcessingMetadata };
      newScope._propagationContext = { ...this._propagationContext };
      newScope._client = this._client;
      newScope._lastEventId = this._lastEventId;
      newScope._conversationId = this._conversationId;
      newScope.refs = { ...this.refs };
      return newScope;
    }
    /**
     * Update the client assigned to this scope.
     * Note that not every scope will have a client assigned - isolation scopes & the global scope will generally not have a client,
     * as well as manually created scopes.
     */
    setClient(client) {
      this._client = client;
    }
    /**
     * Set the ID of the last captured error event.
     * This is generally only captured on the isolation scope.
     */
    setLastEventId(lastEventId2) {
      this._lastEventId = lastEventId2;
    }
    /**
     * Get the client assigned to this scope.
     */
    getClient() {
      return this._client;
    }
    /**
     * Get the ID of the last captured error event.
     * This is generally only available on the isolation scope.
     */
    lastEventId() {
      return this._lastEventId;
    }
    /**
     * @inheritDoc
     */
    addScopeListener(callback) {
      this._scopeListeners.push(callback);
    }
    /**
     * Add an event processor that will be called before an event is sent.
     */
    addEventProcessor(callback) {
      this._eventProcessors.push(callback);
      return this;
    }
    /**
     * Set the user for this scope.
     * Set to `null` to unset the user.
     */
    setUser(user) {
      this._user = user || {
        email: void 0,
        id: void 0,
        ip_address: void 0,
        username: void 0
      };
      if (this._session) {
        updateSession(this._session, { user });
      }
      this._notifyScopeListeners();
      return this;
    }
    /**
     * Get the user from this scope.
     */
    getUser() {
      return this._user;
    }
    /**
     * Set the conversation ID for this scope.
     * Set to `null` to unset the conversation ID.
     */
    setConversationId(conversationId) {
      this._conversationId = conversationId || void 0;
      this._notifyScopeListeners();
      return this;
    }
    /**
     * Set an object that will be merged into existing tags on the scope,
     * and will be sent as tags data with the event.
     */
    setTags(tags) {
      this._tags = {
        ...this._tags,
        ...tags
      };
      this._notifyScopeListeners();
      return this;
    }
    /**
     * Set a single tag that will be sent as tags data with the event.
     */
    setTag(key, value) {
      return this.setTags({ [key]: value });
    }
    /**
     * Sets attributes onto the scope.
     *
     * These attributes are applied to logs, metrics and streamed spans.
     *
     * Supported attribute value types are `string`, `number`, `boolean`, `string[]`, `number[]` and `boolean[]`.
     *
     * @param newAttributes - The attributes to set on the scope, as key-value pairs.
     *
     * @example
     * ```typescript
     * scope.setAttributes({
     *   is_admin: true,
     *   payment_selection: 'credit_card',
     *   render_duration: 150,
     * });
     * ```
     */
    setAttributes(newAttributes) {
      this._attributes = {
        ...this._attributes,
        ...newAttributes
      };
      this._notifyScopeListeners();
      return this;
    }
    /**
     * Sets an attribute onto the scope.
     *
     * These attributes are applied to logs, metrics and streamed spans.
     *
     * Supported attribute value types are `string`, `number`, `boolean`, `string[]`, `number[]` and `boolean[]`.
     *
     * @param key - The attribute key.
     * @param value - The attribute value.
     *
     * @example
     * ```typescript
     * scope.setAttribute('is_admin', true);
     * scope.setAttribute('render_duration', 150);
     * ```
     */
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    setAttribute(key, value) {
      return this.setAttributes({ [key]: value });
    }
    /**
     * Removes the attribute with the given key from the scope.
     *
     * @param key - The attribute key.
     *
     * @example
     * ```typescript
     * scope.removeAttribute('is_admin');
     * ```
     */
    removeAttribute(key) {
      if (key in this._attributes) {
        delete this._attributes[key];
        this._notifyScopeListeners();
      }
      return this;
    }
    /**
     * Set an object that will be merged into existing extra on the scope,
     * and will be sent as extra data with the event.
     */
    setExtras(extras) {
      this._extra = {
        ...this._extra,
        ...extras
      };
      this._notifyScopeListeners();
      return this;
    }
    /**
     * Set a single key:value extra entry that will be sent as extra data with the event.
     */
    setExtra(key, extra) {
      this._extra = { ...this._extra, [key]: extra };
      this._notifyScopeListeners();
      return this;
    }
    /**
     * Sets the fingerprint on the scope to send with the events.
     * @param {string[]} fingerprint Fingerprint to group events in Sentry.
     */
    setFingerprint(fingerprint) {
      this._fingerprint = fingerprint;
      this._notifyScopeListeners();
      return this;
    }
    /**
     * Sets the level on the scope for future events.
     */
    setLevel(level) {
      this._level = level;
      this._notifyScopeListeners();
      return this;
    }
    /**
     * Sets the transaction name on the scope so that the name of e.g. taken server route or
     * the page location is attached to future events.
     *
     * IMPORTANT: Calling this function does NOT change the name of the currently active
     * root span. If you want to change the name of the active root span, use
     * `Sentry.updateSpanName(rootSpan, 'new name')` instead.
     *
     * By default, the SDK updates the scope's transaction name automatically on sensible
     * occasions, such as a page navigation or when handling a new request on the server.
     */
    setTransactionName(name) {
      this._transactionName = name;
      this._notifyScopeListeners();
      return this;
    }
    /**
     * Sets context data with the given name.
     * Data passed as context will be normalized. You can also pass `null` to unset the context.
     * Note that context data will not be merged - calling `setContext` will overwrite an existing context with the same key.
     */
    setContext(key, context) {
      if (context === null) {
        delete this._contexts[key];
      } else {
        this._contexts[key] = context;
      }
      this._notifyScopeListeners();
      return this;
    }
    /**
     * Set the session for the scope.
     */
    setSession(session) {
      if (!session) {
        delete this._session;
      } else {
        this._session = session;
      }
      this._notifyScopeListeners();
      return this;
    }
    /**
     * Get the session from the scope.
     */
    getSession() {
      return this._session;
    }
    /**
     * Updates the scope with provided data. Can work in three variations:
     * - plain object containing updatable attributes
     * - Scope instance that'll extract the attributes from
     * - callback function that'll receive the current scope as an argument and allow for modifications
     */
    update(captureContext) {
      if (!captureContext) {
        return this;
      }
      const scopeToMerge = typeof captureContext === "function" ? captureContext(this) : captureContext;
      const scopeInstance = scopeToMerge instanceof _Scope ? scopeToMerge.getScopeData() : isPlainObject(scopeToMerge) ? captureContext : void 0;
      const {
        tags,
        attributes,
        extra,
        user,
        contexts,
        level,
        fingerprint = [],
        propagationContext,
        conversationId
      } = scopeInstance || {};
      this._tags = { ...this._tags, ...tags };
      this._attributes = { ...this._attributes, ...attributes };
      this._extra = { ...this._extra, ...extra };
      this._contexts = { ...this._contexts, ...contexts };
      if (user && Object.keys(user).length) {
        this._user = user;
      }
      if (level) {
        this._level = level;
      }
      if (fingerprint.length) {
        this._fingerprint = fingerprint;
      }
      if (propagationContext) {
        this._propagationContext = propagationContext;
      }
      if (conversationId) {
        this._conversationId = conversationId;
      }
      return this;
    }
    /**
     * Adds a breadcrumb to the scope.
     * By default, the last 100 breadcrumbs are kept.
     */
    addBreadcrumb(breadcrumb, maxBreadcrumbs) {
      const maxCrumbs = typeof maxBreadcrumbs === "number" ? maxBreadcrumbs : DEFAULT_MAX_BREADCRUMBS;
      if (maxCrumbs <= 0) {
        return this;
      }
      const mergedBreadcrumb = {
        timestamp: dateTimestampInSeconds(),
        ...breadcrumb,
        // Breadcrumb messages can theoretically be infinitely large and they're held in memory so we truncate them not to leak (too much) memory
        message: breadcrumb.message ? truncate(breadcrumb.message, 2048) : breadcrumb.message
      };
      this._breadcrumbs.push(mergedBreadcrumb);
      if (this._breadcrumbs.length > maxCrumbs) {
        this._breadcrumbs = this._breadcrumbs.slice(-maxCrumbs);
      }
      this._notifyScopeListeners();
      return this;
    }
    /**
     * Get the last breadcrumb of the scope.
     */
    getLastBreadcrumb() {
      return this._breadcrumbs[this._breadcrumbs.length - 1];
    }
    /**
     * Clear all breadcrumbs from the scope.
     */
    clearBreadcrumbs() {
      this._breadcrumbs = [];
      this._notifyScopeListeners();
      return this;
    }
    /**
     * Add an attachment to the scope.
     */
    addAttachment(attachment) {
      this._attachments.push(attachment);
      return this;
    }
    /**
     * Clear all attachments from the scope.
     */
    clearAttachments() {
      this._attachments = [];
      return this;
    }
    /**
     * Get the data of this scope, which should be applied to an event during processing.
     */
    getScopeData() {
      return {
        breadcrumbs: this._breadcrumbs,
        attachments: this._attachments,
        contexts: this._contexts,
        tags: this._tags,
        attributes: this._attributes,
        extra: this._extra,
        user: this._user,
        level: this._level,
        fingerprint: this._fingerprint || [],
        eventProcessors: this._eventProcessors,
        propagationContext: this._propagationContext,
        sdkProcessingMetadata: this._sdkProcessingMetadata,
        transactionName: this._transactionName,
        conversationId: this._conversationId
      };
    }
    /**
     * Add data which will be accessible during event processing but won't get sent to Sentry.
     */
    setSDKProcessingMetadata(newData) {
      this._sdkProcessingMetadata = merge(this._sdkProcessingMetadata, newData, 2);
      return this;
    }
    /**
     * Add propagation context to the scope, used for distributed tracing
     */
    setPropagationContext(context) {
      this._propagationContext = context;
      return this;
    }
    /**
     * Get propagation context from the scope, used for distributed tracing
     */
    getPropagationContext() {
      return this._propagationContext;
    }
    /**
     * Capture an exception for this scope.
     *
     * @returns {string} The id of the captured Sentry event.
     */
    captureException(exception, hint) {
      const eventId = hint?.event_id || uuid4();
      if (!this._client) {
        DEBUG_BUILD && debug.warn("No client configured on scope - will not capture exception!");
        return eventId;
      }
      const syntheticException = new Error("Sentry syntheticException");
      this._client.captureException(
        exception,
        {
          originalException: exception,
          syntheticException,
          ...hint,
          event_id: eventId
        },
        this
      );
      return eventId;
    }
    /**
     * Capture a message for this scope.
     *
     * @returns {string} The id of the captured message.
     */
    captureMessage(message, level, hint) {
      const eventId = hint?.event_id || uuid4();
      if (!this._client) {
        DEBUG_BUILD && debug.warn("No client configured on scope - will not capture message!");
        return eventId;
      }
      const syntheticException = hint?.syntheticException ?? new Error(message);
      this._client.captureMessage(
        message,
        level,
        {
          originalException: message,
          syntheticException,
          ...hint,
          event_id: eventId
        },
        this
      );
      return eventId;
    }
    /**
     * Capture a Sentry event for this scope.
     *
     * @returns {string} The id of the captured event.
     */
    captureEvent(event, hint) {
      const eventId = event.event_id || hint?.event_id || uuid4();
      if (!this._client) {
        DEBUG_BUILD && debug.warn("No client configured on scope - will not capture event!");
        return eventId;
      }
      this._client.captureEvent(event, { ...hint, event_id: eventId }, this);
      return eventId;
    }
    /**
     * This will be called on every set call.
     */
    _notifyScopeListeners() {
      if (!this._notifyingListeners) {
        this._notifyingListeners = true;
        this._scopeListeners.forEach((callback) => {
          callback(this);
        });
        this._notifyingListeners = false;
      }
    }
  };

  // node_modules/@sentry/core/build/esm/defaultScopes.js
  function getDefaultCurrentScope() {
    return getGlobalSingleton("defaultCurrentScope", () => new Scope());
  }
  function getDefaultIsolationScope() {
    return getGlobalSingleton("defaultIsolationScope", () => new Scope());
  }

  // node_modules/@sentry/core/build/esm/tracing/constants.js
  var SUPPRESS_TRACING_KEY = "__SENTRY_SUPPRESS_TRACING__";

  // node_modules/@sentry/core/build/esm/utils/chain-and-copy-promiselike.js
  var isActualPromise = (p) => p instanceof Promise && !p[kChainedCopy];
  var kChainedCopy = /* @__PURE__ */ Symbol("chained PromiseLike");
  var chainAndCopyPromiseLike = (original, onSuccess, onError) => {
    const chained = original.then(
      (value) => {
        onSuccess(value);
        return value;
      },
      (err) => {
        onError(err);
        throw err;
      }
    );
    return isActualPromise(chained) && isActualPromise(original) ? chained : copyProps(original, chained);
  };
  var copyProps = (original, chained) => {
    if (!chained) return original;
    let mutated = false;
    for (const key in original) {
      if (key in chained) continue;
      mutated = true;
      const value = original[key];
      if (typeof value === "function") {
        Object.defineProperty(chained, key, {
          value: (...args) => value.apply(original, args),
          enumerable: true,
          configurable: true,
          writable: true
        });
      } else {
        chained[key] = value;
      }
    }
    if (mutated) Object.assign(chained, { [kChainedCopy]: true });
    return chained;
  };

  // node_modules/@sentry/core/build/esm/asyncContext/stackStrategy.js
  var AsyncContextStack = class {
    constructor(scope, isolationScope) {
      let assignedScope;
      if (!scope) {
        assignedScope = new Scope();
      } else {
        assignedScope = scope;
      }
      let assignedIsolationScope;
      if (!isolationScope) {
        assignedIsolationScope = new Scope();
      } else {
        assignedIsolationScope = isolationScope;
      }
      this._stack = [{ scope: assignedScope }];
      this._isolationScope = assignedIsolationScope;
    }
    /**
     * Fork a scope for the stack.
     */
    withScope(callback) {
      const scope = this._pushScope();
      let maybePromiseResult;
      try {
        maybePromiseResult = callback(scope);
      } catch (e) {
        this._popScope();
        throw e;
      }
      if (isThenable(maybePromiseResult)) {
        return chainAndCopyPromiseLike(
          maybePromiseResult,
          () => this._popScope(),
          () => this._popScope()
        );
      }
      this._popScope();
      return maybePromiseResult;
    }
    /**
     * Get the client of the stack.
     */
    getClient() {
      return this.getStackTop().client;
    }
    /**
     * Returns the scope of the top stack.
     */
    getScope() {
      return this.getStackTop().scope;
    }
    /**
     * Get the isolation scope for the stack.
     */
    getIsolationScope() {
      return this._isolationScope;
    }
    /**
     * Returns the topmost scope layer in the order domain > local > process.
     */
    getStackTop() {
      return this._stack[this._stack.length - 1];
    }
    /**
     * Push a scope to the stack.
     */
    _pushScope() {
      const scope = this.getScope().clone();
      this._stack.push({
        client: this.getClient(),
        scope
      });
      return scope;
    }
    /**
     * Pop a scope from the stack.
     */
    _popScope() {
      if (this._stack.length <= 1) return false;
      return !!this._stack.pop();
    }
  };
  function getAsyncContextStack() {
    const registry = getMainCarrier();
    const sentry = getSentryCarrier(registry);
    return sentry.stack = sentry.stack || new AsyncContextStack(getDefaultCurrentScope(), getDefaultIsolationScope());
  }
  function withScope(callback) {
    return getAsyncContextStack().withScope(callback);
  }
  function withSetScope(scope, callback) {
    const stack = getAsyncContextStack();
    return stack.withScope(() => {
      stack.getStackTop().scope = scope;
      return callback(scope);
    });
  }
  function withIsolationScope(callback) {
    return getAsyncContextStack().withScope(() => {
      return callback(getAsyncContextStack().getIsolationScope());
    });
  }
  function getStackAsyncContextStrategy() {
    return {
      suppressTracing: suppressTracingInStack,
      withIsolationScope,
      withScope,
      withSetScope,
      withSetIsolationScope: (_isolationScope, callback) => {
        return withIsolationScope(callback);
      },
      getCurrentScope: () => getAsyncContextStack().getScope(),
      getIsolationScope: () => getAsyncContextStack().getIsolationScope()
    };
  }
  function suppressTracingInStack(callback) {
    return withScope((scope) => {
      scope.setSDKProcessingMetadata({ [SUPPRESS_TRACING_KEY]: true });
      const res = callback();
      scope.setSDKProcessingMetadata({ [SUPPRESS_TRACING_KEY]: void 0 });
      return res;
    });
  }

  // node_modules/@sentry/core/build/esm/asyncContext/index.js
  function getAsyncContextStrategy(carrier) {
    const sentry = getSentryCarrier(carrier);
    if (sentry.acs) {
      return sentry.acs;
    }
    return getStackAsyncContextStrategy();
  }

  // node_modules/@sentry/core/build/esm/attributes.js
  function isAttributeObject(maybeObj) {
    return typeof maybeObj === "object" && maybeObj != null && !Array.isArray(maybeObj) && Object.keys(maybeObj).includes("value");
  }
  function attributeValueToTypedAttributeValue(rawValue, useFallback) {
    const { value, unit } = isAttributeObject(rawValue) ? rawValue : { value: rawValue, unit: void 0 };
    const attributeValue = getTypedAttributeValue(value);
    const checkedUnit = unit && typeof unit === "string" ? { unit } : {};
    if (attributeValue) {
      return { ...attributeValue, ...checkedUnit };
    }
    if (!useFallback || useFallback === "skip-undefined" && value === void 0) {
      return;
    }
    let stringValue = "";
    try {
      stringValue = JSON.stringify(value) ?? "";
    } catch {
    }
    return {
      value: stringValue,
      type: "string",
      ...checkedUnit
    };
  }
  function serializeAttributes(attributes, fallback = false) {
    const serializedAttributes = {};
    for (const [key, value] of Object.entries(attributes ?? {})) {
      const typedValue = attributeValueToTypedAttributeValue(value, fallback);
      if (typedValue) {
        serializedAttributes[key] = typedValue;
      }
    }
    return serializedAttributes;
  }
  function getTypedAttributeValue(value) {
    if (Array.isArray(value)) {
      return { value, type: "array" };
    }
    const primitiveType = typeof value === "string" ? "string" : typeof value === "boolean" ? "boolean" : typeof value === "number" && !Number.isNaN(value) ? Number.isInteger(value) ? "integer" : "double" : null;
    if (primitiveType) {
      return { value, type: primitiveType };
    }
  }

  // node_modules/@sentry/core/build/esm/currentScopes.js
  function getExternalPropagationContext() {
    return getSentryCarrier(getMainCarrier()).externalPropagationContextProvider?.();
  }
  function getCurrentScope() {
    const carrier = getMainCarrier();
    const acs = getAsyncContextStrategy(carrier);
    return acs.getCurrentScope();
  }
  function getIsolationScope() {
    const carrier = getMainCarrier();
    const acs = getAsyncContextStrategy(carrier);
    return acs.getIsolationScope();
  }
  function getGlobalScope() {
    return getGlobalSingleton("globalScope", () => new Scope());
  }
  function withScope2(...rest) {
    const carrier = getMainCarrier();
    const acs = getAsyncContextStrategy(carrier);
    if (rest.length === 2) {
      const [scope, callback] = rest;
      if (!scope) {
        return acs.withScope(callback);
      }
      return acs.withSetScope(scope, callback);
    }
    return acs.withScope(rest[0]);
  }
  function getClient() {
    return getCurrentScope().getClient();
  }
  function getTraceContextFromScope(scope) {
    const externalContext = getExternalPropagationContext();
    if (externalContext) {
      return { trace_id: externalContext.traceId, span_id: externalContext.spanId };
    }
    const propagationContext = scope.getPropagationContext();
    const { traceId, parentSpanId, propagationSpanId } = propagationContext;
    const traceContext = {
      trace_id: traceId,
      span_id: propagationSpanId || generateSpanId()
    };
    if (parentSpanId) {
      traceContext.parent_span_id = parentSpanId;
    }
    return traceContext;
  }

  // node_modules/@sentry/conventions/dist/attributes.mjs
  var wr = "gen_ai.conversation.id";
  var Po = "http.request.header";
  var Vd = "sentry.exclusive_time";
  var Jd = "sentry.is_localhost";
  var mm = "sentry.op";
  var gm = "sentry.origin";
  var hm = "sentry.profile_id";
  var Nm = "sentry.segment.name.source";
  var ib = "url.full";
  var mb = "user_agent.original";

  // node_modules/@sentry/core/build/esm/semanticAttributes.js
  var SEMANTIC_ATTRIBUTE_SENTRY_SAMPLE_RATE = "sentry.sample_rate";
  var SEMANTIC_ATTRIBUTE_SENTRY_PREVIOUS_TRACE_SAMPLE_RATE = "sentry.previous_trace_sample_rate";

  // node_modules/@sentry/core/build/esm/types/spanStatus.js
  var SPAN_STATUS_TYPES = [
    /** The operation completed successfully. */
    "ok",
    /** Deadline expired before operation could complete. */
    "deadline_exceeded",
    /** 401 Unauthorized (actually does mean unauthenticated according to RFC 7235) */
    "unauthenticated",
    /** 403 Forbidden */
    "permission_denied",
    /** 404 Not Found. Some requested entity (file or directory) was not found. */
    "not_found",
    /** 429 Too Many Requests */
    "resource_exhausted",
    /** Client specified an invalid argument. 4xx. */
    "invalid_argument",
    /** 501 Not Implemented */
    "unimplemented",
    /** 503 Service Unavailable */
    "unavailable",
    /** Other/generic 5xx. */
    "internal_error",
    /** Unknown. Any non-standard HTTP status code. */
    "unknown_error",
    /** The operation was cancelled (typically by the user). */
    "cancelled",
    /** Already exists (409) */
    "already_exists",
    /** Operation was rejected because the system is not in a state required for the operation's */
    "failed_precondition",
    /** The operation was aborted, typically due to a concurrency issue. */
    "aborted",
    /** Operation was attempted past the valid range. */
    "out_of_range",
    /** Unrecoverable data loss or corruption */
    "data_loss"
  ];

  // node_modules/@sentry/core/build/esm/tracing/spanstatus.js
  var SPAN_STATUS_UNSET = 0;
  var SPAN_STATUS_OK = 1;
  function isStatusErrorMessageValid(message) {
    return message !== "ok" && SPAN_STATUS_TYPES.includes(message);
  }

  // node_modules/@sentry/core/build/esm/utils/weakRef.js
  function derefWeakRef(ref) {
    if (!ref) {
      return void 0;
    }
    if (typeof ref === "object" && "deref" in ref && typeof ref.deref === "function") {
      try {
        return ref.deref();
      } catch {
        return void 0;
      }
    }
    return ref;
  }

  // node_modules/@sentry/core/build/esm/tracing/utils.js
  var SCOPE_ON_START_SPAN_FIELD = "_sentryScope";
  var ISOLATION_SCOPE_ON_START_SPAN_FIELD = "_sentryIsolationScope";
  function getCapturedScopesOnSpan(span) {
    const spanWithScopes = span;
    return {
      scope: spanWithScopes[SCOPE_ON_START_SPAN_FIELD],
      isolationScope: derefWeakRef(spanWithScopes[ISOLATION_SCOPE_ON_START_SPAN_FIELD])
    };
  }

  // node_modules/@sentry/core/build/esm/utils/baggage.js
  var SENTRY_BAGGAGE_KEY_PREFIX = "sentry-";
  function baggageHeaderToDynamicSamplingContext(baggageHeader) {
    const baggageObject = parseBaggageHeader(baggageHeader);
    if (!baggageObject) {
      return void 0;
    }
    const dynamicSamplingContext = Object.entries(baggageObject).reduce((acc, [key, value]) => {
      if (key.startsWith(SENTRY_BAGGAGE_KEY_PREFIX)) {
        const nonPrefixedKey = key.slice(SENTRY_BAGGAGE_KEY_PREFIX.length);
        acc[nonPrefixedKey] = value;
      }
      return acc;
    }, {});
    if (Object.keys(dynamicSamplingContext).length > 0) {
      return dynamicSamplingContext;
    } else {
      return void 0;
    }
  }
  function parseBaggageHeader(baggageHeader) {
    if (!baggageHeader || !isString(baggageHeader) && !Array.isArray(baggageHeader)) {
      return void 0;
    }
    if (Array.isArray(baggageHeader)) {
      return baggageHeader.reduce((acc, curr) => {
        const currBaggageObject = baggageHeaderToObject(curr);
        Object.entries(currBaggageObject).forEach(([key, value]) => {
          acc[key] = value;
        });
        return acc;
      }, {});
    }
    return baggageHeaderToObject(baggageHeader);
  }
  function baggageHeaderToObject(baggageHeader) {
    return baggageHeader.split(",").map((baggageEntry) => {
      const eqIdx = baggageEntry.indexOf("=");
      if (eqIdx === -1) {
        return [];
      }
      const key = baggageEntry.slice(0, eqIdx);
      const value = baggageEntry.slice(eqIdx + 1);
      return [key, value].map((keyOrValue) => {
        try {
          return decodeURIComponent(keyOrValue.trim());
        } catch {
          return;
        }
      });
    }).reduce((acc, [key, value]) => {
      if (key && value) {
        acc[key] = value;
      }
      return acc;
    }, {});
  }

  // node_modules/@sentry/core/build/esm/utils/dsn.js
  var ORG_ID_REGEX = /^o(\d+)\./;
  var DSN_REGEX = /^(?:(\w+):)\/\/(?:(\w+)(?::(\w+)?)?@)((?:\[[:.%\w]+\]|[\w.-]+))(?::(\d+))?\/(.+)/;
  function isValidProtocol(protocol) {
    return protocol === "http" || protocol === "https";
  }
  function dsnToString(dsn, withPassword = false) {
    const { host, path, pass, port, projectId, protocol, publicKey } = dsn;
    return `${protocol}://${publicKey}${withPassword && pass ? `:${pass}` : ""}@${host}${port ? `:${port}` : ""}/${path ? `${path}/` : path}${projectId}`;
  }
  function dsnFromString(str) {
    const match = DSN_REGEX.exec(str);
    if (!match) {
      consoleSandbox(() => {
        console.error(`Invalid Sentry Dsn: ${str}`);
      });
      return void 0;
    }
    const [protocol, publicKey, pass = "", host = "", port = "", lastPath = ""] = match.slice(1);
    let path = "";
    let projectId = lastPath;
    const split = projectId.split("/");
    if (split.length > 1) {
      path = split.slice(0, -1).join("/");
      projectId = split.pop();
    }
    if (projectId) {
      const projectMatch = projectId.match(/^\d+/);
      if (projectMatch) {
        projectId = projectMatch[0];
      }
    }
    return dsnFromComponents({ host, pass, path, projectId, port, protocol, publicKey });
  }
  function dsnFromComponents(components) {
    return {
      protocol: components.protocol,
      publicKey: components.publicKey || "",
      pass: components.pass || "",
      host: components.host,
      port: components.port || "",
      path: components.path || "",
      projectId: components.projectId
    };
  }
  function validateDsn(dsn) {
    if (!DEBUG_BUILD) {
      return true;
    }
    const { port, projectId, protocol } = dsn;
    const requiredComponents = ["protocol", "publicKey", "host", "projectId"];
    const hasMissingRequiredComponent = requiredComponents.find((component) => {
      if (!dsn[component]) {
        debug.error(`Invalid Sentry Dsn: ${component} missing`);
        return true;
      }
      return false;
    });
    if (hasMissingRequiredComponent) {
      return false;
    }
    if (!projectId.match(/^\d+$/)) {
      debug.error(`Invalid Sentry Dsn: Invalid projectId ${projectId}`);
      return false;
    }
    if (!isValidProtocol(protocol)) {
      debug.error(`Invalid Sentry Dsn: Invalid protocol ${protocol}`);
      return false;
    }
    if (port && isNaN(parseInt(port, 10))) {
      debug.error(`Invalid Sentry Dsn: Invalid port ${port}`);
      return false;
    }
    return true;
  }
  function extractOrgIdFromDsnHost(host) {
    const match = host.match(ORG_ID_REGEX);
    return match?.[1];
  }
  function extractOrgIdFromClient(client) {
    const options = client.getOptions();
    const { host } = client.getDsn() || {};
    let org_id;
    if (options.orgId) {
      org_id = String(options.orgId);
    } else if (host) {
      org_id = extractOrgIdFromDsnHost(host);
    }
    return org_id;
  }
  function makeDsn(from) {
    const components = typeof from === "string" ? dsnFromString(from) : dsnFromComponents(from);
    if (!components || !validateDsn(components)) {
      return void 0;
    }
    return components;
  }

  // node_modules/@sentry/core/build/esm/utils/parseSampleRate.js
  function parseSampleRate(sampleRate) {
    if (typeof sampleRate === "boolean") {
      return Number(sampleRate);
    }
    const rate = typeof sampleRate === "string" ? parseFloat(sampleRate) : sampleRate;
    if (typeof rate !== "number" || isNaN(rate) || rate < 0 || rate > 1) {
      return void 0;
    }
    return rate;
  }

  // node_modules/@sentry/core/build/esm/utils/spanOnScope.js
  var SCOPE_SPAN_FIELD = "span";
  function _getSpanForScope(scope) {
    return derefWeakRef(scope.refs[SCOPE_SPAN_FIELD]);
  }

  // node_modules/@sentry/core/build/esm/utils/spanUtils.js
  var TRACE_FLAG_SAMPLED = 1;
  function spanToTraceContext(span) {
    const { spanId, traceId: trace_id, isRemote } = span.spanContext();
    const parent_span_id = isRemote ? spanId : spanToStaticSpanJSON(span).parent_span_id;
    const scope = getCapturedScopesOnSpan(span).scope;
    const span_id = isRemote ? scope?.getPropagationContext().propagationSpanId || generateSpanId() : spanId;
    return {
      parent_span_id,
      span_id,
      trace_id
    };
  }
  function convertSpanLinksForEnvelope(links) {
    if (links && links.length > 0) {
      return links.map(({ context: { spanId, traceId, traceFlags, ...restContext }, attributes }) => ({
        span_id: spanId,
        trace_id: traceId,
        sampled: traceFlags === TRACE_FLAG_SAMPLED,
        attributes,
        ...restContext
      }));
    } else {
      return void 0;
    }
  }
  function spanTimeInputToSeconds(input) {
    if (typeof input === "number") {
      return ensureTimestampInSeconds(input);
    }
    if (Array.isArray(input)) {
      return input[0] + input[1] / 1e9;
    }
    if (input instanceof Date) {
      return ensureTimestampInSeconds(input.getTime());
    }
    return timestampInSeconds();
  }
  function ensureTimestampInSeconds(timestamp) {
    const isMs = timestamp > 9999999999;
    return isMs ? timestamp / 1e3 : timestamp;
  }
  function spanToStaticSpanJSON(span) {
    if (spanIsSentrySpan(span)) {
      return span.getStaticSpanJSON();
    }
    const { spanId: span_id, traceId: trace_id } = span.spanContext();
    if (spanIsOpenTelemetrySdkTraceBaseSpan(span)) {
      const { attributes, startTime, name, endTime, status, links } = span;
      return {
        span_id,
        trace_id,
        data: attributes,
        description: name,
        parent_span_id: getOtelParentSpanId(span),
        start_timestamp: spanTimeInputToSeconds(startTime),
        // This is [0,0] by default in OTEL, in which case we want to interpret this as no end time
        timestamp: spanTimeInputToSeconds(endTime) || void 0,
        status: getStatusMessage(status),
        op: attributes[mm],
        origin: attributes[gm],
        links: convertSpanLinksForEnvelope(links)
      };
    }
    return {
      span_id,
      trace_id,
      start_timestamp: 0,
      status: "ok",
      data: {}
    };
  }
  function getOtelParentSpanId(span) {
    return "parentSpanId" in span ? span.parentSpanId : "parentSpanContext" in span ? span.parentSpanContext?.spanId : void 0;
  }
  function streamedSpanJsonToSerializedSpan(spanJson) {
    return {
      ...spanJson,
      // We only ever send ended spans, but fall back to the start time (i.e. duration 0) so that
      // sent spans always carry an end timestamp.
      end_timestamp: spanJson.end_timestamp ?? spanJson.start_timestamp,
      attributes: serializeAttributes(spanJson.attributes),
      links: spanJson.links?.map((link) => ({
        ...link,
        attributes: serializeAttributes(link.attributes)
      }))
    };
  }
  function spanIsOpenTelemetrySdkTraceBaseSpan(span) {
    const castSpan = span;
    return !!castSpan.attributes && !!castSpan.startTime && !!castSpan.name && !!castSpan.endTime && !!castSpan.status;
  }
  function spanIsSentrySpan(span) {
    return typeof span.getSpanJSON === "function";
  }
  function spanIsSampled(span) {
    const { traceFlags } = span.spanContext();
    return traceFlags === TRACE_FLAG_SAMPLED;
  }
  function getStatusMessage(status) {
    if (!status || status.code === SPAN_STATUS_UNSET) {
      return "ok";
    }
    if (status.code === SPAN_STATUS_OK) {
      return "ok";
    }
    return status.message && isStatusErrorMessageValid(status.message) ? status.message : "internal_error";
  }
  var ROOT_SPAN_FIELD = "_sentryRootSpan";
  var getRootSpan = INTERNAL_getSegmentSpan;
  function INTERNAL_getSegmentSpan(span) {
    return span[ROOT_SPAN_FIELD] || span;
  }
  function getActiveSpan(scope) {
    const carrier = getMainCarrier();
    const acs = getAsyncContextStrategy(carrier);
    if (acs.getActiveSpan) {
      return acs.getActiveSpan(scope);
    }
    return _getSpanForScope(scope || getCurrentScope());
  }

  // node_modules/@sentry/core/build/esm/utils/hasSpansEnabled.js
  function hasSpansEnabled(maybeOptions) {
    if (typeof __SENTRY_TRACING__ === "boolean" && !__SENTRY_TRACING__) {
      return false;
    }
    const options = maybeOptions || getClient()?.getOptions();
    return !!options && // Note: This check is `!= null`, meaning "nullish". `0` is not "nullish", `undefined` and `null` are. (This comment was brought to you by 15 minutes of questioning life)
    (options.tracesSampleRate != null || !!options.tracesSampler);
  }

  // node_modules/@sentry/core/build/esm/utils/should-ignore-span.js
  function logIgnoredSpan(droppedSpan) {
    debug.log(`Ignoring span ${droppedSpan.op} - ${droppedSpan.description} because it matches \`ignoreSpans\`.`);
  }
  function shouldIgnoreSpan(span, ignoreSpans) {
    if (!ignoreSpans?.length) {
      return false;
    }
    for (const pattern of ignoreSpans) {
      if (isStringOrRegExp(pattern)) {
        if (span.description && isMatchingPattern(span.description, pattern)) {
          DEBUG_BUILD && logIgnoredSpan(span);
          return true;
        }
        continue;
      }
      const hasAttributes = !!pattern.attributes && Object.keys(pattern.attributes).length > 0;
      if (!pattern.name && !pattern.op && !hasAttributes) {
        continue;
      }
      const nameMatches = pattern.name ? span.description && isMatchingPattern(span.description, pattern.name) : true;
      const opMatches = pattern.op ? span.op && isMatchingPattern(span.op, pattern.op) : true;
      const attrsMatch = pattern.attributes ? Object.entries(pattern.attributes).every(
        ([key, valuePattern]) => _matchesAttributeValue(span.attributes?.[key], valuePattern)
      ) : true;
      if (nameMatches && opMatches && attrsMatch) {
        DEBUG_BUILD && logIgnoredSpan(span);
        return true;
      }
    }
    return false;
  }
  function _matchesAttributeValue(actual, pat) {
    if (typeof actual === "string" && (typeof pat === "string" || pat instanceof RegExp)) {
      return isMatchingPattern(actual, pat);
    }
    if (Array.isArray(actual) && Array.isArray(pat)) {
      return actual.length === pat.length && actual.every((v, i) => v === pat[i]);
    }
    return actual === pat;
  }
  function reparentChildSpans(spans, dropSpan) {
    const droppedSpanParentId = dropSpan.parent_span_id;
    const droppedSpanId = dropSpan.span_id;
    if (!droppedSpanParentId) {
      return;
    }
    for (const span of spans) {
      if (span.parent_span_id === droppedSpanId) {
        span.parent_span_id = droppedSpanParentId;
      }
    }
  }
  function isStringOrRegExp(value) {
    return typeof value === "string" || value instanceof RegExp;
  }

  // node_modules/@sentry/core/build/esm/integration.js
  var installedIntegrations = [];
  function filterDuplicates(integrations) {
    const integrationsByName = {};
    integrations.forEach((currentInstance) => {
      const { name } = currentInstance;
      const existingInstance = integrationsByName[name];
      if (existingInstance && !existingInstance.isDefaultInstance && currentInstance.isDefaultInstance) {
        return;
      }
      integrationsByName[name] = currentInstance;
    });
    return Object.values(integrationsByName);
  }
  function getIntegrationsToSetup(options) {
    const defaultIntegrations = options.defaultIntegrations || [];
    const userIntegrations = options.integrations;
    defaultIntegrations.forEach((integration) => {
      integration.isDefaultInstance = true;
    });
    let integrations;
    if (Array.isArray(userIntegrations)) {
      integrations = [...defaultIntegrations, ...userIntegrations];
    } else if (typeof userIntegrations === "function") {
      const resolvedUserIntegrations = userIntegrations(defaultIntegrations);
      integrations = Array.isArray(resolvedUserIntegrations) ? resolvedUserIntegrations : [resolvedUserIntegrations];
    } else {
      integrations = defaultIntegrations;
    }
    return filterDuplicates(integrations);
  }
  function setupIntegrations(client, integrations) {
    const integrationIndex = {};
    integrations.forEach((integration) => {
      if (integration?.beforeSetup) {
        integration.beforeSetup(client);
      }
    });
    integrations.forEach((integration) => {
      if (integration) {
        setupIntegration(client, integration, integrationIndex);
      }
    });
    return integrationIndex;
  }
  function afterSetupIntegrations(client, integrations) {
    for (const integration of integrations) {
      if (integration?.afterAllSetup) {
        integration.afterAllSetup(client);
      }
    }
  }
  function setupIntegration(client, integration, integrationIndex) {
    if (integrationIndex[integration.name]) {
      DEBUG_BUILD && debug.log(`Integration skipped because it was already installed: ${integration.name}`);
      return;
    }
    integrationIndex[integration.name] = integration;
    if (!installedIntegrations.includes(integration.name) && typeof integration.setupOnce === "function") {
      integration.setupOnce();
      installedIntegrations.push(integration.name);
    }
    if (integration.setup && typeof integration.setup === "function") {
      integration.setup(client);
    }
    if (typeof integration.preprocessEvent === "function") {
      const callback = integration.preprocessEvent.bind(integration);
      client.on("preprocessEvent", (event, hint) => callback(event, hint, client));
    }
    if (typeof integration.processEvent === "function") {
      const callback = integration.processEvent.bind(integration);
      const processor = Object.assign((event, hint) => callback(event, hint, client), {
        id: integration.name
      });
      client.addEventProcessor(processor);
    }
    ["processSpan", "processSegmentSpan"].forEach((hook) => {
      const callback = integration[hook];
      if (typeof callback === "function") {
        client.on(hook, (span) => callback.call(integration, span, client));
      }
    });
    DEBUG_BUILD && debug.log(`Integration installed: ${integration.name}`);
  }
  function defineIntegration(fn) {
    return fn;
  }

  // node_modules/@sentry/core/build/esm/constants.js
  var DEFAULT_ENVIRONMENT = "production";

  // node_modules/@sentry/core/build/esm/tracing/sentryNonRecordingSpan.js
  var NON_RECORDING_SPAN_FIELD = /* @__PURE__ */ Symbol.for("sentry.nonRecordingSpan");
  function spanIsNonRecordingSpan(span) {
    return !!span && span[NON_RECORDING_SPAN_FIELD] === true;
  }

  // node_modules/@sentry/core/build/esm/tracing/dynamicSamplingContext.js
  var FROZEN_DSC_FIELD = "_frozenDsc";
  function getDynamicSamplingContextFromClient(trace_id, client) {
    const options = client.getOptions();
    const { publicKey: public_key } = client.getDsn() || {};
    const dsc = {
      environment: options.environment || DEFAULT_ENVIRONMENT,
      release: options.release,
      public_key,
      trace_id,
      org_id: extractOrgIdFromClient(client)
    };
    client.emit("createDsc", dsc);
    return dsc;
  }
  function getDynamicSamplingContextFromScope(client, scope) {
    if (getExternalPropagationContext()) {
      return void 0;
    }
    const propagationContext = scope.getPropagationContext();
    return propagationContext.dsc || getDynamicSamplingContextFromClient(propagationContext.traceId, client);
  }
  function getDynamicSamplingContextFromSpan(span) {
    const client = getClient();
    if (!client) {
      return {};
    }
    const rootSpan = getRootSpan(span);
    const rootSpanJson = spanToStaticSpanJSON(rootSpan);
    const rootSpanAttributes = rootSpanJson.data;
    const traceState = rootSpan.spanContext().traceState;
    const rootSpanSampleRate = traceState?.get("sentry.sample_rate") ?? rootSpanAttributes[SEMANTIC_ATTRIBUTE_SENTRY_SAMPLE_RATE] ?? rootSpanAttributes[SEMANTIC_ATTRIBUTE_SENTRY_PREVIOUS_TRACE_SAMPLE_RATE];
    function applyLocalSampleRateToDsc(dsc2) {
      if (typeof rootSpanSampleRate === "number" || typeof rootSpanSampleRate === "string") {
        dsc2.sample_rate = `${rootSpanSampleRate}`;
      }
      return dsc2;
    }
    const frozenDsc = rootSpan[FROZEN_DSC_FIELD];
    if (frozenDsc) {
      return applyLocalSampleRateToDsc(frozenDsc);
    }
    const isNonRecordingRoot = spanIsNonRecordingSpan(rootSpan);
    const isIgnoredRoot = isNonRecordingRoot && rootSpan.dropReason === "ignored";
    if (isNonRecordingRoot && (!hasSpansEnabled(client.getOptions()) || isIgnoredRoot)) {
      const capturedScope = getCapturedScopesOnSpan(rootSpan).scope;
      const scopeDsc = capturedScope && getDynamicSamplingContextFromScope(client, capturedScope);
      if (scopeDsc) {
        const dsc2 = { ...scopeDsc };
        if (isIgnoredRoot) {
          dsc2.sampled = "false";
        }
        return applyLocalSampleRateToDsc(dsc2);
      }
    }
    const traceStateDsc = traceState?.get("sentry.dsc");
    const dscOnTraceState = traceStateDsc && baggageHeaderToDynamicSamplingContext(traceStateDsc);
    if (dscOnTraceState) {
      return applyLocalSampleRateToDsc(dscOnTraceState);
    }
    const dsc = getDynamicSamplingContextFromClient(span.spanContext().traceId, client);
    const source = rootSpanAttributes[Nm];
    const name = rootSpanJson.description;
    if (source !== "url" && name) {
      dsc.transaction = name;
    }
    if (hasSpansEnabled()) {
      dsc.sampled = String(spanIsSampled(rootSpan));
      dsc.sample_rand = // In OTEL we store the sample rand on the trace state because we cannot access scopes for NonRecordingSpans
      // The Sentry OTEL SpanSampler takes care of writing the sample rand on the root span
      traceState?.get("sentry.sample_rand") ?? // On all other platforms we can actually get the scopes from a root span (we use this as a fallback)
      getCapturedScopesOnSpan(rootSpan).scope?.getPropagationContext().sampleRand.toString();
    }
    applyLocalSampleRateToDsc(dsc);
    client.emit("createDsc", dsc, rootSpan);
    return dsc;
  }

  // node_modules/@sentry/core/build/esm/utils/scopeData.js
  function applyScopeDataToEvent(event, data) {
    const { fingerprint, breadcrumbs, sdkProcessingMetadata } = data;
    applyDataToEvent(event, data);
    applyFingerprintToEvent(event, fingerprint);
    applyBreadcrumbsToEvent(event, breadcrumbs);
    applySdkMetadataToEvent(event, sdkProcessingMetadata);
  }
  function mergeScopeData(data, mergeData) {
    const {
      extra,
      tags,
      attributes,
      user,
      contexts,
      level,
      sdkProcessingMetadata,
      breadcrumbs,
      fingerprint,
      eventProcessors,
      attachments,
      propagationContext,
      transactionName
    } = mergeData;
    mergeAndOverwriteScopeData(data, "extra", extra);
    mergeAndOverwriteScopeData(data, "tags", tags);
    mergeAndOverwriteScopeData(data, "attributes", attributes);
    mergeAndOverwriteScopeData(data, "user", user);
    mergeAndOverwriteScopeData(data, "contexts", contexts);
    data.sdkProcessingMetadata = merge(data.sdkProcessingMetadata, sdkProcessingMetadata, 2);
    if (level) {
      data.level = level;
    }
    if (transactionName) {
      data.transactionName = transactionName;
    }
    if (breadcrumbs.length) {
      data.breadcrumbs = [...data.breadcrumbs, ...breadcrumbs];
    }
    if (fingerprint.length) {
      data.fingerprint = [...data.fingerprint, ...fingerprint];
    }
    if (eventProcessors.length) {
      data.eventProcessors = [...data.eventProcessors, ...eventProcessors];
    }
    if (attachments.length) {
      data.attachments = [...data.attachments, ...attachments];
    }
    data.propagationContext = { ...data.propagationContext, ...propagationContext };
  }
  function mergeAndOverwriteScopeData(data, prop, mergeVal) {
    data[prop] = merge(data[prop], mergeVal, 1);
  }
  function getCombinedScopeData(isolationScope, currentScope) {
    const scopeData = getGlobalScope().getScopeData();
    isolationScope && mergeScopeData(scopeData, isolationScope.getScopeData());
    currentScope && mergeScopeData(scopeData, currentScope.getScopeData());
    return scopeData;
  }
  function applyDataToEvent(event, data) {
    const { extra, tags, user, contexts, level, transactionName } = data;
    if (Object.keys(extra).length) {
      event.extra = { ...extra, ...event.extra };
    }
    if (Object.keys(tags).length) {
      event.tags = { ...tags, ...event.tags };
    }
    if (Object.keys(user).length) {
      event.user = { ...user, ...event.user };
    }
    if (Object.keys(contexts).length) {
      event.contexts = { ...contexts, ...event.contexts };
    }
    if (level) {
      event.level = level;
    }
    if (transactionName && event.type !== "transaction") {
      event.transaction = transactionName;
    }
  }
  function applyBreadcrumbsToEvent(event, breadcrumbs) {
    const mergedBreadcrumbs = [...event.breadcrumbs || [], ...breadcrumbs];
    event.breadcrumbs = mergedBreadcrumbs.length ? mergedBreadcrumbs : void 0;
  }
  function applySdkMetadataToEvent(event, sdkProcessingMetadata) {
    event.sdkProcessingMetadata = {
      ...event.sdkProcessingMetadata,
      ...sdkProcessingMetadata
    };
  }
  function applySpanToEvent(event, span) {
    event.contexts = {
      trace: spanToTraceContext(span),
      ...event.contexts
    };
    event.sdkProcessingMetadata = {
      dynamicSamplingContext: getDynamicSamplingContextFromSpan(span),
      ...event.sdkProcessingMetadata
    };
    const rootSpan = getRootSpan(span);
    const transactionName = spanToStaticSpanJSON(rootSpan).description;
    if (transactionName && !event.transaction && event.type === "transaction") {
      event.transaction = transactionName;
    }
  }
  function applyFingerprintToEvent(event, fingerprint) {
    event.fingerprint = event.fingerprint ? Array.isArray(event.fingerprint) ? event.fingerprint : [event.fingerprint] : [];
    if (fingerprint) {
      event.fingerprint = event.fingerprint.concat(fingerprint);
    }
    if (!event.fingerprint.length) {
      delete event.fingerprint;
    }
  }

  // node_modules/@sentry/core/build/esm/utils/safeCallback.js
  function safeCallback(message, fn, fallback) {
    let result;
    try {
      result = fn();
    } catch (error2) {
      return recover(message, error2, fallback);
    }
    if (isThenable(result)) {
      return result.then(void 0, (error2) => recover(message, error2, fallback));
    }
    return result;
  }
  function recover(message, error2, fallback) {
    DEBUG_BUILD && debug.error(message, error2);
    return fallback(error2);
  }

  // node_modules/@sentry/core/build/esm/tracing/spans/beforeSendSpan.js
  function isStaticBeforeSendSpanCallback(callback) {
    return !!callback && typeof callback === "function" && "_static" in callback && !!callback._static;
  }
  function applyBeforeSendSpanCallback(span, beforeSendSpan) {
    const modifiedSpan = safeCallback(
      DEBUG_BUILD ? "The `beforeSendSpan` callback threw an error, sending the span unmodified:" : "",
      () => beforeSendSpan(span),
      () => span
    );
    return modifiedSpan || span;
  }

  // node_modules/@sentry/core/build/esm/tracing/spans/spanJsonToStreamedSpan.js
  function spanJsonToSerializedStreamedSpan(span) {
    const streamedSpan = {
      trace_id: span.trace_id,
      span_id: span.span_id,
      parent_span_id: span.parent_span_id,
      name: span.description || "",
      start_timestamp: span.start_timestamp,
      end_timestamp: span.timestamp,
      status: !span.status || span.status === "ok" || span.status === "cancelled" ? "ok" : "error",
      is_segment: false,
      attributes: { ...span.data },
      links: span.links
    };
    return streamedSpanJsonToSerializedSpan(streamedSpan);
  }

  // node_modules/@sentry/core/build/esm/tracing/spans/captureSpan.js
  function safeSetSpanJSONAttributes(spanJSON, newAttributes) {
    const originalAttributes = spanJSON.attributes ?? (spanJSON.attributes = {});
    Object.entries(newAttributes).forEach(([key, value]) => {
      if (value != null && !(key in originalAttributes)) {
        originalAttributes[key] = value;
      }
    });
  }

  // node_modules/@sentry/core/build/esm/tracing/spans/hasSpanStreamingEnabled.js
  function hasSpanStreamingEnabled(client) {
    return client.getOptions().traceLifecycle === "stream";
  }

  // node_modules/@sentry/core/build/esm/utils/timer.js
  function safeUnref(timer) {
    if (typeof timer === "object" && typeof timer.unref === "function") {
      timer.unref();
    }
    return timer;
  }

  // node_modules/@sentry/core/build/esm/utils/envelope.js
  function createEnvelope(headers, items = []) {
    return [headers, items];
  }
  function addItemToEnvelope(envelope, newItem) {
    const [headers, items] = envelope;
    return [headers, [...items, newItem]];
  }
  function forEachEnvelopeItem(envelope, callback) {
    const envelopeItems = envelope[1];
    for (const envelopeItem of envelopeItems) {
      const envelopeItemType = envelopeItem[0].type;
      const result = callback(envelopeItem, envelopeItemType);
      if (result) {
        return true;
      }
    }
    return false;
  }
  function envelopeContainsItemType(envelope, types) {
    return forEachEnvelopeItem(envelope, (_, type) => types.includes(type));
  }
  function encodeUTF8(input) {
    const carrier = getSentryCarrier(GLOBAL_OBJ);
    return carrier.encodePolyfill ? carrier.encodePolyfill(input) : new TextEncoder().encode(input);
  }
  function serializeEnvelope(envelope) {
    const [envHeaders, items] = envelope;
    let parts = JSON.stringify(envHeaders);
    function append(next) {
      if (typeof parts === "string") {
        parts = typeof next === "string" ? parts + next : [encodeUTF8(parts), next];
      } else {
        parts.push(typeof next === "string" ? encodeUTF8(next) : next);
      }
    }
    for (const item of items) {
      const [itemHeaders, payload] = item;
      append(`
${JSON.stringify(itemHeaders)}
`);
      if (typeof payload === "string" || payload instanceof Uint8Array) {
        append(payload);
      } else {
        let stringifiedPayload;
        try {
          stringifiedPayload = JSON.stringify(payload);
        } catch {
          stringifiedPayload = JSON.stringify(normalize(payload));
        }
        append(stringifiedPayload);
      }
    }
    return typeof parts === "string" ? parts : concatBuffers(parts);
  }
  function concatBuffers(buffers) {
    const totalLength = buffers.reduce((acc, buf) => acc + buf.length, 0);
    const merged = new Uint8Array(totalLength);
    let offset = 0;
    for (const buffer of buffers) {
      merged.set(buffer, offset);
      offset += buffer.length;
    }
    return merged;
  }
  function createAttachmentEnvelopeItem(attachment) {
    const buffer = typeof attachment.data === "string" ? encodeUTF8(attachment.data) : attachment.data;
    return [
      {
        type: "attachment",
        length: buffer.length,
        filename: attachment.filename,
        content_type: attachment.contentType,
        attachment_type: attachment.attachmentType
      },
      buffer
    ];
  }
  var DATA_CATEGORY_OVERRIDES = {
    sessions: "session",
    event: "error",
    client_report: "internal",
    user_report: "default",
    profile_chunk: "profile",
    replay_event: "replay",
    replay_recording: "replay",
    check_in: "monitor",
    raw_security: "security",
    log: "log_item",
    metric: "trace_metric"
  };
  function _isOverriddenType(type) {
    return type in DATA_CATEGORY_OVERRIDES;
  }
  function envelopeItemTypeToDataCategory(type) {
    return _isOverriddenType(type) ? DATA_CATEGORY_OVERRIDES[type] : type;
  }
  function getSdkMetadataForEnvelopeHeader(metadataOrEvent) {
    if (!metadataOrEvent?.sdk) {
      return;
    }
    const { name, version } = metadataOrEvent.sdk;
    return { name, version };
  }
  function createEventEnvelopeHeaders(event, sdkInfo, tunnel, dsn) {
    const dynamicSamplingContext = event.sdkProcessingMetadata?.dynamicSamplingContext;
    return {
      event_id: event.event_id,
      sent_at: new Date(safeDateNow()).toISOString(),
      ...sdkInfo && { sdk: sdkInfo },
      ...!!tunnel && dsn && { dsn: dsnToString(dsn) },
      ...dynamicSamplingContext && {
        trace: dynamicSamplingContext
      }
    };
  }
  function getDataCategoryByType(type) {
    return type === "replay_event" ? "replay" : type || "error";
  }

  // node_modules/@sentry/core/build/esm/utils/env.js
  function isBrowserBundle() {
    return typeof __SENTRY_BROWSER_BUNDLE__ !== "undefined" && !!__SENTRY_BROWSER_BUNDLE__;
  }
  function getSDKSource() {
    return "npm";
  }

  // node_modules/@sentry/core/build/esm/utils/node.js
  function isNodeEnv() {
    return !isBrowserBundle() && Object.prototype.toString.call(typeof process !== "undefined" ? process : 0) === "[object process]";
  }

  // node_modules/@sentry/core/build/esm/utils/isBrowser.js
  function isBrowser() {
    return typeof window !== "undefined" && (!isNodeEnv() || isElectronNodeRenderer());
  }
  function isElectronNodeRenderer() {
    const process2 = GLOBAL_OBJ.process;
    return process2?.type === "renderer";
  }

  // node_modules/@sentry/core/build/esm/tracing/spans/envelope.js
  function createSpanContainerItem(serializedSpans, client) {
    const inferSetting = client.getDataCollectionOptions().userInfo ? "auto" : "never";
    return [
      { type: "span", item_count: serializedSpans.length, content_type: "application/vnd.sentry.items.span.v2+json" },
      {
        version: 2,
        ingest_settings: isBrowser() ? { infer_ip: inferSetting, infer_user_agent: inferSetting } : void 0,
        items: serializedSpans
      }
    ];
  }

  // node_modules/@sentry/core/build/esm/utils/errorSpanAttribution.js
  var escapedSpanTraceContexts = /* @__PURE__ */ new WeakMap();
  function toWeakMapKey(error2) {
    return isPrimitive(error2) ? void 0 : error2;
  }
  function applyEscapedErrorSpanToEvent(event, hint, scope) {
    const key = toWeakMapKey(hint.originalException);
    const traceContext = key && escapedSpanTraceContexts.get(key);
    if (!traceContext) {
      return;
    }
    const eventTraceContext = event.contexts?.trace;
    const eventTraceId = eventTraceContext?.trace_id ?? (scope && getTraceContextFromScope(scope).trace_id);
    if (eventTraceId !== traceContext.trace_id) {
      return;
    }
    event.contexts = {
      ...event.contexts,
      trace: {
        ...eventTraceContext,
        ...traceContext
      }
    };
  }

  // node_modules/@sentry/core/build/esm/envelope.js
  function _enhanceEventWithSdkInfo(event, newSdkInfo) {
    if (!newSdkInfo) {
      return event;
    }
    const eventSdkInfo = event.sdk || {};
    event.sdk = {
      ...eventSdkInfo,
      name: eventSdkInfo.name || newSdkInfo.name,
      version: eventSdkInfo.version || newSdkInfo.version,
      integrations: [...event.sdk?.integrations || [], ...newSdkInfo.integrations || []],
      packages: [...event.sdk?.packages || [], ...newSdkInfo.packages || []],
      settings: event.sdk?.settings || newSdkInfo.settings ? {
        ...event.sdk?.settings,
        ...newSdkInfo.settings
      } : void 0
    };
    return event;
  }
  function createSessionEnvelope(session, dsn, metadata, tunnel) {
    const sdkInfo = getSdkMetadataForEnvelopeHeader(metadata);
    const envelopeHeaders = {
      sent_at: new Date(safeDateNow()).toISOString(),
      ...sdkInfo && { sdk: sdkInfo },
      ...!!tunnel && dsn && { dsn: dsnToString(dsn) }
    };
    const envelopeItem = "aggregates" in session ? [{ type: "sessions" }, session] : [{ type: "session" }, session.toJSON()];
    return createEnvelope(envelopeHeaders, [envelopeItem]);
  }
  function createEventEnvelope(event, dsn, metadata, tunnel) {
    const sdkInfo = getSdkMetadataForEnvelopeHeader(metadata);
    const eventType = event.type && event.type !== "replay_event" ? event.type : "event";
    _enhanceEventWithSdkInfo(event, metadata?.sdk);
    const envelopeHeaders = createEventEnvelopeHeaders(event, sdkInfo, tunnel, dsn);
    delete event.sdkProcessingMetadata;
    const eventItem = [{ type: eventType }, event];
    return createEnvelope(envelopeHeaders, [eventItem]);
  }

  // node_modules/@sentry/core/build/esm/utils/syncpromise.js
  var STATE_PENDING = 0;
  var STATE_RESOLVED = 1;
  var STATE_REJECTED = 2;
  function resolvedSyncPromise(value) {
    return new SyncPromise((resolve) => {
      resolve(value);
    });
  }
  function rejectedSyncPromise(reason) {
    return new SyncPromise((_, reject) => {
      reject(reason);
    });
  }
  var SyncPromise = class _SyncPromise {
    constructor(executor) {
      this._state = STATE_PENDING;
      this._handlers = [];
      this._runExecutor(executor);
    }
    /** @inheritdoc */
    then(onfulfilled, onrejected) {
      return new _SyncPromise((resolve, reject) => {
        this._handlers.push([
          false,
          (result) => {
            if (!onfulfilled) {
              resolve(result);
            } else {
              try {
                resolve(onfulfilled(result));
              } catch (e) {
                reject(e);
              }
            }
          },
          (reason) => {
            if (!onrejected) {
              reject(reason);
            } else {
              try {
                resolve(onrejected(reason));
              } catch (e) {
                reject(e);
              }
            }
          }
        ]);
        this._executeHandlers();
      });
    }
    /** @inheritdoc */
    catch(onrejected) {
      return this.then((val) => val, onrejected);
    }
    /** @inheritdoc */
    finally(onfinally) {
      return new _SyncPromise((resolve, reject) => {
        let val;
        let isRejected;
        return this.then(
          (value) => {
            isRejected = false;
            val = value;
            if (onfinally) {
              onfinally();
            }
          },
          (reason) => {
            isRejected = true;
            val = reason;
            if (onfinally) {
              onfinally();
            }
          }
        ).then(() => {
          if (isRejected) {
            reject(val);
            return;
          }
          resolve(val);
        });
      });
    }
    /** Excute the resolve/reject handlers. */
    _executeHandlers() {
      if (this._state === STATE_PENDING) {
        return;
      }
      const cachedHandlers = this._handlers.slice();
      this._handlers = [];
      cachedHandlers.forEach((handler) => {
        if (handler[0]) {
          return;
        }
        if (this._state === STATE_RESOLVED) {
          handler[1](this._value);
        }
        if (this._state === STATE_REJECTED) {
          handler[2](this._value);
        }
        handler[0] = true;
      });
    }
    /** Run the executor for the SyncPromise. */
    _runExecutor(executor) {
      const setResult = (state, value) => {
        if (this._state !== STATE_PENDING) {
          return;
        }
        if (isThenable(value)) {
          void value.then(resolve, reject);
          return;
        }
        this._state = state;
        this._value = value;
        this._executeHandlers();
      };
      const resolve = (value) => {
        setResult(STATE_RESOLVED, value);
      };
      const reject = (reason) => {
        setResult(STATE_REJECTED, reason);
      };
      try {
        executor(resolve, reject);
      } catch (e) {
        reject(e);
      }
    }
  };

  // node_modules/@sentry/core/build/esm/eventProcessors.js
  function notifyEventProcessors(processors, event, hint, index = 0, onDrop) {
    try {
      const result = _notifyEventProcessors(event, hint, processors, index, onDrop);
      return isThenable(result) ? result : resolvedSyncPromise(result);
    } catch (error2) {
      return rejectedSyncPromise(error2);
    }
  }
  function _notifyEventProcessors(event, hint, processors, index, onDrop) {
    const processor = processors[index];
    if (!event || !processor) {
      return event;
    }
    const processorName = `Event processor "${processor.id || "?"}"`;
    let callbackError = false;
    const result = safeCallback(
      DEBUG_BUILD ? `${processorName} threw an error, dropping event:` : "",
      () => processor({ ...event }, hint),
      () => {
        callbackError = true;
        return null;
      }
    );
    DEBUG_BUILD && result === null && debug.log(`${processorName} dropped event`);
    if (isThenable(result)) {
      return result.then((final) => {
        if (!final) {
          onDrop?.(callbackError ? "callback_error" : "event_processor");
          return null;
        }
        return _notifyEventProcessors(final, hint, processors, index + 1, onDrop);
      });
    }
    if (!result) {
      onDrop?.(callbackError ? "callback_error" : "event_processor");
      return null;
    }
    return _notifyEventProcessors(result, hint, processors, index + 1, onDrop);
  }

  // node_modules/@sentry/core/build/esm/utils/debug-ids.js
  var parsedStackResults;
  var lastSentryKeysCount;
  var lastNativeKeysCount;
  var cachedFilenameDebugIds;
  function getFilenameToDebugIdMap(stackParser) {
    const sentryDebugIdMap = GLOBAL_OBJ._sentryDebugIds;
    const nativeDebugIdMap = GLOBAL_OBJ._debugIds;
    if (!sentryDebugIdMap && !nativeDebugIdMap) {
      return {};
    }
    const sentryDebugIdKeys = sentryDebugIdMap ? Object.keys(sentryDebugIdMap) : [];
    const nativeDebugIdKeys = nativeDebugIdMap ? Object.keys(nativeDebugIdMap) : [];
    if (cachedFilenameDebugIds && sentryDebugIdKeys.length === lastSentryKeysCount && nativeDebugIdKeys.length === lastNativeKeysCount) {
      return cachedFilenameDebugIds;
    }
    lastSentryKeysCount = sentryDebugIdKeys.length;
    lastNativeKeysCount = nativeDebugIdKeys.length;
    cachedFilenameDebugIds = {};
    if (!parsedStackResults) {
      parsedStackResults = {};
    }
    const processDebugIds = (debugIdKeys, debugIdMap) => {
      for (const key of debugIdKeys) {
        const debugId = debugIdMap[key];
        const result = parsedStackResults?.[key];
        if (result && cachedFilenameDebugIds && debugId) {
          cachedFilenameDebugIds[result[0]] = debugId;
          if (parsedStackResults) {
            parsedStackResults[key] = [result[0], debugId];
          }
        } else if (debugId) {
          const parsedStack = stackParser(key);
          for (let i = parsedStack.length - 1; i >= 0; i--) {
            const stackFrame = parsedStack[i];
            const filename = stackFrame?.filename;
            if (filename && cachedFilenameDebugIds && parsedStackResults) {
              cachedFilenameDebugIds[filename] = debugId;
              parsedStackResults[key] = [filename, debugId];
              break;
            }
          }
        }
      }
    };
    if (sentryDebugIdMap) {
      processDebugIds(sentryDebugIdKeys, sentryDebugIdMap);
    }
    if (nativeDebugIdMap) {
      processDebugIds(nativeDebugIdKeys, nativeDebugIdMap);
    }
    return cachedFilenameDebugIds;
  }

  // node_modules/@sentry/core/build/esm/utils/eventUtils.js
  function isInternalException(hint) {
    return hint.data?.__sentry__ === true;
  }
  function getPossibleEventMessages(event) {
    const possibleMessages = [];
    if (event.message) {
      possibleMessages.push(event.message);
    }
    try {
      const lastException = event.exception.values[event.exception.values.length - 1];
      if (lastException?.value) {
        possibleMessages.push(lastException.value);
        if (lastException.type) {
          possibleMessages.push(`${lastException.type}: ${lastException.value}`);
        }
      }
    } catch {
    }
    return possibleMessages;
  }

  // node_modules/@sentry/core/build/esm/utils/prepareEvent.js
  function prepareEvent(options, event, hint, scope, client, isolationScope) {
    const { normalizeDepth = 3, normalizeMaxBreadth = 1e3 } = options;
    const prepared = {
      ...event,
      event_id: event.event_id || hint.event_id || uuid4(),
      timestamp: event.timestamp || dateTimestampInSeconds()
    };
    const integrations = hint.integrations || options.integrations.map((i) => i.name);
    applyClientOptions(prepared, options);
    applyIntegrationsMetadata(prepared, integrations);
    if (client) {
      client.emit("applyFrameMetadata", event);
    }
    if (event.type === void 0) {
      applyDebugIds(prepared, options.stackParser);
    }
    const finalScope = getFinalScope(scope, hint.captureContext);
    if (hint.mechanism) {
      addExceptionMechanismToCapturedException(prepared, hint.mechanism);
    }
    const clientEventProcessors = client ? client.getEventProcessors() : [];
    const data = getCombinedScopeData(isolationScope, finalScope);
    const attachments = [...hint.attachments || [], ...data.attachments];
    if (attachments.length) {
      hint.attachments = attachments;
    }
    applyScopeDataToEvent(prepared, data);
    const span = getActiveSpan(finalScope);
    if (span) {
      applySpanToEvent(prepared, span);
    }
    applyEscapedErrorSpanToEvent(prepared, hint, finalScope);
    const eventProcessors = [
      ...clientEventProcessors,
      // Run scope event processors _after_ all other processors
      ...data.eventProcessors
    ];
    const isTransaction = event.type === "transaction";
    const spanCountBeforeProcessing = event.spans?.length || 0;
    const result = isInternalException(hint) ? resolvedSyncPromise(prepared) : notifyEventProcessors(eventProcessors, prepared, hint, 0, (reason) => {
      if (!client) {
        return;
      }
      client.recordDroppedEvent(reason, getDataCategoryByType(event.type));
      if (isTransaction) {
        client.recordDroppedEvent(reason, "span", 1 + spanCountBeforeProcessing);
      }
    });
    return result.then((evt) => {
      if (!evt) {
        return null;
      }
      if (isTransaction && client) {
        const droppedSpanCount = spanCountBeforeProcessing - (evt.spans?.length || 0);
        if (droppedSpanCount > 0) {
          client.recordDroppedEvent("event_processor", "span", droppedSpanCount);
        }
      }
      applyDebugMeta(evt);
      if (typeof normalizeDepth === "number" && normalizeDepth > 0) {
        return normalizeEvent(evt, normalizeDepth, normalizeMaxBreadth);
      }
      return evt;
    });
  }
  function applyClientOptions(event, options) {
    const { environment, release, dist, maxValueLength } = options;
    event.environment = event.environment || environment || DEFAULT_ENVIRONMENT;
    if (!event.release && release) {
      event.release = release;
    }
    if (!event.dist && dist) {
      event.dist = dist;
    }
    const request = event.request;
    if (request?.url && maxValueLength) {
      request.url = truncate(request.url, maxValueLength);
    }
    if (maxValueLength) {
      event.exception?.values?.forEach((exception) => {
        if (exception.value) {
          exception.value = truncate(exception.value, maxValueLength);
        }
      });
    }
  }
  function applyDebugIds(event, stackParser) {
    const filenameDebugIdMap = getFilenameToDebugIdMap(stackParser);
    event.exception?.values?.forEach((exception) => {
      exception.stacktrace?.frames?.forEach((frame) => {
        if (frame.filename) {
          frame.debug_id = filenameDebugIdMap[frame.filename];
        }
      });
    });
  }
  function applyDebugMeta(event) {
    const filenameDebugIdMap = {};
    event.exception?.values?.forEach((exception) => {
      exception.stacktrace?.frames?.forEach((frame) => {
        if (frame.debug_id) {
          if (frame.abs_path) {
            filenameDebugIdMap[frame.abs_path] = frame.debug_id;
          } else if (frame.filename) {
            filenameDebugIdMap[frame.filename] = frame.debug_id;
          }
          delete frame.debug_id;
        }
      });
    });
    if (Object.keys(filenameDebugIdMap).length === 0) {
      return;
    }
    event.debug_meta = event.debug_meta || {};
    event.debug_meta.images = event.debug_meta.images || [];
    const images = event.debug_meta.images;
    Object.entries(filenameDebugIdMap).forEach(([filename, debug_id]) => {
      images.push({
        type: "sourcemap",
        code_file: filename,
        debug_id
      });
    });
  }
  function applyIntegrationsMetadata(event, integrationNames) {
    if (integrationNames.length > 0) {
      event.sdk = event.sdk || {};
      event.sdk.integrations = [...event.sdk.integrations || [], ...integrationNames];
    }
  }
  function normalizeEvent(event, depth, maxBreadth) {
    if (!event) {
      return null;
    }
    const normalized = {
      ...event,
      ...event.breadcrumbs && {
        breadcrumbs: event.breadcrumbs.map((b) => ({
          ...b,
          ...b.data && {
            data: normalize(b.data, depth, maxBreadth)
          }
        }))
      },
      ...event.user && {
        user: normalize(event.user, depth, maxBreadth)
      },
      ...event.contexts && {
        contexts: normalize(event.contexts, depth, maxBreadth)
      },
      ...event.extra && {
        extra: normalize(event.extra, depth, maxBreadth)
      }
    };
    if (event.contexts?.trace && normalized.contexts) {
      normalized.contexts.trace = event.contexts.trace;
      if (event.contexts.trace.data) {
        normalized.contexts.trace.data = normalize(event.contexts.trace.data, depth, maxBreadth);
      }
    }
    if (event.spans) {
      normalized.spans = event.spans.map((span) => {
        return {
          ...span,
          ...span.data && {
            data: normalize(span.data, depth, maxBreadth)
          }
        };
      });
    }
    if (event.contexts?.flags && normalized.contexts) {
      normalized.contexts.flags = normalize(event.contexts.flags, 3, maxBreadth);
    }
    return normalized;
  }
  function getFinalScope(scope, captureContext) {
    if (!captureContext) {
      return scope;
    }
    const finalScope = scope ? scope.clone() : new Scope();
    finalScope.update(captureContext);
    return finalScope;
  }
  function parseEventHintOrCaptureContext(hint) {
    if (!hint) {
      return void 0;
    }
    if (hintIsScopeOrFunction(hint)) {
      return { captureContext: hint };
    }
    if (hintIsScopeContext(hint)) {
      return {
        captureContext: hint
      };
    }
    return hint;
  }
  function hintIsScopeOrFunction(hint) {
    return hint instanceof Scope || typeof hint === "function";
  }
  var captureContextKeys = [
    "user",
    "level",
    "extra",
    "contexts",
    "tags",
    "fingerprint",
    "propagationContext"
  ];
  function hintIsScopeContext(hint) {
    return Object.keys(hint).some((key) => captureContextKeys.includes(key));
  }

  // node_modules/@sentry/core/build/esm/exports.js
  function captureException(exception, hint) {
    return getCurrentScope().captureException(exception, parseEventHintOrCaptureContext(hint));
  }
  function captureEvent(event, hint) {
    return getCurrentScope().captureEvent(event, hint);
  }
  function startSession(context) {
    const isolationScope = getIsolationScope();
    const { user } = getCombinedScopeData(isolationScope, getCurrentScope());
    const { userAgent } = GLOBAL_OBJ.navigator || {};
    const session = makeSession({
      user,
      ...userAgent && { userAgent },
      ...context
    });
    const currentSession = isolationScope.getSession();
    if (currentSession?.status === "ok") {
      updateSession(currentSession, { status: "exited" });
    }
    endSession();
    isolationScope.setSession(session);
    return session;
  }
  function endSession() {
    const isolationScope = getIsolationScope();
    const currentScope = getCurrentScope();
    const session = currentScope.getSession() || isolationScope.getSession();
    if (session) {
      closeSession(session);
    }
    _sendSessionUpdate();
    isolationScope.setSession();
  }
  function _sendSessionUpdate() {
    const isolationScope = getIsolationScope();
    const client = getClient();
    const session = isolationScope.getSession();
    if (session && client) {
      client.captureSession(session);
    }
  }
  function captureSession(end = false) {
    if (end) {
      endSession();
      return;
    }
    _sendSessionUpdate();
  }

  // node_modules/@sentry/core/build/esm/api.js
  var SENTRY_API_VERSION = "7";
  function getBaseApiEndpoint(dsn) {
    const protocol = dsn.protocol ? `${dsn.protocol}:` : "";
    const port = dsn.port ? `:${dsn.port}` : "";
    return `${protocol}//${dsn.host}${port}${dsn.path ? `/${dsn.path}` : ""}/api/`;
  }
  function _getIngestEndpoint(dsn) {
    return `${getBaseApiEndpoint(dsn)}${dsn.projectId}/envelope/`;
  }
  function _encodedAuth(dsn, sdkInfo) {
    const params = {
      sentry_version: SENTRY_API_VERSION
    };
    if (dsn.publicKey) {
      params.sentry_key = dsn.publicKey;
    }
    if (sdkInfo) {
      params.sentry_client = `${sdkInfo.name}/${sdkInfo.version}`;
    }
    return new URLSearchParams(params).toString();
  }
  function getEnvelopeEndpointWithUrlEncodedAuth(dsn, tunnel, sdkInfo) {
    return tunnel ? tunnel : `${_getIngestEndpoint(dsn)}?${_encodedAuth(dsn, sdkInfo)}`;
  }

  // node_modules/@sentry/core/build/esm/logs/envelope.js
  function createLogContainerEnvelopeItem(items, inferUserData) {
    const inferSetting = inferUserData ? "auto" : "never";
    return [
      {
        type: "log",
        item_count: items.length,
        content_type: "application/vnd.sentry.items.log+json"
      },
      {
        version: 2,
        ...isBrowser() && {
          ingest_settings: { infer_ip: inferSetting, infer_user_agent: inferSetting }
        },
        items
      }
    ];
  }
  function createLogEnvelope(logs, metadata, tunnel, dsn, inferUserData) {
    const headers = {};
    if (metadata?.sdk) {
      headers.sdk = {
        name: metadata.sdk.name,
        version: metadata.sdk.version
      };
    }
    if (!!tunnel && !!dsn) {
      headers.dsn = dsnToString(dsn);
    }
    return createEnvelope(headers, [createLogContainerEnvelopeItem(logs, inferUserData)]);
  }

  // node_modules/@sentry/core/build/esm/logs/internal.js
  function _INTERNAL_flushLogsBuffer(client, maybeLogBuffer) {
    const logBuffer = maybeLogBuffer ?? _INTERNAL_getLogBuffer(client) ?? [];
    if (logBuffer.length === 0) {
      return;
    }
    const clientOptions = client.getOptions();
    const envelope = createLogEnvelope(
      logBuffer,
      clientOptions._metadata,
      clientOptions.tunnel,
      client.getDsn(),
      client.getDataCollectionOptions().userInfo
    );
    _getBufferMap().set(client, []);
    client.emit("flushLogs");
    client.sendEnvelope(envelope);
  }
  function _INTERNAL_getLogBuffer(client) {
    return _getBufferMap().get(client);
  }
  function _getBufferMap() {
    return getGlobalSingleton("clientToLogBufferMap", () => /* @__PURE__ */ new WeakMap());
  }

  // node_modules/@sentry/core/build/esm/metrics/envelope.js
  function createMetricContainerEnvelopeItem(items, inferUserData) {
    const inferSetting = inferUserData ? "auto" : "never";
    return [
      {
        type: "trace_metric",
        item_count: items.length,
        content_type: "application/vnd.sentry.items.trace-metric+json"
      },
      {
        version: 2,
        ...isBrowser() && {
          ingest_settings: { infer_ip: inferSetting, infer_user_agent: inferSetting }
        },
        items
      }
    ];
  }
  function createMetricEnvelope(metrics, metadata, tunnel, dsn, inferUserData) {
    const headers = {};
    if (metadata?.sdk) {
      headers.sdk = {
        name: metadata.sdk.name,
        version: metadata.sdk.version
      };
    }
    if (!!tunnel && !!dsn) {
      headers.dsn = dsnToString(dsn);
    }
    return createEnvelope(headers, [createMetricContainerEnvelopeItem(metrics, inferUserData)]);
  }

  // node_modules/@sentry/core/build/esm/metrics/internal.js
  function _INTERNAL_flushMetricsBuffer(client, maybeMetricBuffer) {
    const metricBuffer = maybeMetricBuffer ?? _INTERNAL_getMetricBuffer(client) ?? [];
    if (metricBuffer.length === 0) {
      return;
    }
    const clientOptions = client.getOptions();
    const envelope = createMetricEnvelope(
      metricBuffer,
      clientOptions._metadata,
      clientOptions.tunnel,
      client.getDsn(),
      client.getDataCollectionOptions().userInfo
    );
    _getBufferMap2().set(client, []);
    client.emit("flushMetrics");
    client.sendEnvelope(envelope);
  }
  function _INTERNAL_getMetricBuffer(client) {
    return _getBufferMap2().get(client);
  }
  function _getBufferMap2() {
    return getGlobalSingleton("clientToMetricBufferMap", () => /* @__PURE__ */ new WeakMap());
  }

  // node_modules/@sentry/core/build/esm/tracing/spans/extractGenAiSpans.js
  function extractGenAiSpansFromEvent(event, client) {
    if (event.type !== "transaction" || !event.spans?.length || !event.sdkProcessingMetadata?.hasGenAiSpans || hasSpanStreamingEnabled(client)) {
      return void 0;
    }
    const genAiSpans = [];
    const remainingSpans = [];
    for (const span of event.spans) {
      if (span.op?.startsWith("gen_ai.")) {
        genAiSpans.push(spanJsonToSerializedStreamedSpan(span));
      } else {
        remainingSpans.push(span);
      }
    }
    if (genAiSpans.length === 0) {
      return void 0;
    }
    event.spans = remainingSpans;
    return createSpanContainerItem(genAiSpans, client);
  }

  // node_modules/@sentry/core/build/esm/utils/promisebuffer.js
  var SENTRY_BUFFER_FULL_ERROR = /* @__PURE__ */ Symbol.for("SentryBufferFullError");
  function makePromiseBuffer(limit = 100) {
    const buffer = /* @__PURE__ */ new Set();
    function isReady() {
      return buffer.size < limit;
    }
    function remove(task) {
      buffer.delete(task);
    }
    function add(taskProducer) {
      if (!isReady()) {
        return rejectedSyncPromise(SENTRY_BUFFER_FULL_ERROR);
      }
      const task = taskProducer();
      buffer.add(task);
      void task.then(
        () => remove(task),
        () => remove(task)
      );
      return task;
    }
    function drain(timeout) {
      if (!buffer.size) {
        return resolvedSyncPromise(true);
      }
      const drainPromise = Promise.allSettled(Array.from(buffer)).then(() => true);
      if (!timeout) {
        return drainPromise;
      }
      const promises = [
        drainPromise,
        new Promise((resolve) => safeUnref(setTimeout(() => resolve(false), timeout)))
      ];
      return Promise.race(promises);
    }
    return {
      get $() {
        return Array.from(buffer);
      },
      add,
      drain
    };
  }

  // node_modules/@sentry/core/build/esm/utils/ratelimit.js
  var DEFAULT_RETRY_AFTER = 60 * 1e3;
  function parseRetryAfterHeader(header, now = safeDateNow()) {
    const headerDelay = parseInt(`${header}`, 10);
    if (!isNaN(headerDelay)) {
      return headerDelay * 1e3;
    }
    const headerDate = Date.parse(`${header}`);
    if (!isNaN(headerDate)) {
      return headerDate - now;
    }
    return DEFAULT_RETRY_AFTER;
  }
  function disabledUntil(limits, dataCategory) {
    return limits[dataCategory] || limits.all || 0;
  }
  function isRateLimited(limits, dataCategory, now = safeDateNow()) {
    return disabledUntil(limits, dataCategory) > now;
  }
  function updateRateLimits(limits, { statusCode, headers }, now = safeDateNow()) {
    const updatedRateLimits = {
      ...limits
    };
    const rateLimitHeader = headers?.["x-sentry-rate-limits"];
    const retryAfterHeader = headers?.["retry-after"];
    if (rateLimitHeader) {
      for (const limit of rateLimitHeader.trim().split(",")) {
        const [retryAfter, categories, , , namespaces] = limit.split(":", 5);
        const headerDelay = parseInt(retryAfter, 10);
        const delay = (!isNaN(headerDelay) ? headerDelay : 60) * 1e3;
        if (!categories) {
          updatedRateLimits.all = now + delay;
        } else {
          for (const category of categories.split(";")) {
            if (category === "metric_bucket") {
              if (!namespaces || namespaces.split(";").includes("custom")) {
                updatedRateLimits[category] = now + delay;
              }
            } else {
              updatedRateLimits[category] = now + delay;
            }
          }
        }
      }
    } else if (retryAfterHeader) {
      updatedRateLimits.all = now + parseRetryAfterHeader(retryAfterHeader, now);
    } else if (statusCode === 429) {
      updatedRateLimits.all = now + 60 * 1e3;
    }
    return updatedRateLimits;
  }

  // node_modules/@sentry/core/build/esm/transports/base.js
  var DEFAULT_TRANSPORT_BUFFER_SIZE = 64;
  function createTransport(options, makeRequest, buffer = makePromiseBuffer(
    options.bufferSize || DEFAULT_TRANSPORT_BUFFER_SIZE
  )) {
    let rateLimits = {};
    const flush2 = (timeout) => buffer.drain(timeout);
    function recordItemLoss(reason, [headers, payload], type) {
      const dataCategory = envelopeItemTypeToDataCategory(type);
      if (type === "transaction") {
        options.recordDroppedEvent(reason, "span", (payload.spans?.length ?? 0) + 1);
      }
      options.recordDroppedEvent(reason, dataCategory, typeof headers.item_count === "number" ? headers.item_count : 1);
    }
    function send(envelope) {
      const filteredEnvelopeItems = [];
      forEachEnvelopeItem(envelope, (item, type) => {
        if (isRateLimited(rateLimits, envelopeItemTypeToDataCategory(type))) {
          recordItemLoss("ratelimit_backoff", item, type);
        } else {
          filteredEnvelopeItems.push(item);
        }
      });
      if (filteredEnvelopeItems.length === 0) {
        return Promise.resolve({});
      }
      const filteredEnvelope = createEnvelope(envelope[0], filteredEnvelopeItems);
      const recordEnvelopeLoss = (reason) => {
        if (envelopeContainsItemType(filteredEnvelope, ["client_report"])) {
          DEBUG_BUILD && debug.warn(`Dropping client report. Will not send outcomes (reason: ${reason}).`);
          return;
        }
        forEachEnvelopeItem(filteredEnvelope, (item, type) => {
          recordItemLoss(reason, item, type);
        });
      };
      const requestTask = () => makeRequest({ body: serializeEnvelope(filteredEnvelope) }).then(
        (response) => {
          if (response.statusCode === 413) {
            DEBUG_BUILD && debug.error(
              "Sentry responded with status code 413. Envelope was discarded due to exceeding size limits."
            );
            recordEnvelopeLoss("send_error");
            return response;
          }
          if (DEBUG_BUILD && response.statusCode !== void 0 && (response.statusCode < 200 || response.statusCode >= 300)) {
            debug.warn(`Sentry responded with status code ${response.statusCode} to sent event.`);
          }
          rateLimits = updateRateLimits(rateLimits, response);
          return response;
        },
        (error2) => {
          recordEnvelopeLoss("network_error");
          DEBUG_BUILD && debug.error("Encountered error running transport request:", error2);
          throw error2;
        }
      );
      return buffer.add(requestTask).then(
        (result) => result,
        (error2) => {
          if (error2 === SENTRY_BUFFER_FULL_ERROR) {
            DEBUG_BUILD && debug.error("Skipped sending event because buffer is full.");
            recordEnvelopeLoss("queue_overflow");
            return Promise.resolve({});
          } else {
            throw error2;
          }
        }
      );
    }
    return {
      send,
      flush: flush2
    };
  }

  // node_modules/@sentry/core/build/esm/utils/clientreport.js
  function createClientReportEnvelope(discarded_events, dsn, timestamp) {
    const clientReportItem = [
      { type: "client_report" },
      {
        timestamp: timestamp || dateTimestampInSeconds(),
        discarded_events
      }
    ];
    return createEnvelope(dsn ? { dsn } : {}, [clientReportItem]);
  }

  // node_modules/@sentry/core/build/esm/utils/transactionEvent.js
  function convertTransactionEventToSpanJson(event) {
    const { trace_id, parent_span_id, span_id, status, origin, data, op } = event.contexts?.trace ?? {};
    return {
      data: data ?? {},
      description: event.transaction,
      op,
      parent_span_id,
      span_id: span_id ?? "",
      start_timestamp: event.start_timestamp ?? 0,
      status: status ?? "ok",
      timestamp: event.timestamp,
      trace_id: trace_id ?? "",
      origin,
      profile_id: data?.[hm],
      exclusive_time: data?.[Vd],
      measurements: event.measurements,
      is_segment: true
    };
  }
  function convertSpanJsonToTransactionEvent(span) {
    return {
      type: "transaction",
      timestamp: span.timestamp,
      start_timestamp: span.start_timestamp,
      transaction: span.description,
      contexts: {
        trace: {
          trace_id: span.trace_id,
          span_id: span.span_id,
          parent_span_id: span.parent_span_id,
          op: span.op,
          status: span.status,
          origin: span.origin,
          data: {
            ...span.data,
            ...span.profile_id && { [hm]: span.profile_id },
            ...span.exclusive_time && { [Vd]: span.exclusive_time }
          }
        }
      },
      measurements: span.measurements
    };
  }

  // node_modules/@sentry/core/build/esm/utils/warnAboutIgnoredTransactionOptions.js
  function maybeWarnAboutIgnoredTransactionOptions(options) {
    if (options.traceLifecycle !== "stream" || // oxlint-disable-next-line typescript/no-deprecated
    !(options.beforeSendTransaction || options.ignoreTransactions?.length)) {
      return;
    }
    consoleSandbox(() => {
      console.warn(
        "[Sentry] `beforeSendTransaction` and `ignoreTransactions` are ignored with `traceLifecycle: 'stream'` (enabled by default). Use `beforeSendSpan` and `ignoreSpans` instead, or set `traceLifecycle: 'static'`."
      );
    });
  }

  // node_modules/@sentry/core/build/esm/utils/data-collection/resolveDataCollectionOptions.js
  var DEFAULTS = {
    userInfo: true,
    cookies: true,
    httpHeaders: { request: true, response: true },
    httpBodies: ["incomingRequest", "outgoingRequest", "incomingResponse", "outgoingResponse"],
    urlQueryParams: true,
    graphQL: { document: true, variables: true },
    genAI: { inputs: true, outputs: true },
    mcp: { inputs: true, outputs: true },
    databaseQueryData: true,
    queues: true,
    stackFrameVariables: true,
    frameContextLines: 5
  };
  function isCollectBehavior(value) {
    return typeof value === "boolean" || "allow" in value || "deny" in value;
  }
  function resolveHttpHeaders(httpHeaders) {
    if (httpHeaders === void 0) {
      return { ...DEFAULTS.httpHeaders };
    }
    if (isCollectBehavior(httpHeaders)) {
      return { request: httpHeaders, response: httpHeaders };
    }
    return {
      request: httpHeaders.request ?? DEFAULTS.httpHeaders.request,
      response: httpHeaders.response ?? DEFAULTS.httpHeaders.response
    };
  }
  function resolveDataCollectionOptions(options) {
    const dc = options.dataCollection ?? {};
    return {
      userInfo: dc.userInfo ?? DEFAULTS.userInfo,
      cookies: dc.cookies ?? DEFAULTS.cookies,
      httpHeaders: resolveHttpHeaders(dc.httpHeaders),
      httpBodies: dc.httpBodies ?? DEFAULTS.httpBodies,
      urlQueryParams: dc.urlQueryParams ?? DEFAULTS.urlQueryParams,
      graphQL: {
        document: dc.graphQL?.document ?? DEFAULTS.graphQL.document,
        variables: dc.graphQL?.variables ?? DEFAULTS.graphQL.variables
      },
      genAI: {
        inputs: dc.genAI?.inputs ?? DEFAULTS.genAI.inputs,
        outputs: dc.genAI?.outputs ?? DEFAULTS.genAI.outputs
      },
      mcp: {
        inputs: dc.mcp?.inputs ?? DEFAULTS.mcp.inputs,
        outputs: dc.mcp?.outputs ?? DEFAULTS.mcp.outputs
      },
      databaseQueryData: dc.databaseQueryData ?? DEFAULTS.databaseQueryData,
      queues: dc.queues ?? DEFAULTS.queues,
      stackFrameVariables: dc.stackFrameVariables ?? DEFAULTS.stackFrameVariables,
      frameContextLines: dc.frameContextLines ?? DEFAULTS.frameContextLines
    };
  }

  // node_modules/@sentry/core/build/esm/client.js
  var ALREADY_SEEN_ERROR = "Not capturing exception because it's already been captured.";
  var MISSING_RELEASE_FOR_SESSION_ERROR = "Discarded session because of missing or non-string release";
  var INTERNAL_ERROR_SYMBOL = /* @__PURE__ */ Symbol.for("SentryInternalError");
  var DO_NOT_SEND_EVENT_SYMBOL = /* @__PURE__ */ Symbol.for("SentryDoNotSendEventError");
  var DEFAULT_FLUSH_INTERVAL = 5e3;
  var CLOSED_CLIENT_SYMBOL = /* @__PURE__ */ Symbol.for("SentryClosedClient");
  function isClientClosed(client) {
    return CLOSED_CLIENT_SYMBOL in client;
  }
  function _makeInternalError(message) {
    return {
      message,
      [INTERNAL_ERROR_SYMBOL]: true
    };
  }
  function _makeDoNotSendEventError(message) {
    return {
      message,
      [DO_NOT_SEND_EVENT_SYMBOL]: true
    };
  }
  function _isInternalError(error2) {
    return isObjectLike(error2) && INTERNAL_ERROR_SYMBOL in error2;
  }
  function _isDoNotSendEventError(error2) {
    return isObjectLike(error2) && DO_NOT_SEND_EVENT_SYMBOL in error2;
  }
  function setupWeightBasedFlushing(client, afterCaptureHook, flushHook, estimateSizeFn, flushFn) {
    let weight = 0;
    let flushTimeout;
    let isTimerActive = false;
    client.on(flushHook, () => {
      weight = 0;
      clearTimeout(flushTimeout);
      isTimerActive = false;
    });
    client.on(afterCaptureHook, (item) => {
      weight += estimateSizeFn(item);
      if (weight >= 8e5) {
        flushFn(client);
      } else if (!isTimerActive) {
        const flushInterval = client.getOptions()._flushInterval ?? DEFAULT_FLUSH_INTERVAL;
        if (flushInterval > 0) {
          isTimerActive = true;
          flushTimeout = safeUnref(
            setTimeout(() => {
              flushFn(client);
            }, flushInterval)
          );
        }
      }
    });
    client.on("flush", () => {
      flushFn(client);
    });
  }
  var Client = class {
    /**
     * Initializes this client instance.
     *
     * @param options Options for the client.
     */
    constructor(options) {
      this._options = {
        attachStacktrace: true,
        ...options,
        traceLifecycle: options.traceLifecycle === "static" ? "static" : "stream"
      };
      this._integrations = {};
      this._numProcessing = 0;
      this._outcomes = {};
      this._hooks = {};
      this._eventProcessors = [];
      this._promiseBuffer = makePromiseBuffer(options.transportOptions?.bufferSize ?? DEFAULT_TRANSPORT_BUFFER_SIZE);
      this._dataCollection = resolveDataCollectionOptions(options);
      this._unhandledSessionStatus = "crashed";
      if (options.dsn) {
        this._dsn = makeDsn(options.dsn);
      } else {
        DEBUG_BUILD && debug.warn("No DSN provided, client will not send events.");
      }
      const { beforeSendSpan, traceLifecycle } = this._options;
      if (DEBUG_BUILD && beforeSendSpan && isStaticBeforeSendSpanCallback(beforeSendSpan) !== (traceLifecycle === "static")) {
        consoleSandbox(() => {
          console.warn(
            `Ignoring \`beforeSendSpan\`: ${traceLifecycle === "static" ? "wrap it with" : "remove"} \`Sentry.withStaticSpan\` to use it with \`traceLifecycle: "${traceLifecycle}"\`.`
          );
        });
      }
      if (this._dsn) {
        const url = getEnvelopeEndpointWithUrlEncodedAuth(
          this._dsn,
          options.tunnel,
          options._metadata ? options._metadata.sdk : void 0
        );
        this._transport = options.transport({
          tunnel: this._options.tunnel,
          recordDroppedEvent: this.recordDroppedEvent.bind(this),
          ...options.transportOptions,
          url
        });
      }
      setupWeightBasedFlushing(this, "afterCaptureLog", "flushLogs", estimateLogSizeInBytes, _INTERNAL_flushLogsBuffer);
      setupWeightBasedFlushing(
        this,
        "afterCaptureMetric",
        "flushMetrics",
        estimateMetricSizeInBytes,
        _INTERNAL_flushMetricsBuffer
      );
    }
    /**
     * Captures an exception event and sends it to Sentry.
     *
     * Unlike `captureException` exported from every SDK, this method requires that you pass it the current scope.
     */
    captureException(exception, hint, scope) {
      const eventId = uuid4();
      if (checkOrSetAlreadyCaught(exception)) {
        DEBUG_BUILD && debug.log(ALREADY_SEEN_ERROR);
        return eventId;
      }
      const hintWithEventId = {
        event_id: eventId,
        ...hint
      };
      this._process(
        () => this.eventFromException(exception, hintWithEventId).then((event) => this._captureEvent(event, hintWithEventId, scope)).then((res) => res),
        "error"
      );
      return hintWithEventId.event_id;
    }
    /**
     * Captures a message event and sends it to Sentry.
     *
     * Unlike `captureMessage` exported from every SDK, this method requires that you pass it the current scope.
     */
    captureMessage(message, level, hint, currentScope) {
      const hintWithEventId = {
        event_id: uuid4(),
        ...hint
      };
      const eventMessage = isParameterizedString(message) ? message : String(message);
      const isMessage = isPrimitive(message);
      const promisedEvent = isMessage ? this.eventFromMessage(eventMessage, level, hintWithEventId) : this.eventFromException(message, hintWithEventId);
      this._process(
        () => promisedEvent.then((event) => this._captureEvent(event, hintWithEventId, currentScope)),
        isMessage ? "unknown" : "error"
      );
      return hintWithEventId.event_id;
    }
    /**
     * Captures a manually created event and sends it to Sentry.
     *
     * Unlike `captureEvent` exported from every SDK, this method requires that you pass it the current scope.
     */
    captureEvent(event, hint, currentScope) {
      const eventId = uuid4();
      if (hint?.originalException && checkOrSetAlreadyCaught(hint.originalException)) {
        DEBUG_BUILD && debug.log(ALREADY_SEEN_ERROR);
        return eventId;
      }
      const hintWithEventId = {
        event_id: eventId,
        ...hint
      };
      const sdkProcessingMetadata = event.sdkProcessingMetadata || {};
      const capturedSpanScope = sdkProcessingMetadata.capturedSpanScope;
      const capturedSpanIsolationScope = sdkProcessingMetadata.capturedSpanIsolationScope;
      const dataCategory = getDataCategoryByType(event.type);
      this._process(
        () => this._captureEvent(event, hintWithEventId, capturedSpanScope || currentScope, capturedSpanIsolationScope),
        dataCategory
      );
      return hintWithEventId.event_id;
    }
    /**
     * Captures a session.
     */
    captureSession(session) {
      this.sendSession(session);
      updateSession(session, { init: false });
    }
    /**
     * Get the current Dsn.
     */
    getDsn() {
      return this._dsn;
    }
    /**
     * Get the current options.
     */
    getOptions() {
      return this._options;
    }
    /**
     * Get the resolved data collection configuration.
     */
    getDataCollectionOptions() {
      return this._dataCollection;
    }
    /**
     * Get the SDK metadata.
     * @see SdkMetadata
     */
    getSdkMetadata() {
      return this._options._metadata;
    }
    /**
     * Returns the transport that is used by the client.
     * Please note that the transport gets lazy initialized so it will only be there once the first event has been sent.
     */
    getTransport() {
      return this._transport;
    }
    /**
     * Wait for all events to be sent or the timeout to expire, whichever comes first.
     *
     * @param timeout Maximum time in ms the client should wait for events to be flushed. Omitting this parameter will
     *   cause the client to wait until all events are sent before resolving the promise.
     * @returns A promise that will resolve with `true` if all events are sent before the timeout, or `false` if there are
     * still events in the queue when the timeout is reached.
     */
    // @ts-expect-error - PromiseLike is a subset of Promise
    async flush(timeout) {
      const transport = this._transport;
      this.emit("flush");
      if (!transport) {
        return true;
      }
      const clientFinished = await this._isClientDoneProcessing(timeout);
      const transportFlushed = await transport.flush(timeout);
      return clientFinished && transportFlushed;
    }
    /**
     * Flush the event queue and set the client to `enabled = false`. See {@link Client.flush}.
     *
     * @param {number} timeout Maximum time in ms the client should wait before shutting down. Omitting this parameter will cause
     *   the client to wait until all events are sent before disabling itself.
     * @returns {Promise<boolean>} A promise which resolves to `true` if the flush completes successfully before the timeout, or `false` if
     * it doesn't.
     */
    // @ts-expect-error - PromiseLike is a subset of Promise
    async close(timeout) {
      Object.defineProperty(this, CLOSED_CLIENT_SYMBOL, { value: true });
      const result = await this.flush(timeout);
      this.getOptions().enabled = false;
      this.emit("close");
      return result;
    }
    /**
     * Get all installed event processors.
     */
    getEventProcessors() {
      return this._eventProcessors;
    }
    /**
     * Adds an event processor that applies to any event processed by this client.
     */
    addEventProcessor(eventProcessor) {
      this._eventProcessors.push(eventProcessor);
    }
    /**
     * Initialize this client.
     * Call this after the client was set on a scope.
     */
    init() {
      if (this._isEnabled() || // Force integrations to be setup even if no DSN was set when we have
      // Spotlight enabled. This is particularly important for browser as we
      // don't support the `spotlight` option there and rely on the users
      // adding the `spotlightBrowserIntegration()` to their integrations which
      // wouldn't get initialized with the check below when there's no DSN set.
      this._options.integrations.some(({ name }) => name.startsWith("Spotlight"))) {
        this._setupIntegrations();
        maybeWarnAboutIgnoredTransactionOptions(this._options);
      }
    }
    /**
     * Gets an installed integration by its name.
     *
     * @returns {Integration|undefined} The installed integration or `undefined` if no integration with that `name` was installed.
     */
    getIntegrationByName(integrationName) {
      return this._integrations[integrationName];
    }
    /**
     * Returns the names of all installed integrations.
     */
    getIntegrationNames() {
      return Object.keys(this._integrations);
    }
    /**
     * Add an integration to the client.
     * This can be used to e.g. lazy load integrations.
     * In most cases, this should not be necessary,
     * and you're better off just passing the integrations via `integrations: []` at initialization time.
     * However, if you find the need to conditionally load & add an integration, you can use `addIntegration` to do so.
     */
    addIntegration(integration) {
      const isAlreadyInstalled = this._integrations[integration.name];
      if (!isAlreadyInstalled && integration.beforeSetup) {
        integration.beforeSetup(this);
      }
      setupIntegration(this, integration, this._integrations);
      if (!isAlreadyInstalled) {
        afterSetupIntegrations(this, [integration]);
      }
    }
    /**
     * Send a fully prepared event to Sentry.
     */
    sendEvent(event, hint = {}) {
      this.emit("beforeSendEvent", event, hint);
      const genAiSpanItem = extractGenAiSpansFromEvent(event, this);
      let env = createEventEnvelope(event, this._dsn, this._options._metadata, this._options.tunnel);
      if (!isInternalException(hint)) {
        for (const attachment of hint.attachments || []) {
          env = addItemToEnvelope(env, createAttachmentEnvelopeItem(attachment));
        }
      }
      if (genAiSpanItem) {
        env = addItemToEnvelope(env, genAiSpanItem);
      }
      this.sendEnvelope(env).then((sendResponse) => this.emit("afterSendEvent", event, sendResponse));
    }
    /**
     * Send a session or session aggregrates to Sentry.
     */
    sendSession(session) {
      const { release: clientReleaseOption, environment: clientEnvironmentOption = DEFAULT_ENVIRONMENT } = this._options;
      if ("aggregates" in session) {
        const sessionAttrs = session.attrs || {};
        if (!sessionAttrs.release && !clientReleaseOption) {
          DEBUG_BUILD && debug.warn(MISSING_RELEASE_FOR_SESSION_ERROR);
          return;
        }
        sessionAttrs.release = sessionAttrs.release || clientReleaseOption;
        sessionAttrs.environment = sessionAttrs.environment || clientEnvironmentOption;
        session.attrs = sessionAttrs;
      } else {
        if (!session.release && !clientReleaseOption) {
          DEBUG_BUILD && debug.warn(MISSING_RELEASE_FOR_SESSION_ERROR);
          return;
        }
        session.release = session.release || clientReleaseOption;
        session.environment = session.environment || clientEnvironmentOption;
      }
      this.emit("beforeSendSession", session);
      const env = createSessionEnvelope(session, this._dsn, this._options._metadata, this._options.tunnel);
      this.sendEnvelope(env);
    }
    /**
     * Record on the client that an event got dropped (ie, an event that will not be sent to Sentry).
     */
    recordDroppedEvent(reason, category, count = 1) {
      if (this._options.sendClientReports) {
        const key = `${reason}:${category}`;
        DEBUG_BUILD && debug.log(`Recording outcome: "${key}"${count > 1 ? ` (${count} times)` : ""}`);
        this._outcomes[key] = (this._outcomes[key] || 0) + count;
      }
    }
    /**
     * Register a hook on this client.
     */
    on(hook, callback) {
      const hookCallbacks = this._hooks[hook] = this._hooks[hook] || /* @__PURE__ */ new Set();
      const uniqueCallback = (...args) => callback(...args);
      hookCallbacks.add(uniqueCallback);
      return () => {
        hookCallbacks.delete(uniqueCallback);
      };
    }
    /**
     * Emit a hook that was previously registered via `on()`.
     */
    emit(hook, ...rest) {
      const callbacks = this._hooks[hook];
      if (callbacks) {
        callbacks.forEach((callback) => callback(...rest));
      }
    }
    /**
     * Send an envelope to Sentry.
     */
    // @ts-expect-error - PromiseLike is a subset of Promise
    async sendEnvelope(envelope) {
      this.emit("beforeEnvelope", envelope);
      if (this._isEnabled() && this._transport) {
        try {
          const result = await this._transport.send(envelope);
          this.emit("afterEnvelope", envelope);
          return result;
        } catch (reason) {
          DEBUG_BUILD && debug.error("Error while sending envelope:", reason);
          return {};
        }
      }
      DEBUG_BUILD && debug.error("Transport disabled");
      return {};
    }
    /**
     * Register a cleanup function to be called when the client is disposed.
     * This is useful for integrations that need to clean up global state.
     *
     * NOTE: This is a no-op in the base `Client` class. Subclasses like `ServerRuntimeClient`
     * override this method to actually register and execute cleanup callbacks.
     */
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    registerCleanup(callback) {
    }
    /**
     * Disposes of the client and releases all resources.
     *
     * Subclasses should override this method to clean up their own resources, including invoking
     * any callbacks registered via {@link Client.registerCleanup}. The base implementation is a
     * no-op and does NOT execute registered cleanup callbacks.
     *
     * After calling dispose(), the client should not be used anymore.
     */
    dispose() {
    }
    /* eslint-enable @typescript-eslint/unified-signatures */
    /** Setup integrations for this client. */
    _setupIntegrations() {
      const { integrations } = this._options;
      this._integrations = setupIntegrations(this, integrations);
      afterSetupIntegrations(this, integrations);
    }
    /** Updates existing session based on the provided event */
    _updateSessionFromEvent(session, event) {
      let unhandled = event.level === "fatal";
      let errored = false;
      const exceptions = event.exception?.values;
      if (exceptions) {
        errored = true;
        unhandled = false;
        for (const ex of exceptions) {
          if (ex.mechanism?.handled === false) {
            unhandled = true;
            break;
          }
        }
      }
      const sessionNonTerminal = session.status === "ok";
      const shouldUpdateAndSend = sessionNonTerminal && session.errors === 0 || sessionNonTerminal && unhandled;
      if (shouldUpdateAndSend) {
        updateSession(session, {
          ...unhandled && { status: this._unhandledSessionStatus },
          errors: session.errors || Number(errored || unhandled)
        });
        this.captureSession(session);
      }
    }
    /**
     * Determine if the client is finished processing. Returns a promise because it will wait `timeout` ms before saying
     * "no" (resolving to `false`) in order to give the client a chance to potentially finish first.
     *
     * @param timeout The time, in ms, after which to resolve to `false` if the client is still busy. Passing `0` (or not
     * passing anything) will make the promise wait as long as it takes for processing to finish before resolving to
     * `true`.
     * @returns A promise which will resolve to `true` if processing is already done or finishes before the timeout, and
     * `false` otherwise
     */
    async _isClientDoneProcessing(timeout) {
      let ticked = 0;
      while (!timeout || ticked < timeout) {
        await new Promise((resolve) => setTimeout(resolve, 1));
        if (!this._numProcessing) {
          return true;
        }
        ticked++;
      }
      return false;
    }
    /** Determines whether this SDK is enabled and a transport is present. */
    _isEnabled() {
      return this.getOptions().enabled !== false && this._transport !== void 0;
    }
    /**
     * Adds common information to events.
     *
     * The information includes release and environment from `options`,
     * breadcrumbs and context (extra, tags and user) from the scope.
     *
     * Information that is already present in the event is never overwritten. For
     * nested objects, such as the context, keys are merged.
     *
     * @param event The original event.
     * @param hint May contain additional information about the original exception.
     * @param currentScope A scope containing event metadata.
     * @returns A new event with more information.
     */
    _prepareEvent(event, hint, currentScope, isolationScope) {
      const options = this.getOptions();
      const integrations = this.getIntegrationNames();
      if (!hint.integrations && integrations.length) {
        hint.integrations = integrations;
      }
      this.emit("preprocessEvent", event, hint);
      if (!event.type) {
        isolationScope.setLastEventId(event.event_id || hint.event_id);
      }
      return prepareEvent(options, event, hint, currentScope, this, isolationScope).then((evt) => {
        if (evt === null) {
          return evt;
        }
        this.emit("postprocessEvent", evt, hint);
        evt.contexts = {
          trace: { ...evt.contexts?.trace, ...getTraceContextFromScope(currentScope) },
          ...evt.contexts
        };
        const dynamicSamplingContext = getDynamicSamplingContextFromScope(this, currentScope);
        evt.sdkProcessingMetadata = {
          dynamicSamplingContext,
          ...evt.sdkProcessingMetadata
        };
        return evt;
      });
    }
    /**
     * Processes the event and logs an error in case of rejection
     * @param event
     * @param hint
     * @param scope
     */
    _captureEvent(event, hint = {}, currentScope = getCurrentScope(), isolationScope = getIsolationScope()) {
      if (DEBUG_BUILD && isErrorEvent2(event)) {
        debug.log(`Captured error event \`${getPossibleEventMessages(event)[0] || "<unknown>"}\``);
      }
      return this._processEvent(event, hint, currentScope, isolationScope).then(
        (finalEvent) => {
          return finalEvent.event_id;
        },
        (reason) => {
          if (DEBUG_BUILD) {
            if (_isDoNotSendEventError(reason)) {
              debug.log(reason.message);
            } else if (_isInternalError(reason)) {
              debug.warn(reason.message);
            } else {
              debug.warn(reason);
            }
          }
          return void 0;
        }
      );
    }
    /**
     * Processes an event (either error or message) and sends it to Sentry.
     *
     * This also adds breadcrumbs and context information to the event. However,
     * platform specific meta data (such as the User's IP address) must be added
     * by the SDK implementor.
     *
     *
     * @param event The event to send to Sentry.
     * @param hint May contain additional information about the original exception.
     * @param currentScope A scope containing event metadata.
     * @returns A SyncPromise that resolves with the event or rejects in case event was/will not be send.
     */
    _processEvent(event, hint, currentScope, isolationScope) {
      const options = this.getOptions();
      const { sampleRate } = options;
      const isTransaction = isTransactionEvent(event);
      const isError2 = isErrorEvent2(event);
      const eventType = event.type || "error";
      const beforeSendLabel = `before send for type \`${eventType}\``;
      let beforeSendDropReason = "before_send";
      let ignoredSpanCount = 0;
      const parsedSampleRate = typeof sampleRate === "undefined" ? void 0 : parseSampleRate(sampleRate);
      const dataCategory = getDataCategoryByType(event.type);
      let preparedSpanCount = 0;
      return this._prepareEvent(event, hint, currentScope, isolationScope).then((prepared) => {
        if (prepared === null) {
          throw _makeDoNotSendEventError("An event processor returned `null`, will not send event.");
        }
        preparedSpanCount = prepared.spans?.length || 0;
        if (isInternalException(hint)) {
          return prepared;
        }
        return processBeforeSend(
          options,
          prepared,
          hint,
          (reason) => {
            beforeSendDropReason = reason;
          },
          (count) => {
            ignoredSpanCount = count;
          }
        );
      }).then((processedEvent) => {
        if (ignoredSpanCount) {
          this.recordDroppedEvent("ignored", "span", ignoredSpanCount);
        }
        const isValidEvent = isPlainObject(processedEvent);
        if (!isValidEvent || processedEvent === null) {
          this.recordDroppedEvent(beforeSendDropReason, dataCategory);
          if (isTransaction) {
            this.recordDroppedEvent(beforeSendDropReason, "span", 1 + preparedSpanCount - ignoredSpanCount);
          }
          if (processedEvent !== null) {
            throw _makeInternalError(`${beforeSendLabel} must return \`null\` or a valid event.`);
          }
          const dropMessage = beforeSendDropReason === "ignored" ? "Transaction matched `ignoreSpans`" : `${beforeSendLabel} ${beforeSendDropReason === "callback_error" ? "threw an error" : "returned `null`"}`;
          throw _makeDoNotSendEventError(`${dropMessage}, will not send event.`);
        }
        const session = currentScope.getSession() || isolationScope.getSession();
        if (isError2 && session) {
          this._updateSessionFromEvent(session, processedEvent);
        }
        if (isError2 && typeof parsedSampleRate === "number" && safeMathRandom() > parsedSampleRate) {
          this.recordDroppedEvent("sample_rate", "error");
          throw _makeDoNotSendEventError(
            `Discarding event because it's not included in the random sample (sampling rate = ${sampleRate})`
          );
        }
        if (isTransaction) {
          const droppedSpanCount = preparedSpanCount - ignoredSpanCount - (processedEvent.spans?.length || 0);
          if (droppedSpanCount > 0) {
            this.recordDroppedEvent("before_send", "span", droppedSpanCount);
          }
        }
        const transactionInfo = processedEvent.transaction_info;
        if (isTransaction && transactionInfo && processedEvent.transaction !== event.transaction) {
          const source = "custom";
          processedEvent.transaction_info = {
            ...transactionInfo,
            source
          };
        }
        this.sendEvent(processedEvent, hint);
        return processedEvent;
      }).then(null, (reason) => {
        if (_isDoNotSendEventError(reason) || _isInternalError(reason)) {
          throw reason;
        }
        this.captureException(reason, {
          mechanism: {
            handled: false,
            type: "internal"
          },
          data: {
            __sentry__: true
          },
          originalException: reason
        });
        throw _makeInternalError(
          `Event processing pipeline threw an error, original event will not be sent. Details have been sent as a new event.
Reason: ${reason}`
        );
      });
    }
    /**
     * Occupies the client with processing and event
     */
    _process(taskProducer, dataCategory) {
      this._numProcessing++;
      void this._promiseBuffer.add(taskProducer).then(
        (value) => {
          this._numProcessing--;
          return value;
        },
        (reason) => {
          this._numProcessing--;
          if (reason === SENTRY_BUFFER_FULL_ERROR) {
            this.recordDroppedEvent("queue_overflow", dataCategory);
          }
          return reason;
        }
      );
    }
    /**
     * Clears outcomes on this client and returns them.
     */
    _clearOutcomes() {
      const outcomes = this._outcomes;
      this._outcomes = {};
      return Object.entries(outcomes).map(([key, quantity]) => {
        const [reason, category] = key.split(":");
        return {
          reason,
          category,
          quantity
        };
      });
    }
    /**
     * Sends client reports as an envelope.
     */
    _flushOutcomes() {
      DEBUG_BUILD && debug.log("Flushing outcomes...");
      const outcomes = this._clearOutcomes();
      if (outcomes.length === 0) {
        DEBUG_BUILD && debug.log("No outcomes to send");
        return;
      }
      if (!this._dsn) {
        DEBUG_BUILD && debug.log("No dsn provided, will not send outcomes");
        return;
      }
      DEBUG_BUILD && debug.log("Sending outcomes:", outcomes);
      const envelope = createClientReportEnvelope(outcomes, this._options.tunnel && dsnToString(this._dsn));
      this.sendEnvelope(envelope);
    }
  };
  function processBeforeSend(options, event, hint, onDrop, onIgnoredSpans) {
    const {
      beforeSend,
      ignoreSpans,
      // oxlint-disable-next-line typescript/no-deprecated
      beforeSendTransaction
    } = options;
    const beforeSendSpan = isStaticBeforeSendSpanCallback(options.beforeSendSpan) && options.beforeSendSpan;
    let processedEvent = event;
    if (isErrorEvent2(processedEvent) && beforeSend) {
      const errorEvent = processedEvent;
      return safeCallback(
        DEBUG_BUILD ? "The `beforeSend` callback threw an error, dropping the event:" : "",
        () => beforeSend(errorEvent, hint),
        () => {
          onDrop("callback_error");
          return null;
        }
      );
    }
    if (isTransactionEvent(processedEvent)) {
      if (beforeSendSpan || ignoreSpans) {
        const rootSpanJson = convertTransactionEventToSpanJson(processedEvent);
        if (ignoreSpans?.length && shouldIgnoreSpan(
          { description: rootSpanJson.description, op: rootSpanJson.op, attributes: rootSpanJson.data },
          ignoreSpans
        )) {
          onDrop("ignored");
          return null;
        }
        if (beforeSendSpan) {
          const processedRootSpanJson = applyBeforeSendSpanCallback(rootSpanJson, beforeSendSpan);
          processedEvent = merge(event, convertSpanJsonToTransactionEvent(processedRootSpanJson));
        }
        if (processedEvent.spans) {
          const processedSpans = [];
          const initialSpans = processedEvent.spans;
          for (const span of initialSpans) {
            if (ignoreSpans?.length && shouldIgnoreSpan({ description: span.description, op: span.op, attributes: span.data }, ignoreSpans)) {
              reparentChildSpans(initialSpans, span);
              continue;
            }
            if (beforeSendSpan) {
              processedSpans.push(applyBeforeSendSpanCallback(span, beforeSendSpan));
            } else {
              processedSpans.push(span);
            }
          }
          onIgnoredSpans(initialSpans.length - processedSpans.length);
          processedEvent.spans = processedSpans;
        }
      }
      if (beforeSendTransaction) {
        return safeCallback(
          DEBUG_BUILD ? "The `beforeSendTransaction` callback threw an error, dropping the event:" : "",
          () => beforeSendTransaction(processedEvent, hint),
          () => {
            onDrop("callback_error");
            return null;
          }
        );
      }
    }
    return processedEvent;
  }
  function isErrorEvent2(event) {
    return event.type === void 0;
  }
  function isTransactionEvent(event) {
    return event.type === "transaction";
  }
  function estimateMetricSizeInBytes(metric) {
    let weight = 0;
    if (metric.name) {
      weight += metric.name.length * 2;
    }
    weight += 8;
    return weight + estimateAttributesSizeInBytes(metric.attributes);
  }
  function estimateLogSizeInBytes(log2) {
    let weight = 0;
    if (log2.message) {
      weight += log2.message.length * 2;
    }
    return weight + estimateAttributesSizeInBytes(log2.attributes);
  }
  function estimateAttributesSizeInBytes(attributes) {
    if (!attributes) {
      return 0;
    }
    let weight = 0;
    Object.values(attributes).forEach((value) => {
      if (Array.isArray(value)) {
        weight += value.length * estimatePrimitiveSizeInBytes(value[0]);
      } else if (isPrimitive(value)) {
        weight += estimatePrimitiveSizeInBytes(value);
      } else {
        weight += 100;
      }
    });
    return weight;
  }
  function estimatePrimitiveSizeInBytes(value) {
    if (typeof value === "string") {
      return value.length * 2;
    } else if (typeof value === "number") {
      return 8;
    } else if (typeof value === "boolean") {
      return 4;
    }
    return 0;
  }

  // node_modules/@sentry/core/build/esm/sdk.js
  function initAndBind(clientClass, options) {
    if (options.debug === true) {
      if (DEBUG_BUILD) {
        debug.enable();
      } else {
        consoleSandbox(() => {
          console.warn("[Sentry] Cannot initialize SDK with `debug` option using a non-debug bundle.");
        });
      }
    }
    warnIfClientIsActive();
    const scope = getCurrentScope();
    scope.update(options.initialScope);
    const client = new clientClass(options);
    setCurrentClient(client);
    client.init();
    return client;
  }
  function getActiveClient() {
    const client = getClient();
    return client && !isClientClosed(client) ? client : void 0;
  }
  function warnIfClientIsActive() {
    if (getActiveClient()) {
      consoleSandbox(() => {
        console.warn(
          "[Sentry] `Sentry.init()` was called more than once. The new client replaces the active client, but the active client is not closed, so state from both can mix. Call `Sentry.init()` only once, or call `await Sentry.close()` before you call it again."
        );
      });
    }
  }
  function setCurrentClient(client) {
    getCurrentScope().setClient(client);
  }

  // node_modules/@sentry/core/build/esm/utils/data-collection/filtering-snippets.js
  var FILTERED_VALUE = "[Filtered]";
  var SENSITIVE_KEY_SNIPPETS = [
    "auth",
    "token",
    "secret",
    "session",
    // for the user_session cookie
    "password",
    "passwd",
    "pwd",
    "key",
    "jwt",
    "bearer",
    "sso",
    "saml",
    "csrf",
    "xsrf",
    "credentials",
    "sid",
    "identity",
    // Always treat cookie headers as sensitive in case individual key-value cookie pairs cannot properly be extracted
    "set-cookie",
    "cookie"
  ];

  // node_modules/@sentry/core/build/esm/utils/data-collection/filterKeyValueData.js
  function isSensitiveKey(lower, denySnippets) {
    return denySnippets.some((snippet) => lower.includes(snippet));
  }
  function shouldFilterDataKey(key, behavior, additionalDenyTerms) {
    if (behavior === false) {
      return true;
    }
    const lowerKey = key.toLowerCase();
    const denySnippets = additionalDenyTerms != null ? [...SENSITIVE_KEY_SNIPPETS, ...additionalDenyTerms] : SENSITIVE_KEY_SNIPPETS;
    if (isSensitiveKey(lowerKey, denySnippets)) {
      return true;
    }
    if (behavior === true) {
      return false;
    }
    const terms = "deny" in behavior ? behavior.deny : behavior.allow;
    const matchesConfiguredTerm = terms.some((term) => lowerKey.includes(term.toLowerCase()));
    return "deny" in behavior ? matchesConfiguredTerm : !matchesConfiguredTerm;
  }
  function filterKeyValueData(data, behavior, additionalDenyTerms) {
    if (behavior === false) {
      return {};
    }
    const result = {};
    for (const key of Object.keys(data)) {
      result[key] = shouldFilterDataKey(key, behavior, additionalDenyTerms) ? FILTERED_VALUE : data[key];
    }
    return result;
  }

  // node_modules/@sentry/core/build/esm/utils/data-collection/filterQueryParams.js
  function filterQueryParams(queryString, behavior) {
    if (!queryString || behavior === false) {
      return void 0;
    }
    return queryString.split("&").map((pair) => {
      const separatorIndex = pair.indexOf("=");
      const encodedKey = separatorIndex === -1 ? pair : pair.slice(0, separatorIndex);
      const key = new URLSearchParams(`${encodedKey}=`).keys().next().value;
      return key !== void 0 && shouldFilterDataKey(key, behavior) ? `${encodedKey}=${FILTERED_VALUE}` : pair;
    }).join("&");
  }

  // node_modules/@sentry/core/build/esm/utils/data-collection/filterUrlQuery.js
  function filterUrlQuery(url, behavior) {
    const fragmentStart = url.indexOf("#");
    const queryEnd = fragmentStart === -1 ? url.length : fragmentStart;
    const queryStart = url.indexOf("?");
    if (queryStart === -1 || queryStart > queryEnd) {
      return url;
    }
    const prefix = url.slice(0, queryStart);
    const query = url.slice(queryStart + 1, queryEnd);
    const suffix = url.slice(queryEnd);
    const filtered = filterQueryParams(query, behavior);
    return filtered ? `${prefix}?${filtered}${suffix}` : `${prefix}${suffix}`;
  }

  // node_modules/@sentry/core/build/esm/utils/data-collection/filterCollectedUrl.js
  function urlQueryParamsBehavior(client) {
    return (client ?? getClient())?.getDataCollectionOptions().urlQueryParams ?? true;
  }
  function filterCollectedUrl(url, client) {
    return url === void 0 ? void 0 : filterUrlQuery(url, urlQueryParamsBehavior(client));
  }

  // node_modules/@sentry/core/build/esm/utils/url.js
  function parseUrl(url) {
    if (!url) {
      return {};
    }
    const match = url.match(/^(([^:/?#]+):)?(\/\/([^/?#]*))?([^?#]*)(\?([^#]*))?(#(.*))?$/);
    if (!match) {
      return {};
    }
    const query = match[6] || "";
    const fragment = match[8] || "";
    return {
      host: match[4],
      path: match[5],
      protocol: match[2],
      search: query,
      hash: fragment,
      relative: match[5] + query + fragment
      // everything minus origin
    };
  }
  function stripDataUrlContent(url, includeDataPrefix = true) {
    if (url.startsWith("data:")) {
      const match = url.match(/^data:([^;,]+)/);
      const mimeType = match ? match[1] : "text/plain";
      const isBase64 = url.includes(";base64,");
      const dataStart = url.indexOf(",");
      let dataPrefix = "";
      if (includeDataPrefix && dataStart !== -1) {
        const data = url.slice(dataStart + 1);
        dataPrefix = data.length > 10 ? `${data.slice(0, 10)}... [truncated]` : data;
      }
      return `data:${mimeType}${isBase64 ? ",base64" : ""}${dataPrefix ? `,${dataPrefix}` : ""}`;
    }
    return url;
  }

  // node_modules/@sentry/core/build/esm/utils/ipAddress.js
  function addAutoIpAddressToSession(session) {
    if ("aggregates" in session) {
      if (session.attrs?.["ip_address"] === void 0) {
        session.attrs = {
          ...session.attrs,
          ip_address: "{{auto}}"
        };
      }
    } else {
      if (session.ipAddress === void 0) {
        session.ipAddress = "{{auto}}";
      }
    }
  }

  // node_modules/@sentry/core/build/esm/utils/sdkMetadata.js
  function applySdkMetadata(options, name, names = [name], source = "npm") {
    const sdk = (options._metadata = options._metadata || {}).sdk = options._metadata.sdk || {};
    if (!sdk.name) {
      sdk.name = `sentry.javascript.${name}`;
      sdk.packages = names.map((name2) => ({
        name: `${source}:@sentry/${name2}`,
        version: SDK_VERSION
      }));
      sdk.version = SDK_VERSION;
    }
  }

  // node_modules/@sentry/core/build/esm/breadcrumbs.js
  var DEFAULT_BREADCRUMBS = 100;
  function addBreadcrumb(breadcrumb, hint) {
    const client = getClient();
    const isolationScope = getIsolationScope();
    if (!client) return;
    const { beforeBreadcrumb = null, maxBreadcrumbs = DEFAULT_BREADCRUMBS } = client.getOptions();
    if (maxBreadcrumbs <= 0) return;
    const timestamp = dateTimestampInSeconds();
    const mergedBreadcrumb = { timestamp, ...breadcrumb };
    const finalBreadcrumb = beforeBreadcrumb ? safeCallback(
      DEBUG_BUILD ? "The `beforeBreadcrumb` callback threw an error, dropping the breadcrumb:" : "",
      () => consoleSandbox(() => beforeBreadcrumb(mergedBreadcrumb, hint)),
      () => null
    ) : mergedBreadcrumb;
    if (finalBreadcrumb === null) return;
    if (client.emit) {
      client.emit("beforeAddBreadcrumb", finalBreadcrumb, hint);
    }
    isolationScope.addBreadcrumb(finalBreadcrumb, maxBreadcrumbs);
  }

  // node_modules/@sentry/core/build/esm/integrations/functiontostring.js
  var INTEGRATION_NAME = "FunctionToString";
  var SETUP_CLIENTS = /* @__PURE__ */ new WeakMap();
  var _functionToStringIntegration = (() => {
    return {
      name: INTEGRATION_NAME,
      setupOnce() {
        const originalFunctionToString = Function.prototype.toString;
        try {
          Function.prototype.toString = function(...args) {
            const originalFunction = getOriginalFunction(this);
            let unwrappedFunction;
            try {
              if (SETUP_CLIENTS.has(getClient()) && originalFunction !== void 0) {
                unwrappedFunction = originalFunction;
              }
            } catch {
            }
            return originalFunctionToString.apply(unwrappedFunction ?? this, args);
          };
        } catch {
        }
      },
      setup(client) {
        SETUP_CLIENTS.set(client, true);
      }
    };
  });
  var functionToStringIntegration = defineIntegration(_functionToStringIntegration);

  // node_modules/@sentry/core/build/esm/integrations/eventFilters.js
  var DEFAULT_IGNORE_ERRORS = [
    /^Script error\.?$/,
    /^Javascript error: Script error\.? on line 0$/,
    /^ResizeObserver loop completed with undelivered notifications.$/,
    // The browser logs this when a ResizeObserver handler takes a bit longer. Usually this is not an actual issue though. It indicates slowness.
    /^Cannot redefine property: googletag$/,
    // This is thrown when google tag manager is used in combination with an ad blocker
    /^Can't find variable: gmo$/,
    // Error from Google Search App https://issuetracker.google.com/issues/396043331
    /^undefined is not an object \(evaluating 'a\.[A-Z]'\)$/,
    // Random error that happens but not actionable or noticeable to end-users.
    /can't redefine non-configurable property "solana"/,
    // Probably a browser extension or custom browser (Brave) throwing this error
    /vv\(\)\.getRestrictions is not a function/,
    // Error thrown by GTM, seemingly not affecting end-users
    /Can't find variable: _AutofillCallbackHandler/,
    // Unactionable error in instagram webview https://developers.facebook.com/community/threads/320013549791141/
    /Object Not Found Matching Id:\d+, MethodName:simulateEvent/,
    // unactionable error from CEFSharp, a .NET library that embeds chromium in .NET apps
    /Java exception was raised during method invocation$/,
    // error from Facebook Mobile browser (https://github.com/getsentry/sentry-javascript/issues/15065, https://github.com/getsentry/sentry-javascript/issues/23733)
    /Java object is gone$/
    // error from Facebook Mobile browser (https://github.com/getsentry/sentry-javascript/issues/15065, https://github.com/getsentry/sentry-javascript/issues/23733)
  ];
  var INTEGRATION_NAME2 = "EventFilters";
  var eventFiltersIntegration = defineIntegration((options = {}) => {
    let mergedOptions;
    return {
      name: INTEGRATION_NAME2,
      setup(client) {
        const clientOptions = client.getOptions();
        mergedOptions = _mergeOptions(options, clientOptions);
      },
      processEvent(event, _hint, client) {
        if (!mergedOptions) {
          const clientOptions = client.getOptions();
          mergedOptions = _mergeOptions(options, clientOptions);
        }
        return _shouldDropEvent(event, mergedOptions) ? null : event;
      }
    };
  });
  function _mergeOptions(internalOptions = {}, clientOptions = {}) {
    return {
      allowUrls: [...internalOptions.allowUrls || [], ...clientOptions.allowUrls || []],
      denyUrls: [...internalOptions.denyUrls || [], ...clientOptions.denyUrls || []],
      ignoreErrors: [
        ...internalOptions.ignoreErrors || [],
        ...clientOptions.ignoreErrors || [],
        ...internalOptions.disableErrorDefaults ? [] : DEFAULT_IGNORE_ERRORS
      ],
      ignoreTransactions: [...internalOptions.ignoreTransactions || [], ...clientOptions.ignoreTransactions || []]
    };
  }
  function _shouldDropEvent(event, options) {
    if (!event.type) {
      if (_isIgnoredError(event, options.ignoreErrors)) {
        DEBUG_BUILD && debug.warn(
          `Event dropped due to being matched by \`ignoreErrors\` option.
Event: ${getEventDescription(event)}`
        );
        return true;
      }
      if (_isUselessError(event)) {
        DEBUG_BUILD && debug.warn(
          `Event dropped due to not having an error message, error type or stacktrace.
Event: ${getEventDescription(
            event
          )}`
        );
        return true;
      }
      if (_isDeniedUrl(event, options.denyUrls)) {
        DEBUG_BUILD && debug.warn(
          `Event dropped due to being matched by \`denyUrls\` option.
Event: ${getEventDescription(
            event
          )}.
Url: ${_getEventFilterUrl(event)}`
        );
        return true;
      }
      if (!_isAllowedUrl(event, options.allowUrls)) {
        DEBUG_BUILD && debug.warn(
          `Event dropped due to not being matched by \`allowUrls\` option.
Event: ${getEventDescription(
            event
          )}.
Url: ${_getEventFilterUrl(event)}`
        );
        return true;
      }
    } else if (event.type === "transaction") {
      if (_isIgnoredTransaction(event, options.ignoreTransactions)) {
        DEBUG_BUILD && debug.warn(
          `Event dropped due to being matched by \`ignoreTransactions\` option.
Event: ${getEventDescription(event)}`
        );
        return true;
      }
    }
    return false;
  }
  function _isIgnoredError(event, ignoreErrors) {
    if (!ignoreErrors?.length) {
      return false;
    }
    return getPossibleEventMessages(event).some((message) => stringMatchesSomePattern(message, ignoreErrors));
  }
  function _isIgnoredTransaction(event, ignoreTransactions) {
    if (!ignoreTransactions?.length) {
      return false;
    }
    const name = event.transaction;
    return name ? stringMatchesSomePattern(name, ignoreTransactions) : false;
  }
  function _isDeniedUrl(event, denyUrls) {
    if (!denyUrls?.length) {
      return false;
    }
    const url = _getEventFilterUrl(event);
    return !url ? false : stringMatchesSomePattern(url, denyUrls);
  }
  function _isAllowedUrl(event, allowUrls) {
    if (!allowUrls?.length) {
      return true;
    }
    const url = _getEventFilterUrl(event);
    return !url ? true : stringMatchesSomePattern(url, allowUrls);
  }
  function _getLastValidUrl(frames = []) {
    for (let i = frames.length - 1; i >= 0; i--) {
      const frame = frames[i];
      if (frame && frame.filename !== "<anonymous>" && frame.filename !== "[native code]") {
        return frame.filename || null;
      }
    }
    return null;
  }
  function _getEventFilterUrl(event) {
    try {
      const rootException = [...event.exception?.values ?? []].reverse().find((value) => value.mechanism?.parent_id === void 0 && value.stacktrace?.frames?.length);
      const frames = rootException?.stacktrace?.frames;
      return frames ? _getLastValidUrl(frames) : null;
    } catch {
      DEBUG_BUILD && debug.error(`Cannot extract url for event ${getEventDescription(event)}`);
      return null;
    }
  }
  function _isUselessError(event) {
    if (!event.exception?.values?.length) {
      return false;
    }
    return (
      // No top-level message
      !event.message && // There are no exception values that have a stacktrace, a non-generic-Error type or value
      !event.exception.values.some((value) => value.stacktrace || value.type && value.type !== "Error" || value.value)
    );
  }

  // node_modules/@sentry/core/build/esm/utils/aggregate-errors.js
  function applyAggregateErrorsToEvent(exceptionFromErrorImplementation, parser, key, limit, event, hint) {
    if (!event.exception?.values || !hint || !isError(hint.originalException)) {
      return;
    }
    const originalException = event.exception.values.length > 0 ? event.exception.values[event.exception.values.length - 1] : void 0;
    if (originalException) {
      event.exception.values = aggregateExceptionsFromError(
        exceptionFromErrorImplementation,
        parser,
        limit,
        hint.originalException,
        key,
        event.exception.values,
        originalException,
        0
      );
    }
  }
  function aggregateExceptionsFromError(exceptionFromErrorImplementation, parser, limit, error2, key, prevExceptions, exception, exceptionId) {
    if (prevExceptions.length >= limit + 1) {
      return prevExceptions;
    }
    let newExceptions = [...prevExceptions];
    if (isError(error2[key])) {
      applyExceptionGroupFieldsForParentException(exception, exceptionId, error2);
      const newException = exceptionFromErrorImplementation(parser, error2[key]);
      const newExceptionId = newExceptions.length;
      applyExceptionGroupFieldsForChildException(newException, key, newExceptionId, exceptionId);
      newExceptions = aggregateExceptionsFromError(
        exceptionFromErrorImplementation,
        parser,
        limit,
        error2[key],
        key,
        [newException, ...newExceptions],
        newException,
        newExceptionId
      );
    }
    if (isExceptionGroup(error2)) {
      error2.errors.forEach((childError, i) => {
        if (isError(childError)) {
          applyExceptionGroupFieldsForParentException(exception, exceptionId, error2);
          const newException = exceptionFromErrorImplementation(parser, childError);
          const newExceptionId = newExceptions.length;
          applyExceptionGroupFieldsForChildException(newException, `errors[${i}]`, newExceptionId, exceptionId);
          newExceptions = aggregateExceptionsFromError(
            exceptionFromErrorImplementation,
            parser,
            limit,
            childError,
            key,
            [newException, ...newExceptions],
            newException,
            newExceptionId
          );
        }
      });
    }
    if (isSuppressedError(error2)) {
      ["error", "suppressed"].forEach((property) => {
        const childError = error2[property];
        if (isError(childError)) {
          applyExceptionGroupFieldsForParentException(exception, exceptionId, error2);
          const newException = exceptionFromErrorImplementation(parser, childError);
          const newExceptionId = newExceptions.length;
          applyExceptionGroupFieldsForChildException(newException, property, newExceptionId, exceptionId);
          newExceptions = aggregateExceptionsFromError(
            exceptionFromErrorImplementation,
            parser,
            limit,
            childError,
            key,
            [newException, ...newExceptions],
            newException,
            newExceptionId
          );
        }
      });
    }
    return newExceptions;
  }
  function isExceptionGroup(error2) {
    return Array.isArray(error2.errors);
  }
  function isSuppressedError(error2) {
    return "error" in error2 && "suppressed" in error2;
  }
  function applyExceptionGroupFieldsForParentException(exception, exceptionId, error2) {
    exception.mechanism = {
      handled: true,
      type: "auto.core.linked_errors",
      ...isExceptionGroup(error2) && { is_exception_group: true },
      ...exception.mechanism,
      exception_id: exceptionId
    };
  }
  function applyExceptionGroupFieldsForChildException(exception, source, exceptionId, parentId) {
    exception.mechanism = {
      handled: true,
      ...exception.mechanism,
      type: "chained",
      source,
      exception_id: exceptionId,
      parent_id: parentId
    };
  }

  // node_modules/@sentry/core/build/esm/utils/eventbuilder.js
  function hasSentryFetchUrlHost(error2) {
    return isError(error2) && "__sentry_fetch_url_host__" in error2 && typeof error2.__sentry_fetch_url_host__ === "string";
  }
  function _enhanceErrorWithSentryInfo(error2) {
    if (hasSentryFetchUrlHost(error2)) {
      return `${error2.message} (${error2.__sentry_fetch_url_host__})`;
    }
    return error2.message;
  }

  // node_modules/@sentry/core/build/esm/instrument/console.js
  var _filter = /* @__PURE__ */ new Set([]);
  function addConsoleInstrumentationHandler(handler) {
    const type = "console";
    const removeHandler = addHandler(type, handler);
    maybeInstrument(type, instrumentConsole);
    return removeHandler;
  }
  function addConsoleInstrumentationFilter(filter) {
    for (const f of filter) {
      _filter.add(f);
    }
    return () => {
      for (const f of filter) {
        _filter.delete(f);
      }
    };
  }
  var instrumentedLevels = /* @__PURE__ */ new Set();
  function instrumentConsole() {
    if (!("console" in GLOBAL_OBJ)) {
      return;
    }
    CONSOLE_LEVELS.forEach(function(level) {
      if (instrumentedLevels.has(level) || !(level in GLOBAL_OBJ.console)) {
        return;
      }
      instrumentedLevels.add(level);
      fill(GLOBAL_OBJ.console, level, function(originalConsoleMethod) {
        originalConsoleMethods[level] = originalConsoleMethod;
        return function(...args) {
          const firstArg = args[0];
          const log2 = originalConsoleMethods[level];
          const isFiltered = _filter.size && typeof firstArg === "string" && stringMatchesSomePattern(firstArg, _filter);
          if (!isFiltered) {
            triggerHandlers("console", { args, level });
          }
          if (!isFiltered || DEBUG_BUILD && debug.isEnabled()) {
            log2?.apply(GLOBAL_OBJ.console, args);
          }
        };
      });
    });
  }

  // node_modules/@sentry/core/build/esm/utils/severity.js
  function severityLevelFromString(level) {
    return level === "warn" ? "warning" : ["fatal", "error", "warning", "log", "info", "debug"].includes(level) ? level : "log";
  }

  // node_modules/@sentry/core/build/esm/integrations/dedupe.js
  var INTEGRATION_NAME3 = "Dedupe";
  var _dedupeIntegration = (() => {
    let previousEvent;
    return {
      name: INTEGRATION_NAME3,
      processEvent(currentEvent) {
        if (currentEvent.type) {
          return currentEvent;
        }
        try {
          if (_shouldDropEvent2(currentEvent, previousEvent)) {
            DEBUG_BUILD && debug.warn("Event dropped due to being a duplicate of previously captured event.");
            return null;
          }
        } catch {
        }
        return previousEvent = currentEvent;
      }
    };
  });
  var dedupeIntegration = defineIntegration(_dedupeIntegration);
  function _shouldDropEvent2(currentEvent, previousEvent) {
    if (!previousEvent) {
      return false;
    }
    if (_isSameMessageEvent(currentEvent, previousEvent)) {
      return true;
    }
    if (_isSameExceptionEvent(currentEvent, previousEvent)) {
      return true;
    }
    return false;
  }
  function _isSameMessageEvent(currentEvent, previousEvent) {
    const currentMessage = currentEvent.message;
    const previousMessage = previousEvent.message;
    if (!currentMessage && !previousMessage) {
      return false;
    }
    if (currentMessage && !previousMessage || !currentMessage && previousMessage) {
      return false;
    }
    if (currentMessage !== previousMessage) {
      return false;
    }
    if (!_isSameFingerprint(currentEvent, previousEvent)) {
      return false;
    }
    if (!_isSameStacktrace(currentEvent, previousEvent)) {
      return false;
    }
    return true;
  }
  function _isSameExceptionEvent(currentEvent, previousEvent) {
    const previousException = _getExceptionFromEvent(previousEvent);
    const currentException = _getExceptionFromEvent(currentEvent);
    if (!previousException || !currentException) {
      return false;
    }
    if (previousException.type !== currentException.type || previousException.value !== currentException.value) {
      return false;
    }
    if (!_isSameFingerprint(currentEvent, previousEvent)) {
      return false;
    }
    if (!_isSameStacktrace(currentEvent, previousEvent)) {
      return false;
    }
    return true;
  }
  function _isSameStacktrace(currentEvent, previousEvent) {
    const currentFrames = getFramesFromEvent(currentEvent);
    const previousFrames = getFramesFromEvent(previousEvent);
    if (!currentFrames || !previousFrames) {
      return !currentFrames && !previousFrames;
    }
    if (previousFrames.length !== currentFrames.length) {
      return false;
    }
    for (let i = 0; i < previousFrames.length; i++) {
      const frameA = previousFrames[i];
      const frameB = currentFrames[i];
      if (frameA.filename !== frameB.filename || frameA.lineno !== frameB.lineno || frameA.colno !== frameB.colno || frameA.function !== frameB.function) {
        return false;
      }
    }
    return true;
  }
  function _isSameFingerprint(currentEvent, previousEvent) {
    const currentFingerprint = currentEvent.fingerprint;
    const previousFingerprint = previousEvent.fingerprint;
    if (!currentFingerprint || !previousFingerprint) {
      return !currentFingerprint && !previousFingerprint;
    }
    try {
      return !!(currentFingerprint.join("") === previousFingerprint.join(""));
    } catch {
      return false;
    }
  }
  function _getExceptionFromEvent(event) {
    return event.exception?.values?.[0];
  }

  // node_modules/@sentry/core/build/esm/integrations/console.js
  var INTEGRATION_NAME4 = "Console";
  var consoleIntegration = defineIntegration((options = {}) => {
    const levels = new Set(options.levels || CONSOLE_LEVELS);
    return {
      name: INTEGRATION_NAME4,
      setup(client) {
        const unsubscribe = addConsoleInstrumentationHandler(({ args, level }) => {
          if (getClient() !== client || !levels.has(level)) {
            return;
          }
          addConsoleBreadcrumb(level, args);
        });
        client.registerCleanup(unsubscribe);
        if (options.filter) {
          const unsubscribe2 = addConsoleInstrumentationFilter(options.filter);
          client.registerCleanup(unsubscribe2);
        }
      }
    };
  });
  function addConsoleBreadcrumb(level, args) {
    const breadcrumb = {
      category: "console",
      data: {
        arguments: args,
        logger: "console"
      },
      level: severityLevelFromString(level),
      message: formatConsoleArgs(args)
    };
    if (level === "assert") {
      if (args[0] === false) {
        const assertionArgs = args.slice(1);
        breadcrumb.message = assertionArgs.length > 0 ? `Assertion failed: ${formatConsoleArgs(assertionArgs)}` : "Assertion failed";
        breadcrumb.data.arguments = assertionArgs;
      } else {
        return;
      }
    }
    addBreadcrumb(breadcrumb, {
      input: args,
      level
    });
  }
  function formatConsoleArgs(values) {
    return "util" in GLOBAL_OBJ && typeof GLOBAL_OBJ.util.format === "function" ? GLOBAL_OBJ.util.format(...values) : safeJoin(values, " ");
  }

  // node_modules/@sentry/core/build/esm/integrations/conversationId.js
  var INTEGRATION_NAME5 = "ConversationId";
  var _conversationIdIntegration = (() => {
    return {
      name: INTEGRATION_NAME5,
      setup(client) {
        client.on("spanStart", (span) => {
          const scopeData = getCurrentScope().getScopeData();
          const isolationScopeData = getIsolationScope().getScopeData();
          const conversationId = scopeData.conversationId || isolationScopeData.conversationId;
          if (conversationId) {
            const { op, data: attributes, description: name } = spanToStaticSpanJSON(span);
            if (!op?.startsWith("gen_ai.") && !attributes["ai.operationId"] && !name?.startsWith("ai.")) {
              return;
            }
            span.setAttribute(wr, conversationId);
          }
        });
      }
    };
  });
  var conversationIdIntegration = defineIntegration(_conversationIdIntegration);

  // node_modules/@sentry/core/build/esm/utils/supports.js
  var WINDOW = GLOBAL_OBJ;
  function _isFetchSupported() {
    if (!("fetch" in WINDOW)) {
      return false;
    }
    try {
      new Headers();
      new Request("data:,");
      new Response();
      return true;
    } catch {
      return false;
    }
  }
  function isNativeFunction(func) {
    return func && /^function\s+\w+\(\)\s+\{\s+\[native code\]\s+\}$/.test(func.toString());
  }
  function supportsNativeFetch() {
    if (typeof EdgeRuntime === "string") {
      return true;
    }
    if (!_isFetchSupported()) {
      return false;
    }
    if (isNativeFunction(WINDOW.fetch)) {
      return true;
    }
    let result = false;
    const doc = WINDOW.document;
    if (doc && typeof doc.createElement === "function") {
      try {
        const sandbox = doc.createElement("iframe");
        sandbox.hidden = true;
        doc.head.appendChild(sandbox);
        if (sandbox.contentWindow?.fetch) {
          result = isNativeFunction(sandbox.contentWindow.fetch);
        }
        doc.head.removeChild(sandbox);
      } catch (err) {
        DEBUG_BUILD && debug.warn("Could not create sandbox iframe for pure fetch check, bailing to window.fetch: ", err);
      }
    }
    return result;
  }

  // node_modules/@sentry/core/build/esm/instrument/fetch.js
  function addFetchInstrumentationHandler(handler) {
    const type = "fetch";
    const removeHandler = addHandler(type, handler);
    maybeInstrument(type, () => instrumentFetch());
    return removeHandler;
  }
  function instrumentFetch(onFetchResolved) {
    if (isBrowser() && !supportsNativeFetch()) {
      return;
    }
    fill(GLOBAL_OBJ, "fetch", function(originalFetch) {
      return new Proxy(originalFetch, {
        apply(target, _thisArg, args) {
          const virtualError = new Error();
          const { method, url } = parseFetchArgs(args);
          const handlerData = {
            args,
            fetchData: {
              method,
              url
            },
            startTimestamp: timestampInSeconds() * 1e3,
            // // Adding the error to be able to fingerprint the failed fetch event in HttpClient instrumentation
            virtualError,
            headers: getHeadersFromFetchArgs(args)
          };
          if (!onFetchResolved) {
            triggerHandlers("fetch", {
              ...handlerData
            });
          }
          return Reflect.apply(target, GLOBAL_OBJ, args).then(
            async (response) => {
              if (onFetchResolved) {
                onFetchResolved(response);
              } else {
                triggerHandlers("fetch", {
                  ...handlerData,
                  endTimestamp: timestampInSeconds() * 1e3,
                  response
                });
              }
              return response;
            },
            (error2) => {
              triggerHandlers("fetch", {
                ...handlerData,
                endTimestamp: timestampInSeconds() * 1e3,
                error: error2
              });
              if (isError(error2) && error2.stack === void 0) {
                error2.stack = virtualError.stack;
                addNonEnumerableProperty(error2, "framesToPop", 1);
              }
              const client = getClient();
              const enhanceOption = client?.getOptions().enhanceFetchErrorMessages ?? "always";
              const shouldEnhance = enhanceOption !== false;
              if (shouldEnhance && isError(error2) && error2.name === "TypeError" && (error2.message === "Failed to fetch" || error2.message === "Load failed" || error2.message === "NetworkError when attempting to fetch resource.")) {
                try {
                  const url2 = new URL(handlerData.fetchData.url);
                  const hostname = url2.host;
                  if (enhanceOption === "always") {
                    error2.message = `${error2.message} (${hostname})`;
                  } else {
                    addNonEnumerableProperty(error2, "__sentry_fetch_url_host__", hostname);
                  }
                } catch {
                }
              }
              throw error2;
            }
          );
        }
      });
    });
  }
  function hasProp(obj, prop) {
    return isObjectLike(obj) && !!obj[prop];
  }
  function getUrlFromResource(resource) {
    if (typeof resource === "string") {
      return resource;
    }
    if (!resource) {
      return "";
    }
    if (hasProp(resource, "url")) {
      return resource.url;
    }
    if (resource.toString) {
      return resource.toString();
    }
    return "";
  }
  function parseFetchArgs(fetchArgs) {
    if (fetchArgs.length === 0) {
      return { method: "GET", url: "" };
    }
    if (fetchArgs.length === 2) {
      const [resource, options] = fetchArgs;
      return {
        url: getUrlFromResource(resource),
        method: hasProp(options, "method") ? String(options.method).toUpperCase() : (
          // Request object as first argument
          isRequest(resource) && hasProp(resource, "method") ? String(resource.method).toUpperCase() : "GET"
        )
      };
    }
    const arg = fetchArgs[0];
    return {
      url: getUrlFromResource(arg),
      method: hasProp(arg, "method") ? String(arg.method).toUpperCase() : "GET"
    };
  }
  function getHeadersFromFetchArgs(fetchArgs) {
    const [requestArgument, optionsArgument] = fetchArgs;
    try {
      if (typeof optionsArgument === "object" && optionsArgument !== null && "headers" in optionsArgument && optionsArgument.headers) {
        return new Headers(optionsArgument.headers);
      }
      if (isRequest(requestArgument)) {
        return new Headers(requestArgument.headers);
      }
    } catch {
    }
    return;
  }

  // node_modules/@sentry/core/build/esm/utils/breadcrumb-log-level.js
  function getBreadcrumbLogLevelFromHttpStatusCode(statusCode) {
    if (statusCode === void 0) {
      return void 0;
    } else if (statusCode >= 400 && statusCode < 500) {
      return "warning";
    } else if (statusCode >= 500) {
      return "error";
    } else {
      return void 0;
    }
  }

  // node_modules/@sentry/browser-utils/build/esm/debug-build.js
  var DEBUG_BUILD2 = typeof __SENTRY_DEBUG__ === "undefined" || __SENTRY_DEBUG__;

  // node_modules/@sentry/browser-utils/build/esm/types.js
  var WINDOW2 = GLOBAL_OBJ;

  // node_modules/@sentry/browser-utils/build/esm/htmlTreeAsString.js
  var DEFAULT_MAX_STRING_LENGTH = 80;
  var accessors = {};
  try {
    if (typeof Node !== "undefined") {
      accessors.parentNode = Object.getOwnPropertyDescriptor(Node.prototype, "parentNode").get;
    }
    if (typeof Element !== "undefined") {
      accessors.tagName = Object.getOwnPropertyDescriptor(Element.prototype, "tagName").get;
      accessors.id = Object.getOwnPropertyDescriptor(Element.prototype, "id").get;
      accessors.className = Object.getOwnPropertyDescriptor(Element.prototype, "className").get;
      accessors.getAttribute = Element.prototype.getAttribute;
    }
    if (typeof HTMLElement !== "undefined") {
      accessors.dataset = Object.getOwnPropertyDescriptor(HTMLElement.prototype, "dataset").get;
    }
  } catch {
  }
  function _safeRead(el, prop, arg) {
    const fn = accessors[prop];
    if (fn) {
      try {
        return fn.call(el, arg);
      } catch {
      }
    }
    const val = el[prop];
    return typeof val === "function" ? val.call(el, arg) : val;
  }
  function htmlTreeAsString(elem, options = {}) {
    if (!elem) {
      return "<unknown>";
    }
    try {
      let currentElem = elem;
      const MAX_TRAVERSE_HEIGHT = 5;
      const out = [];
      let height = 0;
      let len = 0;
      const separator = " > ";
      const sepLength = separator.length;
      let nextStr;
      const keyAttrs = Array.isArray(options) ? options : options.keyAttrs;
      const maxStringLength = !Array.isArray(options) && options.maxStringLength || DEFAULT_MAX_STRING_LENGTH;
      while (currentElem && height++ < MAX_TRAVERSE_HEIGHT) {
        nextStr = _htmlElementAsString(currentElem, keyAttrs);
        if (nextStr === "html" || height > 1 && len + out.length * sepLength + nextStr.length >= maxStringLength) {
          break;
        }
        out.push(nextStr);
        len += nextStr.length;
        currentElem = _safeRead(currentElem, "parentNode");
      }
      return out.reverse().join(separator);
    } catch {
      return "<unknown>";
    }
  }
  function _htmlElementAsString(el, keyAttrs) {
    const out = [];
    const tagName = _safeRead(el, "tagName");
    if (!tagName) {
      return "";
    }
    if (typeof HTMLElement !== "undefined") {
      if (el instanceof HTMLElement) {
        const dataset = _safeRead(el, "dataset");
        if (dataset) {
          if (dataset["sentryComponent"]) {
            return dataset["sentryComponent"];
          }
          if (dataset["sentryElement"]) {
            return dataset["sentryElement"];
          }
        }
      }
    }
    out.push(tagName.toLowerCase());
    const keyAttrPairs = keyAttrs?.length ? keyAttrs.filter((keyAttr) => _safeRead(el, "getAttribute", keyAttr)).map((keyAttr) => [keyAttr, _safeRead(el, "getAttribute", keyAttr)]) : null;
    if (keyAttrPairs?.length) {
      keyAttrPairs.forEach((keyAttrPair) => {
        out.push(`[${keyAttrPair[0]}="${keyAttrPair[1]}"]`);
      });
    } else {
      const id = _safeRead(el, "id");
      if (id) {
        out.push(`#${id}`);
      }
      const className = _safeRead(el, "className");
      if (className && isString(className)) {
        const classes = className.split(/\s+/);
        for (const c of classes) {
          out.push(`.${c}`);
        }
      }
    }
    for (const k of ["aria-label", "type", "name", "title", "alt"]) {
      const attr = _safeRead(el, "getAttribute", k);
      if (attr) {
        out.push(`[${k}="${attr}"]`);
      }
    }
    return out.join("");
  }

  // node_modules/@sentry/browser-utils/build/esm/web-vitals/utils.js
  function addPageListener(type, listener, options) {
    if (WINDOW2.document) {
      WINDOW2.addEventListener(type, listener, options);
    }
  }
  function removePageListener(type, listener, options) {
    if (WINDOW2.document) {
      WINDOW2.removeEventListener(type, listener, options);
    }
  }
  var whenIdleOrHidden = (cb) => {
    const rIC = WINDOW2.requestIdleCallback || WINDOW2.setTimeout;
    if (WINDOW2.document?.visibilityState === "hidden") {
      cb();
    } else {
      let called = false;
      const runOnce = () => {
        if (!called) {
          cb();
          called = true;
        }
      };
      addPageListener("visibilitychange", runOnce, { once: true, capture: true });
      rIC(() => {
        runOnce();
        removePageListener("visibilitychange", runOnce, { capture: true });
      });
    }
  };

  // node_modules/@sentry/browser-utils/build/esm/component-name.js
  function getComponentName(elem, maxTraverseHeight = 5) {
    if (!GLOBAL_OBJ.HTMLElement) {
      return null;
    }
    let currentElem = elem;
    for (let i = 0; i < maxTraverseHeight; i++) {
      if (!currentElem) {
        return null;
      }
      if (currentElem instanceof HTMLElement) {
        if (currentElem.dataset["sentryComponent"]) {
          return currentElem.dataset["sentryComponent"];
        }
        if (currentElem.dataset["sentryElement"]) {
          return currentElem.dataset["sentryElement"];
        }
      }
      currentElem = currentElem.parentNode;
    }
    return null;
  }

  // node_modules/@sentry/browser-utils/build/esm/getLocationHref.js
  function getLocationHref() {
    try {
      return WINDOW2.document?.location.href ?? "";
    } catch {
      return "";
    }
  }

  // node_modules/@sentry/browser-utils/build/esm/routing.js
  var CLIENT_ROUTE_PROVIDERS = /* @__PURE__ */ new WeakMap();
  function setRouteProvider(provider, client = getClient()) {
    if (!client) {
      DEBUG_BUILD2 && debug.warn("Cannot set a route provider without a client.");
      return;
    }
    if (DEBUG_BUILD2 && getRouteProvider(client)) {
      debug.warn(
        "A route provider is already registered for this client and will be replaced. Routes only the previous provider knows about will no longer resolve."
      );
    }
    CLIENT_ROUTE_PROVIDERS.set(client, provider);
  }
  function getRouteProvider(client = getClient()) {
    return client && CLIENT_ROUTE_PROVIDERS.get(client);
  }

  // node_modules/@sentry/browser-utils/build/esm/instrumentation/dom.js
  var DEBOUNCE_DURATION = 1e3;
  var debounceTimerID;
  var lastCapturedEventType;
  var lastCapturedEventTargetId;
  function getCapture(options) {
    return typeof options === "boolean" ? options : !!options?.capture;
  }
  function addClickKeypressInstrumentationHandler(handler) {
    const type = "dom";
    addHandler(type, handler);
    maybeInstrument(type, instrumentDOM);
  }
  function instrumentDOM() {
    if (!WINDOW2.document) {
      return;
    }
    const triggerDOMHandler = triggerHandlers.bind(null, "dom");
    const globalDOMEventHandler = makeDOMEventHandler(triggerDOMHandler, true);
    WINDOW2.document.addEventListener("click", globalDOMEventHandler, false);
    WINDOW2.document.addEventListener("keypress", globalDOMEventHandler, false);
    ["EventTarget", "Node"].forEach((target) => {
      const globalObject = WINDOW2;
      const proto = globalObject[target]?.prototype;
      if (!proto?.hasOwnProperty?.("addEventListener")) {
        return;
      }
      fill(proto, "addEventListener", function(originalAddEventListener) {
        return function(type, listener, options) {
          if ((type === "click" || type == "keypress") && listener) {
            try {
              const handlers2 = this.__sentry_instrumentation_handlers__ = this.__sentry_instrumentation_handlers__ || {};
              const handlerForType = handlers2[type] = handlers2[type] || {
                captureListeners: /* @__PURE__ */ new WeakSet(),
                bubbleListeners: /* @__PURE__ */ new WeakSet(),
                listenerCount: 0
              };
              const capture = getCapture(options);
              if (!handlerForType.handler) {
                const handler = makeDOMEventHandler(triggerDOMHandler);
                handlerForType.handler = handler;
                handlerForType.capture = capture;
                originalAddEventListener.call(this, type, handler, handlerForType.capture);
              }
              const listeners = handlerForType[capture ? "captureListeners" : "bubbleListeners"];
              if (!listeners.has(listener)) {
                if (typeof options === "object" && (options?.once || options?.signal)) {
                  handlerForType.sticky = true;
                } else {
                  listeners.add(listener);
                  handlerForType.listenerCount++;
                }
              }
            } catch {
            }
          }
          return originalAddEventListener.call(this, type, listener, options);
        };
      });
      fill(
        proto,
        "removeEventListener",
        function(originalRemoveEventListener) {
          return function(type, listener, options) {
            if ((type === "click" || type == "keypress") && listener) {
              try {
                const handlers2 = this.__sentry_instrumentation_handlers__ || {};
                const handlerForType = handlers2[type];
                if (handlerForType?.[getCapture(options) ? "captureListeners" : "bubbleListeners"].delete(listener)) {
                  if (!--handlerForType.listenerCount && !handlerForType.sticky) {
                    originalRemoveEventListener.call(this, type, handlerForType.handler, handlerForType.capture);
                    handlerForType.handler = void 0;
                    delete handlers2[type];
                  }
                  if (Object.keys(handlers2).length === 0) {
                    delete this.__sentry_instrumentation_handlers__;
                  }
                }
              } catch {
              }
            }
            return originalRemoveEventListener.call(this, type, listener, options);
          };
        }
      );
    });
  }
  function isSimilarToLastCapturedEvent(event) {
    if (event.type !== lastCapturedEventType) {
      return false;
    }
    try {
      if (!event.target || event.target._sentryId !== lastCapturedEventTargetId) {
        return false;
      }
    } catch {
    }
    return true;
  }
  function shouldSkipDOMEvent(eventType, target) {
    if (eventType !== "keypress") {
      return false;
    }
    if (!target?.tagName) {
      return true;
    }
    if (target.tagName === "INPUT" || target.tagName === "TEXTAREA" || target.isContentEditable) {
      return false;
    }
    return true;
  }
  function makeDOMEventHandler(handler, globalListener = false) {
    return (event) => {
      if (!event || event["_sentryCaptured"]) {
        return;
      }
      const target = getEventTarget(event);
      if (shouldSkipDOMEvent(event.type, target)) {
        return;
      }
      addNonEnumerableProperty(event, "_sentryCaptured", true);
      if (target && !target._sentryId) {
        addNonEnumerableProperty(target, "_sentryId", uuid4());
      }
      const name = event.type === "keypress" ? "input" : event.type;
      if (!isSimilarToLastCapturedEvent(event)) {
        const handlerData = { event, name, global: globalListener };
        handler(handlerData);
        lastCapturedEventType = event.type;
        lastCapturedEventTargetId = target ? target._sentryId : void 0;
      }
      clearTimeout(debounceTimerID);
      debounceTimerID = WINDOW2.setTimeout(() => {
        lastCapturedEventTargetId = void 0;
        lastCapturedEventType = void 0;
      }, DEBOUNCE_DURATION);
    };
  }
  function getEventTarget(event) {
    try {
      return event.target;
    } catch {
      return null;
    }
  }

  // node_modules/@sentry/browser-utils/build/esm/instrumentation/history.js
  var lastHref;
  function supportsHistory() {
    return "history" in WINDOW2 && !!WINDOW2.history;
  }
  function addHistoryInstrumentationHandler(handler) {
    const type = "history";
    addHandler(type, handler);
    maybeInstrument(type, instrumentHistory);
  }
  function instrumentHistory() {
    WINDOW2.addEventListener("popstate", () => {
      const to = WINDOW2.location.href;
      const from = lastHref;
      lastHref = to;
      if (from === to) {
        return;
      }
      const handlerData = { from, to };
      triggerHandlers("history", handlerData);
    });
    if (!supportsHistory()) {
      return;
    }
    function historyReplacementFunction(originalHistoryFunction) {
      return function(...args) {
        const url = args.length > 2 ? args[2] : void 0;
        if (url) {
          const from = lastHref;
          const to = getAbsoluteUrl(String(url));
          lastHref = to;
          if (from === to) {
            return originalHistoryFunction.apply(this, args);
          }
          const handlerData = { from, to };
          triggerHandlers("history", handlerData);
        }
        return originalHistoryFunction.apply(this, args);
      };
    }
    fill(WINDOW2.history, "pushState", historyReplacementFunction);
    fill(WINDOW2.history, "replaceState", historyReplacementFunction);
  }
  function getAbsoluteUrl(urlOrPath) {
    try {
      const url = new URL(urlOrPath, WINDOW2.location.origin);
      return url.toString();
    } catch {
      return urlOrPath;
    }
  }

  // node_modules/@sentry/browser-utils/build/esm/getNativeImplementation.js
  var cachedImplementations = {};
  function getNativeImplementation(name) {
    const cached = cachedImplementations[name];
    if (cached) {
      return cached;
    }
    let impl = WINDOW2[name];
    if (isNativeFunction(impl)) {
      return cachedImplementations[name] = impl.bind(WINDOW2);
    }
    const document2 = WINDOW2.document;
    if (document2 && typeof document2.createElement === "function") {
      try {
        const sandbox = document2.createElement("iframe");
        sandbox.hidden = true;
        document2.head.appendChild(sandbox);
        const contentWindow = sandbox.contentWindow;
        if (contentWindow?.[name]) {
          impl = contentWindow[name];
        }
        document2.head.removeChild(sandbox);
      } catch (e) {
        DEBUG_BUILD2 && debug.warn(`Could not create sandbox iframe for ${name} check, bailing to window.${name}: `, e);
      }
    }
    if (!impl) {
      return impl;
    }
    return cachedImplementations[name] = impl.bind(WINDOW2);
  }
  function clearCachedImplementation(name) {
    cachedImplementations[name] = void 0;
  }

  // node_modules/@sentry/browser-utils/build/esm/instrumentation/xhr.js
  var SENTRY_XHR_DATA_KEY = "__sentry_xhr_v3__";
  function addXhrInstrumentationHandler(handler) {
    const type = "xhr";
    addHandler(type, handler);
    maybeInstrument(type, instrumentXHR);
  }
  function instrumentXHR() {
    if (!WINDOW2.XMLHttpRequest) {
      return;
    }
    const xhrproto = XMLHttpRequest.prototype;
    xhrproto.open = new Proxy(xhrproto.open, {
      apply(originalOpen, xhrOpenThisArg, xhrOpenArgArray) {
        let virtualError = new Error();
        const startTimestamp = timestampInSeconds() * 1e3;
        const method = isString(xhrOpenArgArray[0]) ? xhrOpenArgArray[0].toUpperCase() : void 0;
        const url = parseXhrUrlArg(xhrOpenArgArray[1]);
        if (!method || !url) {
          return originalOpen.apply(xhrOpenThisArg, xhrOpenArgArray);
        }
        xhrOpenThisArg[SENTRY_XHR_DATA_KEY] = {
          method,
          url,
          request_headers: {}
        };
        if (method === "POST" && url.match(/sentry_key/)) {
          xhrOpenThisArg.__sentry_own_request__ = true;
        }
        const onreadystatechangeHandler = () => {
          const xhrInfo = xhrOpenThisArg[SENTRY_XHR_DATA_KEY];
          if (!xhrInfo) {
            return;
          }
          if (xhrOpenThisArg.readyState === 4) {
            try {
              xhrInfo.status_code = xhrOpenThisArg.status;
            } catch {
            }
            const handlerData = {
              endTimestamp: timestampInSeconds() * 1e3,
              startTimestamp,
              xhr: xhrOpenThisArg,
              virtualError
            };
            triggerHandlers("xhr", handlerData);
            virtualError = void 0;
            xhrOpenThisArg.removeEventListener("readystatechange", onreadystatechangeHandler);
          }
        };
        if ("onreadystatechange" in xhrOpenThisArg && typeof xhrOpenThisArg.onreadystatechange === "function") {
          xhrOpenThisArg.onreadystatechange = new Proxy(xhrOpenThisArg.onreadystatechange, {
            apply(originalOnreadystatechange, onreadystatechangeThisArg, onreadystatechangeArgArray) {
              onreadystatechangeHandler();
              return originalOnreadystatechange.apply(onreadystatechangeThisArg, onreadystatechangeArgArray);
            }
          });
        } else {
          xhrOpenThisArg.addEventListener("readystatechange", onreadystatechangeHandler);
        }
        xhrOpenThisArg.setRequestHeader = new Proxy(xhrOpenThisArg.setRequestHeader, {
          apply(originalSetRequestHeader, setRequestHeaderThisArg, setRequestHeaderArgArray) {
            const [header, value] = setRequestHeaderArgArray;
            const xhrInfo = setRequestHeaderThisArg[SENTRY_XHR_DATA_KEY];
            if (xhrInfo && isString(header) && isString(value)) {
              xhrInfo.request_headers[header.toLowerCase()] = value;
            }
            return originalSetRequestHeader.apply(setRequestHeaderThisArg, setRequestHeaderArgArray);
          }
        });
        return originalOpen.apply(xhrOpenThisArg, xhrOpenArgArray);
      }
    });
    xhrproto.send = new Proxy(xhrproto.send, {
      apply(originalSend, sendThisArg, sendArgArray) {
        const sentryXhrData = sendThisArg[SENTRY_XHR_DATA_KEY];
        if (!sentryXhrData) {
          return originalSend.apply(sendThisArg, sendArgArray);
        }
        if (sendArgArray[0] !== void 0) {
          sentryXhrData.body = sendArgArray[0];
        }
        const handlerData = {
          startTimestamp: timestampInSeconds() * 1e3,
          xhr: sendThisArg
        };
        triggerHandlers("xhr", handlerData);
        return originalSend.apply(sendThisArg, sendArgArray);
      }
    });
  }
  function parseXhrUrlArg(url) {
    if (isString(url)) {
      return url;
    }
    try {
      return url.toString();
    } catch {
    }
    return void 0;
  }

  // node_modules/@sentry/browser-utils/build/esm/is.js
  function isElement2(wat) {
    if (typeof Element === "undefined") {
      return false;
    }
    try {
      return wat instanceof Element;
    } catch {
      return false;
    }
  }

  // node_modules/@sentry/browser/build/npm/esm/prod/helpers.js
  var WINDOW3 = GLOBAL_OBJ;
  var ignoreOnError = 0;
  var ignoredErrorReports = [];
  function shouldIgnoreOnError(data) {
    if (ignoreOnError > 0) {
      return true;
    }
    const index = data ? ignoredErrorReports.findIndex((report) => isSameErrorReport(report, data)) : -1;
    if (index === -1) {
      return false;
    }
    ignoredErrorReports.splice(index, 1);
    return true;
  }
  function isSameErrorReport(a, b) {
    return a.msg === b.msg && a.url === b.url && a.line === b.line && a.column === b.column;
  }
  function ignoreNextOnError() {
    ignoreOnError++;
    setTimeout(() => {
      ignoreOnError--;
    });
  }
  function wrap(fn, options = {}) {
    function isFunction(fn2) {
      return typeof fn2 === "function";
    }
    if (!isFunction(fn)) {
      return fn;
    }
    try {
      const hasOwnWrapper = Object.prototype.hasOwnProperty.call(fn, "__sentry_wrapped__");
      if (hasOwnWrapper) {
        const wrapper = fn.__sentry_wrapped__;
        if (typeof wrapper === "function") {
          return wrapper;
        } else {
          return fn;
        }
      }
      if (getOriginalFunction(fn)) {
        return fn;
      }
    } catch {
      return fn;
    }
    const sentryWrapped = function(...args) {
      GLOBAL_OBJ._sentryWrappedDepth = (GLOBAL_OBJ._sentryWrappedDepth || 0) + 1;
      try {
        const wrappedArguments = args.map((arg) => wrap(arg, options));
        return fn.apply(this, wrappedArguments);
      } catch (ex) {
        ignoreNextOnError();
        withScope2((scope) => {
          scope.addEventProcessor((event) => {
            if (options.mechanism) {
              addExceptionTypeValue(event, void 0, void 0);
              addExceptionMechanism(event, options.mechanism);
            }
            event.extra = {
              ...event.extra,
              arguments: args
            };
            return event;
          });
          captureException(ex);
        });
        throw ex;
      } finally {
        GLOBAL_OBJ._sentryWrappedDepth = (GLOBAL_OBJ._sentryWrappedDepth || 0) - 1;
      }
    };
    try {
      for (const property in fn) {
        if (Object.prototype.hasOwnProperty.call(fn, property)) {
          sentryWrapped[property] = fn[property];
        }
      }
    } catch {
    }
    markFunctionWrapped(sentryWrapped, fn);
    addNonEnumerableProperty(fn, "__sentry_wrapped__", sentryWrapped);
    try {
      const descriptor = Object.getOwnPropertyDescriptor(sentryWrapped, "name");
      if (descriptor.configurable) {
        Object.defineProperty(sentryWrapped, "name", {
          get() {
            return fn.name;
          }
        });
      }
    } catch {
    }
    return sentryWrapped;
  }
  function getHttpRequestData(client) {
    const url = getLocationHref();
    const { referrer } = WINDOW3.document || {};
    const { userAgent } = WINDOW3.navigator || {};
    const headers = {
      ...referrer && { Referer: filterCollectedUrl(referrer, client) },
      ...userAgent && { "User-Agent": userAgent }
    };
    const request = {
      url,
      headers
    };
    return request;
  }

  // node_modules/@sentry/browser/build/npm/esm/prod/eventbuilder.js
  function exceptionFromError2(stackParser, ex) {
    const frames = parseStackFrames2(stackParser, ex);
    const exception = {
      type: extractType(ex),
      value: extractMessage(ex)
    };
    if (frames.length) {
      exception.stacktrace = { frames };
    }
    if (exception.type === void 0 && exception.value === "") {
      exception.value = "Unrecoverable error caught";
    }
    return exception;
  }
  function eventFromPlainObject(stackParser, exception, syntheticException, isUnhandledRejection) {
    const client = getClient();
    const normalizeDepth = client?.getOptions().normalizeDepth;
    const errorFromProp = getErrorPropertyFromObject(exception);
    const extra = {
      __serialized__: normalizeToSize(exception, normalizeDepth)
    };
    if (errorFromProp) {
      return {
        exception: {
          values: [exceptionFromError2(stackParser, errorFromProp)]
        },
        extra
      };
    }
    const exceptionValue = {
      type: isEvent(exception) ? exception.constructor.name : isUnhandledRejection ? "UnhandledRejection" : "Error",
      value: getNonErrorObjectExceptionValue(exception, { isUnhandledRejection })
    };
    const event = {
      exception: {
        values: [exceptionValue]
      },
      extra
    };
    if (syntheticException) {
      const frames = parseStackFrames2(stackParser, syntheticException);
      if (frames.length) {
        event.exception.values[0].stacktrace = { frames };
      }
    }
    return event;
  }
  function eventFromError(stackParser, ex) {
    return {
      exception: {
        values: [exceptionFromError2(stackParser, ex)]
      }
    };
  }
  function parseStackFrames2(stackParser, ex) {
    const stacktrace = ex.stacktrace || ex.stack || "";
    const skipLines = getSkipFirstStackStringLines(ex);
    const framesToPop = getPopFirstTopFrames(ex);
    try {
      return stackParser(stacktrace, skipLines, framesToPop);
    } catch {
    }
    return [];
  }
  var reactMinifiedRegexp = /Minified React error #\d+;/i;
  function getSkipFirstStackStringLines(ex) {
    if (ex && reactMinifiedRegexp.test(ex.message)) {
      return 1;
    }
    return 0;
  }
  function getPopFirstTopFrames(ex) {
    if (typeof ex.framesToPop === "number") {
      return ex.framesToPop;
    }
    return 0;
  }
  function isWebAssemblyException(exception) {
    if (typeof WebAssembly !== "undefined" && typeof WebAssembly.Exception !== "undefined") {
      return exception instanceof WebAssembly.Exception;
    } else {
      return false;
    }
  }
  function extractType(ex) {
    const name = ex?.name;
    if (!name && isWebAssemblyException(ex)) {
      const hasTypeInMessage = ex.message && Array.isArray(ex.message) && ex.message.length == 2;
      return hasTypeInMessage ? ex.message[0] : "WebAssembly.Exception";
    }
    return name;
  }
  function extractMessage(ex) {
    const message = ex?.message;
    if (isWebAssemblyException(ex)) {
      if (Array.isArray(ex.message) && ex.message.length == 2) {
        return ex.message[1];
      }
      return "wasm exception";
    }
    if (!message) {
      return "No error message";
    }
    if (message.error && typeof message.error.message === "string") {
      return _enhanceErrorWithSentryInfo(message.error);
    }
    return _enhanceErrorWithSentryInfo(ex);
  }
  function eventFromException(stackParser, exception, hint, attachStacktrace) {
    const syntheticException = hint?.syntheticException || void 0;
    const event = eventFromUnknownInput2(stackParser, exception, syntheticException, attachStacktrace);
    addExceptionMechanism(event);
    event.level = "error";
    if (hint?.event_id) {
      event.event_id = hint.event_id;
    }
    return resolvedSyncPromise(event);
  }
  function eventFromMessage2(stackParser, message, level = "info", hint, attachStacktrace) {
    const syntheticException = hint?.syntheticException || void 0;
    const event = eventFromString(stackParser, message, syntheticException, attachStacktrace);
    event.level = level;
    if (hint?.event_id) {
      event.event_id = hint.event_id;
    }
    return resolvedSyncPromise(event);
  }
  function eventFromUnknownInput2(stackParser, exception, syntheticException, attachStacktrace, isUnhandledRejection) {
    let event;
    if (isErrorEvent(exception) && exception.error) {
      const errorEvent = exception;
      return eventFromError(stackParser, errorEvent.error);
    }
    if (isDOMError(exception) || isDOMException(exception)) {
      const domException = exception;
      if ("stack" in exception) {
        event = eventFromError(stackParser, exception);
        const firstException = event.exception?.values?.[0];
        if (attachStacktrace && syntheticException && firstException && !firstException.stacktrace) {
          const frames = parseStackFrames2(stackParser, syntheticException);
          if (frames.length) {
            firstException.stacktrace = { frames };
            addExceptionMechanism(event, { synthetic: true });
          }
        }
      } else {
        const name = domException.name || (isDOMError(domException) ? "DOMError" : "DOMException");
        const message = domException.message ? `${name}: ${domException.message}` : name;
        event = eventFromString(stackParser, message, syntheticException, attachStacktrace);
        addExceptionTypeValue(event, message);
      }
      return event;
    }
    if (isError(exception)) {
      return eventFromError(stackParser, exception);
    }
    if (isPlainObject(exception) || isEvent(exception)) {
      const objectException = exception;
      event = eventFromPlainObject(stackParser, objectException, syntheticException, isUnhandledRejection);
      addExceptionMechanism(event, {
        synthetic: true
      });
      return event;
    }
    const stringifiedException = String(exception);
    event = eventFromString(stackParser, stringifiedException, syntheticException, attachStacktrace);
    addExceptionTypeValue(event, stringifiedException, void 0);
    addExceptionMechanism(event, {
      synthetic: true
    });
    return event;
  }
  function eventFromString(stackParser, message, syntheticException, attachStacktrace) {
    const event = {};
    if (attachStacktrace && syntheticException) {
      const frames = parseStackFrames2(stackParser, syntheticException);
      if (frames.length) {
        event.exception = {
          values: [{ value: message, stacktrace: { frames } }]
        };
      }
      addExceptionMechanism(event, { synthetic: true });
    }
    if (isParameterizedString(message)) {
      const { __sentry_template_string__, __sentry_template_values__ } = message;
      event.logentry = {
        message: __sentry_template_string__,
        params: __sentry_template_values__
      };
      return event;
    }
    event.message = message;
    return event;
  }
  function getNonErrorObjectExceptionValue(exception, { isUnhandledRejection }) {
    const keys = extractExceptionKeysForMessage(exception);
    const captureType = isUnhandledRejection ? "promise rejection" : "exception";
    if (isErrorEvent(exception)) {
      return `Event \`ErrorEvent\` captured as ${captureType} with message \`${exception.message}\``;
    }
    if (isEvent(exception)) {
      const className = getObjectClassName(exception);
      return `Event \`${className}\` (type=${exception.type}) captured as ${captureType}`;
    }
    return `Object captured as ${captureType} with keys: ${keys}`;
  }
  function getObjectClassName(obj) {
    try {
      const prototype = Object.getPrototypeOf(obj);
      return prototype ? prototype.constructor.name : void 0;
    } catch {
    }
  }
  function getErrorPropertyFromObject(obj) {
    return Object.values(obj).find(isError);
  }

  // node_modules/@sentry/browser/build/npm/esm/prod/client.js
  var BrowserClient = class extends Client {
    /**
     * Creates a new Browser SDK instance.
     *
     * @param options Configuration options for this SDK.
     */
    constructor(options) {
      const opts = applyDefaultOptions(options);
      const sdkSource = WINDOW3.SENTRY_SDK_SOURCE || getSDKSource();
      applySdkMetadata(opts, "browser", ["browser"], sdkSource);
      super(opts);
      if (opts.routeProvider) {
        setRouteProvider(opts.routeProvider, this);
      }
      this._unhandledSessionStatus = "unhandled";
      const { userInfo } = this.getDataCollectionOptions();
      if (opts._metadata?.sdk) {
        opts._metadata.sdk.settings = {
          // Only allow IP inferral by Relay if the user opted in via dataCollection
          infer_ip: userInfo ? "auto" : "never",
          // purposefully allowing already passed settings to override the default
          ...opts._metadata.sdk.settings
        };
      }
      const { sendClientReports } = this._options;
      const checkDrift = () => {
        timestampInSeconds();
      };
      const listeners = [
        // Flush buffered data when the page becomes hidden (e.g. tab switch, navigation, or the page
        // being discarded). `flush()` emits the `flush` hook, which drains the span (streaming), log and
        // metric buffers and hands the resulting envelopes to the transport (which uses `keepalive`).
        // Client report outcomes don't listen to the `flush` hook, so we flush them separately.
        [
          WINDOW3.document,
          "visibilitychange",
          () => {
            checkDrift();
            if (WINDOW3.document.visibilityState === "hidden") {
              if (sendClientReports) {
                this._flushOutcomes();
              }
              queueMicrotask(() => {
                void this.flush();
              });
            }
          }
        ],
        // `freeze` and `resume` are only fired by Chromium browsers. Other browsers never fire them, so these listeners
        // are no-ops there.
        [WINDOW3.document, "freeze", checkDrift],
        [WINDOW3.document, "resume", checkDrift],
        // Pages restored from the back/forward cache were paused while they were cached.
        [WINDOW3, "pagehide", checkDrift],
        [WINDOW3, "pageshow", checkDrift]
      ];
      listeners.forEach(([target, name, listener]) => target?.addEventListener?.(name, listener));
      this.on(
        "close",
        () => listeners.forEach(([target, name, listener]) => target?.removeEventListener?.(name, listener))
      );
      if (userInfo) {
        this.on("beforeSendSession", addAutoIpAddressToSession);
      }
    }
    /**
     * @inheritDoc
     */
    eventFromException(exception, hint) {
      return eventFromException(this._options.stackParser, exception, hint, this._options.attachStacktrace);
    }
    /**
     * @inheritDoc
     */
    eventFromMessage(message, level = "info", hint) {
      return eventFromMessage2(this._options.stackParser, message, level, hint, this._options.attachStacktrace);
    }
    /**
     * @inheritDoc
     */
    _prepareEvent(event, hint, currentScope, isolationScope) {
      event.platform = event.platform || "javascript";
      return super._prepareEvent(event, hint, currentScope, isolationScope);
    }
  };
  function applyDefaultOptions(optionsArg) {
    return {
      release: typeof __SENTRY_RELEASE__ === "string" ? __SENTRY_RELEASE__ : WINDOW3.SENTRY_RELEASE?.id,
      // This supports the variable that sentry-webpack-plugin injects
      sendClientReports: true,
      // We default this to true, as it is the safer scenario
      parentSpanIsAlwaysRootSpan: true,
      ...optionsArg
    };
  }

  // node_modules/@sentry/browser/build/npm/esm/prod/transports/fetch.js
  var DEFAULT_BROWSER_TRANSPORT_BUFFER_SIZE = 40;
  function makeFetchTransport(options, nativeFetch = getNativeImplementation("fetch")) {
    let pendingBodySize = 0;
    let pendingCount = 0;
    async function makeRequest(request) {
      const requestSize = request.body.length;
      pendingBodySize += requestSize;
      pendingCount++;
      const requestOptions = {
        body: request.body,
        method: "POST",
        referrerPolicy: "strict-origin",
        headers: options.headers,
        // Outgoing requests are usually cancelled when navigating to a different page, causing a "TypeError: Failed to
        // fetch" error and sending a "network_error" client-outcome - in Chrome, the request status shows "(cancelled)".
        // The `keepalive` flag keeps outgoing requests alive, even when switching pages. We want this since we're
        // frequently sending events right before the user is switching pages (eg. when finishing navigation transactions).
        // Gotchas:
        // - `keepalive` isn't supported by Firefox
        // - As per spec (https://fetch.spec.whatwg.org/#http-network-or-cache-fetch):
        //   If the sum of contentLength and inflightKeepaliveBytes is greater than 64 kibibytes, then return a network error.
        //   We will therefore only activate the flag when we're below that limit.
        // There is also a limit of requests that can be open at the same time, so we also limit this to 15
        // See https://github.com/getsentry/sentry-javascript/pull/7553 for details
        keepalive: pendingBodySize <= 6e4 && pendingCount < 15,
        ...options.fetchOptions
      };
      try {
        const response = await nativeFetch(options.url, requestOptions);
        return {
          statusCode: response.status,
          headers: {
            "x-sentry-rate-limits": response.headers.get("X-Sentry-Rate-Limits"),
            "retry-after": response.headers.get("Retry-After")
          }
        };
      } catch (e) {
        clearCachedImplementation("fetch");
        throw e;
      } finally {
        pendingBodySize -= requestSize;
        pendingCount--;
      }
    }
    return createTransport(
      options,
      makeRequest,
      makePromiseBuffer(options.bufferSize || DEFAULT_BROWSER_TRANSPORT_BUFFER_SIZE)
    );
  }

  // node_modules/@sentry/browser/build/npm/esm/prod/debug-build.js
  var DEBUG_BUILD3 = typeof __SENTRY_DEBUG__ === "undefined" || __SENTRY_DEBUG__;

  // node_modules/@sentry/browser/build/npm/esm/prod/stack-parsers.js
  var CHROME_PRIORITY = 30;
  var GECKO_PRIORITY = 50;
  function createFrame(filename, func, lineno, colno) {
    const frame = {
      filename,
      function: func === "<anonymous>" ? UNKNOWN_FUNCTION : func,
      in_app: true
      // All browser frames are considered in_app
    };
    if (lineno !== void 0) {
      frame.lineno = lineno;
    }
    if (colno !== void 0) {
      frame.colno = colno;
    }
    return frame;
  }
  var chromeRegexNoFnName = /^\s*at (\S+?)(?::(\d+))(?::(\d+))\s*$/i;
  var chromeRegex = /^\s*at (?:(.+?\)(?: \[.+\])?|.*?) ?\((?:address at )?)?(?:async )?((?:<anonymous>|[-a-z]+:|.*bundle|\/)?.*?)(?::(\d+))?(?::(\d+))?\)?\s*$/i;
  var chromeEvalRegex = /\((\S*)(?::(\d+))(?::(\d+))\)/;
  var chromeDataUriRegex = /at (.+?) ?\(data:(.+?),/;
  var chromeStackParserFn = (line) => {
    const dataUriMatch = line.match(chromeDataUriRegex);
    if (dataUriMatch) {
      return {
        filename: `<data:${dataUriMatch[2]}>`,
        function: dataUriMatch[1]
      };
    }
    const noFnParts = chromeRegexNoFnName.exec(line);
    if (noFnParts) {
      const [, filename, line2, col] = noFnParts;
      return createFrame(filename, UNKNOWN_FUNCTION, +line2, +col);
    }
    const parts = chromeRegex.exec(line);
    if (parts) {
      const isEval = parts[2]?.indexOf("eval") === 0;
      if (isEval) {
        const subMatch = chromeEvalRegex.exec(parts[2]);
        if (subMatch) {
          parts[2] = subMatch[1];
          parts[3] = subMatch[2];
          parts[4] = subMatch[3];
        }
      }
      const [func, filename] = extractSafariExtensionDetails(parts[1] || UNKNOWN_FUNCTION, parts[2]);
      return createFrame(filename, func, parts[3] ? +parts[3] : void 0, parts[4] ? +parts[4] : void 0);
    }
    return;
  };
  var chromeStackLineParser = [CHROME_PRIORITY, chromeStackParserFn];
  var geckoREgex = /^\s*(.*?)(?:\((.*?)\))?(?:^|@)?((?:[-a-z]+)?:\/.*?|\[native code\]|[^@]*(?:bundle|\d+\.js)|\/[\w\-. /=]+)(?::(\d+))?(?::(\d+))?\s*$/i;
  var geckoEvalRegex = /(\S+) line (\d+)(?: > eval line \d+)* > eval/i;
  var gecko = (line) => {
    const parts = geckoREgex.exec(line);
    if (parts) {
      const isEval = parts[3] && parts[3].indexOf(" > eval") > -1;
      if (isEval) {
        const subMatch = geckoEvalRegex.exec(parts[3]);
        if (subMatch) {
          parts[1] = parts[1] || "eval";
          parts[3] = subMatch[1];
          parts[4] = subMatch[2];
          parts[5] = "";
        }
      }
      let filename = parts[3];
      let func = parts[1] || UNKNOWN_FUNCTION;
      [func, filename] = extractSafariExtensionDetails(func, filename);
      return createFrame(filename, func, parts[4] ? +parts[4] : void 0, parts[5] ? +parts[5] : void 0);
    }
    return;
  };
  var geckoStackLineParser = [GECKO_PRIORITY, gecko];
  var defaultStackLineParsers = [chromeStackLineParser, geckoStackLineParser];
  var defaultStackParser = createStackParser(...defaultStackLineParsers);
  var extractSafariExtensionDetails = (func, filename) => {
    const isSafariExtension = func.indexOf("safari-extension") !== -1;
    const isSafariWebExtension = func.indexOf("safari-web-extension") !== -1;
    return isSafariExtension || isSafariWebExtension ? [
      func.indexOf("@") !== -1 ? func.split("@")[0] : UNKNOWN_FUNCTION,
      isSafariExtension ? `safari-extension:${filename}` : `safari-web-extension:${filename}`
    ] : [func, filename];
  };

  // node_modules/@sentry/browser/build/npm/esm/prod/integrations/breadcrumbs.js
  var MAX_ALLOWED_STRING_LENGTH = 1024;
  var INTEGRATION_NAME6 = "Breadcrumbs";
  var _breadcrumbsIntegration = ((options = {}) => {
    const _options = {
      dom: true,
      fetch: true,
      history: true,
      sentry: true,
      xhr: true,
      ...options
    };
    return {
      name: INTEGRATION_NAME6,
      setup(client) {
        if (_options.dom) {
          addClickKeypressInstrumentationHandler(_getDomBreadcrumbHandler(client, _options.dom));
        }
        if (_options.xhr) {
          addXhrInstrumentationHandler(_getXhrBreadcrumbHandler(client));
        }
        if (_options.fetch) {
          addFetchInstrumentationHandler(_getFetchBreadcrumbHandler(client));
        }
        if (_options.history) {
          addHistoryInstrumentationHandler(_getHistoryBreadcrumbHandler(client));
        }
        if (_options.sentry) {
          client.on("beforeSendEvent", _getSentryBreadcrumbHandler(client));
        }
      }
    };
  });
  var breadcrumbsIntegration = defineIntegration(_breadcrumbsIntegration);
  function _getSentryBreadcrumbHandler(client) {
    return function addSentryBreadcrumb(event) {
      if (getClient() !== client) {
        return;
      }
      addBreadcrumb(
        {
          category: `sentry.${event.type === "transaction" ? "transaction" : "event"}`,
          event_id: event.event_id,
          level: event.level,
          message: getEventDescription(event)
        },
        {
          event
        }
      );
    };
  }
  function _getDomBreadcrumbHandler(client, dom) {
    return function _innerDomBreadcrumb(handlerData) {
      if (getClient() !== client) {
        return;
      }
      let target;
      let componentName;
      let keyAttrs = typeof dom === "object" ? dom.serializeAttribute : void 0;
      let maxStringLength = typeof dom === "object" && typeof dom.maxStringLength === "number" ? dom.maxStringLength : void 0;
      if (maxStringLength && maxStringLength > MAX_ALLOWED_STRING_LENGTH) {
        DEBUG_BUILD3 && debug.warn(
          `\`dom.maxStringLength\` cannot exceed ${MAX_ALLOWED_STRING_LENGTH}, but a value of ${maxStringLength} was configured. Sentry will use ${MAX_ALLOWED_STRING_LENGTH} instead.`
        );
        maxStringLength = MAX_ALLOWED_STRING_LENGTH;
      }
      if (typeof keyAttrs === "string") {
        keyAttrs = [keyAttrs];
      }
      try {
        const event = handlerData.event;
        const element = _isEvent(event) ? event.target : event;
        target = htmlTreeAsString(element, { keyAttrs, maxStringLength });
        componentName = getComponentName(element);
      } catch {
        target = "<unknown>";
      }
      if (target.length === 0) {
        return;
      }
      const breadcrumb = {
        category: `ui.${handlerData.name}`,
        message: target
      };
      if (componentName) {
        breadcrumb.data = { "ui.component_name": componentName };
      }
      addBreadcrumb(breadcrumb, {
        event: handlerData.event,
        name: handlerData.name,
        global: handlerData.global
      });
    };
  }
  function _getXhrBreadcrumbHandler(client) {
    return function _xhrBreadcrumb(handlerData) {
      if (getClient() !== client) {
        return;
      }
      const { startTimestamp, endTimestamp } = handlerData;
      const sentryXhrData = handlerData.xhr[SENTRY_XHR_DATA_KEY];
      if (!startTimestamp || !endTimestamp || !sentryXhrData) {
        return;
      }
      const { method, url, status_code, body } = sentryXhrData;
      const data = {
        method,
        url: filterCollectedUrl(url),
        status_code
      };
      const hint = {
        xhr: handlerData.xhr,
        input: body,
        startTimestamp,
        endTimestamp
      };
      const breadcrumb = {
        category: "xhr",
        data,
        type: "http",
        level: getBreadcrumbLogLevelFromHttpStatusCode(status_code)
      };
      client.emit("beforeOutgoingRequestBreadcrumb", breadcrumb, hint);
      addBreadcrumb(breadcrumb, hint);
    };
  }
  function _getFetchBreadcrumbHandler(client) {
    return function _fetchBreadcrumb(handlerData) {
      if (getClient() !== client) {
        return;
      }
      const { startTimestamp, endTimestamp } = handlerData;
      if (!endTimestamp) {
        return;
      }
      if (handlerData.fetchData.url.match(/sentry_key/) && handlerData.fetchData.method === "POST") {
        return;
      }
      if (handlerData.error) {
        const hint = {
          data: handlerData.error,
          input: handlerData.args,
          startTimestamp,
          endTimestamp
        };
        const breadcrumb = {
          category: "fetch",
          data: { ...handlerData.fetchData, url: filterCollectedUrl(handlerData.fetchData.url) },
          level: "error",
          type: "http"
        };
        client.emit("beforeOutgoingRequestBreadcrumb", breadcrumb, hint);
        addBreadcrumb(breadcrumb, hint);
      } else {
        const response = handlerData.response;
        const data = {
          ...handlerData.fetchData,
          url: filterCollectedUrl(handlerData.fetchData.url),
          status_code: response?.status
        };
        const hint = {
          input: handlerData.args,
          response,
          startTimestamp,
          endTimestamp
        };
        const breadcrumb = {
          category: "fetch",
          data,
          type: "http",
          level: getBreadcrumbLogLevelFromHttpStatusCode(data.status_code)
        };
        client.emit("beforeOutgoingRequestBreadcrumb", breadcrumb, hint);
        addBreadcrumb(breadcrumb, hint);
      }
    };
  }
  function _getHistoryBreadcrumbHandler(client) {
    return function _historyBreadcrumb(handlerData) {
      if (getClient() !== client) {
        return;
      }
      let from = handlerData.from;
      let to = handlerData.to;
      const parsedLoc = parseUrl(WINDOW3.location.href);
      let parsedFrom = from ? parseUrl(from) : void 0;
      const parsedTo = parseUrl(to);
      if (!parsedFrom?.path) {
        parsedFrom = parsedLoc;
      }
      if (parsedLoc.protocol === parsedTo.protocol && parsedLoc.host === parsedTo.host) {
        to = parsedTo.relative;
      }
      if (parsedLoc.protocol === parsedFrom.protocol && parsedLoc.host === parsedFrom.host) {
        from = parsedFrom.relative;
      }
      addBreadcrumb({
        category: "navigation",
        data: {
          from: filterCollectedUrl(from),
          to: filterCollectedUrl(to)
        }
      });
    };
  }
  function _isEvent(event) {
    return !!event && !!event.target;
  }

  // node_modules/@sentry/browser/build/npm/esm/prod/integrations/browserapierrors.js
  var DEFAULT_EVENT_TARGET = "EventTarget,Window,Node,ApplicationCache,AudioTrackList,BroadcastChannel,ChannelMergerNode,CryptoOperation,EventSource,FileReader,HTMLUnknownElement,IDBDatabase,IDBRequest,IDBTransaction,KeyOperation,MediaController,MessagePort,ModalWindow,Notification,SVGElementInstance,Screen,SharedWorker,TextTrack,TextTrackCue,TextTrackList,WebSocket,WebSocketWorker,Worker,XMLHttpRequest,XMLHttpRequestEventTarget,XMLHttpRequestUpload".split(
    ","
  );
  var INTEGRATION_NAME7 = "BrowserApiErrors";
  var _browserApiErrorsIntegration = ((options = {}) => {
    const _options = {
      XMLHttpRequest: true,
      eventTarget: true,
      requestAnimationFrame: true,
      setInterval: true,
      setTimeout: true,
      unregisterOriginalCallbacks: false,
      ...options
    };
    return {
      name: INTEGRATION_NAME7,
      // TODO: This currently only works for the first client this is setup
      // We may want to adjust this to check for client etc.
      setupOnce() {
        if (_options.setTimeout) {
          fill(WINDOW3, "setTimeout", _wrapTimeFunction);
        }
        if (_options.setInterval) {
          fill(WINDOW3, "setInterval", _wrapTimeFunction);
        }
        if (_options.requestAnimationFrame) {
          fill(WINDOW3, "requestAnimationFrame", _wrapRAF);
        }
        if (_options.XMLHttpRequest && "XMLHttpRequest" in WINDOW3) {
          fill(XMLHttpRequest.prototype, "send", _wrapXHR);
        }
        const eventTargetOption = _options.eventTarget;
        if (eventTargetOption) {
          const eventTarget = Array.isArray(eventTargetOption) ? eventTargetOption : DEFAULT_EVENT_TARGET;
          eventTarget.forEach((target) => _wrapEventTarget(target, _options));
        }
      }
    };
  });
  var browserApiErrorsIntegration = defineIntegration(_browserApiErrorsIntegration);
  function _wrapTimeFunction(original) {
    return function(...args) {
      const originalCallback = args[0];
      args[0] = wrap(originalCallback, {
        mechanism: {
          handled: false,
          type: `auto.browser.browserapierrors.${getFunctionName(original)}`
        }
      });
      return original.apply(this, args);
    };
  }
  function _wrapRAF(original) {
    return function(callback) {
      return original.apply(this, [
        wrap(callback, {
          mechanism: {
            data: {
              handler: getFunctionName(original)
            },
            handled: false,
            type: "auto.browser.browserapierrors.requestAnimationFrame"
          }
        })
      ]);
    };
  }
  function _wrapXHR(originalSend) {
    return function(...args) {
      const xhr = this;
      const xmlHttpRequestProps = ["onload", "onerror", "onprogress", "onreadystatechange"];
      xmlHttpRequestProps.forEach((prop) => {
        if (prop in xhr && typeof xhr[prop] === "function") {
          fill(xhr, prop, function(original) {
            const wrapOptions = {
              mechanism: {
                data: {
                  handler: getFunctionName(original)
                },
                handled: false,
                type: `auto.browser.browserapierrors.xhr.${prop}`
              }
            };
            const originalFunction = getOriginalFunction(original);
            if (originalFunction) {
              wrapOptions.mechanism.data.handler = getFunctionName(originalFunction);
            }
            return wrap(original, wrapOptions);
          });
        }
      });
      return originalSend.apply(this, args);
    };
  }
  function _wrapEventTarget(target, integrationOptions) {
    const globalObject = WINDOW3;
    const proto = globalObject[target]?.prototype;
    if (!proto?.hasOwnProperty?.("addEventListener")) {
      return;
    }
    fill(proto, "addEventListener", function(original) {
      return function(eventName, fn, options) {
        try {
          if (isEventListenerObject(fn)) {
            fn.handleEvent = wrap(fn.handleEvent, {
              mechanism: {
                data: {
                  handler: getFunctionName(fn),
                  target
                },
                handled: false,
                type: "auto.browser.browserapierrors.handleEvent"
              }
            });
          }
        } catch {
        }
        if (integrationOptions.unregisterOriginalCallbacks) {
          unregisterOriginalCallback(this, eventName, fn);
        }
        return original.apply(this, [
          eventName,
          wrap(fn, {
            mechanism: {
              data: {
                handler: getFunctionName(fn),
                target
              },
              handled: false,
              type: "auto.browser.browserapierrors.addEventListener"
            }
          }),
          options
        ]);
      };
    });
    fill(proto, "removeEventListener", function(originalRemoveEventListener) {
      return function(eventName, fn, options) {
        try {
          if (Object.prototype.hasOwnProperty.call(fn, "__sentry_wrapped__")) {
            const originalEventHandler = fn.__sentry_wrapped__;
            if (originalEventHandler) {
              originalRemoveEventListener.call(this, eventName, originalEventHandler, options);
            }
          }
        } catch {
        }
        return originalRemoveEventListener.call(this, eventName, fn, options);
      };
    });
  }
  function isEventListenerObject(obj) {
    return typeof obj.handleEvent === "function";
  }
  function unregisterOriginalCallback(target, eventName, fn) {
    if (target && typeof target === "object" && "removeEventListener" in target && typeof target.removeEventListener === "function") {
      target.removeEventListener(eventName, fn);
    }
  }

  // node_modules/@sentry/browser/build/npm/esm/prod/integrations/browsersession.js
  var browserSessionIntegration = defineIntegration((options = {}) => {
    const lifecycle = options.lifecycle ?? "page";
    return {
      name: "BrowserSession",
      setupOnce() {
        if (typeof WINDOW3.document === "undefined") {
          DEBUG_BUILD3 && debug.warn("Using the `browserSessionIntegration` in non-browser environments is not supported.");
          return;
        }
        startSession({ ignoreDuration: true });
        let initialSessionSent = false;
        whenIdleOrHidden(() => {
          if (!initialSessionSent) {
            captureSession();
            initialSessionSent = true;
          }
        });
        const isolationScope = getIsolationScope();
        let previousUser = isolationScope.getUser();
        isolationScope.addScopeListener((scope) => {
          const maybeNewUser = scope.getUser();
          if (previousUser?.id !== maybeNewUser?.id || previousUser?.ip_address !== maybeNewUser?.ip_address) {
            previousUser = maybeNewUser;
            if (initialSessionSent) {
              captureSession();
            }
          }
        });
        if (lifecycle === "route") {
          addHistoryInstrumentationHandler(({ from, to }) => {
            if (from !== to) {
              startSession({ ignoreDuration: true });
              captureSession();
              initialSessionSent = true;
            }
          });
        }
      }
    };
  });

  // node_modules/@sentry/browser/build/npm/esm/prod/integrations/culturecontext.js
  var INTEGRATION_NAME8 = "CultureContext";
  var _cultureContextIntegration = (() => {
    return {
      name: INTEGRATION_NAME8,
      preprocessEvent(event) {
        const culture = getCultureContext();
        if (culture) {
          event.contexts = {
            ...event.contexts,
            culture: { ...culture, ...event.contexts?.culture }
          };
        }
      },
      processSegmentSpan(span) {
        const culture = getCultureContext();
        if (culture) {
          safeSetSpanJSONAttributes(span, {
            "culture.locale": culture.locale,
            "culture.timezone": culture.timezone,
            "culture.calendar": culture.calendar
          });
        }
      }
    };
  });
  var cultureContextIntegration = defineIntegration(_cultureContextIntegration);
  function getCultureContext() {
    try {
      const intl = WINDOW3.Intl;
      if (!intl) {
        return void 0;
      }
      const options = intl.DateTimeFormat().resolvedOptions();
      return {
        locale: options.locale,
        timezone: options.timeZone,
        calendar: options.calendar
      };
    } catch {
      return void 0;
    }
  }

  // node_modules/@sentry/browser/build/npm/esm/prod/integrations/globalhandlers.js
  var INTEGRATION_NAME9 = "GlobalHandlers";
  var _globalHandlersIntegration = ((options = {}) => {
    const _options = {
      onerror: true,
      onunhandledrejection: true,
      ...options
    };
    return {
      name: INTEGRATION_NAME9,
      setupOnce() {
        Error.stackTraceLimit = 50;
      },
      setup(client) {
        if (_options.onerror) {
          _installGlobalOnErrorHandler(client);
          globalHandlerLog("onerror");
        }
        if (_options.onunhandledrejection) {
          _installGlobalOnUnhandledRejectionHandler(client);
          globalHandlerLog("onunhandledrejection");
        }
      }
    };
  });
  var globalHandlersIntegration = defineIntegration(_globalHandlersIntegration);
  function _installGlobalOnErrorHandler(client) {
    addGlobalErrorInstrumentationHandler((data) => {
      const { stackParser, attachStacktrace } = getOptions();
      if (getClient() !== client || shouldIgnoreOnError(data)) {
        return;
      }
      const { msg, url, line, column, error: error2 } = data;
      const event = _enhanceEventWithInitialFrame(
        eventFromUnknownInput2(stackParser, error2 || msg, void 0, attachStacktrace, false),
        url,
        line,
        column
      );
      event.level = "error";
      captureEvent(event, {
        originalException: error2,
        mechanism: {
          handled: false,
          type: "auto.browser.global_handlers.onerror"
        }
      });
    });
  }
  function _installGlobalOnUnhandledRejectionHandler(client) {
    addGlobalUnhandledRejectionInstrumentationHandler((e) => {
      const { stackParser, attachStacktrace } = getOptions();
      if (getClient() !== client || shouldIgnoreOnError()) {
        return;
      }
      const error2 = _getUnhandledRejectionError(e);
      const event = isPrimitive(error2) ? _eventFromRejectionWithPrimitive(error2) : eventFromUnknownInput2(stackParser, error2, void 0, attachStacktrace, true);
      event.level = "error";
      captureEvent(event, {
        originalException: error2,
        mechanism: {
          handled: false,
          type: "auto.browser.global_handlers.onunhandledrejection"
        }
      });
    });
  }
  function _getUnhandledRejectionError(error2) {
    if (isPrimitive(error2)) {
      return error2;
    }
    try {
      if ("reason" in error2) {
        return error2.reason;
      }
      if ("detail" in error2 && "reason" in error2.detail) {
        return error2.detail.reason;
      }
    } catch {
    }
    return error2;
  }
  function _eventFromRejectionWithPrimitive(reason) {
    return {
      exception: {
        values: [
          {
            type: "UnhandledRejection",
            // String() is needed because the Primitive type includes symbols (which can't be automatically stringified)
            value: `Non-Error promise rejection captured with value: ${String(reason)}`
          }
        ]
      }
    };
  }
  function _enhanceEventWithInitialFrame(event, url, lineno, colno) {
    const e = event.exception = event.exception || {};
    const ev = e.values = e.values || [];
    const ev0 = ev[0] = ev[0] || {};
    const ev0s = ev0.stacktrace = ev0.stacktrace || {};
    const ev0sf = ev0s.frames = ev0s.frames || [];
    if (ev0sf.length === 0) {
      ev0sf.push({
        colno,
        lineno,
        filename: getFilenameFromUrl(url) ?? getLocationHref(),
        function: UNKNOWN_FUNCTION,
        in_app: true
      });
    }
    return event;
  }
  function globalHandlerLog(type) {
    DEBUG_BUILD3 && debug.log(`Global Handler attached: ${type}`);
  }
  function getOptions() {
    const client = getClient();
    const options = client?.getOptions() || {
      stackParser: () => [],
      attachStacktrace: false
    };
    return options;
  }
  function getFilenameFromUrl(url) {
    if (!isString(url) || url.length === 0) {
      return void 0;
    }
    if (url.startsWith("data:")) {
      return `<${stripDataUrlContent(url, false)}>`;
    }
    return url;
  }

  // node_modules/@sentry/browser/build/npm/esm/prod/integrations/httpcontext.js
  var httpContextIntegration = defineIntegration(() => {
    return {
      name: "HttpContext",
      preprocessEvent(event, _hint, client) {
        if (!WINDOW3.navigator && !WINDOW3.location && !WINDOW3.document) {
          return;
        }
        const { url, headers: collectedHeaders } = getHttpRequestData(client);
        const behavior = client.getDataCollectionOptions().httpHeaders.request;
        const userHeaders = Object.entries(event.request?.headers ?? {}).filter(([key]) => !(key in collectedHeaders));
        const headers = {
          ...filterKeyValueData(collectedHeaders, behavior),
          ...Object.fromEntries(userHeaders)
        };
        event.request = {
          url: filterCollectedUrl(url, client),
          ...event.request,
          ...Object.keys(headers).length > 0 ? { headers } : { headers: void 0 }
        };
      },
      processSpan(span, client) {
        if (!WINDOW3.navigator && !WINDOW3.location && !WINDOW3.document) {
          return;
        }
        const reqData = getHttpRequestData(client);
        const headers = filterKeyValueData(
          reqData.headers,
          client.getDataCollectionOptions().httpHeaders.request
        );
        const referer = headers["Referer"];
        const { hostname, protocol } = WINDOW3.location || {};
        safeSetSpanJSONAttributes(span, {
          // This attribute is used by the "Filter out events from legacy browsers and crawlers" features on the Sentry backend.
          // Therefore, it's set on every span.
          [mb]: headers["User-Agent"],
          // Likewise for the "Filter out localhost events" feature. Deliberately inlined rather than
          // sharing the server-side helper, which costs bundle size for request headers and IPs that
          // don't exist here. Mirrors Relay's localhost filter (relay-filter/src/localhost.rs).
          [Jd]: protocol === "file:" || hostname === "localhost" || hostname === "127.0.0.1" || // `location.hostname` keeps the brackets for IPv6 hosts, so this is `[::1]`, not `::1`.
          hostname === "[::1]" || !!hostname?.endsWith(".localhost"),
          // These attributes, we only need on the segment span (analogous to the `request` context for events)
          ...span.is_segment && {
            // Coerce empty string to undefined so the helper's nullish check drops it,
            // rather than writing an empty `url.full` attribute onto the span.
            [ib]: span.attributes?.[mm] !== "http.client" ? filterCollectedUrl(reqData.url) : void 0,
            [`${Po}.referer`]: referer ? [referer] : void 0
          }
        });
      }
    };
  });

  // node_modules/@sentry/browser/build/npm/esm/prod/integrations/linkederrors.js
  var DEFAULT_KEY = "cause";
  var DEFAULT_LIMIT = 5;
  var INTEGRATION_NAME10 = "LinkedErrors";
  var _linkedErrorsIntegration = ((options = {}) => {
    const limit = options.limit || DEFAULT_LIMIT;
    const key = options.key || DEFAULT_KEY;
    return {
      name: INTEGRATION_NAME10,
      preprocessEvent(event, hint, client) {
        const options2 = client.getOptions();
        applyAggregateErrorsToEvent(
          // This differs from the LinkedErrors integration in core by using a different exceptionFromError function
          exceptionFromError2,
          options2.stackParser,
          key,
          limit,
          event,
          hint
        );
      }
    };
  });
  var linkedErrorsIntegration = defineIntegration(_linkedErrorsIntegration);

  // node_modules/@sentry/browser/build/npm/esm/prod/normalizeStringifyValue.js
  var HTML_ELEMENT_CONSTRUCTOR_NAME_REGEX = /^HTML(\w*)Element$/;
  function normalizeStringifyValue(value) {
    if (typeof window !== "undefined" && value === window) {
      return "[Window]";
    }
    if (typeof document !== "undefined" && value === document) {
      return "[Document]";
    }
    if (isElement2(value)) {
      const objName = getConstructorName2(value);
      if (HTML_ELEMENT_CONSTRUCTOR_NAME_REGEX.test(objName)) {
        return `[HTMLElement: ${htmlTreeAsString(value)}]`;
      }
    }
    return void 0;
  }
  function getConstructorName2(value) {
    const prototype = Object.getPrototypeOf(value);
    return prototype?.constructor ? prototype.constructor.name : "null prototype";
  }

  // node_modules/@sentry/browser/build/npm/esm/prod/utils/detectBrowserExtension.js
  function checkAndWarnIfIsEmbeddedBrowserExtension() {
    if (_isEmbeddedBrowserExtension()) {
      if (DEBUG_BUILD3) {
        consoleSandbox(() => {
          console.error(
            "[Sentry] You cannot use Sentry.init() in a browser extension, see: https://docs.sentry.io/platforms/javascript/best-practices/browser-extensions/"
          );
        });
      }
      return true;
    }
    return false;
  }
  function _isEmbeddedBrowserExtension() {
    if (typeof WINDOW3.window === "undefined") {
      return false;
    }
    const _window = WINDOW3;
    if (_window.nw) {
      return false;
    }
    const extensionObject = _window["chrome"] || _window["browser"];
    if (!extensionObject?.runtime?.id) {
      return false;
    }
    const href = getLocationHref();
    const isDedicatedExtensionPage = WINDOW3 === WINDOW3.top && /^(?:chrome-extension|moz-extension|ms-browser-extension|safari-web-extension):\/\//.test(href);
    return !isDedicatedExtensionPage;
  }

  // node_modules/@sentry/browser/build/npm/esm/prod/sdk.js
  function getDefaultIntegrations(_options) {
    return [
      eventFiltersIntegration(),
      functionToStringIntegration(),
      conversationIdIntegration(),
      browserApiErrorsIntegration(),
      breadcrumbsIntegration(),
      consoleIntegration(),
      globalHandlersIntegration(),
      linkedErrorsIntegration(),
      dedupeIntegration(),
      httpContextIntegration(),
      cultureContextIntegration(),
      browserSessionIntegration()
    ];
  }
  function init(options = {}) {
    const shouldDisableBecauseIsBrowserExtenstion = !options.skipBrowserExtensionCheck && checkAndWarnIfIsEmbeddedBrowserExtension();
    let defaultIntegrations = options.defaultIntegrations == null ? getDefaultIntegrations() : options.defaultIntegrations;
    const integrations = getIntegrationsToSetup({
      integrations: options.integrations,
      defaultIntegrations
    });
    const clientOptions = {
      ...options,
      enabled: shouldDisableBecauseIsBrowserExtenstion ? false : options.enabled,
      stackParser: stackParserFromStackParserOptions(options.stackParser || defaultStackParser),
      integrations,
      transport: options.transport || makeFetchTransport
    };
    setNormalizeStringifier(normalizeStringifyValue);
    return initAndBind(BrowserClient, clientOptions);
  }

  // statisticscore/app.jsx
  init({
    dsn: "https://9e7d8f743b524be1941923c21df3e747@bugsink.jasmine.uber.space/1",
    // Alternatively, use `process.env.npm_package_version` for a dynamic release version
    // if your build tool supports it.
    release: "statistics@latest",
    integrations: [],
    tracesSampleRate: 0
  });
})();
/*! Bundled license information:

@sentry/core/build/esm/utils/env.js:
  (*! __SENTRY_SDK_SOURCE__ *)
*/
