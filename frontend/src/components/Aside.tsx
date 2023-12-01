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
  const dealers = ['Ozon', 'Yandex', 'Wildberries']

  const [date, setDate] = useState<DateRange | undefined>({
    from: new Date(2023, 10, 27),
    to: addDays(new Date(2023, 10, 27), 1),
  })

  return (
    <aside className="mr-4">
      <section >
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
                      {date.from.toLocaleDateString('ru', { month: 'short', day: 'numeric', year: 'numeric' })} -{" "}
                      {date.to.toLocaleDateString('ru', { month: 'short', day: 'numeric', year: 'numeric' })}
                      {/* {format(date.to, "LLL dd, y")} */}
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
        <div className="grid gap-2">
          <div className="flex items-center space-x-2">
            <Checkbox id="match" />
            <Label htmlFor="match">Сопоставлено</Label>
          </div>
          <div className="flex items-center space-x-2">
            <Checkbox id="not-match" />
            <Label htmlFor="not-match">Несопоставлено</Label>
          </div>
          <div className="flex items-center space-x-2">
            <Checkbox id="not-match" />
            <Label htmlFor="not-match">Ненайденные</Label>
          </div>
        </div>
      </section>
      <section className="mt-4">
        <p className="font-bold mb-2 text-lg">Количество позиций</p>
        <div className="grid gap-2">
          <div className="flex items-center space-x-2">
            <Checkbox id="3" />
            <Label htmlFor="3">3</Label>
          </div>
          <div className="flex items-center space-x-2">
            <Checkbox id="5" />
            <Label htmlFor="5">5</Label>
          </div>
          <div className="flex items-center space-x-2">
            <Checkbox id="10" />
            <Label htmlFor="10">10</Label>
          </div>
        </div>
      </section>
    </aside>
  )
}

export default Aside