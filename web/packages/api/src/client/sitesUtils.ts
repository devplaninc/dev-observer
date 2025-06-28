export function normalizeDomain(url: string): string {
  const parsed = new URL(url);
  let domain = parsed.hostname;
  // Remove www. prefix if present
  if (domain.startsWith('www.')) {
    domain = domain.substring(4);
  }
  // Replace non-alphanumeric characters with underscores
  domain = domain.replace(/[^a-zA-Z0-9]/g, '_');
  return domain;
}

export function normalizeName(url: string): string {
  const parsed = new URL(url);
  let path = parsed.pathname;
  // Remove trailing slash
  if (path.endsWith('/')) {
    path = path.slice(0, -1);
  }
  // Use the last part of the path as the name, or 'root' if empty
  let name = path ? path.split('/').pop() || 'root' : 'root';
  // Replace non-alphanumeric characters with underscores
  name = name.replace(/[^a-zA-Z0-9]/g, '_');
  // If name is empty, use 'root'
  if (!name) {
    name = 'root';
  }
  return name;
}