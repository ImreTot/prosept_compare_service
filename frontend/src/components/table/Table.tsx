import { Data, columns } from "./columns"
import { DataTable } from "./data-table"

export default function Table() {
  const data: Data[] = [
    {
      id: "728ed52f",
      dealerName: "Item 1",
      dealer: "Dealer 1",
      manufacturerId: 123,
      manufacturerName: 'Smbd 1',
      category: 'Bio stuff',
      dateMarkup: '2023',
      dateParsing: '2023',
      matched: '√',
      recommendedPrice: '1800p',
      dealerPrice: '1400р',
      url: 'https://google.com'
    },
    // {
    //   id: "728ed52f",
    //   dealerName: "Item 2",
    //   dealer: "Dealer 2",
    //   manufacturerId: 156,
    //   manufacturerName: 'Smbd 2',
    //   category: 'Other stuff',
    //   dateMarkup: '2024',
    //   dateParsing: '2024',
    //   matched: '×',
    //   recommendedPrice: '1800p',
    //   dealerPrice: '1400р'
    // },
    // {
    //   id: "728ed52f",
    //   dealerName: "Item 3",
    //   dealer: "Dealer 3",
    //   manufacturerId: 116,
    //   manufacturerName: 'Smbd 3',
    //   category: 'Cleaning',
    //   dateMarkup: '2022',
    //   dateParsing: '2022',
    //   matched: '×',
    //   recommendedPrice: '1800p',
    //   dealerPrice: '1400р'
    // },
  ]

  return (
    <div>
      <DataTable columns={columns} data={data} />
    </div>
  )
}