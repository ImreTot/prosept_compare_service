
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
    <aside className="flex-1">
      <p className="mb-4">Категория</p>
      <div>
        {categories.map((category, index) => (
          <div key={index}>
            <h2>{category.name}</h2>
            {category.children && (
              <ul className="ml-4">
                {category.children.map((child, childIndex) => (
                  <li key={childIndex}>{child.name}</li>
                ))}
              </ul>
            )}
          </div>
        ))}
      </div>
      <div className="mt-10">
        <p>Дилеры</p>
        {dealers.map((dealer) => (
          <div key={dealer}>
            <h2>{dealer}</h2>
          </div>
        ))}
      </div>
      <div>

        <input type="date" id="start" name="trip-start" value="2018-07-22" min="2018-01-01" max="2018-12-31" />
      </div>
      <div>
        сопоставлено
        <input type="checkbox" />
      </div>
    </aside>
  )
}

export default Aside