import { normalizeDomain, normalizeName } from '../sitesUtils';

describe('normalizeDomain', () => {
  test('should normalize a regular domain', () => {
    expect(normalizeDomain('https://example.com')).toBe('example_com');
  });

  test('should remove www prefix', () => {
    expect(normalizeDomain('https://www.example.com')).toBe('example_com');
  });

  test('should handle subdomains', () => {
    expect(normalizeDomain('https://sub.example.com')).toBe('sub_example_com');
  });

  test('should replace special characters with underscores', () => {
    expect(normalizeDomain('https://example-site.com')).toBe('example_site_com');
  });

  test('should handle domains with ports', () => {
    expect(normalizeDomain('https://example.com:8080')).toBe('example_com');
  });
  test('should handle domains with ports', () => {
    expect(normalizeDomain('http://example.com:8080')).toBe('example_com');
  });

  test('should handle domains with query parameters', () => {
    expect(normalizeDomain('https://example.com?param=value')).toBe('example_com');
  });

  test('should handle domains with paths', () => {
    expect(normalizeDomain('https://example.com/path/to/resource')).toBe('example_com');
  });
});

describe('normalizeName', () => {
  test('should extract the last part of the path', () => {
    expect(normalizeName('https://example.com/path/to/resource')).toBe('resource');
  });

  test('should remove trailing slash', () => {
    expect(normalizeName('https://example.com/path/to/resource/')).toBe('resource');
  });

  test('should use "root" for empty paths', () => {
    expect(normalizeName('https://example.com')).toBe('root');
  });

  test('should use "root" for root path', () => {
    expect(normalizeName('https://example.com/')).toBe('root');
  });

  test('should replace special characters with underscores', () => {
    expect(normalizeName('https://example.com/path/to/special-resource')).toBe('special_resource');
  });

  test('should handle query parameters', () => {
    expect(normalizeName('https://example.com/resource?param=value')).toBe('resource');
  });

  test('should handle hash fragments', () => {
    expect(normalizeName('https://example.com/resource#section')).toBe('resource');
  });

  test('should handle complex URLs', () => {
    expect(normalizeName('https://sub.example.com:8080/path/to/resource?param=value#section')).toBe('resource');
  });
});