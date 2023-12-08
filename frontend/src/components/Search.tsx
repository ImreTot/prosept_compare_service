import { Input } from "@/components/ui/input"
import { Button } from "./ui/button"
import { SearchIcon } from "lucide-react"

const Search = () => {
  return (
    <form action="" className="flex items-center gap-1">
      <Input type="text" placeholder="Поиск" className="text-lg py-6" />
      <Button type="submit" className="py-6"><SearchIcon /></Button>
    </form>
  )
}

export default Search