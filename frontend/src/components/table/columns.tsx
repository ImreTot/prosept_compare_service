import { ColumnDef } from "@tanstack/react-table"
import { ArrowUpDown } from "lucide-react"
import { Button } from "../ui/button"

export type Data = {
  id: string
  dealer: string,
  dealerName: string
  dealerPrice: string
  matched: string,
  dateMarkup: string
  dateParsing: string
  manufacturerId: number,
  manufacturerName: string,
  category: string,
  recommendedPrice: string,
  url: string
}

export const columns: ColumnDef<Data>[] = [
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
    accessorKey: "dealerName",
    header: "Назв. дилера",
  },
  {
    accessorKey: "dealerPrice",
    header: "Цена",
  },
  {
    accessorKey: "url",
    header: 'Ссылка',
    cell: ({ row }) => {
      const name = row.getValue('dealerName') as string
      const url = row.getValue('url') as string
      return <a href={url} className="">{name}</a>
    }
  },
  {
    accessorKey: "matched",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Соп.
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      )
    },
  },
  {
    accessorKey: "dateParsing",
    header: "Дата парсинга",
  },
  {
    accessorKey: "manufacturerId",
    header: "Артикул",
  },
  {
    accessorKey: "manufacturerName",
    header: "Назв. 1С",
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
    accessorKey: "recommendedPrice",
    header: "Рек. цена",
  },
  {
    accessorKey: "dateMarkup",
    header: "Дата разметки",
  },
]