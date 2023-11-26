import { Label } from "@/components/ui/label"
import { Checkbox } from "@/components/ui/checkbox"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Calendar } from "@/components/ui/calendar"
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover"
import { addDays, format } from "date-fns"
import { Calendar as CalendarIcon } from "lucide-react"
import { DateRange } from "react-day-picker"
import { useState } from 'react'

const Aside = () => {
  const categories = [
    { name: 'Антимикробная обработка', children: [{ name: 'Ванные комнаты' }, { name: 'Личная гигиена' }, { name: 'Универсальные средства' }] },
    { name: 'Профессиональные моющие средства' },
    { name: 'Защита древесины' },
    { name: 'Строительная химия' },
    { name: 'Бытовая химия' },
  ]
  const dealers = ['Ozon', 'Yandex', 'Wildberries']

  const [date, setDate] = useState<DateRange | undefined>({
    from: new Date(2023, 10, 27),
    to: addDays(new Date(2023, 10, 27), 1),
  })

  return (
    <aside className="mr-4">
      <section>
        <p className="font-bold mb-2 text-lg">Категория</p>
        {categories.map((category, index) => (
          <div key={index} className="mb-1 text-[0.9rem]">
            <h2 className="hover:text-pink-300 transition-colors cursor-pointer">{category.name}</h2>
            {category.children && (
              <ul className="ml-4">
                {category.children.map((child, childIndex) => (
                  <li key={childIndex} className="hover:text-pink-300 transition-colors cursor-pointer">{child.name}</li>
                ))}
              </ul>
            )}
          </div>
        ))}
      </section>
      <section className="mt-4">
        <p className="font-bold mb-2 text-lg">Дилеры</p>
        <div className="grid gap-2">
          {dealers.map((dealer) => (
            <div key={dealer} className="flex items-center space-x-2">
              <Checkbox id={dealer} />
              <Label htmlFor={dealer}>{dealer}</Label>
            </div>
          ))}
        </div>
      </section>
      <section className="mt-4">
        <p className="font-bold mb-2 text-lg">Даты записей</p>
        <div className="grid gap-2">
          <Popover>
            <PopoverTrigger asChild>
              <Button
                id="date"
                variant={"outline"}
                className={cn(
                  "w-[300px] justify-start text-left font-normal",
                  !date && "text-muted-foreground"
                )}
              >
                <CalendarIcon className="mr-2 h-4 w-4" />
                {date?.from ? (
                  date.to ? (
                    <>
                      {format(date.from, "LLL dd, y")} -{" "}
                      {format(date.to, "LLL dd, y")}
                    </>
                  ) : (
                    format(date.from, "LLL dd, y")
                  )
                ) : (
                  <span>Pick a date</span>
                )}
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-auto p-0" align="start">
              <Calendar
                initialFocus
                mode="range"
                defaultMonth={date?.from}
                selected={date}
                onSelect={setDate}
                numberOfMonths={2}
              />
            </PopoverContent>
          </Popover>
        </div>
      </section>

      <section className="mt-4">
        <p className="font-bold mb-2 text-lg">Статус</p>
        <div className="flex items-center space-x-2">
          <Checkbox id="terms" />
          <Label htmlFor="terms">Сопоставлено</Label>
        </div>
      </section>
    </aside>
  )
}

export default Aside