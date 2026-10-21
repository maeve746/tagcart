export const formatDate = (value, short = false) => new Intl.DateTimeFormat('en-US', {
  month: short ? 'short' : 'long', day: 'numeric', year: 'numeric',
}).format(new Date(`${value}T00:00:00`))

export const formatCurrency = (value) => new Intl.NumberFormat('en-US', {
  style: 'currency', currency: 'USD', maximumFractionDigits: 0,
}).format(value)
