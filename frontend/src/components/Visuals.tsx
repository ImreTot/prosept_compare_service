const Visuals = () => {
  return (
    <div className="flex flex-col flex-1 justify-between">
      Visuals
      <div className="flex items-center justify-evenly">
        <button type="button" aria-label="да">Да</button>
        <button type="button" aria-label="нет">Нет</button>
        <button type="button" aria-label="отложить">Отложить</button>
      </div>
    </div>
  )
}

export default Visuals