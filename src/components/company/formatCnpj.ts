/** "11222333000181" -> "11.222.333/0001-81". Valores fora do padrao voltam como vieram. */
export const formatCnpj = (value: string) => {
  const digits = value.replace(/\D/g, '');
  if (digits.length !== 14) return value;
  return digits.replace(/^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})$/, '$1.$2.$3/$4-$5');
};
