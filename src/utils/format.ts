const currencyFormatter = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' });

export const formatCurrency = (value: number) => currencyFormatter.format(value);

/** Valor com sinal: "+ R$ 10,00" para entradas e "- R$ 10,00" para saídas. */
export const formatSignedAmount = (amount: number, entryType: string) =>
  `${entryType === 'credit' ? '+' : '-'} ${formatCurrency(amount)}`;

/** Eixo de gráficos: "R$ 1,5k" ou "R$ 1,2 mi". */
export const formatCompactCurrency = (value: number) => {
  const abs = Math.abs(value);
  if (abs >= 1_000_000) return `R$ ${(value / 1_000_000).toLocaleString('pt-BR', { maximumFractionDigits: 1 })} mi`;
  if (abs >= 1_000) return `R$ ${(value / 1_000).toLocaleString('pt-BR', { maximumFractionDigits: 1 })}k`;
  return `R$ ${Math.round(value)}`;
};

export const formatDateTime = (value: string) => {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString('pt-BR');
};

/** Datas ISO "YYYY-MM-DD" vindas do backend, sem conversão de fuso. */
export const formatIsoDate = (value: string | null | undefined) => {
  if (!value) return '-';
  const [year, month, day] = value.split('-');
  return `${day}/${month}/${year}`;
};

const ISO_DATE = /^(\d{4})-(\d{2})-(\d{2})$/;

/** "YYYY-MM-DD" vira meia-noite no fuso local (new Date(iso) leria UTC e recuaria um dia no Brasil). */
export const parseIsoDate = (value: string): Date => {
  const match = ISO_DATE.exec(value);
  return match ? new Date(Number(match[1]), Number(match[2]) - 1, Number(match[3])) : new Date(value);
};

const startOfDay = (date: Date) => new Date(date.getFullYear(), date.getMonth(), date.getDate()).getTime();

/** "Hoje", "Ontem" ou "12 set." (com ano opcional). Horario so quando o valor carrega hora. */
export const formatRelativeDate = (value: string, withYear = false) => {
  const date = parseIsoDate(value);
  const diffDays = Math.round((startOfDay(new Date()) - startOfDay(date)) / 86_400_000);
  const time = ISO_DATE.test(value)
    ? ''
    : `, ${date.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}`;

  if (diffDays === 0) return `Hoje${time}`;
  if (diffDays === 1) return `Ontem${time}`;
  return date.toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: 'short',
    ...(withYear ? { year: 'numeric' } : {}),
  });
};

/** "12 set" para colunas de data de tabela. */
export const formatShortDate = (value: string) =>
  parseIsoDate(value).toLocaleDateString('pt-BR', { day: '2-digit', month: 'short' }).replace(' de ', ' ').replace('.', '');

/** Hoje no calendario local, "YYYY-MM-DD". */
export const todayIso = () => {
  const now = new Date();
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;
};
