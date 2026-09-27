export function total(subtotal: number, discount: number): number {
  const result = subtotal - discount;
  if (result < 0) throw new Error("negative total");
  return result;
}
