export function isObject(value) {
  return value !== null
    && typeof value === 'object'
    && !isArray(value);
}

export function isArray(value) {
  return Array.isArray(value);
}

export function isUndefined(value) {
  return typeof value === 'undefined';
}

export function isString(value) {
  return typeof value === 'string';
}

export function isNumber(value) {
  return typeof value === 'number';
}

export function isBoolean(value) {
  return typeof value === 'boolean';
}

export function isSimple(data: any) {
  return isBoolean(data)
    || isString(data)
    || isNumber(data)
    || isUndefined(data)
    || null === data;
}

export function formatValue(data: any) {
  if (false === data) {
    return 'False';
  }
  if (true === data) {
    return 'True';
  }
  if (null === data) {
    return 'None';
  }
  return data;
}
