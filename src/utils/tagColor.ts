/**
 * Tags usam tons dessaturados que convivem com o esmeralda da marca: nenhuma
 * cor compete com os valores de entrada (verde) e saida (vermelho).
 */
const PALETTE = [
  '#5fb99a',
  '#7ea9c9',
  '#c9a96b',
  '#b48da9',
  '#9aa6b2',
  '#c98f78',
  '#93b878',
  '#8896d0',
];

export function colorForTag(id: string): string {
  let hash = 0;
  for (let i = 0; i < id.length; i++) {
    hash = (hash * 31 + id.charCodeAt(i)) >>> 0;
  }
  return PALETTE[hash % PALETTE.length] as string;
}
