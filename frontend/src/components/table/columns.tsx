import { ColumnDef } from "@tanstack/react-table"
import { ArrowUpDown } from "lucide-react"
import { Button } from "../ui/button"

export type Payment = {
  id: string
  dealerId: number
  dealerName: string
  dealer: string,
  manufacturerId: number,
  manufacturerName: string,
  category: string,
  matched: string,
  date: string
}

export const columns: ColumnDef<Payment>[] = [
  {
    accessorKey: "dealer",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Дилер
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      )
    },
  },
  {
    accessorKey: "dealerId",
    header: "Артикул дилера",
  },
  {
    accessorKey: "dealerName",
    header: "Наименование дилера",
  },
  {
    accessorKey: "manufacturerId",
    header: "Артикул производителя",
  },
  {
    accessorKey: "manufacturerName",
    header: "Название производителя",
  },
  {
    accessorKey: "category",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Категория
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      )
    },
  },
  {
    accessorKey: "matched",
    header: "Сопоставлено",
  },
  {
    accessorKey: "date",
    header: "Дата",
  },
]