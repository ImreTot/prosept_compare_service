import { Label } from "@/components/ui/label"
import { Checkbox } from "@/components/ui/checkbox"

const Aside = () => {
  const categories = [
    { name: 'Антимикробная обработка', children: [{ name: 'Ванные комнаты' }, { name: 'Личная гигиена' }, { name: 'Универсальные средства' }] },
    { name: 'Профессиональные моющие средства' },
    { name: 'Защита древесины' },
    { name: 'Строительная химия' },
    { name: 'Бытовая химия' },
  ]
  const dealers = ['Ozon', 'Yandex', 'Wildberries']
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
            // <div className="hover:text-pink-300 transition-colors cursor-pointer">
            // <h2>{dealer}</h2>
            // </div>
          ))}
        </div>
      </section>
      <section className="mt-4">
        <p className="font-bold mb-2 text-lg">Даты записей</p>
        <input type="date" id="start" name="trip-start" value="2018-07-22" min="2018-01-01" max="2018-12-31" />
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