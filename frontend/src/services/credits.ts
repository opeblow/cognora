import { api } from "./api"
import type { CreditBalance } from "@/types"

export const creditService = {
  getBalance: () => api.get<CreditBalance>("/credits/balance"),
}
