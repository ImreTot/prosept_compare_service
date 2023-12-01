import { Payment, columns } from "./columns"
import { DataTable } from "./data-table"

export default function Table() {
  const data: Payment[] = [
    {
      id: "728ed52f",
      dealerId: 100,
      dealerName: "Item 1",
      dealer: "Dealer 1",
      manufacturerId: 123,
      manufacturerName: 'Smbd 1',
      category: 'Bio stuff',
      date: '2023',
      matched: '√'
    },
    {
      id: "728ed52f",
      dealerId: 66,
      dealerName: "Item 2",
      dealer: "Dealer 2",
      manufacturerId: 156,
      manufacturerName: 'Smbd 2',
      category: 'Other stuff',
      date: '2024',
      matched: '×'
    },
    {
      id: "728ed52f",
      dealerId: 88,
      dealerName: "Item 3",
      dealer: "Dealer 3",
      manufacturerId: 116,
      manufacturerName: 'Smbd 3',
      category: 'Cleaning',
      date: '2022',
      matched: '×'
    },
  ]

  return (
    <div className="container mx-auto">
      <DataTable columns={columns} data={data} />
    </div>
  )
}