import { Input } from "@/components/ui/input"
import { Button } from "./ui/button"

const Search = () => {
  return (
    <form action="" className="flex">
      <Input type="text" placeholder="Поиск" />
      <Button type="submit">Поиск</Button>
    </form>
  )
}

export default Search