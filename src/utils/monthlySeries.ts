import type { TransactionDto } from '@/services/transactionService';

export interface MonthBucket {
  key: string;
  /** "nov" */
  label: string;
  /** "novembro de 2026" */
  fullLabel: string;
  income: number;
  expense: number;
  net: number;
  count: number;
}

type Entry = Pick<TransactionDto, 'date' | 'amount' | 'entryType'>;

/** Agrupa lancamentos nos ultimos `months` meses (o ultimo e o mes de `now`), incluindo meses vazios. */
export const buildMonthlySeries = (transactions: Entry[], months: number, now = new Date()): MonthBucket[] => {
  const buckets = Array.from({ length: months }, (_, index) => {
    const date = new Date(now.getFullYear(), now.getMonth() - (months - 1 - index), 1);
    return {
      key: `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`,
      label: date.toLocaleDateString('pt-BR', { month: 'short' }).replace('.', ''),
      fullLabel: date.toLocaleDateString('pt-BR', { month: 'long', year: 'numeric' }).replace(/^./, (c) => c.toUpperCase()),
      income: 0,
      expense: 0,
      net: 0,
      count: 0,
    };
  });
  const byKey = new Map(buckets.map((bucket) => [bucket.key, bucket]));

  for (const transaction of transactions) {
    const bucket = byKey.get(transaction.date.slice(0, 7));
    if (!bucket) continue;
    bucket.count += 1;
    if (transaction.entryType === 'credit') bucket.income += transaction.amount;
    else bucket.expense += transaction.amount;
  }
  for (const bucket of buckets) bucket.net = bucket.income - bucket.expense;
  return buckets;
};

/** Arredonda o teto de um eixo para um numero "redondo" (1, 2, 2.5, 5 x 10^n). */
export const niceCeil = (value: number): number => {
  if (value <= 0) return 1;
  const exponent = Math.floor(Math.log10(value));
  const base = 10 ** exponent;
  const fraction = value / base;
  const step = [1, 2, 2.5, 5, 10].find((candidate) => fraction <= candidate) ?? 10;
  return step * base;
};
